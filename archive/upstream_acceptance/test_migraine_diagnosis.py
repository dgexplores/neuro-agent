"""
Migraine Diagnosis Acceptance Tests using pytest-bdd

This module contains pytest-bdd test scenarios for migraine diagnosis functionality.
Maps to: backend/tests/acceptance/features/migraine_diagnosis.feature

Test execution:
    pytest backend/tests/acceptance/test_migraine_diagnosis.py -v
    pytest backend/tests/acceptance/test_migraine_diagnosis.py -k "typical_migraine" -v
    pytest backend/tests/acceptance/test_migraine_diagnosis.py -m critical -v

Requirements:
    pip install pytest pytest-bdd requests pydantic
"""

import json
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Load all scenarios from the feature file
scenarios('features/migraine_diagnosis.feature')


# ============================================================================
# Data Models for Test Context
# ============================================================================

@dataclass
class PatientInfo:
    """Patient demographic information"""
    age: Optional[int] = None
    gender: Optional[str] = None
    case_id: Optional[str] = None


@dataclass
class Symptom:
    """Patient symptom details"""
    symptom_name: str
    severity: Optional[int] = None
    duration_hours: Optional[float] = None
    location: Optional[str] = None
    quality: Optional[str] = None


@dataclass
class VitalSigns:
    """Patient vital signs"""
    blood_pressure: Optional[str] = None
    heart_rate: Optional[int] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None
    gcs_score: Optional[int] = None


@dataclass
class MedicalHistory:
    """Patient medical history"""
    previous_migraine_attacks: Optional[int] = None
    previous_attacks: Optional[int] = None
    family_history: Optional[str] = None
    triggers: Optional[str] = None
    medications: Optional[str] = None
    risk_factors: Optional[str] = None


@dataclass
class MedicationUsage:
    """Medication usage tracking"""
    medication: str
    frequency: str
    duration_months: int
    overuse_criteria_met: bool = False


@dataclass
class TestContext:
    """Test scenario context container"""
    patient_info: PatientInfo = field(default_factory=PatientInfo)
    chief_complaint: str = ""
    symptoms: List[Symptom] = field(default_factory=list)
    vital_signs: VitalSigns = field(default_factory=VitalSigns)
    medical_history: MedicalHistory = field(default_factory=MedicalHistory)
    medications: List[MedicationUsage] = field(default_factory=list)
    neurological_exam: str = ""
    confirmations: List[str] = field(default_factory=list)
    red_flags_absent: bool = False

    # Request/Response data
    api_endpoint: str = ""
    request_payload: Dict[str, Any] = field(default_factory=dict)
    response_status_code: Optional[int] = None
    response_body: Dict[str, Any] = field(default_factory=dict)
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_time_ms: Optional[float] = None

    # Timing data for performance testing
    timestamps: Dict[str, float] = field(default_factory=dict)

    # System state
    system_state: Dict[str, Any] = field(default_factory=dict)
    locale: str = "en-US"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def context():
    """Create a fresh test context for each scenario"""
    return TestContext()


@pytest.fixture
def api_client():
    """
    FastAPI test client fixture
    TODO: Import from fastapi.testclient import TestClient
    TODO: Replace with actual FastAPI app instance
    """
    # Placeholder - replace with actual implementation
    class MockAPIClient:
        def __init__(self):
            self.base_url = "http://testserver"

        def post(self, endpoint: str, json: Dict, headers: Dict = None):
            """Mock POST request"""
            # TODO: Replace with actual TestClient.post()
            raise NotImplementedError("Replace with actual FastAPI TestClient")

        def get(self, endpoint: str, headers: Dict = None):
            """Mock GET request"""
            # TODO: Replace with actual TestClient.get()
            raise NotImplementedError("Replace with actual FastAPI TestClient")

    return MockAPIClient()


@pytest.fixture
def bedrock_mock():
    """
    Mock AWS Bedrock service for deterministic testing
    TODO: Implement moto or boto3 stubber
    """
    # Placeholder - replace with actual mock implementation
    class MockBedrockService:
        def invoke_model(self, model_id: str, body: Dict) -> Dict:
            """Mock Bedrock model invocation"""
            # TODO: Return deterministic diagnosis responses based on input
            raise NotImplementedError("Implement Bedrock mock responses")

    return MockBedrockService()


@pytest.fixture
def dynamodb_mock():
    """
    Mock DynamoDB for case storage testing
    TODO: Use moto for DynamoDB mocking
    """
    # Placeholder - replace with actual mock implementation
    class MockDynamoDB:
        def __init__(self):
            self.tables = {}

        def put_item(self, table_name: str, item: Dict):
            """Mock DynamoDB put_item"""
            # TODO: Implement in-memory storage
            raise NotImplementedError("Implement DynamoDB mock")

        def get_item(self, table_name: str, key: Dict):
            """Mock DynamoDB get_item"""
            # TODO: Implement in-memory retrieval
            raise NotImplementedError("Implement DynamoDB mock")

    return MockDynamoDB()


# ============================================================================
# Background Steps (共用前置條件)
# ============================================================================

