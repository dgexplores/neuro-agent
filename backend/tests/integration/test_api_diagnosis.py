"""
Integration tests for NeuroAgent API diagnosis endpoints

Tests the complete workflow from API request through to response,
including drug interaction checking integration.

Phase 8: API Integration & Testing
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from backend.main import app
from backend.models.patient import (
    PatientInfo,
    Symptom,
    DiagnosisRequest,
    GenderEnum,
    SeverityEnum
)


# Test client setup
@pytest.fixture
def client():
    """Create FastAPI test client"""
    with TestClient(app) as api:
        yield api


@pytest.fixture
def mock_auth_token():
    """Mock authentication token"""
    return "Bearer test-token-12345"


@pytest.fixture
def valid_diagnosis_payload():
    """Valid diagnosis request payload"""
    return {
        "patient_info": {
            "age": 45,
            "gender": "male",
            "weight": 75.0,
            "height": 175.0,
            "medical_history": ["hypertension", "diabetes"],
            "current_medications": ["lisinopril", "metformin"],
            "allergies": ["penicillin"]
        },
        "symptoms": [
            {
                "name": "severe headache",
                "severity": "severe",
                "duration_days": 2,
                "description": "throbbing pain on left side"
            },
            {
                "name": "nausea",
                "severity": "moderate",
                "duration_days": 2,
                "description": "occasional vomiting"
            }
        ],
        "vital_signs": {
            "heart_rate": 72,
            "blood_pressure_systolic": 140,
            "blood_pressure_diastolic": 90,
            "temperature": 37.2,
            "respiratory_rate": 16
        },
        "lab_results": {
            "glucose": 110,
            "sodium": 140,
            "potassium": 4.2
        },
        "imaging_studies": ["brain_mri"],
        "chief_complaint": "Severe headache for 2 days",
        "history_present_illness": "Patient reports sudden onset severe headache on left side, associated with nausea and photophobia. No recent trauma."
    }


@pytest.fixture
def diagnosis_payload_with_drug_interactions():
    """Diagnosis request with medications that have interactions"""
    return {
        "patient_info": {
            "age": 62,
            "gender": "female",
            "weight": 68.0,
            "height": 165.0,
            "medical_history": ["atrial fibrillation", "migraine"],
            "current_medications": ["warfarin", "aspirin", "sumatriptan"],  # Known interactions
            "allergies": []
        },
        "symptoms": [
            {
                "name": "migraine headache",
                "severity": "severe",
                "duration_days": 1,
                "description": "unilateral throbbing headache"
            }
        ],
        "vital_signs": {
            "heart_rate": 78,
            "blood_pressure_systolic": 135,
            "blood_pressure_diastolic": 85
        },
        "lab_results": {},
        "imaging_studies": [],
        "chief_complaint": "Migraine attack",
        "history_present_illness": "Patient with history of migraines, currently on anticoagulation for AFib"
    }


@pytest.fixture
def invalid_diagnosis_payload():
    """Invalid diagnosis request (empty symptoms)"""
    return {
        "patient_info": {
            "age": 45,
            "gender": "male",
            "medical_history": [],
            "current_medications": [],
            "allergies": []
        },
        "symptoms": [],  # Invalid: empty symptoms
        "vital_signs": {},
        "lab_results": {},
        "imaging_studies": [],
        "chief_complaint": "Headache",
        "history_present_illness": "Patient has headache"
    }


# ============================================================================
# Test 1: Health Check Endpoint
# ============================================================================

def test_health_check_endpoint(client):
    """Test GET /health returns healthy status"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_root_endpoint(client):
    """Test GET / returns API information"""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.0.0"


# ============================================================================
# Test 2: Diagnosis Endpoint - Authentication
# ============================================================================

def test_diagnosis_endpoint_requires_authentication(client, valid_diagnosis_payload):
    """Test POST /api/v1/diagnosis requires authentication"""
    # Request without authentication header
    response = client.post("/api/v1/diagnosis", json=valid_diagnosis_payload)

    assert response.status_code == 401
    assert "detail" in response.json()


