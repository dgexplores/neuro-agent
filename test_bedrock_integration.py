#!/usr/bin/env python3
"""
Test real AWS Bedrock integration with different diagnosis cases
"""

import asyncio
import os
from dotenv import load_dotenv
from backend.agents.neuro_agent import NeuroAgent
from backend.services.bedrock_service import BedrockService
from backend.models.patient import DiagnosisRequest, PatientInfo, Symptom, GenderEnum, SeverityEnum

# Load environment variables
load_dotenv()

async def test_bedrock_connection():
    """Test connection to AWS Bedrock and get real diagnosis"""

    print("\n" + "="*70)
    print("TESTING REAL AWS BEDROCK CONNECTION")
    print("="*70)

    # Verify AWS credentials are loaded
    print("\n[Step 1] Verifying AWS credentials...")
    region = os.getenv("AWS_REGION")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not all([region, access_key, secret_key]):
        print("[ERROR] AWS credentials not found in .env")
        print(f"  AWS_REGION: {region}")
        print(f"  AWS_ACCESS_KEY_ID: {access_key is not None}")
        print(f"  AWS_SECRET_ACCESS_KEY: {secret_key is not None}")
        return False

    print(f"[OK] AWS credentials loaded:")
    print(f"  Region: {region}")
    print(f"  Access Key: {access_key[:15]}...")

    # Initialize services
    print("\n[Step 2] Initializing Bedrock service...")
    try:
        bedrock_service = BedrockService()
        agent = NeuroAgent(bedrock_service)
        print("[OK] Services initialized successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize services: {e}")
        return False

    # Test Case: Real migraine diagnosis
    print("\n[Step 3] Testing real diagnosis with Bedrock...")
    print("  Case: 35-year-old female with migraine symptoms")

    patient_info = PatientInfo(
        age=35,
        gender=GenderEnum.FEMALE,
        medical_history=["no significant history"],
        current_medications=[],
        allergies=[]
    )

    symptoms = [
        Symptom(name="headache", severity=SeverityEnum.SEVERE, duration_days=2),
        Symptom(name="photophobia", severity=SeverityEnum.MODERATE, duration_days=2),
        Symptom(name="nausea", severity=SeverityEnum.MODERATE, duration_days=2),
    ]

    request = DiagnosisRequest(
        patient_info=patient_info,
        symptoms=symptoms,
        vital_signs={"bp_systolic": 120.0, "bp_diastolic": 80.0, "heart_rate": 78.0, "temperature": 37.2},
        lab_results={},
        imaging_studies=[],
        chief_complaint="Severe headache with sensitivity to light",
        history_present_illness="Acute onset headache 2 hours ago, associated with photophobia and nausea"
    )

    try:
        print("  Invoking Bedrock model...")
        result = await agent.analyze_case(request)

        print("\n[OK] Diagnosis completed successfully!")
        print(f"\n  Case ID: {result['case_id']}")
        print(f"  Overall Confidence: {result['confidence']:.0%}")

        print(f"\n  Top Diagnoses:")
        for i, diagnosis in enumerate(result['diagnosis'][:3], 1):
            print(f"    {i}. {diagnosis.get('condition', 'Unknown')} - {diagnosis.get('confidence', 0):.0%}")

        print(f"\n  Recommendations:")
        for rec in result['recommendations'][:3]:
            print(f"    - {rec}")

        return True

    except Exception as e:
        print(f"\n[ERROR] Bedrock invocation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_bedrock_connection()

    print("\n" + "="*70)
    if success:
        print("[SUCCESS] AWS Bedrock integration is working!")
        print("Your NeuroAgent system is now properly configured and connected")
    else:
        print("[INFO] Note: If Bedrock test failed, the fallback diagnosis system will still work")
        print("Check that your AWS credentials are valid and have Bedrock access")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