@given("NeuroAgent 診斷服務已啟動", target_fixture="neuro_agent_service")
def neuro_agent_service_started(context):
    """Background: NeuroAgent diagnosis service is running"""
    context.system_state['neuro_agent_running'] = True
    # TODO: Start or verify FastAPI app is running
    return context


@given("AWS Bedrock 連線正常")
def bedrock_connection_healthy(context, bedrock_mock):
    """Background: AWS Bedrock connection is healthy"""
    context.system_state['bedrock_connected'] = True
    # TODO: Verify Bedrock service connectivity
    pass


@given("醫學知識庫載入完成")
def medical_knowledge_loaded(context):
    """Background: Medical knowledge base loaded"""
    context.system_state['knowledge_base_loaded'] = True
    # TODO: Load medical knowledge base (drug interactions, ICHD-3 criteria)
    pass


@given("ICHD3 偏頭痛診斷標準已載入")
def ichd3_criteria_loaded(context):
    """Background: ICHD-3 migraine criteria loaded"""
    context.system_state['ichd3_loaded'] = True
    # TODO: Load ICHD-3 diagnostic criteria
    pass


# ============================================================================
# Scenario 1: Typical Migraine Without Aura - Given Steps
# ============================================================================

@given(parsers.parse("患者基本資料如下:\n{table_data}"), target_fixture="patient_basic_info")
@given("患者基本資料如下:", target_fixture="patient_basic_info")
def patient_basic_info(context, table_data=None):
    """Given: Patient basic information"""
    # TODO: Parse table data from Gherkin table
    # Expected format: | field | value |
    #                  | age   | 32    |
    #                  | gender| female|
    # For now, set placeholder values
    context.patient_info.age = 32
    context.patient_info.gender = "female"
    context.patient_info.case_id = "MIG-001"
    return context


@given(parsers.parse("患者基本資料不完整:\n{table_data}"))
@given("患者基本資料不完整:")
def patient_incomplete_info(context, table_data=None):
    """Given: Patient incomplete information (for validation testing)"""
    # TODO: Parse invalid data from table
    context.patient_info.age = -5  # Invalid age
    context.patient_info.gender = "unknown"  # Invalid gender
    context.patient_info.case_id = "MIG-ERR-001"
    return context


@given(parsers.parse('患者主訴為 "{chief_complaint}"'))
def patient_chief_complaint(context, chief_complaint):
    """Given: Patient chief complaint"""
    context.chief_complaint = chief_complaint
    return context


@given(parsers.parse('患者主訴為空字串 "{empty_string}"'))
def patient_empty_chief_complaint(context, empty_string):
    """Given: Patient chief complaint is empty (validation test)"""
    context.chief_complaint = empty_string
    return context


@given("患者症狀清單包含:")
@given(parsers.parse("患者症狀清單包含:\n{table_data}"))
def patient_symptoms_list(context, table_data=None):
    """Given: Patient symptoms list"""
    # TODO: Parse symptoms from table
    # Example symptoms for typical migraine
    context.symptoms = [
        Symptom(
            symptom_name="headache",
            severity=8,
            duration_hours=12,
            location="right frontotemporal",
            quality="throbbing"
        ),
        Symptom(symptom_name="nausea", severity=6, duration_hours=12),
        Symptom(symptom_name="photophobia", severity=7, duration_hours=12),
        Symptom(symptom_name="phonophobia", severity=7, duration_hours=12),
    ]
    return context


@given("患者症狀清單為空陣列 []")
def patient_empty_symptoms(context):
    """Given: Patient symptoms list is empty (validation test)"""
    context.symptoms = []
    return context


@given("患者症狀清單包含紅旗症狀:")
@given(parsers.parse("患者症狀清單包含紅旗症狀:\n{table_data}"))
def patient_red_flag_symptoms(context, table_data=None):
    """Given: Patient symptoms include red flags"""
    # TODO: Parse red flag symptoms from table
    context.symptoms = [
        Symptom(
            symptom_name="sudden_severe_headache",
            severity=10,
            duration_hours=0.017,  # <1 minute
            location="diffuse",
            quality="worst headache of life"
        ),
        Symptom(symptom_name="neck_stiffness", severity=7, duration_hours=0.083),
        Symptom(symptom_name="photophobia", severity=9, duration_hours=0.033),
        Symptom(symptom_name="confusion", severity=5, duration_hours=0.167),
    ]
    return context


@given("患者病史包含:")
@given(parsers.parse("患者病史包含:\n{table_data}"))
def patient_medical_history(context, table_data=None):
    """Given: Patient medical history"""
    # TODO: Parse medical history from table
    context.medical_history.previous_migraine_attacks = 6
    context.medical_history.family_history = "mother has migraine"
    context.medical_history.triggers = "stress, menstruation, lack of sleep"
    context.medical_history.medications = "ibuprofen PRN"
    return context


