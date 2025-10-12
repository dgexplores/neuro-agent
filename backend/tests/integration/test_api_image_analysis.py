"""
E2E Integration tests for Medical Image Analysis API

Phase 7-2: Image Analysis Placeholder Testing
Tests the complete image upload and analysis workflow,
ensuring correct JSON format and structure.

These tests verify:
1. Image upload endpoint functionality
2. JSON response structure matches specification
3. All required fields are present with correct types
4. Error handling for invalid inputs
5. Authentication requirements
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from io import BytesIO
from datetime import datetime

from backend.main import app


# Test client setup
@pytest.fixture
def client():
    """Create FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_auth_token():
    """Mock authentication token"""
    return "Bearer test-token-image-analysis"


@pytest.fixture
def valid_image_file():
    """Create a mock image file for testing"""
    # Create a simple fake image file (1x1 pixel PNG)
    fake_image_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return BytesIO(fake_image_data)


@pytest.fixture
def invalid_text_file():
    """Create a non-image file for error testing"""
    return BytesIO(b"This is a text file, not an image")


# ============================================================================
# Test 1: Image Upload Endpoint - Authentication
# ============================================================================

def test_image_upload_requires_authentication(client, valid_image_file):
    """Test POST /api/v1/upload-image requires authentication"""
    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("test_brain_mri.jpg", valid_image_file, "image/jpeg")}
    )

    assert response.status_code == 403
    assert "detail" in response.json()


# ============================================================================
# Test 2: Image Upload Endpoint - Valid Upload
# ============================================================================

@patch('backend.main.verify_token')
def test_image_upload_success(mock_verify_token, client, valid_image_file, mock_auth_token):
    """Test POST /api/v1/upload-image with valid image file"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("brain_scan.jpg", valid_image_file, "image/jpeg")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify top-level response structure
    assert "image_id" in data
    assert "status" in data
    assert "timestamp" in data
    assert "image_metadata" in data
    assert "analysis" in data
    assert "recommendations" in data
    assert "disclaimer" in data
    assert "processing_metadata" in data


# ============================================================================
# Test 3: JSON Format Verification - Top Level Fields
# ============================================================================

@patch('backend.main.verify_token')
def test_image_analysis_response_top_level_structure(
    mock_verify_token,
    client,
    valid_image_file,
    mock_auth_token
):
    """Test that image analysis response has correct top-level JSON structure"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("mri_scan.png", valid_image_file, "image/png")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    # Required top-level fields
    required_fields = [
        "image_id",
        "status",
        "timestamp",
        "image_metadata",
        "analysis",
        "recommendations",
        "disclaimer",
        "processing_metadata"
    ]

    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Verify field types
    assert isinstance(data["image_id"], str), "image_id should be string (UUID)"
    assert isinstance(data["status"], str), "status should be string"
    assert isinstance(data["timestamp"], str), "timestamp should be ISO format string"
    assert isinstance(data["image_metadata"], dict), "image_metadata should be dict"
    assert isinstance(data["analysis"], dict), "analysis should be dict"
    assert isinstance(data["recommendations"], list), "recommendations should be list"
    assert isinstance(data["disclaimer"], str), "disclaimer should be string"
    assert isinstance(data["processing_metadata"], dict), "processing_metadata should be dict"


# ============================================================================
# Test 4: JSON Format Verification - image_metadata Structure
# ============================================================================

