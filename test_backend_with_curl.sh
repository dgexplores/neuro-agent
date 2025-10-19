#!/bin/bash

# Direct Backend API Testing with curl
# No frontend involved - direct API calls

BACKEND_URL="https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"
TOKEN="REDACTED"

echo "=================================================="
echo "NeuroAgent Backend Direct API Tests"
echo "=================================================="
echo ""
echo "Backend: $BACKEND_URL"
echo ""

# Test 1: Health Check (No auth required)
echo "[Test 1] Health Check"
echo "=================================================="
curl -X GET "$BACKEND_URL/health" \
  -H "Content-Type: application/json" 2>/dev/null | jq . || echo "curl failed"
echo ""

# Test 2: Migraine Case
echo "[Test 2] Migraine Diagnosis"
echo "=================================================="
curl -X POST "$BACKEND_URL/api/v1/diagnosis" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
  }' 2>/dev/null | jq '.diagnosis[0]' || echo "curl failed"
echo ""

# Test 3: Stroke Case
echo "[Test 3] Stroke Diagnosis"
echo "=================================================="
curl -X POST "$BACKEND_URL/api/v1/diagnosis" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 68,
      "gender": "male",
      "medical_history": ["hypertension", "diabetes", "atrial fibrillation"],
      "current_medications": ["lisinopril", "metformin", "warfarin"],
      "allergies": []
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
    "history_present_illness": "Acute stroke symptoms"
  }' 2>/dev/null | jq '.diagnosis[0]' || echo "curl failed"
echo ""

# Test 4: Seizure Case
echo "[Test 4] Seizure Diagnosis"
echo "=================================================="
curl -X POST "$BACKEND_URL/api/v1/diagnosis" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
    "history_present_illness": "Sudden loss of consciousness with convulsions"
  }' 2>/dev/null | jq '.diagnosis[0]' || echo "curl failed"
echo ""

# Test 5: Parkinsons Case
echo "[Test 5] Parkinsons Diagnosis"
echo "=================================================="
curl -X POST "$BACKEND_URL/api/v1/diagnosis" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 72,
      "gender": "male",
      "medical_history": ["hypertension"],
      "current_medications": ["amlodipine"],
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
    "chief_complaint": "Tremor and slowness",
    "history_present_illness": "Progressive tremor and slowness over 6 months"
  }' 2>/dev/null | jq '.diagnosis[0]' || echo "curl failed"
echo ""

# Test 6: MS Case
echo "[Test 6] Multiple Sclerosis Diagnosis"
echo "=================================================="
curl -X POST "$BACKEND_URL/api/v1/diagnosis" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
    "imaging_studies": [],
    "chief_complaint": "Vision loss and numbness",
    "history_present_illness": "Acute vision loss with paresthesias"
  }' 2>/dev/null | jq '.diagnosis[0]' || echo "curl failed"
echo ""

echo "=================================================="
echo "Testing Complete!"
echo "=================================================="
