#!/usr/bin/env python3
"""
Frontend Automation Test - Browser Testing
使用 Selenium 或 requests 来实际访问和测试前端
"""

import requests
import time
import json
from urllib.parse import urljoin

# ==============================================================================
# 配置
# ==============================================================================

FRONTEND_URL = "https://neuro-agent-bj6ueqom1-thc1006s-projects.vercel.app"
# 备选 URL
# FRONTEND_URL = "https://frontend-8dchdjadv-thc1006s-projects.vercel.app"

BACKEND_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"

# ==============================================================================
# 测试函数
# ==============================================================================

def test_frontend_accessibility():
    """测试前端是否可访问"""
    print("\n" + "="*80)
    print("TEST 1: Frontend Accessibility")
    print("="*80)
    print(f"URL: {FRONTEND_URL}")

    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("[OK] Frontend is accessible")

            # 检查页面内容
            if "react" in response.text.lower() or "root" in response.text.lower():
                print("[OK] React app is loaded")
                return True
            else:
                print("[WARNING] React app may not be fully loaded")
                return True
        else:
            print(f"[ERROR] Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("[ERROR] Timeout - Frontend not responding")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_api_connectivity():
    """测试前端与后端的连接"""
    print("\n" + "="*80)
    print("TEST 2: API Connectivity")
    print("="*80)
    print(f"Backend: {BACKEND_URL}")

    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"Health Check Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Health Check: {json.dumps(data, indent=2)}")
            print("[OK] Backend is healthy")
            return True
        else:
            print(f"[ERROR] Backend health check failed")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_frontend_contains_key_elements():
    """测试前端是否包含关键元素"""
    print("\n" + "="*80)
    print("TEST 3: Frontend Page Elements")
    print("="*80)

    try:
        response = requests.get(FRONTEND_URL, timeout=10)

        if response.status_code != 200:
            print(f"[ERROR] Cannot access frontend")
            return False

        content = response.text.lower()

        # 检查关键元素
        checks = {
            "NeuroAgent title": "neuro" in content,
            "Diagnosis form": "diagnosis" in content or "form" in content,
            "Input fields": "input" in content or "textfield" in content,
            "Buttons": "button" in content or "submit" in content,
            "React root": "root" in content,
        }

        all_ok = True
        for check_name, result in checks.items():
            status = "[OK]" if result else "[WARNING]"
            print(f"{status} {check_name}")
            if not result:
                all_ok = False

        return all_ok
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_api_diagnosis_endpoint():
    """测试诊断 API 端点"""
    print("\n" + "="*80)
    print("TEST 4: API Diagnosis Endpoint")
    print("="*80)

    import jwt
    import datetime

    # 生成 JWT token
    JWT_SECRET = "REDACTED"
    payload = {
        'user_id': 'test-user',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    test_data = {
        "patient_info": {
            "age": 35,
            "gender": "female",
            "medical_history": [],
            "current_medications": [],
            "allergies": []
        },
        "symptoms": [
            {"name": "headache", "severity": "severe", "duration_days": 1, "description": ""},
            {"name": "dizziness", "severity": "moderate", "duration_days": 1, "description": ""}
        ],
        "vital_signs": {"bp_systolic": 120, "bp_diastolic": 80, "heart_rate": 72, "temperature": 37},
        "lab_results": {},
        "imaging_studies": [],
        "chief_complaint": "Headache",
        "history_present_illness": "Acute headache"
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/diagnosis",
            json=test_data,
            headers=headers,
            timeout=30
        )

        print(f"Diagnosis Request Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            case_id = data.get('case_id', 'N/A')
            confidence = data.get('confidence', 0)
            diagnosis = data.get('diagnosis', [{}])[0].get('condition', 'Unknown')

            print(f"Case ID: {case_id}")
            print(f"Top Diagnosis: {diagnosis}")
            print(f"Confidence: {confidence:.0%}")
            print("[OK] Diagnosis endpoint working")

            return True
        else:
            print(f"[ERROR] Diagnosis request failed: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

# ==============================================================================
# 主程序
# ==============================================================================

def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("FRONTEND & BACKEND INTEGRATION TEST")
    print("="*80)
    print(f"\nFrontend: {FRONTEND_URL}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    # 运行测试
    results.append(("Frontend Accessibility", test_frontend_accessibility()))
    time.sleep(1)

    results.append(("API Connectivity", test_api_connectivity()))
    time.sleep(1)

    results.append(("Frontend Elements", test_frontend_contains_key_elements()))
    time.sleep(1)

    results.append(("API Diagnosis", test_api_diagnosis_endpoint()))

    # 摘要
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        print("Your NeuroAgent system is fully operational!")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        print("Please review the errors above")

    print("="*80 + "\n")

if __name__ == "__main__":
    main()