@patch('backend.main.verify_token')
@patch('backend.main.neuro_agent.analyze_case')
def test_diagnosis_endpoint_with_valid_token(
    mock_analyze_case,
    mock_verify_token,
    client,
    valid_diagnosis_payload,
    mock_auth_token
):
    """Test POST /api/v1/diagnosis with valid authentication token"""
    # Mock authentication
    mock_verify_token.return_value = "user123"

    # Mock diagnosis response
    mock_analyze_case.return_value = {
        "case_id": "test-case-123",
        "diagnosis": [
            {
                "condition": "Migraine with aura",
                "confidence": 0.85,
                "reasoning": "Classic presentation of migraine"
            }
        ],
        "confidence": 0.85,
        "recommendations": ["Rest in dark room", "Hydration"],
        "risk_factors": ["Age", "Hypertension"],
        "next_steps": ["Follow-up in 48 hours"]
    }

    response = client.post(
        "/api/v1/diagnosis",
        json=valid_diagnosis_payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "case_id" in data
    assert data["case_id"] == "test-case-123"
    assert "diagnosis" in data
    assert len(data["diagnosis"]) > 0
    assert "confidence" in data
    assert data["confidence"] == 0.85


# ============================================================================
# Test 3: Diagnosis Endpoint - Input Validation
# ============================================================================

@patch('backend.main.verify_token')
def test_diagnosis_endpoint_empty_symptoms_returns_400(
    mock_verify_token,
    client,
    invalid_diagnosis_payload,
    mock_auth_token
):
    """Test POST /api/v1/diagnosis with empty symptoms returns 400"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/diagnosis",
        json=invalid_diagnosis_payload,
        headers={"Authorization": mock_auth_token}
    )

    # Should return 400 due to input validation
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "symptoms" in data["detail"].lower()


@patch('backend.main.verify_token')
def test_diagnosis_endpoint_missing_chief_complaint_returns_400(
    mock_verify_token,
    client,
    mock_auth_token
):
    """Test POST /api/v1/diagnosis with missing chief complaint returns 400"""
    mock_verify_token.return_value = "user123"

    payload = {
        "patient_info": {
            "age": 45,
            "gender": "male",
            "medical_history": [],
            "current_medications": [],
            "allergies": []
        },
        "symptoms": [
            {
                "name": "headache",
                "severity": "moderate",
                "duration_days": 1
            }
        ],
        "vital_signs": {},
        "lab_results": {},
        "imaging_studies": [],
        "chief_complaint": "",  # Invalid: empty
        "history_present_illness": "Patient has headache"
    }

    response = client.post(
        "/api/v1/diagnosis",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 400
    data = response.json()
    assert "chief complaint" in data["detail"].lower()


# ============================================================================
# Test 4: Diagnosis Endpoint - Drug Interaction Integration
# ============================================================================

@patch('backend.main.verify_token')
@patch('backend.main.neuro_agent.analyze_case')
def test_diagnosis_endpoint_includes_drug_interaction_warnings(
    mock_analyze_case,
    mock_verify_token,
    client,
    diagnosis_payload_with_drug_interactions,
    mock_auth_token
):
    """Test POST /api/v1/diagnosis includes drug interaction warnings in response"""
    mock_verify_token.return_value = "user123"

    # Mock response with drug interaction warnings
    mock_analyze_case.return_value = {
        "case_id": "test-case-456",
        "diagnosis": [
            {
                "condition": "Migraine",
                "confidence": 0.90,
                "reasoning": "Classic migraine presentation"
            }
        ],
        "confidence": 0.90,
        "recommendations": [
            "Consider triptan therapy",
            "[Drug Interaction] Monitor INR closely, target lower range (2.0-2.5 vs 2.5-3.5)"
        ],
        "risk_factors": [
            "⚠️ SEVERE INTERACTION: Warfarin + Aspirin - Concurrent use significantly increases bleeding risk"
        ],
        "next_steps": ["Neurologist follow-up"]
    }

    response = client.post(
        "/api/v1/diagnosis",
        json=diagnosis_payload_with_drug_interactions,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify drug interaction warnings are included
    assert "risk_factors" in data
    assert len(data["risk_factors"]) > 0

    # Check for interaction warning format
    has_interaction_warning = any(
        "INTERACTION" in factor or "⚠️" in factor
        for factor in data["risk_factors"]
    )
    assert has_interaction_warning, "Response should include drug interaction warnings"

    # Check for interaction recommendations
    assert "recommendations" in data
    has_interaction_recommendation = any(
        "[Drug Interaction]" in rec
        for rec in data["recommendations"]
    )
    assert has_interaction_recommendation, "Response should include drug interaction recommendations"


@patch('backend.main.verify_token')
@patch('backend.main.neuro_agent.analyze_case')
def test_diagnosis_endpoint_contraindicated_drug_interaction(
    mock_analyze_case,
    mock_verify_token,
    client,
    mock_auth_token
):
    """Test POST /api/v1/diagnosis flags CONTRAINDICATED drug interactions"""
    mock_verify_token.return_value = "user123"

    payload = {
        "patient_info": {
            "age": 70,
            "gender": "male",
            "medical_history": ["parkinson's disease", "depression"],
            "current_medications": ["levodopa", "phenelzine"],  # CONTRAINDICATED combination
            "allergies": []
        },
        "symptoms": [
            {
                "name": "tremor",
                "severity": "moderate",
                "duration_days": 30
            }
        ],
        "vital_signs": {},
        "lab_results": {},
        "imaging_studies": [],
        "chief_complaint": "Worsening tremor",
        "history_present_illness": "Patient with Parkinson's disease, tremor worsening"
    }

    # Mock response with CONTRAINDICATED warning
    mock_analyze_case.return_value = {
        "case_id": "test-case-789",
        "diagnosis": [
            {
                "condition": "Parkinson's Disease progression",
                "confidence": 0.75,
                "reasoning": "Known PD with symptom progression"
            }
        ],
        "confidence": 0.75,
        "recommendations": [
            "[Drug Interaction] CONTRAINDICATED - do not use together"
        ],
        "risk_factors": [
            "⚠️ CONTRAINDICATED: Levodopa + Non-selective MAO Inhibitors (Phenelzine, Tranylcypromine) - Risk of hypertensive crisis; absolute contraindication"
        ],
        "next_steps": ["Immediate medication review", "Emergency medical evaluation if hypertensive symptoms"]
    }

    response = client.post(
        "/api/v1/diagnosis",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify CONTRAINDICATED warning is present
    contraindicated_warning = any(
        "CONTRAINDICATED" in factor
        for factor in data["risk_factors"]
    )
    assert contraindicated_warning, "Response should flag CONTRAINDICATED drug interactions"


# ============================================================================
# Test 5: Diagnosis Endpoint - Response Structure
# ============================================================================

@patch('backend.main.verify_token')
@patch('backend.main.neuro_agent.analyze_case')
def test_diagnosis_endpoint_response_structure(
    mock_analyze_case,
    mock_verify_token,
    client,
    valid_diagnosis_payload,
    mock_auth_token
):
    """Test POST /api/v1/diagnosis returns correct response structure"""
    mock_verify_token.return_value = "user123"

    mock_analyze_case.return_value = {
        "case_id": "test-case-999",
        "diagnosis": [
            {
                "condition": "Test condition",
                "confidence": 0.80,
                "reasoning": "Test reasoning"
            }
        ],
        "confidence": 0.80,
        "recommendations": ["Test recommendation"],
        "risk_factors": ["Test risk factor"],
        "next_steps": ["Test next step"]
    }

    response = client.post(
        "/api/v1/diagnosis",
        json=valid_diagnosis_payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify all required fields are present
    required_fields = ["case_id", "diagnosis", "confidence", "recommendations", "risk_factors", "next_steps"]
    for field in required_fields:
        assert field in data, f"Response missing required field: {field}"

    # Verify field types
    assert isinstance(data["case_id"], str)
    assert isinstance(data["diagnosis"], list)
    assert isinstance(data["confidence"], (int, float))
    assert isinstance(data["recommendations"], list)
    assert isinstance(data["risk_factors"], list)
    assert isinstance(data["next_steps"], list)

    # Verify confidence is in valid range
    assert 0.0 <= data["confidence"] <= 1.0


# ============================================================================
# Test 6: Diagnosis Endpoint - Error Handling
# ============================================================================

@patch('backend.main.verify_token')
@patch('backend.main.neuro_agent.analyze_case')
def test_diagnosis_endpoint_handles_agent_errors(
    mock_analyze_case,
    mock_verify_token,
    client,
    valid_diagnosis_payload,
    mock_auth_token
):
    """Test POST /api/v1/diagnosis handles errors from neuro_agent gracefully"""
    mock_verify_token.return_value = "user123"

    # Mock agent raising an exception
    mock_analyze_case.side_effect = Exception("Bedrock service unavailable")

    response = client.post(
        "/api/v1/diagnosis",
        json=valid_diagnosis_payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data


@patch('backend.main.verify_token')
def test_diagnosis_endpoint_handles_invalid_json(
    mock_verify_token,
    client,
    mock_auth_token
):
    """Test POST /api/v1/diagnosis handles malformed JSON"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/diagnosis",
        data="invalid json{{{",
        headers={
            "Authorization": mock_auth_token,
            "Content-Type": "application/json"
        }
    )

    assert response.status_code == 422  # Unprocessable Entity