@given("患者病史顯示:")
@given(parsers.parse("患者病史顯示:\n{table_data}"))
def patient_history_shows(context, table_data=None):
    """Given: Patient history shows specific details"""
    # TODO: Parse from table
    # Used in red flag scenario
    context.medical_history.previous_attacks = 0  # First attack
    context.medical_history.risk_factors = "hypertension, smoking"
    context.medical_history.medications = "amlodipine 5mg daily"
    return context


@given("患者病史缺少關鍵欄位:")
@given(parsers.parse("患者病史缺少關鍵欄位:\n{table_data}"))
def patient_history_missing_fields(context, table_data=None):
    """Given: Patient history missing key fields (validation test)"""
    context.medical_history.previous_attacks = None
    context.medical_history.medications = None
    return context


@given("患者生命徵象正常:")
@given(parsers.parse("患者生命徵象正常:\n{table_data}"))
def patient_normal_vital_signs(context, table_data=None):
    """Given: Patient vital signs are normal"""
    # TODO: Parse vital signs from table
    context.vital_signs.blood_pressure = "118/76"
    context.vital_signs.heart_rate = 78
    context.vital_signs.temperature = 36.8
    context.vital_signs.respiratory_rate = 16
    return context


@given("患者生命徵象異常:")
@given(parsers.parse("患者生命徵象異常:\n{table_data}"))
def patient_abnormal_vital_signs(context, table_data=None):
    """Given: Patient vital signs are abnormal"""
    # TODO: Parse abnormal vital signs
    context.vital_signs.blood_pressure = "178/102"
    context.vital_signs.heart_rate = 105
    context.vital_signs.temperature = 37.2
    context.vital_signs.gcs_score = 14
    return context


@given("患者生命徵象包含無效數值:")
@given(parsers.parse("患者生命徵象包含無效數值:\n{table_data}"))
def patient_invalid_vital_signs(context, table_data=None):
    """Given: Patient vital signs contain invalid values"""
    context.vital_signs.blood_pressure = "999/999"
    context.vital_signs.heart_rate = -10
    context.vital_signs.temperature = "高燒"  # Invalid type
    context.vital_signs.respiratory_rate = None
    return context


@given(parsers.parse('患者確認 "{confirmation}"'))
def patient_confirms(context, confirmation):
    """Given: Patient confirms specific symptom detail"""
    context.confirmations.append(confirmation)
    return context


@given("患者無紅旗症狀（無發燒、頸部僵硬、意識改變、神經學缺損）")
def patient_no_red_flags(context):
    """Given: Patient has no red flag symptoms"""
    context.red_flags_absent = True
    return context


@given(parsers.parse('神經學檢查發現 "{finding}"'))
def neurological_exam_finding(context, finding):
    """Given: Neurological examination finding"""
    context.neurological_exam = finding
    return context


# ============================================================================
# Medication Overuse Headache Scenario - Given Steps
# ============================================================================

@given("患者用藥記錄顯示過度使用:")
@given(parsers.parse("患者用藥記錄顯示過度使用:\n{table_data}"))
def patient_medication_overuse(context, table_data=None):
    """Given: Patient medication records show overuse"""
    # TODO: Parse medication usage from table
    context.medications = [
        MedicationUsage(
            medication="acetaminophen 500mg + caffeine",
            frequency="15+ days/month",
            duration_months=6,
            overuse_criteria_met=True
        ),
        MedicationUsage(
            medication="ibuprofen 400mg",
            frequency="10+ days/month",
            duration_months=4,
            overuse_criteria_met=True
        ),
        MedicationUsage(
            medication="sumatriptan 100mg",
            frequency="8+ days/month",
            duration_months=3,
            overuse_criteria_met=True
        ),
    ]
    return context


# ============================================================================
# Performance Testing - Given Steps
# ============================================================================

@given(parsers.parse("系統負載為正常狀態 (並發用戶 <{max_users:d})"))
def system_normal_load(context, max_users):
    """Given: System load is normal state"""
    context.system_state['concurrent_users'] = max_users
    context.system_state['load_state'] = 'normal'
    return context


@given(parsers.parse("AWS Bedrock API quota 剩餘 >{percentage}%"))
def bedrock_quota_remaining(context, percentage):
    """Given: Bedrock API quota remaining"""
    context.system_state['bedrock_quota_remaining_pct'] = int(percentage)
    return context


@given("Lambda 函式已處於溫啟動狀態 (warm start)")
def lambda_warm_start(context):
    """Given: Lambda function is in warm start state"""
    context.system_state['lambda_state'] = 'warm'
    return context


@given("患者資料包含完整的偏頭痛症狀 (參照 Scenario 1)")
def patient_complete_migraine_data(context):
    """Given: Patient data contains complete migraine symptoms"""
    # Reuse Scenario 1 data
    patient_basic_info(context)
    patient_chief_complaint(context, "右側太陽穴搏動性頭痛，持續12小時，伴噁心和畏光")
    patient_symptoms_list(context)
    patient_medical_history(context)
    patient_normal_vital_signs(context)
    return context


# ============================================================================
# Localization Testing - Given Steps
# ============================================================================

