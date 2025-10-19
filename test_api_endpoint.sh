#!/bin/bash
# Test the API endpoint directly without a browser

API_URL="http://localhost:8000"
DEMO_TOKEN="REDACTED"

echo "=========================================="
echo "Testing NeuroAgent API Endpoints"
echo "=========================================="

# Test 1: Health Check
echo -e "\n[Test 1] Health Check"
curl -X GET "$API_URL/health" 2>/dev/null | jq .

# Test 2: Migraine Case
echo -e "\n[Test 2] Submitting Migraine Case..."
curl -X POST "$API_URL/api/v1/diagnosis" \
  -H "Authorization: Bearer $DEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' 2>/dev/null | jq .

# Test 3: Stroke Case
echo -e "\n[Test 3] Submitting Stroke Case..."
curl -X POST "$API_URL/api/v1/diagnosis" \
  -H "Authorization: Bearer $DEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' 2>/dev/null | jq .

echo -e "\n=========================================="
echo "API Testing Complete"
echo "=========================================="
