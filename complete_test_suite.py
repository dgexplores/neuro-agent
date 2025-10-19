#!/usr/bin/env python3
"""
Complete NeuroAgent Backend Testing Suite
包含 JWT token 生成和所有测试案例
"""

import requests
import json
import jwt
import datetime
import sys
from typing import Tuple, Dict, Any

# ==============================================================================
# 配置
# ==============================================================================

# 选择后端 URL
# BACKEND_URL = "http://localhost:8000"  # 本地开发
BACKEND_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"  # 生产

# JWT 配置
JWT_SECRET = "REDACTED"
JWT_ALGORITHM = "HS256"

# ==============================================================================
# 生成 JWT Token
# ==============================================================================

def generate_jwt_token(user_id: str = "test-user", hours: int = 24) -> str:
    """生成有效的 JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# ==============================================================================
# 测试案例定义
# ==============================================================================

TEST_CASES = [
    {
        "id": 1,
        "name": "Chronic Migraine",
        "age": 35,
        "gender": "female",
        "description": "35-year-old female with chronic migraine",
        "payload": {
            "patient_info": {
                "age": 35,
                "gender": "female",
                "medical_history": ["hypertension"],
                "current_medications": ["propranolol"],
                "allergies": []
            },
            "symptoms": [
                {"name": "throbbing headache", "severity": "severe", "duration_days": 3, "description": "Bilateral throbbing pain"},
                {"name": "photophobia", "severity": "moderate", "duration_days": 3, "description": "Sensitivity to light"},
                {"name": "nausea", "severity": "moderate", "duration_days": 3, "description": "Mild nausea"},
                {"name": "fatigue", "severity": "mild", "duration_days": 3, "description": ""}
            ],
            "vital_signs": {
                "bp_systolic": 130,
                "bp_diastolic": 85,
                "heart_rate": 72,
                "temperature": 36.8
            },
            "lab_results": {},
            "imaging_studies": [],
            "chief_complaint": "Severe throbbing headache with light sensitivity",
            "history_present_illness": "Acute onset of severe bilateral throbbing headache with photophobia and nausea"
        }
    },
    {
        "id": 2,
        "name": "Acute Ischemic Stroke",
        "age": 68,
        "gender": "male",
        "description": "68-year-old male with acute stroke symptoms",
        "payload": {
            "patient_info": {
                "age": 68,
                "gender": "male",
                "medical_history": ["hypertension", "diabetes", "atrial fibrillation"],
                "current_medications": ["lisinopril", "metformin", "warfarin"],
                "allergies": ["penicillin"]
            },
            "symptoms": [
                {"name": "acute onset weakness", "severity": "severe", "duration_days": 0, "description": "Right arm and leg weakness"},
                {"name": "facial drooping", "severity": "severe", "duration_days": 0, "description": "Right side facial drooping"},
                {"name": "speech difficulty", "severity": "severe", "duration_days": 0, "description": "Slurred speech"},
                {"name": "confusion", "severity": "moderate", "duration_days": 0, "description": ""}
            ],
            "vital_signs": {
                "bp_systolic": 165,
                "bp_diastolic": 98,
                "heart_rate": 92,
                "temperature": 37.2
            },
            "lab_results": {},
            "imaging_studies": [],
            "chief_complaint": "Sudden onset weakness and speech difficulty",
            "history_present_illness": "Sudden onset of right-sided weakness and speech difficulty 45 minutes ago"
        }
    },
    {
        "id": 3,
        "name": "Generalized Tonic-Clonic Seizure",
        "age": 28,
        "gender": "female",
        "description": "28-year-old female with first unprovoked seizure",
        "payload": {
            "patient_info": {
                "age": 28,
                "gender": "female",
                "medical_history": [],
                "current_medications": [],
                "allergies": []
            },
            "symptoms": [
                {"name": "loss of consciousness", "severity": "severe", "duration_days": 0, "description": "Unresponsive for 2 minutes"},
                {"name": "muscle convulsions", "severity": "severe", "duration_days": 0, "description": "Generalized tonic-clonic convulsions"},
                {"name": "tongue biting", "severity": "moderate", "duration_days": 0, "description": "Biting of tongue"},
                {"name": "incontinence", "severity": "mild", "duration_days": 0, "description": "Urinary incontinence"},
                {"name": "post-ictal confusion", "severity": "moderate", "duration_days": 0, "description": ""}
            ],
            "vital_signs": {
                "bp_systolic": 145,
                "bp_diastolic": 92,
                "heart_rate": 118,
                "temperature": 37.5
            },
            "lab_results": {},
            "imaging_studies": [],
            "chief_complaint": "First seizure episode",
            "history_present_illness": "Sudden loss of consciousness followed by generalized tonic-clonic convulsions"
        }
    },
    {
        "id": 4,
        "name": "Parkinson's Disease",
        "age": 72,
        "gender": "male",
        "description": "72-year-old male with progressive tremor and rigidity",
        "payload": {
            "patient_info": {
                "age": 72,
                "gender": "male",
                "medical_history": ["hypertension", "hyperlipidemia"],
                "current_medications": ["amlodipine", "simvastatin"],
                "allergies": []
            },
            "symptoms": [
                {"name": "resting tremor", "severity": "moderate", "duration_days": 180, "description": "Pill-rolling tremor in right hand"},
                {"name": "bradykinesia", "severity": "moderate", "duration_days": 180, "description": "Slowness of movement"},
                {"name": "rigidity", "severity": "moderate", "duration_days": 180, "description": "Increased muscle tone"},
                {"name": "postural instability", "severity": "mild", "duration_days": 120, "description": "Balance difficulties"},
                {"name": "shuffling gait", "severity": "mild", "duration_days": 120, "description": "Shortened stride"}
            ],
            "vital_signs": {
                "bp_systolic": 128,
                "bp_diastolic": 82,
                "heart_rate": 68,
                "temperature": 37.0
            },
            "lab_results": {},
            "imaging_studies": [],
            "chief_complaint": "Progressive tremor and slowness of movement",
            "history_present_illness": "6-month history of progressive tremor and slowness"
        }
    },
    {
        "id": 5,
        "name": "Multiple Sclerosis",
        "age": 35,
        "gender": "female",
        "description": "35-year-old female with demyelinating disease",
        "payload": {
            "patient_info": {
                "age": 35,
                "gender": "female",
                "medical_history": ["optic neuritis"],
                "current_medications": [],
                "allergies": []
            },
            "symptoms": [
                {"name": "blurred vision", "severity": "moderate", "duration_days": 14, "description": "Left eye vision loss"},
                {"name": "numbness and tingling", "severity": "moderate", "duration_days": 10, "description": "Right arm and leg paresthesias"},
                {"name": "weakness", "severity": "mild", "duration_days": 10, "description": "Right leg weakness"},
                {"name": "fatigue", "severity": "moderate", "duration_days": 21, "description": "Overwhelming fatigue"},
                {"name": "heat intolerance", "severity": "mild", "duration_days": 21, "description": "Symptoms worsen with heat"}
            ],
            "vital_signs": {
                "bp_systolic": 118,
                "bp_diastolic": 76,
                "heart_rate": 76,
                "temperature": 37.0
            },
            "lab_results": {},
            "imaging_studies": ["MRI brain with gadolinium"],
            "chief_complaint": "Vision loss and numbness",
            "history_present_illness": "2-week history of vision loss and paresthesias"
        }
    }
]

# ==============================================================================
# 测试函数
# ==============================================================================

def test_health_check() -> bool:
    """测试健康检查端点"""
    print("\n[Step 1] Health Check (No Authentication Required)")
    print("-" * 80)

    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_diagnosis(token: str, test_case: Dict) -> Tuple[bool, str]:
    """测试诊断端点"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    case_id = test_case["id"]
    name = test_case["name"]
    description = test_case["description"]

    print(f"\n[Test Case {case_id}] {name}")
    print(f"Description: {description}")
    print("-" * 80)

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/diagnosis",
            json=test_case["payload"],
            headers=headers,
            timeout=30
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            diagnosis = data.get('diagnosis', [{}])[0]
            condition = diagnosis.get('condition', 'Unknown')
            confidence = diagnosis.get('confidence', 0)
            case_id = data.get('case_id', 'N/A')

            print(f"Case ID: {case_id}")
            print(f"Top Diagnosis: {condition}")
            print(f"Confidence: {confidence:.0%}")

            # 显示所有诊断
            print("\nDifferential Diagnoses:")
            for i, diag in enumerate(data.get('diagnosis', [])[:3], 1):
                cond = diag.get('condition', 'Unknown')
                conf = diag.get('confidence', 0)
                print(f"  {i}. {cond} ({conf:.0%})")

            return True, condition
        else:
            error = response.text[:200]
            print(f"Error: {error}")
            return False, "ERROR"

    except requests.exceptions.Timeout:
        print("Timeout: Backend may be cold starting or not responding")
        return False, "TIMEOUT"
    except Exception as e:
        print(f"Exception: {e}")
        return False, "EXCEPTION"