@given(parsers.parse('患者使用繁體中文介面 (locale="{locale}")'))
def patient_uses_traditional_chinese(context, locale):
    """Given: Patient uses Traditional Chinese interface"""
    context.locale = locale
    return context


@given("患者輸入症狀使用中文醫療術語:")
@given(parsers.parse("患者輸入症狀使用中文醫療術語:\n{table_data}"))
def patient_chinese_symptom_terms(context, table_data=None):
    """Given: Patient inputs symptoms using Chinese medical terms"""
    # TODO: Parse Chinese symptom terms
    context.chief_complaint = "單側搏動性頭痛、噁心嘔吐、畏光畏聲"
    return context


@given(parsers.parse('API 請求標頭包含 "{header_value}"'))
def api_request_header(context, header_value):
    """Given: API request header contains specific value"""
    # Parse "Accept-Language: zh-TW" format
    if ':' in header_value:
        key, value = header_value.split(':', 1)
        context.request_payload.setdefault('headers', {})[key.strip()] = value.strip()
    return context


# ============================================================================
# Scenario Outline - Given Steps (Parameterized)
# ============================================================================

@given(parsers.parse("患者年齡為 {age:d} 歲，性別為 {gender}"))
def patient_age_and_gender(context, age, gender):
    """Given: Patient age and gender (for parameterized tests)"""
    context.patient_info.age = age
    context.patient_info.gender = gender
    return context


@given(parsers.parse("既往偏頭痛發作次數為 {count:d} 次"))
def previous_migraine_count(context, count):
    """Given: Previous migraine attack count"""
    context.medical_history.previous_migraine_attacks = count
    return context


@given(parsers.parse("頭痛持續 {hours:d} 小時"))
def headache_duration_hours(context, hours):
    """Given: Headache duration in hours"""
    if not context.symptoms:
        context.symptoms.append(Symptom(symptom_name="headache", duration_hours=hours))
    else:
        context.symptoms[0].duration_hours = hours
    return context


@given(parsers.parse("符合 ICHD-3 Criterion C 項數為 {count:d} 項"))
def criterion_c_met_count(context, count):
    """Given: Number of ICHD-3 Criterion C items met"""
    context.system_state['criterion_c_met'] = count
    return context


@given(parsers.parse("符合 ICHD-3 Criterion D 項數為 {count:d} 項"))
def criterion_d_met_count(context, count):
    """Given: Number of ICHD-3 Criterion D items met"""
    context.system_state['criterion_d_met'] = count
    return context


@given(parsers.parse("紅旗症狀數量為 {count:d} 個"))
def red_flag_count(context, count):
    """Given: Number of red flag symptoms"""
    context.system_state['red_flags_count'] = count
    return context


# ============================================================================
# When Steps (API Requests)
# ============================================================================

@when(parsers.parse('送出診斷請求到 "{endpoint}"'))
def send_diagnosis_request(context, endpoint, api_client):
    """When: Send diagnosis request to API endpoint"""
    context.api_endpoint = endpoint

    # Build request payload from context
    context.request_payload = {
        "patient_info": {
            "age": context.patient_info.age,
            "gender": context.patient_info.gender,
            "case_id": context.patient_info.case_id,
        },
        "chief_complaint": context.chief_complaint,
        "symptoms": [
            {
                "symptom_name": s.symptom_name,
                "severity": s.severity,
                "duration_hours": s.duration_hours,
                "location": s.location,
                "quality": s.quality,
            }
            for s in context.symptoms
        ],
        "vital_signs": {
            "blood_pressure": context.vital_signs.blood_pressure,
            "heart_rate": context.vital_signs.heart_rate,
            "temperature": context.vital_signs.temperature,
            "respiratory_rate": context.vital_signs.respiratory_rate,
            "gcs_score": context.vital_signs.gcs_score,
        },
        "medical_history": {
            "previous_attacks": context.medical_history.previous_migraine_attacks or context.medical_history.previous_attacks,
            "family_history": context.medical_history.family_history,
            "triggers": context.medical_history.triggers,
            "medications": context.medical_history.medications,
            "risk_factors": context.medical_history.risk_factors,
        }
    }

    # TODO: Make actual API request
    # start_time = time.time()
    # response = api_client.post(endpoint, json=context.request_payload)
    # context.response_time_ms = (time.time() - start_time) * 1000
    # context.response_status_code = response.status_code
    # context.response_body = response.json()
    # context.response_headers = dict(response.headers)

    # Placeholder for now
    context.response_status_code = 200
    context.response_body = {}
    context.response_headers = {}

    return context


@when(parsers.parse('送出診斷請求到 "{endpoint1}" 並同時觸發 "{endpoint2}"'))
def send_multiple_requests(context, endpoint1, endpoint2, api_client):
    """When: Send diagnosis request and trigger drug interaction check"""
    # First request (diagnosis)
    send_diagnosis_request(context, endpoint1, api_client)

    # Second request (drug interaction)
    # TODO: Implement drug interaction check
    context.api_endpoint = f"{endpoint1}+{endpoint2}"

    return context


