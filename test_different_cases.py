#!/usr/bin/env python3
"""
Test script to verify different diagnosis cases return different results
"""

import asyncio
import json
from backend.agents.neuro_agent import NeuroAgent
from backend.services.bedrock_service import BedrockService
from backend.models.patient import DiagnosisRequest, PatientInfo, Symptom, GenderEnum, SeverityEnum

async def test_case(case_name: str, age: int, gender: str, symptoms: list, medical_history: list):
    """Test a single case"""
    print(f"\n{'='*60}")
    print(f"Testing case: {case_name}")
    print(f"{'='*60}")

    # Create bedrock service and agent
    bedrock_service = BedrockService()
    agent = NeuroAgent(bedrock_service)

    # Create patient info
    patient_info = PatientInfo(
        age=age,
        gender=gender,
        medical_history=medical_history,
        current_medications=[],
        allergies=[]
    )

    # Create symptoms
    symptom_objects = [
        Symptom(
            name=symptom,
            severity=SeverityEnum.MODERATE,
            duration_days=7,
            description=""
        )
        for symptom in symptoms
    ]

    # Create diagnosis request
    request = DiagnosisRequest(
        patient_info=patient_info,
        symptoms=symptom_objects,
        vital_signs={},
        lab_results={},
        imaging_studies=[],
        chief_complaint=symptoms[0] if symptoms else "General assessment",
        history_present_illness=", ".join(symptoms) if symptoms else "No specific history"
    )

    # Analyze case
    try:
        result = await agent.analyze_case(request)

        print(f"\n[OK] Case ID: {result['case_id']}")
        print(f"[OK] Overall Confidence: {result['confidence']:.2%}")
        print(f"\nDiagnoses:")
        for i, diagnosis in enumerate(result['diagnosis'], 1):
            print(f"  {i}. {diagnosis.get('condition', 'Unknown')} - {diagnosis.get('confidence', 0):.0%} confidence")
            if 'reasoning' in diagnosis:
                print(f"     Reasoning: {diagnosis['reasoning'][:100]}...")

        print(f"\nRecommendations:")
        for rec in result['recommendations'][:3]:
            print(f"  - {rec}")

        print(f"\nRisk Factors:")
        for risk in result['risk_factors'][:3]:
            print(f"  - {risk}")

        return result

    except Exception as e:
        print(f"[ERROR] Error processing case: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run test cases"""
    print("\n" + "="*60)
    print("NEUROAGENT DIAGNOSIS TEST SUITE")
    print("Testing if different cases produce different diagnoses")
    print("="*60)

    # Test Case 1: Migraine symptoms
    case1 = await test_case(
        case_name="Case 1: Migraine",
        age=35,
        gender=GenderEnum.FEMALE,
        symptoms=["headache", "photophobia", "nausea"],
        medical_history=["no significant history"]
    )

    # Test Case 2: Stroke symptoms
    case2 = await test_case(
        case_name="Case 2: Acute Stroke",
        age=65,
        gender=GenderEnum.MALE,
        symptoms=["acute onset weakness", "facial drooping", "speech difficulty"],
        medical_history=["hypertension", "diabetes"]
    )

    # Test Case 3: Seizure symptoms
    case3 = await test_case(
        case_name="Case 3: Seizure",
        age=25,
        gender=GenderEnum.MALE,
        symptoms=["loss of consciousness", "muscle convulsions", "tongue biting"],
        medical_history=["no significant history"]
    )

    # Test Case 4: Parkinson's symptoms
    case4 = await test_case(
        case_name="Case 4: Parkinson's Disease",
        age=70,
        gender=GenderEnum.MALE,
        symptoms=["resting tremor", "bradykinesia", "rigidity"],
        medical_history=["hypertension", "hyperlipidemia"]
    )

    # Compare results
    print(f"\n\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")

    cases = [
        ("Case 1 (Migraine)", case1),
        ("Case 2 (Stroke)", case2),
        ("Case 3 (Seizure)", case3),
        ("Case 4 (Parkinson's)", case4)
    ]

    for case_name, result in cases:
        if result:
            top_diagnosis = result['diagnosis'][0].get('condition', 'Unknown') if result['diagnosis'] else 'None'
            print(f"✓ {case_name}: {top_diagnosis}")
        else:
            print(f"✗ {case_name}: FAILED")

    # Check if results are different
    diagnoses = [
        (result['diagnosis'][0].get('condition', 'Unknown') if result and result['diagnosis'] else 'None')
        for _, result in cases
    ]

    unique_diagnoses = set(diagnoses)

    if len(unique_diagnoses) == len(diagnoses):
        print(f"\n✅ SUCCESS: All {len(diagnoses)} cases returned DIFFERENT diagnoses!")
    else:
        print(f"\n⚠️  WARNING: Only {len(unique_diagnoses)} unique diagnoses for {len(diagnoses)} different cases")
        print(f"   This may indicate the system is not processing inputs correctly.")

if __name__ == "__main__":
    asyncio.run(main())
