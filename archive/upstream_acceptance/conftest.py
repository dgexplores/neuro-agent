"""
Pytest-BDD Configuration and Shared Fixtures

This module provides shared fixtures, configuration, and utilities for
acceptance testing using pytest-bdd framework.

Usage:
    pytest backend/tests/acceptance/ -v
    pytest backend/tests/acceptance/ -m critical -v
    pytest backend/tests/acceptance/ --html=reports/acceptance_report.html
"""

import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

# TODO: Import actual FastAPI app
# from backend.main import app


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "critical: Critical path tests (must pass for MVP)"
    )
    config.addinivalue_line(
        "markers", "positive: Positive test cases (expected success)"
    )
    config.addinivalue_line(
        "markers", "negative: Negative test cases (expected failure/error)"
    )
    config.addinivalue_line(
        "markers", "validation: Input validation tests"
    )
    config.addinivalue_line(
        "markers", "red_flag: Red flag symptom detection tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and SLA tests"
    )
    config.addinivalue_line(
        "markers", "localization: Multi-language/i18n tests"
    )
    config.addinivalue_line(
        "markers", "drug_interaction: Drug interaction checking tests"
    )
    config.addinivalue_line(
        "markers", "parameterized: Parameterized test scenarios"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring external services"
    )


# ============================================================================
# Environment Configuration
# ============================================================================

@pytest.fixture(scope="session")
def test_config():
    """Test environment configuration"""
    return {
        "API_BASE_URL": os.getenv("TEST_API_BASE_URL", "http://testserver"),
        "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
        "DYNAMODB_TABLE": os.getenv("TEST_DYNAMODB_TABLE", "NeuroAgent-PatientCases-Test"),
        "BEDROCK_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "TEST_TIMEOUT": int(os.getenv("TEST_TIMEOUT", "30")),
        "ENABLE_MOCKS": os.getenv("ENABLE_MOCKS", "true").lower() == "true",
    }


# ============================================================================
# FastAPI Test Client
# ============================================================================

@pytest.fixture(scope="session")
def fastapi_app():
    """
    FastAPI application instance

    TODO: Replace with actual app import when backend is implemented
    """
    # from backend.main import app
    # return app

    # Placeholder - create minimal FastAPI app for testing structure
    from fastapi import FastAPI
    app = FastAPI(title="NeuroAgent Test API")

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

    @app.post("/api/v1/diagnosis")
    def mock_diagnosis_endpoint(request: Dict[str, Any]):
        """Mock diagnosis endpoint for testing structure"""
        return {
            "case_id": request.get("patient_info", {}).get("case_id", "TEST-001"),
            "diagnosis": [
                {
                    "condition": "Migraine without aura (ICHD-3 1.1)",
                    "confidence": 0.87,
                    "category": "Neurological"
                }
            ],
            "recommendations": [],
            "red_flags": [],
            "metadata": {
                "confidence_score": 0.87,
                "evidence_strength": "strong"
            }
        }

    return app


@pytest.fixture(scope="function")
def api_client(fastapi_app):
    """
    FastAPI TestClient for making API requests

    Returns:
        TestClient: FastAPI test client instance
    """
    return TestClient(fastapi_app)


# ============================================================================
# AWS Service Mocks
# ============================================================================

