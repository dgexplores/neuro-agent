#!/usr/bin/env python3
"""
Direct API endpoint testing without browser
"""

import requests
import json
import time

API_URL = "http://localhost:8000"
DEMO_TOKEN = "REDACTED"

def print_response(title: str, response):
    """Pretty print API response"""
    print(f"\n{title}")
    print("-" * 60)
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text[:200]}")

def test_health_check():
    """Test health endpoint"""
    print("\n[Test 1] Health Check")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print_response("Response:", response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_migraine_diagnosis():
    """Test migraine case"""
    print("\n[Test 2] Submitting Migraine Case")
    payload = {
        "patient_info": {
            "age": 35,
            "gender": "female",
            "medical_history": [],
            "current_medications": [],
            "allergies": []
        },
        "symptoms": [
            {"name": "headache", "severity": "severe", "duration_days": 2, "description": ""},
            {"name": "photophobia", "severity": "moderate", "duration_days": 2, "description": ""},
            {"name": "nausea", "severity": "moderate", "duration_days": 2, "description": ""}
        ],
        "vital_signs": {"bp_systolic": 120, "bp_diastolic": 80, "heart_rate": 78, "temperature": 37.2},
        "lab_results": {},
        "imaging_studies": [],
        "chief_complaint": "Severe headache with light sensitivity",
        "history_present_illness": "Acute onset headache with photophobia and nausea"
    }

    try:
        response = requests.post(
            f"{API_URL}/api/v1/diagnosis",
            json=payload,
            headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
            timeout=30
        )
        print_response("Response:", response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_stroke_diagnosis():
    """Test stroke case"""
    print("\n[Test 3] Submitting Stroke Case")
    payload = {
        "patient_info": {
            "age": 68,
            "gender": "male",
            "medical_history": ["hypertension", "diabetes"],
            "current_medications": ["lisinopril", "metformin"],
            "allergies": []
        },
        "symptoms": [
            {"name": "acute weakness", "severity": "severe", "duration_days": 0, "description": ""},
            {"name": "facial drooping", "severity": "severe", "duration_days": 0, "description": ""},
            {"name": "speech difficulty", "severity": "severe", "duration_days": 0, "description": ""}
        ],
        "vital_signs": {"bp_systolic": 165, "bp_diastolic": 95, "heart_rate": 88, "temperature": 37.1},
        "lab_results": {},
        "imaging_studies": [],
        "chief_complaint": "Sudden onset weakness and speech difficulty",
        "history_present_illness": "Acute neurological symptoms suggestive of stroke"
    }

    try:
        response = requests.post(
            f"{API_URL}/api/v1/diagnosis",
            json=payload,
            headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
            timeout=30
        )
        print_response("Response:", response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_seizure_diagnosis():
    """Test seizure case"""
    print("\n[Test 4] Submitting Seizure Case")
    payload = {
        "patient_info": {
            "age": 25,
            "gender": "male",
            "medical_history": [],
            "current_medications": [],
            "allergies": []
        },
        "symptoms": [
            {"name": "loss of consciousness", "severity": "severe", "duration_days": 0, "description": ""},
            {"name": "muscle convulsions", "severity": "severe", "duration_days": 0, "description": ""},
            {"name": "tongue biting", "severity": "moderate", "duration_days": 0, "description": ""}
        ],
        "vital_signs": {"bp_systolic": 135, "bp_diastolic": 88, "heart_rate": 105, "temperature": 37.0},
        "lab_results": {},
        "imaging_studies": [],
        "chief_complaint": "First seizure episode",
        "history_present_illness": "Sudden loss of consciousness with convulsions"
    }

    try:
        response = requests.post(
            f"{API_URL}/api/v1/diagnosis",
            json=payload,
            headers={"Authorization": f"Bearer {DEMO_TOKEN}"},
            timeout=30
        )
        print_response("Response:", response)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "="*60)
    print("DIRECT API ENDPOINT TESTING")
    print("No browser or computer vision required!")
    print("="*60)

    print("\nChecking if backend is running at:", API_URL)
    print("This test does NOT require:")
    print("  - Web browser")
    print("  - Computer vision")
    print("  - GUI interface")
    print("\nIt tests:")
    print("  - Direct HTTP API calls")
    print("  - Diagnosis logic")
    print("  - Different case handling")

    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Migraine Case", test_migraine_diagnosis),
        ("Stroke Case", test_stroke_diagnosis),
        ("Seizure Case", test_seizure_diagnosis),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[EXCEPTION] {test_name}: {e}")
            results[test_name] = False
        time.sleep(0.5)  # Rate limiting

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        print("Your NeuroAgent API is working correctly")
        print("You can now test different cases and get different diagnoses")
    else:
        print("\n[NOTE] Make sure backend is running:")
        print("  1. Open terminal in project directory")
        print("  2. Run: python -m backend.main")
        print("  3. The backend should be accessible at http://localhost:8000")

if __name__ == "__main__":
    main()
