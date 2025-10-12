"""
Test Data Generator for NeuroAgent Load Testing

Phase 8-1: Performance Testing
Generates realistic medical data for load testing
"""

import random
from io import BytesIO
from typing import Dict, List, Any


# Authentication token for load testing
AUTH_TOKEN = "test-load-testing-token-12345"


# Realistic medical test data pools
SYMPTOMS = [
    {"name": "severe headache", "severity": "severe", "description": "throbbing pain on left side"},
    {"name": "dizziness", "severity": "moderate", "description": "room spinning sensation"},
    {"name": "nausea", "severity": "moderate", "description": "feeling of sickness"},
    {"name": "blurred vision", "severity": "mild", "description": "difficulty focusing"},
    {"name": "numbness", "severity": "severe", "description": "loss of sensation in right arm"},
    {"name": "confusion", "severity": "moderate", "description": "difficulty concentrating"},
    {"name": "tremor", "severity": "mild", "description": "shaking in hands"},
    {"name": "weakness", "severity": "moderate", "description": "reduced muscle strength"},
    {"name": "photophobia", "severity": "moderate", "description": "sensitivity to light"},
    {"name": "neck stiffness", "severity": "mild", "description": "reduced neck mobility"},
]

CHIEF_COMPLAINTS = [
    "Severe headache for 2 days",
    "Sudden onset dizziness and nausea",
    "Numbness and tingling in right arm",
    "Progressive weakness in legs",
    "Confusion and memory problems",
    "Tremor interfering with daily activities",
    "Severe migraine with visual aura",
    "Balance problems and falls",
    "Persistent headache with neck pain",
    "Seizure-like episode this morning",
]

MEDICAL_HISTORY = [
    ["hypertension"],
    ["diabetes", "hypertension"],
    ["migraine", "anxiety"],
    ["stroke", "hypertension", "diabetes"],
    ["epilepsy"],
    ["parkinson's disease"],
    ["multiple sclerosis"],
    ["depression", "anxiety"],
    [],  # No history
    ["hypertension", "hyperlipidemia"],
]

CURRENT_MEDICATIONS = [
    ["lisinopril", "metformin"],
    ["warfarin", "aspirin"],
    ["sertraline", "sumatriptan"],
    ["levodopa", "carbidopa"],
    ["gabapentin", "pregabalin"],
    ["topiramate", "propranolol"],
    ["phenytoin", "lamotrigine"],
    [],  # No medications
    ["atenolol", "simvastatin"],
    ["amitriptyline", "clonazepam"],
]

AGES = [25, 32, 45, 52, 58, 63, 67, 72, 78, 82]

GENDERS = ["male", "female"]

VITAL_SIGNS_TEMPLATES = [
    {"heart_rate": 72, "blood_pressure_systolic": 120, "blood_pressure_diastolic": 80, "temperature": 37.0},
    {"heart_rate": 88, "blood_pressure_systolic": 140, "blood_pressure_diastolic": 90, "temperature": 37.2},
    {"heart_rate": 65, "blood_pressure_systolic": 110, "blood_pressure_diastolic": 70, "temperature": 36.8},
    {"heart_rate": 95, "blood_pressure_systolic": 150, "blood_pressure_diastolic": 95, "temperature": 37.5},
    {"heart_rate": 78, "blood_pressure_systolic": 130, "blood_pressure_diastolic": 85, "temperature": 37.1},
]

HISTORY_TEMPLATES = [
    "Patient reports gradual onset of symptoms over the past 2-3 days. No recent trauma or infection.",
    "Sudden onset symptoms this morning while at work. No previous similar episodes.",
    "Progressive worsening of symptoms over the past week. Interfering with daily activities.",
    "Intermittent symptoms for past month, worsening in frequency and severity.",
    "Acute onset symptoms following stressful event. No prior medical issues.",
]