@pytest.fixture(scope="function")
def bedrock_mock(test_config):
    """
    Mock AWS Bedrock service for deterministic testing

    Returns:
        MockBedrockService: Mocked Bedrock service
    """
    class MockBedrockService:
        def __init__(self):
            self.model_id = test_config["BEDROCK_MODEL_ID"]
            self.invocation_count = 0
            self.quota_used = 0
            self.quota_limit = 1_000_000  # 1M tokens

        def invoke_model(self, model_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
            """Mock Bedrock model invocation"""
            self.invocation_count += 1

            # Simulate token usage (rough estimate)
            input_text = body.get("messages", [{}])[0].get("content", "")
            estimated_tokens = len(input_text.split()) * 1.3  # Rough tokenization
            self.quota_used += int(estimated_tokens)

            # Simulate latency
            time.sleep(0.1)  # 100ms mock latency

            # Return mock diagnosis based on symptoms
            symptoms = body.get("symptoms", [])
            has_red_flags = any(
                "sudden" in s.get("symptom_name", "").lower() or
                "thunderclap" in s.get("quality", "").lower()
                for s in symptoms
            )

            if has_red_flags:
                return {
                    "diagnosis": [
                        {
                            "condition": "Subarachnoid hemorrhage (SAH)",
                            "confidence": 0.80,
                            "category": "Emergency",
                            "urgency": "CRITICAL"
                        }
                    ],
                    "red_flags": ["Thunderclap onset", "First attack"],
                    "recommendations": ["Immediate CT scan", "Neurosurgery consult"]
                }
            else:
                return {
                    "diagnosis": [
                        {
                            "condition": "Migraine without aura (ICHD-3 1.1)",
                            "confidence": 0.87,
                            "category": "Neurological"
                        },
                        {
                            "condition": "Tension-type headache",
                            "confidence": 0.12,
                            "category": "Neurological"
                        },
                        {
                            "condition": "Medication overuse headache",
                            "confidence": 0.06,
                            "category": "Neurological"
                        }
                    ],
                    "recommendations": [
                        {"type": "treatment", "content": "Consider triptan medication"},
                        {"type": "prophylaxis", "content": "Consider preventive therapy"},
                    ],
                    "red_flags": []
                }

        def get_quota_remaining(self) -> float:
            """Get remaining quota percentage"""
            return ((self.quota_limit - self.quota_used) / self.quota_limit) * 100

    return MockBedrockService()


@pytest.fixture(scope="function")
def dynamodb_mock(test_config):
    """
    Mock DynamoDB for case storage testing

    Returns:
        MockDynamoDB: Mocked DynamoDB service
    """
    class MockDynamoDB:
        def __init__(self):
            self.table_name = test_config["DYNAMODB_TABLE"]
            self.items = {}  # In-memory storage

        def put_item(self, table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
            """Mock DynamoDB put_item"""
            case_id = item.get("case_id")
            self.items[case_id] = {
                **item,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            return {"ResponseMetadata": {"HTTPStatusCode": 200}}

        def get_item(self, table_name: str, key: Dict[str, str]) -> Dict[str, Any]:
            """Mock DynamoDB get_item"""
            case_id = key.get("case_id")
            item = self.items.get(case_id)

            if item:
                return {"Item": item, "ResponseMetadata": {"HTTPStatusCode": 200}}
            else:
                return {"ResponseMetadata": {"HTTPStatusCode": 404}}

        def query(self, table_name: str, index_name: str = None, **kwargs) -> Dict[str, Any]:
            """Mock DynamoDB query"""
            # Return all items (simplified)
            items = list(self.items.values())
            return {
                "Items": items[:20],  # Limit to 20
                "Count": len(items[:20]),
                "ResponseMetadata": {"HTTPStatusCode": 200}
            }

        def clear(self):
            """Clear all items (for test isolation)"""
            self.items.clear()

    mock_db = MockDynamoDB()
    yield mock_db
    mock_db.clear()  # Cleanup after test


@pytest.fixture(scope="function")
def s3_mock():
    """
    Mock S3 for medical image storage testing

    Returns:
        MockS3: Mocked S3 service
    """
    class MockS3:
        def __init__(self):
            self.buckets = {}

        def put_object(self, bucket: str, key: str, body: bytes) -> Dict[str, Any]:
            """Mock S3 put_object"""
            if bucket not in self.buckets:
                self.buckets[bucket] = {}

            self.buckets[bucket][key] = {
                "body": body,
                "size": len(body),
                "upload_time": datetime.utcnow().isoformat()
            }
            return {"ResponseMetadata": {"HTTPStatusCode": 200}}

        def get_object(self, bucket: str, key: str) -> Dict[str, Any]:
            """Mock S3 get_object"""
            if bucket in self.buckets and key in self.buckets[bucket]:
                obj = self.buckets[bucket][key]
                return {
                    "Body": obj["body"],
                    "ContentLength": obj["size"],
                    "ResponseMetadata": {"HTTPStatusCode": 200}
                }
            else:
                raise Exception("NoSuchKey")

    return MockS3()


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def typical_migraine_patient():
    """Typical migraine patient data (Scenario 1)"""
    return {
        "patient_info": {
            "age": 32,
            "gender": "female",
            "case_id": "MIG-001"
        },
        "chief_complaint": "右側太陽穴搏動性頭痛，持續12小時，伴噁心和畏光",
        "symptoms": [
            {
                "symptom_name": "headache",
                "severity": 8,
                "duration_hours": 12,
                "location": "right frontotemporal",
                "quality": "throbbing"
            },
            {
                "symptom_name": "nausea",
                "severity": 6,
                "duration_hours": 12
            },
            {
                "symptom_name": "photophobia",
                "severity": 7,
                "duration_hours": 12
            },
            {
                "symptom_name": "phonophobia",
                "severity": 7,
                "duration_hours": 12
            }
        ],
        "vital_signs": {
            "blood_pressure": "118/76",
            "heart_rate": 78,
            "temperature": 36.8,
            "respiratory_rate": 16
        },
        "medical_history": {
            "previous_migraine_attacks": 6,
            "family_history": "mother has migraine",
            "triggers": "stress, menstruation, lack of sleep",
            "medications": "ibuprofen PRN"
        }
    }


@pytest.fixture
def thunderclap_headache_patient():
    """Thunderclap headache patient data (SAH red flag - Scenario 3)"""
    return {
        "patient_info": {
            "age": 58,
            "gender": "male",
            "case_id": "SAH-001"
        },
        "chief_complaint": "突然劇烈頭痛，像被雷擊，1分鐘內達到最高峰",
        "symptoms": [
            {
                "symptom_name": "sudden_severe_headache",
                "severity": 10,
                "duration_hours": 0.017,  # <1 minute
                "location": "diffuse",
                "quality": "worst headache of life"
            },
            {
                "symptom_name": "neck_stiffness",
                "severity": 7,
                "duration_hours": 0.083
            },
            {
                "symptom_name": "photophobia",
                "severity": 9,
                "duration_hours": 0.033
            },
            {
                "symptom_name": "confusion",
                "severity": 5,
                "duration_hours": 0.167
            }
        ],
        "vital_signs": {
            "blood_pressure": "178/102",
            "heart_rate": 105,
            "temperature": 37.2,
            "respiratory_rate": 20,
            "gcs_score": 14
        },
        "medical_history": {
            "previous_attacks": 0,
            "risk_factors": "hypertension, smoking",
            "medications": "amlodipine 5mg daily"
        },
        "neurological_exam": "Positive meningismus (neck stiffness)"
    }


@pytest.fixture
def invalid_patient_data():
    """Invalid patient data for validation testing (Scenario 2)"""
    return {
        "patient_info": {
            "age": -5,  # Invalid
            "gender": "unknown",  # Invalid enum
            "case_id": "MIG-ERR-001"
        },
        "chief_complaint": "",  # Empty (invalid)
        "symptoms": [],  # Empty (invalid)
        "vital_signs": {
            "blood_pressure": "999/999",  # Out of range
            "heart_rate": -10,  # Negative (invalid)
            "temperature": "高燒",  # Wrong type
            "respiratory_rate": None  # Missing
        },
        "medical_history": {
            "previous_attacks": None,
            "medications": None
        }
    }


@pytest.fixture
def medication_overuse_patient():
    """Medication overuse headache patient (Scenario 5)"""
    return {
        "patient_info": {
            "age": 45,
            "gender": "female",
            "case_id": "MOH-001"
        },
        "chief_complaint": "幾乎每天頭痛，持續3個月，止痛藥越吃越多",
        "symptoms": [
            {
                "symptom_name": "daily_headache",
                "frequency": "20+ days/month",
                "duration_days": 90,
                "pattern": "chronic"
            }
        ],
        "medical_history": {
            "previous_attacks": "15 years of episodic migraine",
            "medication_history": "acetaminophen+caffeine daily for 6 months",
            "frequency_change": "from 2-3 attacks/month to 20+ days/month"
        },
        "medications": [
            {
                "medication": "acetaminophen 500mg + caffeine",
                "frequency": "15+ days/month",
                "duration_months": 6,
                "overuse_criteria_met": True
            },
            {
                "medication": "ibuprofen 400mg",
                "frequency": "10+ days/month",
                "duration_months": 4,
                "overuse_criteria_met": True
            },
            {
                "medication": "sumatriptan 100mg",
                "frequency": "8+ days/month",
                "duration_months": 3,
                "overuse_criteria_met": True
            }
        ]
    }


# ============================================================================
# Performance Testing Utilities
# ============================================================================

@pytest.fixture
def performance_tracker():
    """Performance measurement utility"""
    class PerformanceTracker:
        def __init__(self):
            self.timestamps = {}
            self.metrics = {}

        def record(self, event_name: str):
            """Record timestamp for event"""
            self.timestamps[event_name] = time.time()

        def measure(self, start_event: str, end_event: str) -> float:
            """Measure duration between two events in seconds"""
            if start_event in self.timestamps and end_event in self.timestamps:
                duration = self.timestamps[end_event] - self.timestamps[start_event]
                self.metrics[f"{start_event}_to_{end_event}"] = duration
                return duration
            return 0.0

        def get_total_duration(self, start_event: str, end_event: str) -> float:
            """Get total duration in seconds"""
            return self.measure(start_event, end_event)

        def assert_within_sla(self, start_event: str, end_event: str, max_seconds: float):
            """Assert duration is within SLA"""
            duration = self.measure(start_event, end_event)
            assert duration <= max_seconds, \
                f"Duration {duration:.2f}s exceeds SLA {max_seconds}s for {start_event}→{end_event}"

    return PerformanceTracker()


# ============================================================================
# Database Utilities
# ============================================================================

@pytest.fixture
def db_cleaner(dynamodb_mock):
    """Database cleanup utility"""
    yield dynamodb_mock
    # Cleanup after test
    dynamodb_mock.clear()


# ============================================================================
# Localization Utilities
# ============================================================================

@pytest.fixture
def localization_checker():
    """Localization verification utility"""
    class LocalizationChecker:
        # Simplified Chinese characters (should NOT appear in Traditional Chinese output)
        SIMPLIFIED_CHARS = {
            '无': '無',  # wú (nothing)
            '诊': '診',  # zhěn (diagnose)
            '断': '斷',  # duàn (judge)
            '头': '頭',  # tóu (head)
            '痛': '痛',  # tòng (pain) - same in both
            '药': '藥',  # yào (medicine)
            '检': '檢',  # jiǎn (check)
            '查': '查',  # chá (investigate) - same
            '应': '應',  # yīng (should)
        }

        def contains_simplified_chinese(self, text: str) -> bool:
            """Check if text contains Simplified Chinese characters"""
            return any(char in text for char in self.SIMPLIFIED_CHARS.keys())

        def find_simplified_chars(self, text: str) -> list:
            """Find all Simplified Chinese characters in text"""
            return [char for char in self.SIMPLIFIED_CHARS.keys() if char in text]

        def assert_traditional_only(self, text: str):
            """Assert text contains only Traditional Chinese"""
            simplified = self.find_simplified_chars(text)
            assert len(simplified) == 0, \
                f"Found Simplified Chinese characters: {simplified}"

    return LocalizationChecker()


# ============================================================================
# Logging and Reporting
# ============================================================================

@pytest.fixture(scope="session")
def test_report_dir():
    """Create test report directory"""
    report_dir = "reports/acceptance"
    os.makedirs(report_dir, exist_ok=True)
    return report_dir


@pytest.fixture(autouse=True)
def log_test_info(request):
    """Automatically log test information"""
    test_name = request.node.name
    print(f"\n{'='*80}")
    print(f"Running test: {test_name}")
    print(f"{'='*80}")

    yield

    print(f"\n{'='*80}")
    print(f"Completed test: {test_name}")
    print(f"{'='*80}\n")


# ============================================================================
# Pytest Hooks for Custom Behavior
# ============================================================================

def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    """Hook called when a step fails"""
    print(f"\n❌ Step failed: {step.name}")
    print(f"   Exception: {exception}")


def pytest_bdd_before_scenario(request, feature, scenario):
    """Hook called before each scenario"""
    print(f"\n🎬 Starting scenario: {scenario.name}")


def pytest_bdd_after_scenario(request, feature, scenario):
    """Hook called after each scenario"""
    print(f"✅ Completed scenario: {scenario.name}")


# ============================================================================
# Custom Assertions
# ============================================================================

class DiagnosisAssertions:
    """Custom assertion helpers for diagnosis testing"""

    @staticmethod
    def assert_diagnosis_structure(diagnosis: Dict[str, Any]):
        """Assert diagnosis response has correct structure"""
        required_fields = ['case_id', 'diagnosis', 'recommendations', 'metadata']
        for field in required_fields:
            assert field in diagnosis, f"Missing required field: {field}"

        # Validate diagnosis array
        assert isinstance(diagnosis['diagnosis'], list), "diagnosis must be a list"
        assert len(diagnosis['diagnosis']) > 0, "diagnosis list cannot be empty"

        # Validate first diagnosis
        first_dx = diagnosis['diagnosis'][0]
        assert 'condition' in first_dx, "diagnosis must have 'condition'"
        assert 'confidence' in first_dx, "diagnosis must have 'confidence'"
        assert 0 <= first_dx['confidence'] <= 1, "confidence must be between 0 and 1"

    @staticmethod
    def assert_ichd3_compliance(diagnosis: Dict[str, Any]):
        """Assert diagnosis follows ICHD-3 standards"""
        rationale = diagnosis.get('rationale', '')
        assert 'ICHD-3' in rationale or 'ICHD3' in rationale, \
            "Diagnosis must reference ICHD-3 standards"


@pytest.fixture
def diagnosis_assertions():
    """Provide diagnosis assertion helpers"""
    return DiagnosisAssertions()