# ==============================================================================
# 主程序
# ==============================================================================

def main():
    """运行完整测试套件"""
    print("\n" + "="*80)
    print("NEUROAGENT COMPLETE BACKEND TEST SUITE")
    print("="*80)
    print(f"\nBackend URL: {BACKEND_URL}")
    print(f"Timestamp: {datetime.datetime.now().isoformat()}")

    # 步骤 1: 生成 JWT token
    print("\n" + "="*80)
    print("Step 1: Generating JWT Token")
    print("="*80)

    token = generate_jwt_token()
    print(f"Generated Token: {token[:50]}...")
    print(f"Token Valid For: 24 hours")

    # 步骤 2: 健康检查
    print("\n" + "="*80)
    print("Step 2: Backend Health Check")
    print("="*80)

    health_ok = test_health_check()

    if not health_ok:
        print("\n[ERROR] Backend is not responding!")
        print("Please ensure the backend service is running.")
        sys.exit(1)

    # 步骤 3: 运行诊断测试
    print("\n" + "="*80)
    print("Step 3: Running Diagnosis Tests")
    print("="*80)

    results = []

    for i, test_case in enumerate(TEST_CASES, 1):
        success, diagnosis = test_diagnosis(token, test_case)
        results.append({
            'case_id': test_case['id'],
            'name': test_case['name'],
            'success': success,
            'diagnosis': diagnosis
        })

        if i < len(TEST_CASES):
            import time
            time.sleep(1)  # 速率限制

    # 步骤 4: 摘要和验证
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for r in results if r['success'])

    print(f"\nTest Results: {passed}/{len(TEST_CASES)} passed\n")

    for result in results:
        status = "[PASS]" if result['success'] else "[FAIL]"
        print(f"{status} Case {result['case_id']}: {result['name']}")
        print(f"       -> Diagnosis: {result['diagnosis']}\n")

    # 检查是否有不同的诊断
    diagnoses = [r['diagnosis'] for r in results if r['success'] and r['diagnosis'] != 'ERROR']
    unique_diagnoses = set(diagnoses)

    print("="*80)
    print("VERIFICATION")
    print("="*80)
    print(f"Unique Diagnoses: {len(unique_diagnoses)}/{len(diagnoses)} cases")
    print(f"Different Cases: {len(results)}")

    if len(unique_diagnoses) == len(results):
        print("\n[SUCCESS] All test cases returned DIFFERENT diagnoses!")
        print("Your NeuroAgent system is working correctly!")
    elif len(unique_diagnoses) > 1:
        print(f"\n[WARNING] Only {len(unique_diagnoses)} unique diagnoses for {len(results)} cases")
        print("Some cases may be returning similar diagnoses")
    else:
        print("\n[ERROR] All cases returned the SAME diagnosis")
        print("This indicates a problem with diagnosis differentiation")

    print("="*80 + "\n")

if __name__ == "__main__":
    main()