@patch('backend.main.verify_token')
def test_image_metadata_structure(mock_verify_token, client, valid_image_file, mock_auth_token):
    """Test that image_metadata section has correct structure"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("ct_scan.jpg", valid_image_file, "image/jpeg")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    metadata = response.json()["image_metadata"]

    # Required metadata fields
    required_fields = [
        "filename",
        "size_bytes",
        "content_type",
        "modality",
        "storage_location"
    ]

    for field in required_fields:
        assert field in metadata, f"Missing metadata field: {field}"

    # Verify field types
    assert isinstance(metadata["filename"], str)
    assert isinstance(metadata["size_bytes"], int)
    assert isinstance(metadata["content_type"], str)
    assert isinstance(metadata["modality"], str)
    assert isinstance(metadata["storage_location"], str)

    # Verify field values
    assert metadata["filename"] == "ct_scan.jpg"
    assert metadata["content_type"] == "image/jpeg"
    assert metadata["modality"] in ["CT", "MRI", "X-ray", "PET", "Ultrasound"]
    assert "s3://" in metadata["storage_location"], "Should contain S3 path placeholder"


# ============================================================================
# Test 5: JSON Format Verification - analysis Structure
# ============================================================================

@patch('backend.main.verify_token')
def test_analysis_structure(mock_verify_token, client, valid_image_file, mock_auth_token):
    """Test that analysis section has correct comprehensive structure"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("brain_mri.jpg", valid_image_file, "image/jpeg")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    analysis = response.json()["analysis"]

    # Required analysis fields
    required_fields = [
        "modality",
        "anatomical_region",
        "view_position",
        "quality_score",
        "findings",
        "abnormalities_detected",
        "key_measurements",
        "impression",
        "confidence_score"
    ]

    for field in required_fields:
        assert field in analysis, f"Missing analysis field: {field}"

    # Verify field types
    assert isinstance(analysis["modality"], str)
    assert isinstance(analysis["anatomical_region"], str)
    assert isinstance(analysis["view_position"], str)
    assert isinstance(analysis["quality_score"], (int, float))
    assert isinstance(analysis["findings"], list)
    assert isinstance(analysis["abnormalities_detected"], list)
    assert isinstance(analysis["key_measurements"], dict)
    assert isinstance(analysis["impression"], str)
    assert isinstance(analysis["confidence_score"], (int, float))

    # Verify value ranges
    assert 0.0 <= analysis["quality_score"] <= 1.0, "Quality score should be 0-1"
    assert 0.0 <= analysis["confidence_score"] <= 1.0, "Confidence score should be 0-1"

    # Verify anatomical regions are valid
    valid_regions = ["Brain", "Spine", "Head", "Neck"]
    assert analysis["anatomical_region"] in valid_regions or analysis["anatomical_region"].startswith("Brain")


# ============================================================================
# Test 6: JSON Format Verification - findings Array Structure
# ============================================================================

@patch('backend.main.verify_token')
def test_findings_array_structure(mock_verify_token, client, valid_image_file, mock_auth_token):
    """Test that findings array contains properly structured finding objects"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("scan.jpg", valid_image_file, "image/jpeg")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    findings = response.json()["analysis"]["findings"]

    # Verify findings is a non-empty array
    assert isinstance(findings, list)
    assert len(findings) > 0, "Should have at least one finding"

    # Verify each finding has correct structure
    for finding in findings:
        required_finding_fields = [
            "category",
            "description",
            "confidence",
            "location",
            "severity"
        ]

        for field in required_finding_fields:
            assert field in finding, f"Missing finding field: {field}"

        # Verify field types
        assert isinstance(finding["category"], str)
        assert isinstance(finding["description"], str)
        assert isinstance(finding["confidence"], (int, float))
        assert isinstance(finding["location"], str)
        assert isinstance(finding["severity"], str)

        # Verify value ranges
        assert 0.0 <= finding["confidence"] <= 1.0, "Finding confidence should be 0-1"

        # Verify severity levels
        valid_severities = ["none", "mild", "moderate", "severe", "critical"]
        assert finding["severity"] in valid_severities, f"Invalid severity: {finding['severity']}"


# ============================================================================
# Test 7: JSON Format Verification - key_measurements Structure
# ============================================================================

@patch('backend.main.verify_token')
def test_key_measurements_structure(mock_verify_token, client, valid_image_file, mock_auth_token):
    """Test that key_measurements dict has expected structure"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("brain.jpg", valid_image_file, "image/jpeg")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    measurements = response.json()["analysis"]["key_measurements"]

    # Verify measurements is a dict
    assert isinstance(measurements, dict)
    assert len(measurements) > 0, "Should have at least one measurement"

    # Verify expected measurement fields exist
    expected_fields = ["midline_shift_mm", "ventricular_size", "brain_volume_ml"]
    for field in expected_fields:
        assert field in measurements, f"Missing measurement: {field}"

    # Verify measurement types and values
    assert isinstance(measurements["midline_shift_mm"], (int, float))
    assert isinstance(measurements["ventricular_size"], str)
    assert isinstance(measurements["brain_volume_ml"], (int, float))

    assert measurements["midline_shift_mm"] >= 0, "Midline shift should be non-negative"
    assert measurements["brain_volume_ml"] > 0, "Brain volume should be positive"


