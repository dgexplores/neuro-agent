import pytest
from unittest.mock import Mock, AsyncMock
from backend.agents.neuro_agent import NeuroAgent
from backend.models.patient import DiagnosisRequest, PatientInfo, Symptom, GenderEnum, SeverityEnum

@pytest.fixture
def mock_bedrock_service():
    service = Mock()
    service.invoke_model_direct = AsyncMock(return_value={
        "output": {"text": '{"differential_diagnoses": [{"condition": "test", "confidence": 0.8}]}'}
    })
    return service

@pytest.fixture
def neuro_agent(mock_bedrock_service):
    return NeuroAgent(mock_bedrock_service)

@pytest.fixture
def sample_diagnosis_request():
    return DiagnosisRequest(
        patient_info=PatientInfo(
            age=45,
            gender=GenderEnum.FEMALE,
            medical_history=["hypertension"],
            current_medications=["lisinopril"],
            allergies=[]
        ),
        symptoms=[
            Symptom(name="headache", severity=SeverityEnum.MODERATE, duration_days=3)
        ],
        vital_signs={"bp_systolic": 140, "bp_diastolic": 90},
        lab_results={},
        imaging_studies=[],
        chief_complaint="Severe headache for 3 days",
        history_present_illness="Patient reports sudden onset severe headache"
    )

@pytest.mark.asyncio
async def test_analyze_case(neuro_agent, sample_diagnosis_request):
    """Test case analysis functionality"""

    result = await neuro_agent.analyze_case(sample_diagnosis_request)

    assert "case_id" in result
    assert "diagnosis" in result
    assert "confidence" in result
    assert isinstance(result["recommendations"], list)

def test_prepare_medical_context(neuro_agent, sample_diagnosis_request):
    """Test medical context preparation"""

    context = neuro_agent._prepare_medical_context(sample_diagnosis_request)

    assert "patient_demographics" in context
    assert context["patient_demographics"]["age"] == 45
    assert "presentation" in context
    assert "clinical_data" in context

@pytest.mark.asyncio
async def test_fallback_diagnosis(neuro_agent):
    """Test fallback diagnosis when AI fails"""

    context = {"patient_demographics": {"age": 50}}
    result = neuro_agent._fallback_diagnosis(context)

    assert "diagnosis" in result
    assert result["confidence"] <= 1.0
    assert len(result["recommendations"]) > 0