@when("記錄以下時間戳:")
@when(parsers.parse("記錄以下時間戳:\n{table_data}"))
def record_timestamps(context, table_data=None):
    """When: Record performance timestamps"""
    # TODO: Record timestamps t0-t8 for performance testing
    context.timestamps = {
        't0_request_sent': 0.0,
        't1_api_gateway_received': 0.05,
        't2_lambda_invoked': 0.1,
        't3_bedrock_call_start': 0.15,
        't4_bedrock_call_end': 2.5,
        't5_dynamo_write_start': 2.6,
        't6_dynamo_write_end': 2.8,
        't7_response_returned': 2.9,
        't8_client_received': 3.0,
    }
    return context


# ============================================================================
# Then Steps (Assertions)
# ============================================================================

@then(parsers.parse("API 應在 {seconds:d} 秒內回應成功 (HTTP {status_code:d})"))
def api_responds_success(context, seconds, status_code):
    """Then: API should respond successfully within timeout"""
    assert context.response_status_code == status_code, \
        f"Expected status {status_code}, got {context.response_status_code}"

    if context.response_time_ms:
        assert context.response_time_ms <= seconds * 1000, \
            f"Response time {context.response_time_ms}ms exceeds {seconds}s limit"


@then(parsers.parse("API 應在 {seconds:d} 秒內回應錯誤 (HTTP {status_code:d} {status_text})"))
def api_responds_error(context, seconds, status_code, status_text):
    """Then: API should respond with error within timeout"""
    assert context.response_status_code == status_code, \
        f"Expected status {status_code}, got {context.response_status_code}"


@then(parsers.parse("API 應成功回應 (HTTP {status_code:d})"))
def api_responds_success_simple(context, status_code):
    """Then: API should respond successfully"""
    assert context.response_status_code == status_code


@then(parsers.parse("診斷結果應包含 {count:d} 項鑑別診斷"))
def diagnosis_contains_count(context, count):
    """Then: Diagnosis results should contain N differential diagnoses"""
    diagnoses = context.response_body.get('diagnosis', [])
    assert len(diagnoses) == count, \
        f"Expected {count} diagnoses, got {len(diagnoses)}"


@then("第一鑑別診斷應為:")
@then(parsers.parse("第一鑑別診斷應為:\n{table_data}"))
def first_diagnosis_should_be(context, table_data=None):
    """Then: First differential diagnosis should match expected values"""
    # TODO: Parse expected values from table and assert
    diagnoses = context.response_body.get('diagnosis', [])
    assert len(diagnoses) > 0, "No diagnoses returned"

    first_diagnosis = diagnoses[0]
    # TODO: Assert condition, confidence, category from table
    # Example assertions:
    # assert first_diagnosis['condition'] == "Migraine without aura (ICHD-3 1.1)"
    # assert first_diagnosis['confidence'] >= 0.85
    # assert first_diagnosis['category'] == "Neurological"


@then("第二鑑別診斷應為:")
@then(parsers.parse("第二鑑別診斷應為:\n{table_data}"))
def second_diagnosis_should_be(context, table_data=None):
    """Then: Second differential diagnosis should match expected values"""
    diagnoses = context.response_body.get('diagnosis', [])
    assert len(diagnoses) > 1, "Less than 2 diagnoses returned"
    # TODO: Assert second diagnosis details


@then("第三鑑別診斷應為:")
@then(parsers.parse("第三鑑別診斷應為:\n{table_data}"))
def third_diagnosis_should_be(context, table_data=None):
    """Then: Third differential diagnosis should match expected values"""
    diagnoses = context.response_body.get('diagnosis', [])
    assert len(diagnoses) > 2, "Less than 3 diagnoses returned"
    # TODO: Assert third diagnosis details


@then(parsers.parse("診斷依據應包含 ICHD-3 標準:\n{expected_text}"))
@then("診斷依據應包含 ICHD-3 標準:")
def diagnosis_includes_ichd3_criteria(context, expected_text=None):
    """Then: Diagnosis rationale should include ICHD-3 criteria"""
    rationale = context.response_body.get('rationale', '')
    # TODO: Assert rationale contains key ICHD-3 criteria
    # assert "ICHD-3" in rationale
    # assert "Criterion A" in rationale
    # assert "Criterion B" in rationale


@then(parsers.parse("診斷依據應包含 MOH 標準:\n{expected_text}"))
@then("診斷依據應包含 MOH 標準:")
def diagnosis_includes_moh_criteria(context, expected_text=None):
    """Then: Diagnosis rationale should include MOH criteria"""
    rationale = context.response_body.get('rationale', '')
    # TODO: Assert MOH diagnostic criteria


@then("建議應包含:")
@then(parsers.parse("建議應包含:\n{table_data}"))
def recommendations_should_include(context, table_data=None):
    """Then: Recommendations should include specific items"""
    recommendations = context.response_body.get('recommendations', [])
    # TODO: Parse expected recommendations from table and assert
    # assert any(r['type'] == 'treatment' for r in recommendations)


@then("風險警示應為空（無紅旗症狀）")
def risk_alerts_should_be_empty(context):
    """Then: Risk alerts should be empty (no red flags)"""
    red_flags = context.response_body.get('red_flags', [])
    assert len(red_flags) == 0, f"Expected no red flags, got {len(red_flags)}"


