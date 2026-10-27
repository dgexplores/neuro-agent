"""
Integration tests for Drug Interaction API Endpoint

Phase 8: API Integration & Testing
Tests the dedicated drug interaction checking endpoint
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.main import app


# Test client setup
@pytest.fixture
def client():
    """Create FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_auth_token():
    """Mock authentication token"""
    return "Bearer test-token-drug-check"


# ============================================================================
# Test 1: Authentication
# ============================================================================

def test_drug_interaction_endpoint_requires_authentication(client):
    """Test POST /api/v1/drug-interactions requires authentication"""
    payload = {"medications": ["warfarin", "aspirin"]}

    response = client.post("/api/v1/drug-interactions", json=payload)

    assert response.status_code == 401
    assert "detail" in response.json()


# ============================================================================
# Test 2: Input Validation
# ============================================================================

@patch('backend.main.verify_token')
def test_missing_medications_field_returns_400(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions with missing 'medications' field"""
    mock_verify_token.return_value = "user123"

    payload = {"drugs": ["warfarin", "aspirin"]}  # Wrong field name

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 400
    data = response.json()
    assert "medications" in data["detail"].lower()


@patch('backend.main.verify_token')
def test_medications_not_a_list_returns_400(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions with non-list medications"""
    mock_verify_token.return_value = "user123"

    payload = {"medications": "warfarin, aspirin"}  # String instead of list

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 400
    data = response.json()
    assert "list" in data["detail"].lower()


@patch('backend.main.verify_token')
def test_single_medication_returns_no_interactions(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions with only 1 medication"""
    mock_verify_token.return_value = "user123"

    payload = {"medications": ["warfarin"]}

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["medication_count"] == 1
    assert data["interactions_found"] == 0
    assert "message" in data
    assert "at least 2" in data["message"].lower()


# ============================================================================
# Test 3: Successful Interaction Detection
# ============================================================================

@patch('backend.main.verify_token')
def test_two_medications_with_interaction(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions detects interaction between 2 medications"""
    mock_verify_token.return_value = "user123"

    payload = {"medications": ["warfarin", "aspirin"]}

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "medication_count" in data
    assert "medications_checked" in data
    assert "interactions_found" in data
    assert "interactions" in data
    assert "severity_summary" in data

    # Verify data
    assert data["medication_count"] == 2
    assert data["interactions_found"] == 1
    assert len(data["interactions"]) == 1

    # Verify interaction details
    interaction = data["interactions"][0]
    assert "drug1" in interaction
    assert "drug2" in interaction
    assert "severity" in interaction
    assert "description" in interaction
    assert "recommendations" in interaction

    # Verify it's the correct interaction (Warfarin + Aspirin = SEVERE)
    assert interaction["severity"] == "severe"
    assert "warfarin" in interaction["drug1"].lower() or "warfarin" in interaction["drug2"].lower()
    assert "aspirin" in interaction["drug1"].lower() or "aspirin" in interaction["drug2"].lower()


@patch('backend.main.verify_token')
def test_multiple_medications_multiple_interactions(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions with multiple interacting medications"""
    mock_verify_token.return_value = "user123"

    # Warfarin + Aspirin (SEVERE) + Phenytoin (MODERATE with Warfarin)
    payload = {"medications": ["warfarin", "aspirin", "phenytoin"]}

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["medication_count"] == 3
    assert data["interactions_found"] == 2  # Warfarin+Aspirin and Warfarin+Phenytoin
    assert len(data["interactions"]) == 2

    # Verify interactions are sorted by severity (severe first, then moderate)
    assert data["interactions"][0]["severity"] == "severe"
    assert data["interactions"][1]["severity"] == "moderate"


# ============================================================================
# Test 4: Severity Summary
# ============================================================================

@patch('backend.main.verify_token')
def test_severity_summary_structure(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions returns correct severity summary"""
    mock_verify_token.return_value = "user123"

    payload = {"medications": ["warfarin", "aspirin", "phenytoin"]}

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    summary = data["severity_summary"]
    assert "contraindicated" in summary
    assert "severe" in summary
    assert "moderate" in summary
    assert "minor" in summary

    # Verify counts
    assert isinstance(summary["contraindicated"], int)
    assert isinstance(summary["severe"], int)
    assert isinstance(summary["moderate"], int)
    assert isinstance(summary["minor"], int)

    # Verify correct counts for this combination
    assert summary["severe"] == 1  # Warfarin + Aspirin
    assert summary["moderate"] == 1  # Warfarin + Phenytoin


# ============================================================================
# Test 5: CONTRAINDICATED Interactions
# ============================================================================

@patch('backend.main.verify_token')
def test_contraindicated_interaction_detection(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions detects CONTRAINDICATED interactions"""
    mock_verify_token.return_value = "user123"

    # Levodopa + Phenelzine = CONTRAINDICATED
    payload = {"medications": ["levodopa", "phenelzine"]}

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["interactions_found"] == 1
    interaction = data["interactions"][0]

    assert interaction["severity"] == "contraindicated"
    assert "contraindication" in interaction["description"].lower()

    # Verify severity summary
    assert data["severity_summary"]["contraindicated"] == 1


# ============================================================================
# Test 6: Case-Insensitive Matching
# ============================================================================

@patch('backend.main.verify_token')
def test_case_insensitive_drug_matching(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions handles case-insensitive drug names"""
    mock_verify_token.return_value = "user123"

    # Different case variations
    payload = {"medications": ["WARFARIN", "Aspirin"]}

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["interactions_found"] == 1
    assert data["interactions"][0]["severity"] == "severe"


# ============================================================================
# Test 7: No Interactions Found
# ============================================================================

@patch('backend.main.verify_token')
def test_no_interactions_found(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions with non-interacting medications"""
    mock_verify_token.return_value = "user123"

    # Medications that don't interact (not in our database)
    payload = {"medications": ["metformin", "lisinopril"]}

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["medication_count"] == 2
    assert data["interactions_found"] == 0
    assert len(data["interactions"]) == 0

    # Verify severity summary is all zeros
    summary = data["severity_summary"]
    assert summary["contraindicated"] == 0
    assert summary["severe"] == 0
    assert summary["moderate"] == 0
    assert summary["minor"] == 0


# ============================================================================
# Test 8: Duplicate Medications
# ============================================================================

@patch('backend.main.verify_token')
def test_duplicate_medications(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions handles duplicate medication entries"""
    mock_verify_token.return_value = "user123"

    # Duplicate warfarin entries
    payload = {"medications": ["warfarin", "warfarin", "aspirin"]}

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    # Should deduplicate and find only 1 interaction (not 2)
    assert data["interactions_found"] == 1


# ============================================================================
# Test 9: Empty Medications List
# ============================================================================

@patch('backend.main.verify_token')
def test_empty_medications_list(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions with empty medications list"""
    mock_verify_token.return_value = "user123"

    payload = {"medications": []}

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["medication_count"] == 0
    assert data["interactions_found"] == 0
    assert "message" in data


# ============================================================================
# Test 10: Large Medication List
# ============================================================================

@patch('backend.main.verify_token')
def test_large_medication_list(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions with large medication list"""
    mock_verify_token.return_value = "user123"

    # 10 medications with multiple known interactions
    payload = {
        "medications": [
            "warfarin", "aspirin", "phenytoin", "carbamazepine",
            "levodopa", "sertraline", "sumatriptan", "lithium",
            "ibuprofen", "gabapentin"
        ]
    }

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["medication_count"] == 10
    assert data["interactions_found"] >= 5  # Should find several interactions

    # Verify all interactions have required fields
    for interaction in data["interactions"]:
        assert "drug1" in interaction
        assert "drug2" in interaction
        assert "severity" in interaction
        assert "description" in interaction
        assert "mechanism" in interaction
        assert "clinical_effects" in interaction
        assert "recommendations" in interaction
        assert "references" in interaction


# ============================================================================
# Test 11: Response Structure Validation
# ============================================================================

@patch('backend.main.verify_token')
def test_response_structure_validation(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/drug-interactions returns complete response structure"""
    mock_verify_token.return_value = "user123"

    payload = {"medications": ["warfarin", "aspirin"]}

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify top-level fields
    required_top_fields = [
        "medication_count",
        "medications_checked",
        "interactions_found",
        "interactions",
        "severity_summary"
    ]

    for field in required_top_fields:
        assert field in data, f"Missing required field: {field}"

    # Verify field types
    assert isinstance(data["medication_count"], int)
    assert isinstance(data["medications_checked"], list)
    assert isinstance(data["interactions_found"], int)
    assert isinstance(data["interactions"], list)
    assert isinstance(data["severity_summary"], dict)

    # Verify medications_checked matches input
    assert set(data["medications_checked"]) == {"warfarin", "aspirin"}


# ============================================================================
# Test 12: Complete E2E Workflow
# ============================================================================

@patch('backend.main.verify_token')
def test_complete_drug_interaction_workflow(mock_verify_token, client, mock_auth_token):
    """
    Complete E2E test for drug interaction endpoint

    Tests:
    1. Authentication
    2. Input validation
    3. Interaction detection
    4. Response structure
    5. Severity classification
    """
    mock_verify_token.return_value = "pharmacist_user"

    # Real-world scenario: Patient on multiple medications
    payload = {
        "medications": [
            "sertraline",     # SSRI antidepressant
            "sumatriptan",    # Triptan for migraines (SEVERE interaction with SSRI)
            "warfarin",       # Anticoagulant
            "aspirin"         # NSAID (SEVERE interaction with warfarin)
        ]
    }

    response = client.post(
        "/api/v1/drug-interactions",
        json=payload,
        headers={"Authorization": mock_auth_token}
    )

    # Verify success
    assert response.status_code == 200
    data = response.json()

    # Verify medication count
    assert data["medication_count"] == 4

    # Verify interactions detected
    # Should detect:
    # 1. Sertraline + Sumatriptan (SEVERE - serotonin syndrome)
    # 2. Warfarin + Aspirin (SEVERE - bleeding risk)
    assert data["interactions_found"] == 2

    # Verify severity summary shows SEVERE interactions
    assert data["severity_summary"]["severe"] >= 2

    # Verify interaction details
    severe_interactions = [i for i in data["interactions"] if i["severity"] == "severe"]
    assert len(severe_interactions) >= 2

    # Verify each interaction has complete information
    for interaction in severe_interactions:
        assert len(interaction["clinical_effects"]) > 0
        assert len(interaction["recommendations"]) > 0
        assert len(interaction["mechanism"]) > 0
        assert len(interaction["references"]) > 0

    # Verify recommendations are actionable
    serotonin_interaction = next(
        (i for i in data["interactions"]
         if "sertraline" in i["drug1"].lower() or "sertraline" in i["drug2"].lower()),
        None
    )

    if serotonin_interaction:
        # Verify serotonin syndrome warning
        has_serotonin_warning = any(
            "serotonin" in str(effect).lower()
            for effect in serotonin_interaction["clinical_effects"]
        )
        assert has_serotonin_warning, "Should warn about serotonin syndrome"

    print("\n✅ Complete drug interaction workflow test passed:")
    print(f"   - Medications checked: {data['medication_count']}")
    print(f"   - Interactions found: {data['interactions_found']}")
    print(f"   - CONTRAINDICATED: {data['severity_summary']['contraindicated']}")
    print(f"   - SEVERE: {data['severity_summary']['severe']}")
    print(f"   - MODERATE: {data['severity_summary']['moderate']}")
    print(f"   - MINOR: {data['severity_summary']['minor']}")