# ============================================================================
# Test 8: JSON Format Verification - processing_metadata Structure
# ============================================================================

@patch('backend.main.verify_token')
def test_processing_metadata_structure(
    mock_verify_token,
    client,
    valid_image_file,
    mock_auth_token
):
    """Test that processing_metadata has correct structure"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("test.jpg", valid_image_file, "image/jpeg")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    metadata = response.json()["processing_metadata"]

    # Required processing metadata fields
    required_fields = [
        "model_version",
        "processing_time_ms",
        "sagemaker_endpoint",
        "ai_confidence"
    ]

    for field in required_fields:
        assert field in metadata, f"Missing processing metadata field: {field}"

    # Verify field types
    assert isinstance(metadata["model_version"], str)
    assert isinstance(metadata["processing_time_ms"], (int, float))
    assert isinstance(metadata["sagemaker_endpoint"], str)
    assert isinstance(metadata["ai_confidence"], (int, float))

    # Verify value ranges
    assert metadata["processing_time_ms"] > 0, "Processing time should be positive"
    assert 0.0 <= metadata["ai_confidence"] <= 1.0, "AI confidence should be 0-1"


# ============================================================================
# Test 9: JSON Format Verification - recommendations Array
# ============================================================================

@patch('backend.main.verify_token')
def test_recommendations_array_structure(
    mock_verify_token,
    client,
    valid_image_file,
    mock_auth_token
):
    """Test that recommendations array has correct structure"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("image.jpg", valid_image_file, "image/jpeg")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    recommendations = response.json()["recommendations"]

    # Verify recommendations is a non-empty array
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0, "Should have at least one recommendation"

    # Verify all recommendations are strings
    for rec in recommendations:
        assert isinstance(rec, str), "Each recommendation should be a string"
        assert len(rec) > 0, "Recommendation should not be empty string"

    # Verify contains important disclaimer
    has_professional_review = any(
        "radiolog" in rec.lower() or "professional" in rec.lower()
        for rec in recommendations
    )
    assert has_professional_review, "Should recommend professional radiological review"


# ============================================================================
# Test 10: Error Handling - Invalid File Type
# ============================================================================

@patch('backend.main.verify_token')
def test_invalid_file_type_returns_400(
    mock_verify_token,
    client,
    invalid_text_file,
    mock_auth_token
):
    """Test POST /api/v1/upload-image rejects non-image files"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("document.txt", invalid_text_file, "text/plain")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "file type" in data["detail"].lower() or "invalid" in data["detail"].lower()


# ============================================================================
# Test 11: Error Handling - Missing File
# ============================================================================

@patch('backend.main.verify_token')
def test_missing_file_returns_error(mock_verify_token, client, mock_auth_token):
    """Test POST /api/v1/upload-image without file upload"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        headers={"Authorization": mock_auth_token}
    )

    # Should return 422 (Unprocessable Entity) for missing file
    assert response.status_code == 422


# ============================================================================
# Test 12: Different Image Formats
# ============================================================================

@pytest.mark.parametrize("filename,content_type", [
    ("scan.jpg", "image/jpeg"),
    ("scan.png", "image/png"),
    ("scan.gif", "image/gif"),
    ("scan.bmp", "image/bmp")
])
@patch('backend.main.verify_token')
def test_different_image_formats(
    mock_verify_token,
    client,
    valid_image_file,
    mock_auth_token,
    filename,
    content_type
):
    """Test POST /api/v1/upload-image supports multiple image formats"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": (filename, valid_image_file, content_type)},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify correct filename is captured
    assert data["image_metadata"]["filename"] == filename
    assert data["image_metadata"]["content_type"] == content_type


# ============================================================================
# Test 13: Timestamp Format Verification
# ============================================================================

@patch('backend.main.verify_token')
def test_timestamp_is_valid_iso_format(
    mock_verify_token,
    client,
    valid_image_file,
    mock_auth_token
):
    """Test that timestamp field is valid ISO 8601 format"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("test.jpg", valid_image_file, "image/jpeg")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    timestamp = response.json()["timestamp"]

    # Verify timestamp can be parsed as ISO format
    try:
        parsed_time = datetime.fromisoformat(timestamp)
        assert isinstance(parsed_time, datetime)
    except ValueError:
        pytest.fail(f"Timestamp is not valid ISO format: {timestamp}")