@then("應觸發緊急警示標誌 \"CRITICAL_RED_FLAG_DETECTED\"")
def should_trigger_critical_alert(context):
    """Then: Should trigger critical red flag alert"""
    alerts = context.response_body.get('alerts', [])
    assert any('CRITICAL_RED_FLAG_DETECTED' in alert for alert in alerts), \
        "Critical red flag alert not detected"


@then("Migraine 應 NOT 出現在鑑別診斷清單中")
def migraine_should_not_appear(context):
    """Then: Migraine should NOT appear in differential diagnosis list"""
    diagnoses = context.response_body.get('diagnosis', [])
    migraine_found = any('migraine' in d.get('condition', '').lower() for d in diagnoses)
    assert not migraine_found, "Migraine incorrectly appears in differential diagnosis"


@then(parsers.parse("紅旗症狀警示應包含:\n{expected_text}"))
@then("紅旗症狀警示應包含:")
def red_flag_alerts_should_contain(context, expected_text=None):
    """Then: Red flag symptom alerts should contain specific text"""
    red_flags = context.response_body.get('red_flags', [])
    # TODO: Assert red flag content


@then("建議應包含緊急處置流程:")
@then(parsers.parse("建議應包含緊急處置流程:\n{table_data}"))
def recommendations_include_emergency_protocol(context, table_data=None):
    """Then: Recommendations should include emergency management protocol"""
    recommendations = context.response_body.get('recommendations', [])
    # TODO: Assert emergency protocol steps


@then("信心度元數據應反映緊急性:")
@then(parsers.parse("信心度元數據應反映緊急性:\n{table_data}"))
def confidence_metadata_reflects_urgency(context, table_data=None):
    """Then: Confidence metadata should reflect urgency"""
    metadata = context.response_body.get('metadata', {})
    # TODO: Assert urgency_level, red_flags_detected, etc.


@then("回應應包含信心度元數據:")
@then(parsers.parse("回應應包含信心度元數據:\n{table_data}"))
def response_includes_confidence_metadata(context, table_data=None):
    """Then: Response should include confidence metadata"""
    metadata = context.response_body.get('metadata', {})
    # TODO: Assert confidence_score, evidence_strength, etc.


@then(parsers.parse('診斷結果應儲存至 DynamoDB "{table_name}" 表格'))
def diagnosis_saved_to_dynamodb(context, table_name):
    """Then: Diagnosis results should be saved to DynamoDB table"""
    # TODO: Verify DynamoDB put_item was called
    pass


@then(parsers.parse('case_id "{case_id}" 應可查詢且狀態為 "{status}"'))
def case_id_retrievable_with_status(context, case_id, status):
    """Then: case_id should be retrievable with expected status"""
    # TODO: Query DynamoDB and verify case exists with correct status
    pass


@then("診斷結果應儲存並標記為 \"high_priority\"")
def diagnosis_saved_high_priority(context):
    """Then: Diagnosis should be saved with high_priority flag"""
    # TODO: Verify priority flag in DynamoDB
    pass


@then("應觸發自動通知給值班醫師")
def should_trigger_oncall_notification(context):
    """Then: Should trigger automatic notification to on-call physician"""
    # TODO: Verify notification sent (SNS, email, etc.)
    pass


@then("CloudWatch Alarm \"RedFlagDetected\" 應被觸發")
def cloudwatch_alarm_triggered(context):
    """Then: CloudWatch Alarm should be triggered"""
    # TODO: Verify CloudWatch alarm state
    pass


# ============================================================================
# Validation Error Testing - Then Steps
# ============================================================================

@then(parsers.parse('錯誤訊息應包含 "{error_message}"'))
def error_message_contains(context, error_message):
    """Then: Error message should contain specific text"""
    error = context.response_body.get('detail', '')
    assert error_message in str(error), \
        f"Expected error message to contain '{error_message}'"


@then(parsers.parse("錯誤詳情應列出所有驗證失敗項目:\n{expected_json}"))
@then("錯誤詳情應列出所有驗證失敗項目:")
def error_details_list_validation_failures(context, expected_json=None):
    """Then: Error details should list all validation failures"""
    error_detail = context.response_body.get('detail', [])
    # TODO: Parse expected JSON and assert all validation errors present
    # Expected structure: [{"loc": [...], "msg": "...", "type": "..."}]
    assert isinstance(error_detail, list), "Error detail should be a list"
    # TODO: Assert each expected validation error is present


@then(parsers.parse('回應標頭應包含 "{header_value}"'))
def response_header_contains(context, header_value):
    """Then: Response header should contain specific value"""
    # Parse "X-Validation-Failed: true" format
    if ':' in header_value:
        key, value = header_value.split(':', 1)
        assert context.response_headers.get(key.strip()) == value.strip()


@then("不應產生 DynamoDB 記錄")
def should_not_create_dynamodb_record(context):
    """Then: Should not create DynamoDB record"""
    # TODO: Verify no put_item call was made
    pass


