from typing import Dict, Any, List
import json
import math
import uuid
import logging
from datetime import datetime
from fastapi import HTTPException

from ..models.patient import DiagnosisRequest, PatientCase
from ..services.model_service import ModelService
from ..utils.medical_knowledge import NeuroMedicalKnowledge
from ..utils.input_sanitizer import sanitizer  # Phase 8-2: Security hardening

# Configure logging
logger = logging.getLogger(__name__)

class NeuroAgent:
    def __init__(self, bedrock_service: ModelService):
        self.bedrock_service = bedrock_service
        self.knowledge_base = NeuroMedicalKnowledge()

    async def analyze_case(self, request: DiagnosisRequest) -> Dict[str, Any]:
        """Analyze patient case and provide neurological diagnosis

        Args:
            request: DiagnosisRequest containing patient information and symptoms

        Returns:
            Dict containing diagnosis results

        Raises:
            HTTPException: 400 if validation fails
        """

        # Validate input before processing
        self._validate_diagnosis_request(request)

        case_id = str(uuid.uuid4())

        # Prepare context for AI analysis
        context = self._prepare_medical_context(request)

        # Generate diagnosis using Bedrock AgentCore
        diagnosis_result = await self._generate_diagnosis(context)

        # Enhance with medical knowledge base
        enhanced_result = self._enhance_with_knowledge(diagnosis_result, request)

        return {
            "case_id": case_id,
            "diagnosis": enhanced_result["diagnosis"],
            "confidence": enhanced_result["confidence"],
            "recommendations": enhanced_result["recommendations"],
            "risk_factors": enhanced_result["risk_factors"],
            "next_steps": enhanced_result["next_steps"]
        }

    def _validate_diagnosis_request(self, request: DiagnosisRequest) -> None:
        """
        Validate diagnosis request input

        Args:
            request: DiagnosisRequest to validate

        Raises:
            HTTPException: 400 if validation fails
        """

        # Validate symptoms list
        if not request.symptoms or len(request.symptoms) == 0:
            raise HTTPException(
                status_code=400,
                detail="Symptoms list cannot be empty. At least one symptom is required for diagnosis."
            )

        # Validate chief complaint
        if not request.chief_complaint or not request.chief_complaint.strip():
            raise HTTPException(
                status_code=400,
                detail="Chief complaint cannot be empty. Please provide the patient's primary concern."
            )

        # Validate history of present illness
        if not request.history_present_illness or not request.history_present_illness.strip():
            raise HTTPException(
                status_code=400,
                detail="History of present illness cannot be empty. Please provide patient history."
            )

        # Validate patient age (additional check beyond Pydantic)
        if request.patient_info.age < 0 or request.patient_info.age > 120:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid patient age: {request.patient_info.age}. Age must be between 0 and 120."
            )

        # Warn if excessive symptoms (but don't fail)
        if len(request.symptoms) > 20:
            logger.warning(
                f"Excessive symptoms detected: {len(request.symptoms)} symptoms provided. "
                f"Consider reviewing for data quality. Maximum recommended: 20 symptoms."
            )

    def _prepare_medical_context(self, request: DiagnosisRequest) -> Dict[str, Any]:
        """Prepare structured medical context for AI analysis"""

        symptoms_text = "; ".join([
            f"{s.name} ({s.severity.value}, {s.duration_days} days)"
            for s in request.symptoms
        ])

        context = {
            "patient_demographics": {
                "age": request.patient_info.age,
                "gender": request.patient_info.gender.value,
                "medical_history": request.patient_info.medical_history
            },
            "presentation": {
                "chief_complaint": request.chief_complaint,
                "symptoms": symptoms_text,
                "history": request.history_present_illness
            },
            "clinical_data": {
                "vital_signs": request.vital_signs,
                "lab_results": request.lab_results,
                "imaging": request.imaging_studies
            }
        }

        return context

    async def _generate_diagnosis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use Bedrock AgentCore to generate neurological diagnosis"""

        prompt = self._build_diagnostic_prompt(context)

        try:
            # Use direct model invocation instead of AgentCore
            # This bypasses the need for a valid Agent ID
            response = await self.bedrock_service.invoke_model_direct(prompt)

            return self._parse_agent_response(response)

        except HTTPException:
            raise
        except Exception:
            logger.exception("Assessment model invocation failed")
            raise HTTPException(status_code=503, detail="Assessment model unavailable")

    def _build_diagnostic_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build structured prompt for neurological diagnosis

        Phase 8-2: Input sanitization to prevent prompt injection
        """

        # ✅ SECURITY: Sanitize all user-provided inputs
        chief_complaint = sanitizer.sanitize_medical_complaint(
            context['presentation']['chief_complaint']
        )
        symptoms = sanitizer.sanitize_text(
            context['presentation']['symptoms'],
            max_length=1000
        )
        history = sanitizer.sanitize_medical_history(
            context['presentation']['history']
        )

        # Sanitize medical history list
        medical_history = sanitizer.sanitize_list(
            context['patient_demographics']['medical_history']
        )

        # Sanitize imaging studies list
        imaging_studies = sanitizer.sanitize_list(
            context['clinical_data']['imaging']
        )

        prompt = f"""You are an expert neurologist AI assistant. Analyze this patient case and provide assessment in JSON format ONLY.

Patient: {context['patient_demographics']['age']}-year-old {context['patient_demographics']['gender']}
History: {', '.join(medical_history) if medical_history else 'No significant history'}
Chief Complaint: {chief_complaint}
Symptoms: {symptoms}
History: {history}
Vital Signs: BP {context['clinical_data']['vital_signs'].get('bp_systolic', '?')}/{context['clinical_data']['vital_signs'].get('bp_diastolic', '?')}, HR {context['clinical_data']['vital_signs'].get('heart_rate', '?')} bpm

RESPOND WITH ONLY VALID JSON, NO OTHER TEXT:
{{
    "differential_diagnoses": [
        {{"condition": "condition name", "confidence": 0.85, "reasoning": "clinical reasoning"}},
        {{"condition": "condition name 2", "confidence": 0.65, "reasoning": "clinical reasoning"}},
        {{"condition": "condition name 3", "confidence": 0.45, "reasoning": "clinical reasoning"}}
    ],
    "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
    "risk_factors": ["risk factor 1", "risk factor 2"],
    "next_steps": ["next step 1", "next step 2"]
}}"""

        return prompt

    def _parse_agent_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate structured output rather than manufacturing a fallback success."""
        try:
            data = json.loads(response["output"]["text"])
            diagnoses = data["differential_diagnoses"]
            if not isinstance(diagnoses, list) or not diagnoses:
                raise ValueError("Missing diagnoses")
            for item in diagnoses:
                if (not isinstance(item, dict) or not isinstance(item.get("condition"), str)
                    or isinstance(item.get("confidence"), bool)
                    or not isinstance(item.get("confidence"), (int, float))
                    or not math.isfinite(item["confidence"])
                    or not 0 <= item["confidence"] <= 1):
                    raise ValueError("Invalid diagnosis")
            for name in ("recommendations", "risk_factors", "next_steps"):
                if not isinstance(data.get(name, []), list) or not all(
                    isinstance(value, str) for value in data.get(name, [])
                ):
                    raise ValueError("Invalid response list")
            return {
                "diagnosis": diagnoses,
                "confidence": self._calculate_overall_confidence(data),
                "recommendations": data.get("recommendations", []),
                "risk_factors": data.get("risk_factors", []),
                "next_steps": data.get("next_steps", []),
            }
        except (TypeError, ValueError, KeyError):
            raise HTTPException(status_code=502, detail="Assessment model returned invalid output")

    def _fallback_diagnosis_parsing(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        return {
            "diagnosis": [
                {
                    "condition": "Comprehensive neurological evaluation required",
                    "confidence": 0.4,
                    "reasoning": "Unable to parse structured response from AI model"
                }
            ],
            "confidence": 0.4,
            "recommendations": [
                "Professional neurological consultation recommended",
                "Complete clinical assessment needed"
            ],
            "risk_factors": [],
            "next_steps": ["Refer to neurology specialist"]
        }

    def _calculate_overall_confidence(self, diagnosis_data: Dict[str, Any]) -> float:
        """Calculate overall confidence score from differential diagnoses"""

        diagnoses = diagnosis_data.get("differential_diagnoses", [])
        if not diagnoses:
            return 0.0

        # Weight by position (first diagnosis has highest weight)
        weights = [0.5, 0.3, 0.2]
        total_confidence = 0.0

        for i, diagnosis in enumerate(diagnoses[:3]):
            weight = weights[i] if i < len(weights) else 0.1
            confidence = diagnosis.get("confidence", 0.0)
            total_confidence += weight * confidence

        return min(total_confidence, 1.0)

    def _enhance_with_knowledge(self, result: Dict[str, Any], request: DiagnosisRequest) -> Dict[str, Any]:
        """
        Enhance diagnosis with medical knowledge base

        This method:
        1. Adds evidence-based treatment guidelines for identified conditions
        2. Checks for drug interactions and adds warnings
        3. Formats interaction warnings with severity levels

        Args:
            result: Initial diagnosis result from AI
            request: Original diagnosis request with patient medications

        Returns:
            Enhanced result with additional medical knowledge
        """

        # Add evidence-based recommendations
        enhanced_recommendations = []
        for diagnosis in result["diagnosis"]:
            condition = diagnosis.get("condition", "")
            recommendations = self.knowledge_base.get_treatment_guidelines(condition)
            enhanced_recommendations.extend(recommendations)

        result["recommendations"].extend(enhanced_recommendations)

        # Add drug interaction checks with detailed warnings
        medications = request.patient_info.current_medications
        interactions = self.knowledge_base.check_drug_interactions(medications)

        if interactions:
            # Add to risk_factors with severity-based formatting
            for interaction in interactions:
                severity = interaction["severity"].upper()
                drug1 = interaction["drug1"]
                drug2 = interaction["drug2"]
                description = interaction["description"]

                # Format warning based on severity
                if interaction["severity"] == "contraindicated":
                    warning = f"⚠️ CONTRAINDICATED: {drug1} + {drug2} - {description}"
                elif interaction["severity"] == "severe":
                    warning = f"⚠️ SEVERE INTERACTION: {drug1} + {drug2} - {description}"
                elif interaction["severity"] == "moderate":
                    warning = f"⚠️ MODERATE INTERACTION: {drug1} + {drug2} - {description}"
                else:
                    warning = f"MINOR INTERACTION: {drug1} + {drug2} - {description}"

                result["risk_factors"].append(warning)

                # Add clinical recommendations from interaction
                if interaction["recommendations"]:
                    # Add first 2 most important recommendations
                    for rec in interaction["recommendations"][:2]:
                        result["recommendations"].append(f"[Drug Interaction] {rec}")

        return result

    def _fallback_diagnosis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based diagnosis when AI agent fails"""

        return {
            "diagnosis": [
                {
                    "condition": "Neurological evaluation required",
                    "confidence": 0.5,
                    "reasoning": "Comprehensive neurological assessment needed based on presenting symptoms"
                }
            ],
            "confidence": 0.5,
            "recommendations": [
                "Complete neurological examination",
                "Consider brain MRI if indicated",
                "Laboratory workup as clinically indicated"
            ],
            "risk_factors": ["Age-related neurological changes"],
            "next_steps": ["Referral to neurology specialist"]
        }

    async def analyze_image(self, image_file) -> Dict[str, Any]:
        """Validate an image then request real educational model observations."""
        import os
        import asyncio
        import boto3
        from datetime import timezone
        media_type = getattr(image_file, "content_type", None)
        if media_type not in {"image/jpeg", "image/png"}:
            raise HTTPException(status_code=415, detail="Only JPEG and PNG images are supported")
        data = await image_file.read(3_750_001)
        if len(data) > 3_750_000:
            raise HTTPException(status_code=413, detail="Image exceeds 3.75 MB")
        valid = ((media_type == "image/png" and data.startswith(b"\x89PNG\r\n\x1a\n"))
                 or (media_type == "image/jpeg" and data.startswith(b"\xff\xd8\xff")))
        if not valid:
            raise HTTPException(status_code=400, detail="Image content does not match its media type")
        analysis = await self.bedrock_service.analyze_image(data, media_type)
        image_id = str(uuid.uuid4())
        storage_location = None
        bucket = os.getenv("S3_BUCKET_NAME")
        if bucket:
            key = f"medical-images/{image_id}.{'png' if media_type == 'image/png' else 'jpg'}"
            try:
                client = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
                await asyncio.to_thread(client.put_object, Bucket=bucket, Key=key, Body=data,
                                        ContentType=media_type, ServerSideEncryption="AES256")
                storage_location = f"s3://{bucket}/{key}"
            except Exception:
                raise HTTPException(status_code=503, detail="Image storage unavailable")
        return {
            "image_id": image_id, "status": "analyzed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "image_metadata": {"filename": image_file.filename, "size_bytes": len(data),
                               "content_type": media_type, "storage_location": storage_location},
            "analysis": analysis,
            "disclaimer": "Educational observations only; qualified professional review required.",
            "processing_metadata": {"model_id": self.bedrock_service.model_id}
        }