# ============================================================================
# Test 14: UUID Validation
# ============================================================================

@patch('backend.main.verify_token')
def test_image_id_is_valid_uuid(mock_verify_token, client, valid_image_file, mock_auth_token):
    """Test that image_id is a valid UUID"""
    mock_verify_token.return_value = "user123"

    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("test.jpg", valid_image_file, "image/jpeg")},
        headers={"Authorization": mock_auth_token}
    )

    assert response.status_code == 200
    image_id = response.json()["image_id"]

    # Verify UUID format (8-4-4-4-12 hexadecimal pattern)
    import uuid
    try:
        uuid_obj = uuid.UUID(image_id)
        assert str(uuid_obj) == image_id
    except ValueError:
        pytest.fail(f"image_id is not a valid UUID: {image_id}")


# ============================================================================
# Test 15: Complete E2E Workflow Test
# ============================================================================

@patch('backend.main.verify_token')
def test_complete_image_analysis_e2e_workflow(
    mock_verify_token,
    client,
    valid_image_file,
    mock_auth_token
):
    """
    Complete E2E test for image analysis workflow

    This test verifies:
    1. Authentication works
    2. Image upload succeeds
    3. Complete JSON structure is correct
    4. All required fields are present with correct types
    5. All value ranges are valid
    6. Response includes proper medical disclaimers
    """
    mock_verify_token.return_value = "radiologist_user"

    # Upload image
    response = client.post(
        "/api/v1/upload-image",
        files={"file": ("patient_brain_mri.jpg", valid_image_file, "image/jpeg")},
        headers={"Authorization": mock_auth_token}
    )

    # Verify success
    assert response.status_code == 200

    # Get complete response
    data = response.json()

    # Verify complete structure
    assert "image_id" in data
    assert "status" in data
    assert data["status"] == "analyzed"

    # Verify image metadata
    metadata = data["image_metadata"]
    assert metadata["filename"] == "patient_brain_mri.jpg"
    assert metadata["content_type"] == "image/jpeg"
    assert metadata["modality"] in ["CT", "MRI", "X-ray", "PET"]

    # Verify analysis completeness
    analysis = data["analysis"]
    assert len(analysis["findings"]) >= 1
    assert 0.0 <= analysis["confidence_score"] <= 1.0
    assert len(analysis["impression"]) > 0

    # Verify findings structure
    for finding in analysis["findings"]:
        assert all(key in finding for key in ["category", "description", "confidence", "location", "severity"])
        assert 0.0 <= finding["confidence"] <= 1.0

    # Verify measurements
    measurements = analysis["key_measurements"]
    assert "midline_shift_mm" in measurements
    assert "brain_volume_ml" in measurements

    # Verify recommendations exist
    assert len(data["recommendations"]) > 0

    # Verify medical disclaimer exists
    assert "disclaimer" in data
    assert len(data["disclaimer"]) > 0
    assert "AI" in data["disclaimer"] or "educational" in data["disclaimer"].lower()

    # Verify processing metadata
    proc_meta = data["processing_metadata"]
    assert "model_version" in proc_meta
    assert "processing_time_ms" in proc_meta
    assert proc_meta["processing_time_ms"] > 0

    print("\n✅ Complete E2E image analysis workflow test passed:")
    print(f"   - Image ID: {data['image_id']}")
    print(f"   - Status: {data['status']}")
    print(f"   - Modality: {metadata['modality']}")
    print(f"   - Findings: {len(analysis['findings'])}")
    print(f"   - Confidence: {analysis['confidence_score']}")
    print(f"   - Processing Time: {proc_meta['processing_time_ms']}ms")