@then(parsers.parse('CloudWatch 應記錄 "{log_event}" 日誌事件'))
def cloudwatch_should_log_event(context, log_event):
    """Then: CloudWatch should log specific event"""
    # TODO: Verify CloudWatch logs contain event
    pass


@then("錯誤回應應包含建議修正方式:")
@then(parsers.parse("錯誤回應應包含建議修正方式:\n{table_data}"))
def error_response_includes_suggestions(context, table_data=None):
    """Then: Error response should include suggested fixes"""
    suggestions = context.response_body.get('suggestions', [])
    # TODO: Parse and assert suggested fixes


# ============================================================================
# Drug Interaction Testing - Then Steps
# ============================================================================

@then("藥物交互檢查應回傳警告:")
@then(parsers.parse("藥物交互檢查應回傳警告:\n{table_data}"))
def drug_interaction_warnings(context, table_data=None):
    """Then: Drug interaction check should return warnings"""
    warnings = context.response_body.get('drug_interaction_warnings', [])
    # TODO: Parse and assert warning details


@then("應產生藥物使用報告供病歷參考")
def generate_medication_usage_report(context):
    """Then: Should generate medication usage report"""
    report = context.response_body.get('medication_report')
    assert report is not None, "Medication usage report not generated"


# ============================================================================
# Performance Testing - Then Steps
# ============================================================================

@then(parsers.parse("總回應時間 (t8 - t0) 應 ≤{max_seconds:d} 秒 (warm start)"))
def total_response_time_within_limit(context, max_seconds):
    """Then: Total response time should be within limit"""
    if context.timestamps:
        total_time = context.timestamps['t8_client_received'] - context.timestamps['t0_request_sent']
        assert total_time <= max_seconds, \
            f"Total response time {total_time}s exceeds {max_seconds}s limit"


@then(parsers.parse("Bedrock API 呼叫時間 (t4 - t3) 應 ≤{max_seconds:d} 秒"))
def bedrock_call_time_within_limit(context, max_seconds):
    """Then: Bedrock API call time should be within limit"""
    if context.timestamps:
        bedrock_time = context.timestamps['t4_bedrock_call_end'] - context.timestamps['t3_bedrock_call_start']
        assert bedrock_time <= max_seconds, \
            f"Bedrock call time {bedrock_time}s exceeds {max_seconds}s limit"


@then(parsers.parse("DynamoDB 寫入時間 (t6 - t5) 應 ≤{max_ms:d} 毫秒"))
def dynamodb_write_time_within_limit(context, max_ms):
    """Then: DynamoDB write time should be within limit"""
    if context.timestamps:
        dynamo_time = (context.timestamps['t6_dynamo_write_end'] - context.timestamps['t5_dynamo_write_start']) * 1000
        assert dynamo_time <= max_ms, \
            f"DynamoDB write time {dynamo_time}ms exceeds {max_ms}ms limit"


@then(parsers.parse("API Gateway 延遲 (t1 - t0) 應 ≤{max_ms:d} 毫秒"))
def api_gateway_latency_within_limit(context, max_ms):
    """Then: API Gateway latency should be within limit"""
    if context.timestamps:
        gateway_time = (context.timestamps['t1_api_gateway_received'] - context.timestamps['t0_request_sent']) * 1000
        assert gateway_time <= max_ms


@then(parsers.parse("Lambda 執行時間 (t7 - t2) 應 ≤{max_seconds:d} 秒"))
def lambda_execution_time_within_limit(context, max_seconds):
    """Then: Lambda execution time should be within limit"""
    if context.timestamps:
        lambda_time = context.timestamps['t7_response_returned'] - context.timestamps['t2_lambda_invoked']
        assert lambda_time <= max_seconds


@then("回應應包含效能元數據:")
@then(parsers.parse("回應應包含效能元數據:\n{table_data}"))
def response_includes_performance_metadata(context, table_data=None):
    """Then: Response should include performance metadata"""
    metadata = context.response_body.get('performance', {})
    # TODO: Assert performance metrics


@then("CloudWatch Metrics 應記錄效能指標以供 SLA 監控")
def cloudwatch_metrics_recorded(context):
    """Then: CloudWatch Metrics should record performance indicators"""
    # TODO: Verify CloudWatch metrics published
    pass


# ============================================================================
# Localization Testing - Then Steps
# ============================================================================

@then("診斷結果應以繁體中文回傳")
def diagnosis_in_traditional_chinese(context):
    """Then: Diagnosis results should be returned in Traditional Chinese"""
    # TODO: Verify response contains Traditional Chinese characters
    pass


@then(parsers.parse('診斷名稱應為 "{expected_name}"'))
def diagnosis_name_should_be(context, expected_name):
    """Then: Diagnosis name should match expected value"""
    diagnoses = context.response_body.get('diagnosis', [])
    if diagnoses:
        assert diagnoses[0].get('condition') == expected_name


