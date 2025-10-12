"""
Unit Tests for NeuroAgent Input Validation (TDD - Red Phase)

This module contains unit tests for input validation in the NeuroAgent.analyze_case() method.
Following Test-Driven Development (TDD) Red-Green-Refactor cycle.

Test Strategy:
    1. RED: Write failing test for empty symptoms validation
    2. GREEN: Implement minimum code to pass the test
    3. REFACTOR: Clean up implementation

Requirements:
    - NeuroAgent.analyze_case() should return HTTP 400 for empty symptoms list
    - Validation error should include clear error message
    - Other validation rules should also be tested
"""

import pytest
from fastapi import HTTPException
from unittest.mock import Mock, AsyncMock
from typing import List

from backend.agents.neuro_agent import NeuroAgent
from backend.models.patient import DiagnosisRequest, PatientInfo, Symptom, GenderEnum, SeverityEnum
from backend.services.bedrock_service import BedrockService


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_bedrock_service():
    """Mock BedrockService for testing without AWS"""
    mock_service = Mock(spec=BedrockService)
    mock_service.invoke_agent = AsyncMock(return_value={
        "output": {
            "text": '{"differential_diagnoses": [], "recommendations": [], "risk_factors": [], "next_steps": []}'
        }
    })
    return mock_service


@pytest.fixture
def neuro_agent(mock_bedrock_service):
    """Create NeuroAgent instance with mocked dependencies"""
    return NeuroAgent(bedrock_service=mock_bedrock_service)


@pytest.fixture
def valid_patient_info():
    """Valid patient information fixture"""
    return PatientInfo(
        age=45,
        gender=GenderEnum.FEMALE,
        weight=65.0,
        height=165.0,
        medical_history=["hypertension"],
        current_medications=["amlodipine 5mg"],
        allergies=[]
    )


@pytest.fixture
def valid_symptom():
    """Valid symptom fixture"""
    return Symptom(
        name="headache",
        severity=SeverityEnum.MODERATE,
        duration_days=3,
        description="throbbing pain on right side"
    )


# ============================================================================
# TDD Phase 1: RED - Failing Tests
# ============================================================================

