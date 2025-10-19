#!/usr/bin/env python3
"""
Direct Backend API Testing Script
Test the backend without going through the frontend
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"
# Alternative for local testing:
# BACKEND_URL = "http://localhost:8000"

AUTH_TOKEN = "REDACTED"
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Test cases
test_cases = [
    {
        "name": "Case 1: Chronic Migraine",
        "payload": {
            "patient_info": {
                "age": 35,
                "gender": "female",
                "medical_history": ["hypertension"],
                "current_medications": ["propranolol"],
                "allergies": []
            },
            "symptoms": [
                {"name": "throbbing headache", "severity": "severe", "duration_days": 3, "description": ""},
                {"name": "photophobia", "severity": "moderate", "duration_days": 3, "description": ""},
                {"name": "nausea", "severity": "moderate", "duration_days": 3, "description": ""}
            ],
            "vital_signs": {"bp_systolic": 130, "bp_diastolic": 85, "heart_rate": 72, "temperature": 36.8},
            "lab_results": {},
            "imaging_studies": [],
            "chief_complaint": "Severe throbbing headache",
            "history_present_illness": "Acute onset severe headache with light sensitivity"
        }
    },
    {
        "name": "Case 2: Acute Ischemic Stroke",
        "payload": {
            "patient_info": {
                "age": 68,
                "gender": "male",
                "medical_history": ["hypertension", "diabetes", "atrial fibrillation"],
                "current_medications": ["lisinopril", "metformin", "warfarin"],
                "allergies": ["penicillin"]
            },
            "symptoms": [
                {"name": "acute onset weakness", "severity": "severe", "duration_days": 0, "description": ""},
                {"name": "facial drooping", "severity": "severe", "duration_days": 0, "description": ""},
                {"name": "speech difficulty", "severity": "severe", "duration_days": 0, "description": ""}
            ],
            "vital_signs": {"bp_systolic": 165, "bp_diastolic": 98, "heart_rate": 92, "temperature": 37.2},
            "lab_results": {},
            "imaging_studies": [],
            "chief_complaint": "Sudden weakness and speech difficulty",
            "history_present_illness": "Acute onset of right-sided weakness and speech difficulty"
        }
    },
    {
        "name": "Case 3: Generalized Seizure",
        "payload": {
            "patient_info": {
                "age": 28,
                "gender": "female",
                "medical_history": [],
                "current_medications": [],
                "allergies": []
            },
            "symptoms": [
                {"name": "loss of consciousness", "severity": "severe", "duration_days": 0, "description": ""},
                {"name": "muscle convulsions", "severity": "severe", "duration_days": 0, "description": ""},
                {"name": "tongue biting", "severity": "moderate", "duration_days": 0, "description": ""}
            ],
            "vital_signs": {"bp_systolic": 145, "bp_diastolic": 92, "heart_rate": 118, "temperature": 37.5},
            "lab_results": {},
            "imaging_studies": [],
            "chief_complaint": "First seizure episode",
            "history_present_illness": "Sudden loss of consciousness with generalized convulsions"
        }
    },
    {
        "name": "Case 4: Parkinson's Disease",
        "payload": {
            "patient_info": {
                "age": 72,
                "gender": "male",
                "medical_history": ["hypertension", "depression"],
                "current_medications": ["amlodipine", "sertraline"],
                "allergies": []
            },
            "symptoms": [
                {"name": "resting tremor", "severity": "moderate", "duration_days": 180, "description": ""},
                {"name": "bradykinesia", "severity": "moderate", "duration_days": 180, "description": ""},
                {"name": "rigidity", "severity": "moderate", "duration_days": 180, "description": ""}
            ],
            "vital_signs": {"bp_systolic": 128, "bp_diastolic": 82, "heart_rate": 68, "temperature": 37.0},
            "lab_results": {},
            "imaging_studies": [],
            "chief_complaint": "Tremor and slowness of movement",
            "history_present_illness": "Progressive tremor and slowness over 6 months"
        }
    },
    {
        "name": "Case 5: Multiple Sclerosis",
        "payload": {
            "patient_info": {
                "age": 35,
                "gender": "female",
                "medical_history": ["optic neuritis"],
                "current_medications": [],
                "allergies": []
            },
            "symptoms": [
                {"name": "blurred vision", "severity": "moderate", "duration_days": 14, "description": ""},
                {"name": "numbness and tingling", "severity": "moderate", "duration_days": 10, "description": ""},
                {"name": "weakness", "severity": "mild", "duration_days": 10, "description": ""}
            ],
            "vital_signs": {"bp_systolic": 118, "bp_diastolic": 76, "heart_rate": 76, "temperature": 37.0},
            "lab_results": {},
            "imaging_studies": ["MRI brain"],
            "chief_complaint": "Vision loss and numbness",
            "history_present_illness": "Acute vision loss with paresthesias"
        }
    }
]

def print_separator():
    """Print a separator line"""
    print("\n" + "="*80 + "\n")

def test_health():
    """Test health endpoint"""
    print("[Test] Health Check (No Auth Required)")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_diagnosis(case_name, payload):
    """Test diagnosis endpoint"""
    print(f"[Test] {case_name}")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/diagnosis",
            json=payload,
            headers=headers,
            timeout=30
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Case ID: {data.get('case_id')}")
            print(f"Confidence: {data.get('confidence', 0):.0%}")

            diagnoses = data.get('diagnosis', [])
            print(f"Diagnoses ({len(diagnoses)}):")
            for i, diag in enumerate(diagnoses[:3], 1):
                condition = diag.get('condition', 'Unknown')
                confidence = diag.get('confidence', 0)
                print(f"  {i}. {condition} ({confidence:.0%})")

            return True, data
        else:
            print(f"Error: {response.text[:200]}")
            return False, None

    except requests.exceptions.Timeout:
        print("[ERROR] Timeout - Backend may be cold starting")
        return False, None
    except Exception as e:
        print(f"[ERROR] {e}")
        return False, None

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("NEUROAGENT BACKEND DIRECT API TEST SUITE")
    print("="*80)
    print(f"\nBackend URL: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Test 1: Health check
    print_separator()
    health_ok = test_health()

    if not health_ok:
        print("\n[WARNING] Health check failed. Backend may be offline.")
        print("Local testing? Run: python -m backend.main")
        sys.exit(1)

    # Test 2: Diagnosis endpoints
    print_separator()
    results = []

    for i, case in enumerate(test_cases, 1):
        success, data = test_diagnosis(case['name'], case['payload'])
        results.append({
            'case': case['name'],
            'success': success,
            'diagnosis': data.get('diagnosis', [{}])[0].get('condition') if data else 'N/A'
        })

        if i < len(test_cases):
            import time
            time.sleep(1)  # Rate limiting

    # Summary
    print_separator()
    print("TEST SUMMARY")
    print("="*80)

    diagnoses_found = set()
    for result in results:
        status = "[PASS]" if result['success'] else "[FAIL]"
        diagnosis = result['diagnosis']
        print(f"{status} {result['case']}")
        print(f"       -> {diagnosis}")
        diagnoses_found.add(diagnosis)

    print("\n" + "="*80)
    print(f"Unique diagnoses found: {len(diagnoses_found)}")
    print(f"Expected: {len(test_cases)}")

    if len(diagnoses_found) == len(test_cases):
        print("\n[SUCCESS] All test cases returned DIFFERENT diagnoses!")
    else:
        print("\n[WARNING] Some cases may be returning identical diagnoses")

    print("="*80 + "\n")

if __name__ == "__main__":
    main()
