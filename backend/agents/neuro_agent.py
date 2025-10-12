from typing import Dict, Any, List
import json
import uuid
from datetime import datetime

from ..models.patient import DiagnosisRequest, PatientCase
from ..services.bedrock_service import BedrockService
from ..utils.medical_knowledge import NeuroMedicalKnowledge

class NeuroAgent:
    def __init__(self, bedrock_service: BedrockService):
        self.bedrock_service = bedrock_service
        self.knowledge_base = NeuroMedicalKnowledge()

    async def analyze_case(self, request: DiagnosisRequest) -> Dict[str, Any]:
        """Analyze patient case and provide neurological diagnosis"""

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
        """Build structured prompt for neurological diagnosis"""

        prompt = f"""
        You are an expert neurologist AI assistant. Analyze the following patient case and provide a comprehensive neurological assessment.

        PATIENT INFORMATION:
        - Age: {context['patient_demographics']['age']}
        - Gender: {context['patient_demographics']['gender']}
        - Medical History: {', '.join(context['patient_demographics']['medical_history'])}

        CLINICAL PRESENTATION:
        - Chief Complaint: {context['presentation']['chief_complaint']}
        - Symptoms: {context['presentation']['symptoms']}
        - History of Present Illness: {context['presentation']['history']}

        CLINICAL DATA:
        - Vital Signs: {json.dumps(context['clinical_data']['vital_signs'])}
        - Lab Results: {json.dumps(context['clinical_data']['lab_results'])}
        - Imaging Studies: {', '.join(context['clinical_data']['imaging'])}

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
        """Enhance diagnosis with medical knowledge base"""

        # Add evidence-based recommendations
        enhanced_recommendations = []
        for diagnosis in result["diagnosis"]:
            condition = diagnosis.get("condition", "")
            recommendations = self.knowledge_base.get_treatment_guidelines(condition)
            enhanced_recommendations.extend(recommendations)

        result["recommendations"].extend(enhanced_recommendations)

        # Add drug interaction checks
        medications = request.patient_info.current_medications
        interactions = self.knowledge_base.check_drug_interactions(medications)
        if interactions:
            result["risk_factors"].extend([f"Drug interaction: {i}" for i in interactions])

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
        """Analyze uploaded medical images"""

        image_id = str(uuid.uuid4())

        # In a real implementation, this would process the image
        # using Amazon SageMaker or other image analysis services

        return {
            "image_id": image_id,
            "analysis": {
                "findings": ["Image uploaded successfully"],
                "recommendations": ["Professional radiological interpretation recommended"]
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