@pytest.mark.asyncio
async def test_empty_symptoms_should_return_400_error(neuro_agent, valid_patient_info):
    """
    TEST 1 (RED PHASE): Empty symptoms list should raise HTTPException with status 400

    Given: A diagnosis request with empty symptoms list
    When: analyze_case() is called
    Then: Should raise HTTPException with status_code=400
    And: Error message should indicate "Symptoms list cannot be empty"

    Expected to FAIL initially until validation is implemented.
    """
    # Arrange: Create request with empty symptoms
    request = DiagnosisRequest(
        patient_info=valid_patient_info,
        symptoms=[],  # EMPTY symptoms list - should trigger validation error
        vital_signs={"heart_rate": 72, "blood_pressure_systolic": 120},
        lab_results={},
        imaging_studies=[],
        chief_complaint="Headache for 3 days",
        history_present_illness="Patient reports gradual onset headache"
    )

    # Act & Assert: Should raise HTTPException with 400 status
    with pytest.raises(HTTPException) as exc_info:
        await neuro_agent.analyze_case(request)

    # Verify error details
    assert exc_info.value.status_code == 400
    assert "symptoms" in exc_info.value.detail.lower()
    assert "empty" in exc_info.value.detail.lower() or "required" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_missing_chief_complaint_should_return_400_error(neuro_agent, valid_patient_info, valid_symptom):
    """
    TEST 2 (RED PHASE): Empty chief complaint should raise HTTPException with status 400

    Given: A diagnosis request with empty chief complaint
    When: analyze_case() is called
    Then: Should raise HTTPException with status_code=400

    Expected to FAIL initially until validation is implemented.
    """
    # Arrange: Create request with empty chief complaint
    request = DiagnosisRequest(
        patient_info=valid_patient_info,
        symptoms=[valid_symptom],
        vital_signs={},
        lab_results={},
        imaging_studies=[],
        chief_complaint="",  # EMPTY chief complaint
        history_present_illness="Patient history"
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await neuro_agent.analyze_case(request)

    assert exc_info.value.status_code == 400
    assert "chief complaint" in exc_info.value.detail.lower() or "chief_complaint" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_invalid_patient_age_should_return_400_error(neuro_agent, valid_symptom):
    """
    TEST 3 (RED PHASE): Invalid patient age (negative) should raise validation error

    Note: This may be caught by Pydantic validation before reaching analyze_case(),
    but we test the behavior anyway.

    Expected to FAIL initially if custom validation is needed.
    """
    # Arrange: Create patient with invalid age
    # Note: Pydantic should catch this at model validation level
    with pytest.raises(Exception):  # Could be ValidationError or HTTPException
        invalid_patient = PatientInfo(
            age=-5,  # INVALID negative age
            gender=GenderEnum.MALE,
            medical_history=[],
            current_medications=[],
            allergies=[]
        )


@pytest.mark.asyncio
async def test_valid_request_should_succeed(neuro_agent, valid_patient_info, valid_symptom):
    """
    TEST 4 (POSITIVE CASE): Valid request should return successful diagnosis

    This test should PASS even before implementing validation.
    It ensures we don't break existing functionality.
    """
    # Arrange: Create valid request
    request = DiagnosisRequest(
        patient_info=valid_patient_info,
        symptoms=[valid_symptom],
        vital_signs={"heart_rate": 72},
        lab_results={},
        imaging_studies=[],
        chief_complaint="Headache for 3 days",
        history_present_illness="Patient reports gradual onset headache"
    )

    # Act
    result = await neuro_agent.analyze_case(request)

    # Assert
    assert result is not None
    assert "case_id" in result
    assert "diagnosis" in result
    assert "confidence" in result
    assert isinstance(result["diagnosis"], list)


# ============================================================================
# Additional Validation Tests (To be implemented in future iterations)
# ============================================================================

@pytest.mark.asyncio
async def test_excessive_symptoms_should_warn(neuro_agent, valid_patient_info, caplog):
    """
    TEST: Too many symptoms (>20) should trigger a warning
    but not fail the request
    """
    import logging
    caplog.set_level(logging.WARNING)

    # Create request with 25 symptoms
    excessive_symptoms = [
        Symptom(name=f"symptom_{i}", severity=SeverityEnum.MILD, duration_days=1)
        for i in range(25)
    ]

    request = DiagnosisRequest(
        patient_info=valid_patient_info,
        symptoms=excessive_symptoms,
        vital_signs={},
        lab_results={},
        imaging_studies=[],
        chief_complaint="Multiple symptoms",
        history_present_illness="Patient reports many symptoms"
    )

    result = await neuro_agent.analyze_case(request)

    # Should succeed but include warning in logs
    assert result is not None
    assert "Excessive symptoms detected" in caplog.text
    assert "25 symptoms" in caplog.text


@pytest.mark.asyncio
async def test_potentially_malicious_input_should_be_sanitized(neuro_agent, valid_patient_info):
    """
    TEST: Suspicious input (SQL injection, XSS attempts) should be sanitized

    This test verifies that the NeuroAgent properly sanitizes potentially malicious
    input using the input_sanitizer module before passing to Bedrock.
    """
    from unittest.mock import patch

    suspicious_symptom = Symptom(
        name="<script>alert('xss')</script>",
        severity=SeverityEnum.MILD,
        duration_days=1,
        description="'; DROP TABLE patients; --"
    )

    request = DiagnosisRequest(
        patient_info=valid_patient_info,
        symptoms=[suspicious_symptom],
        vital_signs={},
        lab_results={},
        imaging_studies=[],
        chief_complaint="<img src=x onerror=alert('xss')>",
        history_present_illness="Normal history"
    )

    # Capture the prompt that gets built
    with patch.object(neuro_agent.bedrock_service, 'invoke_agent', new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = {
            "output": {
                "text": '{"differential_diagnoses": [], "recommendations": [], "risk_factors": [], "next_steps": []}'
            }
        }

        result = await neuro_agent.analyze_case(request)

        # Should succeed and sanitize input
        assert result is not None

        # Verify the prompt was sanitized (no HTML/script tags or SQL injection)
        assert mock_invoke.called
        prompt_sent = mock_invoke.call_args[1]['input_text']

        # Verify XSS attempts are sanitized
        assert "<script>" not in prompt_sent
        assert "alert(" not in prompt_sent
        assert "<img" not in prompt_sent
        assert "onerror=" not in prompt_sent

        # Verify SQL injection attempts are sanitized
        assert "DROP TABLE" not in prompt_sent
        assert "'--" not in prompt_sent or "'; DROP" not in prompt_sent


# ============================================================================
# Edge Cases
# ============================================================================

@pytest.mark.asyncio
async def test_single_symptom_should_succeed(neuro_agent, valid_patient_info):
    """
    EDGE CASE: Single symptom should be valid (minimum 1 symptom required)

    This test should PASS after implementing validation.
    """
    single_symptom = Symptom(
        name="dizziness",
        severity=SeverityEnum.SEVERE,
        duration_days=1
    )

    request = DiagnosisRequest(
        patient_info=valid_patient_info,
        symptoms=[single_symptom],  # Only ONE symptom
        vital_signs={},
        lab_results={},
        imaging_studies=[],
        chief_complaint="Sudden dizziness",
        history_present_illness="Patient felt dizzy this morning"
    )

    result = await neuro_agent.analyze_case(request)

    assert result is not None
    assert result["case_id"]


@pytest.mark.asyncio
async def test_whitespace_only_chief_complaint_should_fail(neuro_agent, valid_patient_info, valid_symptom):
    """
    EDGE CASE: Whitespace-only chief complaint should be treated as empty

    Expected to FAIL initially until validation is implemented.
    """
    request = DiagnosisRequest(
        patient_info=valid_patient_info,
        symptoms=[valid_symptom],
        vital_signs={},
        lab_results={},
        imaging_studies=[],
        chief_complaint="   ",  # Only whitespace
        history_present_illness="History"
    )

    with pytest.raises(HTTPException) as exc_info:
        await neuro_agent.analyze_case(request)

    assert exc_info.value.status_code == 400


# ============================================================================
# Test Execution Instructions
# ============================================================================

"""
RUN TESTS (RED PHASE - Expected to FAIL):

    # Run all validation tests (should FAIL for tests 1, 2, and edge cases)
    pytest backend/tests/unit/test_neuro_agent_validation.py -v

    # Run only the main failing test
    pytest backend/tests/unit/test_neuro_agent_validation.py::test_empty_symptoms_should_return_400_error -v

    # Run with verbose output
    pytest backend/tests/unit/test_neuro_agent_validation.py -v -s

EXPECTED OUTPUT (RED PHASE):
    FAILED test_empty_symptoms_should_return_400_error - Did not raise HTTPException
    FAILED test_missing_chief_complaint_should_return_400_error - Did not raise HTTPException
    FAILED test_whitespace_only_chief_complaint_should_fail - Did not raise HTTPException
    PASSED test_valid_request_should_succeed ✓

Next Step: Implement validation in neuro_agent.py to make these tests pass (GREEN PHASE)
"""