@then(parsers.parse("診斷依據應使用繁體中文醫學術語:\n{expected_text}"))
@then("診斷依據應使用繁體中文醫學術語:")
def diagnosis_uses_chinese_terminology(context, expected_text=None):
    """Then: Diagnosis rationale should use Traditional Chinese medical terms"""
    rationale = context.response_body.get('rationale', '')
    # TODO: Verify Traditional Chinese medical terminology


@then("治療建議應使用繁體中文:")
@then(parsers.parse("治療建議應使用繁體中文:\n{table_data}"))
def recommendations_in_chinese(context, table_data=None):
    """Then: Treatment recommendations should be in Traditional Chinese"""
    recommendations = context.response_body.get('recommendations', [])
    # TODO: Verify Chinese recommendations


@then("所有欄位標籤應為繁體中文:")
@then(parsers.parse("所有欄位標籤應為繁體中文:\n{table_data}"))
def all_field_labels_in_chinese(context, table_data=None):
    """Then: All field labels should be in Traditional Chinese"""
    # TODO: Verify all field labels are Traditional Chinese
    pass


@then("回應不應包含簡體中文字元")
def response_no_simplified_chinese(context):
    """Then: Response should not contain Simplified Chinese characters"""
    response_text = json.dumps(context.response_body, ensure_ascii=False)
    # TODO: Implement Simplified Chinese character detection
    # Simplified Chinese characters to check: 无 (vs 無), 诊 (vs 診), etc.
    simplified_chars = ['无', '诊', '断', '头', '痛']
    for char in simplified_chars:
        assert char not in response_text, f"Found Simplified Chinese character: {char}"


# ============================================================================
# Parameterized Testing - Then Steps
# ============================================================================

@then(parsers.parse('偏頭痛診斷信心度應在 {confidence_range} 範圍內'))
def migraine_confidence_in_range(context, confidence_range):
    """Then: Migraine diagnosis confidence should be within range"""
    # Parse range like "0.85-0.95"
    min_conf, max_conf = map(float, confidence_range.split('-'))

    diagnoses = context.response_body.get('diagnosis', [])
    migraine_diagnosis = next((d for d in diagnoses if 'migraine' in d.get('condition', '').lower()), None)

    if migraine_diagnosis:
        confidence = migraine_diagnosis.get('confidence', 0)
        assert min_conf <= confidence <= max_conf, \
            f"Confidence {confidence} not in range [{min_conf}, {max_conf}]"


@then(parsers.parse('診斷品質評級應為 "{expected_rating}"'))
def diagnosis_quality_rating(context, expected_rating):
    """Then: Diagnosis quality rating should match expected value"""
    metadata = context.response_body.get('metadata', {})
    quality_rating = metadata.get('quality_rating', '')
    assert quality_rating == expected_rating, \
        f"Expected quality rating '{expected_rating}', got '{quality_rating}'"


# ============================================================================
# Helper Functions (Not Step Definitions)
# ============================================================================

def parse_table_data(table_text: str) -> List[Dict[str, str]]:
    """
    Parse Gherkin table data into list of dictionaries

    Example input:
        | field  | value  |
        | age    | 32     |
        | gender | female |

    Returns:
        [{'field': 'age', 'value': '32'}, {'field': 'gender', 'value': 'female'}]
    """
    # TODO: Implement table parsing
    lines = table_text.strip().split('\n')
    # Extract headers from first line
    # Extract data rows
    # Return list of dicts
    return []


def build_diagnosis_request_payload(context: TestContext) -> Dict[str, Any]:
    """Build diagnosis API request payload from test context"""
    return {
        "patient_info": {
            "age": context.patient_info.age,
            "gender": context.patient_info.gender,
            "case_id": context.patient_info.case_id,
        },
        "chief_complaint": context.chief_complaint,
        "symptoms": [
            {
                "symptom_name": s.symptom_name,
                "severity": s.severity,
                "duration_hours": s.duration_hours,
                "location": s.location,
                "quality": s.quality,
            }
            for s in context.symptoms
        ],
        "vital_signs": {
            "blood_pressure": context.vital_signs.blood_pressure,
            "heart_rate": context.vital_signs.heart_rate,
            "temperature": context.vital_signs.temperature,
            "respiratory_rate": context.vital_signs.respiratory_rate,
        },
        "medical_history": {
            "previous_attacks": context.medical_history.previous_migraine_attacks,
            "family_history": context.medical_history.family_history,
            "triggers": context.medical_history.triggers,
            "medications": context.medical_history.medications,
        }
    }


# ============================================================================
# Pytest Markers for Selective Test Execution
# ============================================================================

pytest_plugins = ['pytest_bdd']

# Custom markers (define in pytest.ini or conftest.py)
# @pytest.mark.critical - Critical path tests (must pass for MVP)
# @pytest.mark.positive - Positive test cases (expected success)
# @pytest.mark.negative - Negative test cases (expected failure)
# @pytest.mark.validation - Input validation tests
# @pytest.mark.red_flag - Red flag symptom detection tests
# @pytest.mark.performance - Performance and SLA tests
# @pytest.mark.localization - Multi-language tests
# @pytest.mark.drug_interaction - Drug interaction tests