def generate_diagnosis_payload() -> Dict[str, Any]:
    """
    Generate realistic diagnosis request payload

    Returns varied combinations to test different code paths
    and simulate real user behavior
    """
    # Select random but coherent data
    num_symptoms = random.randint(1, 4)
    selected_symptoms = random.sample(SYMPTOMS, num_symptoms)

    # Add duration (1-30 days)
    for symptom in selected_symptoms:
        symptom["duration_days"] = random.randint(1, 30)

    age = random.choice(AGES)
    gender = random.choice(GENDERS)
    medical_history = random.choice(MEDICAL_HISTORY)
    current_medications = random.choice(CURRENT_MEDICATIONS)

    payload = {
        "patient_info": {
            "age": age,
            "gender": gender,
            "weight": random.randint(50, 100),
            "height": random.randint(150, 190),
            "medical_history": medical_history,
            "current_medications": current_medications,
            "allergies": random.choice([[], ["penicillin"], ["sulfa drugs"]])
        },
        "symptoms": selected_symptoms,
        "vital_signs": random.choice(VITAL_SIGNS_TEMPLATES).copy(),
        "lab_results": {
            "glucose": random.randint(80, 140),
            "sodium": random.randint(135, 145),
            "potassium": random.randint(35, 50) / 10,
        },
        "imaging_studies": random.choice([
            [],
            ["brain_mri"],
            ["brain_ct"],
            ["brain_mri", "cervical_spine_xray"]
        ]),
        "chief_complaint": random.choice(CHIEF_COMPLAINTS),
        "history_present_illness": random.choice(HISTORY_TEMPLATES)
    }

    return payload


def generate_drug_interaction_payload() -> Dict[str, List[str]]:
    """
    Generate drug interaction check payload

    Tests various medication combinations including:
    - No interactions
    - Known severe interactions
    - Multiple medications
    """
    medication_sets = [
        ["warfarin", "aspirin"],  # Known SEVERE interaction
        ["sertraline", "sumatriptan"],  # Known SEVERE interaction
        ["levodopa", "phenelzine"],  # Known CONTRAINDICATED
        ["gabapentin", "pregabalin"],  # No interaction
        ["metformin", "lisinopril"],  # No interaction
        ["warfarin", "aspirin", "phenytoin"],  # Multiple interactions
        ["topiramate", "acetazolamide"],  # MODERATE interaction
        random.choice(CURRENT_MEDICATIONS),  # Random from realistic list
    ]

    medications = random.choice(medication_sets)

    return {"medications": medications}


def generate_image_file() -> BytesIO:
    """
    Generate fake image file for upload testing

    Creates minimal valid PNG file to test upload endpoint
    without actual image processing overhead
    """
    # Minimal 1x1 pixel PNG
    fake_image_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    return BytesIO(fake_image_data)


def generate_cache_warming_payloads(count: int = 20) -> List[Dict[str, Any]]:
    """
    Generate set of diagnosis payloads for cache warming

    Creates repeated payloads to pre-populate cache and test
    cache hit rate improvements

    Args:
        count: Number of unique payloads to generate

    Returns:
        List of diagnosis payloads
    """
    payloads = []

    # Generate base payloads
    for _ in range(count):
        payloads.append(generate_diagnosis_payload())

    # Duplicate each payload 2-5 times to simulate cache hits
    warmed_payloads = []
    for payload in payloads:
        duplicates = random.randint(2, 5)
        warmed_payloads.extend([payload] * duplicates)

    # Shuffle to mix original and duplicate requests
    random.shuffle(warmed_payloads)

    return warmed_payloads


# Test data validation
def validate_diagnosis_payload(payload: Dict[str, Any]) -> bool:
    """Validate generated payload matches API schema"""
    required_fields = [
        "patient_info",
        "symptoms",
        "vital_signs",
        "lab_results",
        "imaging_studies",
        "chief_complaint",
        "history_present_illness"
    ]

    return all(field in payload for field in required_fields)


if __name__ == "__main__":
    # Test data generation
    print("Testing NeuroAgent Load Test Data Generator\n")

    # Generate and validate diagnosis payload
    diagnosis = generate_diagnosis_payload()
    print("✓ Generated diagnosis payload")
    print(f"  Symptoms: {len(diagnosis['symptoms'])}")
    print(f"  Medications: {len(diagnosis['patient_info']['current_medications'])}")
    print(f"  Valid: {validate_diagnosis_payload(diagnosis)}")

    # Generate drug interaction payload
    drug_interaction = generate_drug_interaction_payload()
    print("\n✓ Generated drug interaction payload")
    print(f"  Medications: {drug_interaction['medications']}")

    # Generate image file
    image = generate_image_file()
    print("\n✓ Generated image file")
    print(f"  Size: {len(image.getvalue())} bytes")

    # Generate cache warming set
    cache_payloads = generate_cache_warming_payloads(10)
    print("\n✓ Generated cache warming payloads")
    print(f"  Total payloads: {len(cache_payloads)}")
    print(f"  Unique payloads: ~10 (with 2-5x duplicates)")

    print("\n✅ All test data generators working correctly")