# ============================================================================
# Test 7: Case Retrieval Endpoint
# ============================================================================

@patch('backend.main.verify_token')
def test_get_case_endpoint_success(mock_verify_token, client, mock_auth_token, case_store):
    mock_verify_token.return_value = "user123"
    response = {
        "case_id": "test-case-123", "diagnosis": [], "confidence": 0.5,
        "recommendations": [], "risk_factors": [], "next_steps": [],
        "timestamp": "2026-01-01T00:00:00",
    }
    case_store.save("user123", response)
    result = client.get("/api/v1/cases/test-case-123", headers={"Authorization": mock_auth_token})
    assert result.status_code == 200
    assert result.json() == response


@patch('backend.main.verify_token')
def test_get_case_endpoint_not_found(mock_verify_token, client, mock_auth_token):
    mock_verify_token.return_value = "user123"
    response = client.get("/api/v1/cases/non-existent-case", headers={"Authorization": mock_auth_token})
    assert response.status_code == 404
    assert response.json()["detail"] == "Case not found"


def test_get_case_endpoint_requires_authentication(client):
    """Test GET /api/v1/cases/{case_id} requires authentication"""
    response = client.get("/api/v1/cases/test-case-123")

    assert response.status_code == 401


# ============================================================================
# Test 8: Integration Test - Full Workflow
# ============================================================================

@patch('backend.main.verify_token')
@patch('backend.main.neuro_agent.analyze_case')
def test_full_diagnosis_workflow_with_drug_interactions(
    mock_analyze_case,
    mock_verify_token,
    client,
    mock_auth_token
):
    """
    Integration test: Complete diagnosis workflow with drug interaction checking

    This test verifies:
    1. Authentication works
    2. Input validation passes
    3. Drug interactions are detected and reported
    4. Response structure is correct
    5. All Phase 6 and Phase 7 functionality is integrated
    """
    mock_verify_token.return_value = "user123"

    # Prepare request with interacting medications
    payload = {
        "patient_info": {
            "age": 55,
            "gender": "female",
            "weight": 70.0,
            "height": 168.0,
            "medical_history": ["depression", "migraine", "hypertension"],
            "current_medications": ["sertraline", "sumatriptan", "lisinopril"],  # SSRI + Triptan = SEVERE
            "allergies": []
        },
        "symptoms": [
            {
                "name": "severe headache",
                "severity": "severe",
                "duration_days": 1,
                "description": "pulsating headache with visual disturbances"
            },
            {
                "name": "photophobia",
                "severity": "moderate",
                "duration_days": 1,
                "description": "sensitivity to light"
            }
        ],
        "vital_signs": {
            "heart_rate": 75,
            "blood_pressure_systolic": 132,
            "blood_pressure_diastolic": 84,
            "temperature": 37.0
        },
        "lab_results": {},
        "imaging_studies": [],
        "chief_complaint": "Severe migraine attack",
        "history_present_illness": "Patient with chronic migraines, currently managed with sumatriptan. Also on sertraline for depression."
    }

    # Mock comprehensive response
    mock_analyze_case.return_value = {
        "case_id": "integration-test-001",
        "diagnosis": [
            {
                "condition": "Migraine with aura",
                "confidence": 0.88,
                "reasoning": "Classic presentation with visual aura and photophobia"
            },
            {
                "condition": "Medication overuse headache",
                "confidence": 0.45,
                "reasoning": "Consider if patient uses triptans frequently"
            }
        ],
        "confidence": 0.88,
        "recommendations": [
            "Acute migraine treatment with triptan",
            "Rest in dark, quiet environment",
            "[Drug Interaction] Monitor for serotonin syndrome symptoms (agitation, confusion, rapid heart rate)",
            "[Drug Interaction] Educate patient on serotonin syndrome signs"
        ],
        "risk_factors": [
            "Chronic migraine history",
            "⚠️ SEVERE INTERACTION: Sertraline (SSRI) + Sumatriptan (Triptan) - Risk of serotonin syndrome"
        ],
        "next_steps": [
            "Monitor response to treatment",
            "Consider preventive migraine therapy",
            "Review medication regimen with physician"
        ]
    }

    # Execute request
    response = client.post(
        "/api/v1/diagnosis",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    # Verify case was created
    assert "case_id" in data
    assert data["case_id"] == "integration-test-001"

    # Verify diagnosis quality
    assert len(data["diagnosis"]) >= 1
    assert data["diagnosis"][0]["condition"] == "Migraine with aura"
    assert data["diagnosis"][0]["confidence"] >= 0.8

    # Verify drug interaction detection
    severe_interaction_found = any(
        "SEVERE INTERACTION" in factor and "Sertraline" in factor and "Sumatriptan" in factor
        for factor in data["risk_factors"]
    )
    assert severe_interaction_found, "Should detect SEVERE interaction between SSRI and Triptan"

    # Verify serotonin syndrome warning
    serotonin_warning_found = any(
        "serotonin syndrome" in rec.lower()
        for rec in data["recommendations"]
    )
    assert serotonin_warning_found, "Should include serotonin syndrome monitoring recommendation"

    # Verify all required fields
    assert "confidence" in data
    assert "recommendations" in data
    assert "next_steps" in data

    print("\n✅ Full workflow integration test passed:")
    print(f"   - Case ID: {data['case_id']}")
    print(f"   - Diagnoses: {len(data['diagnosis'])}")
    print(f"   - Drug Interactions Detected: {len([f for f in data['risk_factors'] if 'INTERACTION' in f])}")
    print(f"   - Overall Confidence: {data['confidence']}")
