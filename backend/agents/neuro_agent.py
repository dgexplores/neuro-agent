from typing import Dict, Any, List
import json
import uuid
from datetime import datetime
from fastapi import HTTPException

from ..models.patient import DiagnosisRequest, PatientCase
from ..services.bedrock_service import BedrockService
from ..utils.medical_knowledge import NeuroMedicalKnowledge
from ..utils.input_sanitizer import sanitizer  # Phase 8-2: Security hardening

class NeuroAgent:
    def __init__(self, bedrock_service: BedrockService):
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
            # Log warning but allow processing
            # In production, this would use proper logging
            pass

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
            response = await self.bedrock_service.invoke_agent(
                agent_id="neuro-diagnosis-agent",
                session_id=str(uuid.uuid4()),
                input_text=prompt
            )

            return self._parse_agent_response(response)

        except Exception as e:
            # Fallback to rule-based diagnosis
            return self._fallback_diagnosis(context)

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

        prompt = f"""
        You are an expert neurologist AI assistant. Analyze the following patient case and provide a comprehensive neurological assessment.

        PATIENT INFORMATION:
        - Age: {context['patient_demographics']['age']}
        - Gender: {context['patient_demographics']['gender']}
        - Medical History: {', '.join(medical_history) if medical_history else 'None'}

        CLINICAL PRESENTATION:
        - Chief Complaint: {chief_complaint}
        - Symptoms: {symptoms}
        - History of Present Illness: {history}

        CLINICAL DATA:
        - Vital Signs: {json.dumps(context['clinical_data']['vital_signs'])}
        - Lab Results: {json.dumps(context['clinical_data']['lab_results'])}
        - Imaging Studies: {', '.join(imaging_studies) if imaging_studies else 'None'}

        Please provide:
        1. Top 3 differential diagnoses with confidence scores
        2. Clinical reasoning for each diagnosis
        3. Recommended investigations
        4. Risk stratification
        5. Immediate management recommendations

        Format your response as JSON with the following structure:
        {{
            "differential_diagnoses": [
                {{"condition": "...", "confidence": 0.0-1.0, "reasoning": "..."}}
            ],
            "recommendations": ["..."],
            "risk_factors": ["..."],
            "next_steps": ["..."]
        }}
        """

        return prompt

    def _parse_agent_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate Bedrock agent response"""

        try:
            # Extract JSON from response
            if "output" in response:
                output_text = response["output"]["text"]
                diagnosis_data = json.loads(output_text)

                return {
                    "diagnosis": diagnosis_data.get("differential_diagnoses", []),
                    "confidence": self._calculate_overall_confidence(diagnosis_data),
                    "recommendations": diagnosis_data.get("recommendations", []),
                    "risk_factors": diagnosis_data.get("risk_factors", []),
                    "next_steps": diagnosis_data.get("next_steps", [])
                }
        except (json.JSONDecodeError, KeyError):
            pass

        # Fallback parsing
        return self._fallback_diagnosis_parsing(response)

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
        """
        Analyze uploaded medical images (CT, MRI, X-ray)

        Phase 7-2: Image Analysis Placeholder with SageMaker Integration Roadmap

        Args:
            image_file: Uploaded image file (UploadFile from FastAPI)

        Returns:
            Dict containing structured image analysis results with findings,
            confidence scores, abnormalities, and recommendations

        Future Enhancement Roadmap:
            TODO: Integrate with AWS SageMaker for real AI-powered image analysis
            TODO: Upload image to S3 bucket for persistent storage
            TODO: Invoke SageMaker endpoint for medical image segmentation
            TODO: Implement AWS Rekognition Medical for automated abnormality detection
            TODO: Add DICOM format support for medical imaging standards
            TODO: Integrate with radiological lexicon (RadLex) for standardized terminology
        """

        image_id = str(uuid.uuid4())

        # TODO: Phase 7-2.1 - AWS S3 Upload
        # In production, upload to S3:
        # s3_client = boto3.client('s3')
        # s3_key = f"medical-images/{image_id}/{image_file.filename}"
        # s3_client.upload_fileobj(image_file.file, BUCKET_NAME, s3_key)
        # image_url = f"s3://{BUCKET_NAME}/{s3_key}"

        # TODO: Phase 7-2.2 - SageMaker Inference
        # Invoke SageMaker endpoint for image analysis:
        # sagemaker_runtime = boto3.client('sagemaker-runtime')
        # response = sagemaker_runtime.invoke_endpoint(
        #     EndpointName='neuro-image-analysis-endpoint',
        #     ContentType='application/x-image',
        #     Body=image_file.file.read()
        # )
        # analysis_result = json.loads(response['Body'].read())

        # TODO: Phase 7-2.3 - AWS Rekognition Medical
        # Use Rekognition Medical for automated detection:
        # rekognition = boto3.client('rekognition')
        # response = rekognition.detect_medical_labels(
        #     Image={'S3Object': {'Bucket': BUCKET_NAME, 'Name': s3_key}}
        # )

        # PLACEHOLDER: Structured fake response for MVP/testing
        # This response format matches what the real SageMaker endpoint will return
        fake_modality = "MRI"  # Could be CT, MRI, X-ray based on file metadata

        return {
            "image_id": image_id,
            "status": "analyzed",
            "timestamp": datetime.now().isoformat(),
            "image_metadata": {
                "filename": getattr(image_file, 'filename', 'unknown.jpg'),
                "size_bytes": getattr(image_file, 'size', 0),
                "content_type": getattr(image_file, 'content_type', 'image/jpeg'),
                "modality": fake_modality,
                "storage_location": f"s3://neuro-agent-images/{image_id}/placeholder.jpg"  # Placeholder
            },
            "analysis": {
                "modality": fake_modality,
                "anatomical_region": "Brain",
                "view_position": "Axial",
                "quality_score": 0.92,
                "findings": [
                    {
                        "category": "Normal Anatomy",
                        "description": "Brain parenchyma appears normal with no evidence of acute infarction",
                        "confidence": 0.95,
                        "location": "Bilateral cerebral hemispheres",
                        "severity": "none"
                    },
                    {
                        "category": "Vascular",
                        "description": "Normal caliber of major intracranial vessels",
                        "confidence": 0.88,
                        "location": "Circle of Willis",
                        "severity": "none"
                    },
                    {
                        "category": "Ventricles",
                        "description": "Ventricular system is normal in size and configuration",
                        "confidence": 0.93,
                        "location": "Lateral ventricles",
                        "severity": "none"
                    }
                ],
                "abnormalities_detected": [],  # Empty for normal scan
                "key_measurements": {
                    "midline_shift_mm": 0.0,
                    "ventricular_size": "normal",
                    "brain_volume_ml": 1400
                },
                "impression": "No acute intracranial abnormality detected. Normal brain MRI.",
                "confidence_score": 0.91
            },
            "recommendations": [
                "Professional radiological interpretation recommended for clinical decision-making",
                "Correlate with clinical findings and patient symptoms",
                "Consider follow-up imaging if symptoms persist or worsen",
                "AI analysis should be used as decision support, not definitive diagnosis"
            ],
            "disclaimer": "This is an AI-generated analysis for educational and demonstration purposes. All medical images must be reviewed by a qualified radiologist for clinical use.",
            "processing_metadata": {
                "model_version": "placeholder-v1.0",
                "processing_time_ms": 250,  # Simulated processing time
                "sagemaker_endpoint": "neuro-image-analysis-endpoint-placeholder",
                "ai_confidence": 0.91
            }
        }

    async def get_case(self, case_id: str) -> Dict[str, Any]:
        """Retrieve case information"""

        # In a real implementation, this would query DynamoDB
        return {
            "case_id": case_id,
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }
