from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import asyncio
import sqlite3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

# Load configuration before importing modules that read JWT and provider settings.
load_dotenv()

from .models.patient import PatientCase, DiagnosisRequest, DiagnosisResponse
from .agents.neuro_agent import NeuroAgent
from .services.model_service import create_model_service
from .utils.auth import verify_token, create_public_demo_token
from .services.case_store import SQLiteCaseStore, get_case_store
from .services.demo_access import (
    SAMPLES, DEMO_TTL_SECONDS, demo_config, require_demo_enabled, get_demo_budget,
)

app = FastAPI(
    title="NeuroAgent API",
    description="AI-Driven Neurological Diagnosis Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - SECURITY HARDENED (Phase 8-2)
# Use environment-based origin configuration
ALLOWED_ORIGINS_STR = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"  # Default for development
)

# Parse ALLOWED_ORIGINS - support both comma-separated and special patterns
if ALLOWED_ORIGINS_STR == "*":
    # For demo/production with dynamic Vercel URLs, allow all origins
    # In production, restrict this properly
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = ALLOWED_ORIGINS_STR.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,  # Must be False for wildcard origins
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
    max_age=3600,  # Cache preflight for 1 hour
)

# Security
security = HTTPBearer()

# Initialize services
bedrock_service = create_model_service()
neuro_agent = NeuroAgent(bedrock_service)

@app.get("/")
async def root():
    return {"message": "NeuroAgent API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {os.getenv("MODEL_PROVIDER", "bedrock").lower(): "not_checked"}}


@app.get("/api/v1/demo/config")
async def get_demo_config():
    """Advertise only public demo capabilities and fictional inputs."""
    return demo_config()


@app.post("/api/v1/demo/session")
async def start_demo_session():
    require_demo_enabled()
    return {"access_token": create_public_demo_token(), "token_type": "bearer",
            "expires_in": DEMO_TTL_SECONDS, "scope": "demo"}


class DemoAssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sample_id: str = Field(min_length=1, max_length=80)


@app.post("/api/v1/demo/diagnosis", response_model=DiagnosisResponse)
async def create_demo_diagnosis(
    request: DemoAssessmentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    case_store=Depends(get_case_store),
    budget=Depends(get_demo_budget),
):
    """Reserve one bounded real inference for a server-owned fictional input."""
    require_demo_enabled()
    user_id = verify_token(credentials.credentials, allow_demo=True, require_demo=True)
    sample = SAMPLES.get(request.sample_id)
    if sample is None:
        raise HTTPException(status_code=404, detail="Synthetic example not found")
    try:
        # Failed model calls also consume the reservation: retries may incur cost.
        await asyncio.to_thread(budget.reserve, user_id)
        result = await neuro_agent.analyze_case(DiagnosisRequest(**sample["request"]))
        response = DiagnosisResponse(**result)
        await asyncio.to_thread(case_store.save, user_id, response.model_dump(mode="json"))
        return response
    except HTTPException:
        raise
    except (sqlite3.Error, BotoCoreError, ClientError, OSError):
        raise HTTPException(status_code=503, detail="Demo storage unavailable")
    except Exception:
        raise HTTPException(status_code=503, detail="Assessment service unavailable")

@app.post("/api/v1/diagnosis", response_model=DiagnosisResponse)
async def create_diagnosis(
    request: DiagnosisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    case_store: SQLiteCaseStore = Depends(get_case_store),
):
    """Create a new neurological diagnosis based on patient data"""
    try:
        # Verify authentication
        user_id = verify_token(credentials.credentials)

        # Process diagnosis request
        result = await neuro_agent.analyze_case(request)

        response = DiagnosisResponse(
            case_id=result["case_id"],
            diagnosis=result["diagnosis"],
            confidence=result["confidence"],
            recommendations=result["recommendations"],
            risk_factors=result["risk_factors"],
            next_steps=result["next_steps"]
        )
        await asyncio.to_thread(case_store.save, user_id, response.model_dump(mode="json"))
        return response
    except (sqlite3.Error, BotoCoreError, ClientError):
        raise HTTPException(status_code=503, detail="Case storage unavailable")
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 for validation errors)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/upload-image")
async def upload_medical_image(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload and analyze medical images (MRI, CT scans)"""
    try:
        user_id = verify_token(credentials.credentials)

        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Process image
        result = await neuro_agent.analyze_image(file)

        # Return complete analysis result (Phase 7-2)
        return result
    except HTTPException:
        # Re-raise HTTP exceptions (like 400 for invalid file type)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/drug-interactions")
async def check_drug_interactions(
    medications: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Check for drug interactions among a list of medications

    Phase 8: Dedicated Drug Interaction Endpoint

    Request body:
    {
        "medications": ["drug1", "drug2", "drug3"]
    }

    Returns list of interactions sorted by severity (contraindicated > severe > moderate > minor)
    """
    try:
        user_id = verify_token(credentials.credentials)

        # Validate input
        if "medications" not in medications:
            raise HTTPException(
                status_code=400,
                detail="Request must include 'medications' field with list of medication names"
            )

        meds_list = medications["medications"]

        if not isinstance(meds_list, list):
            raise HTTPException(
                status_code=400,
                detail="'medications' must be a list of strings"
            )

        if len(meds_list) < 2:
            return {
                "medication_count": len(meds_list),
                "interactions_found": 0,
                "interactions": [],
                "message": "At least 2 medications required for interaction checking"
            }

        # Check for interactions using knowledge base
        interactions = neuro_agent.knowledge_base.check_drug_interactions(meds_list)

        return {
            "medication_count": len(meds_list),
            "medications_checked": meds_list,
            "interactions_found": len(interactions),
            "interactions": interactions,
            "severity_summary": {
                "contraindicated": len([i for i in interactions if i["severity"] == "contraindicated"]),
                "severe": len([i for i in interactions if i["severity"] == "severe"]),
                "moderate": len([i for i in interactions if i["severity"] == "moderate"]),
                "minor": len([i for i in interactions if i["severity"] == "minor"])
            }
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/cases/{case_id}", response_model=DiagnosisResponse)
async def get_case(
    case_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    case_store: SQLiteCaseStore = Depends(get_case_store),
):
    """Retrieve a stored response belonging to the authenticated user."""
    user_id = verify_token(credentials.credentials, allow_demo=True)
    try:
        case = await asyncio.to_thread(case_store.get, user_id, case_id)
    except (sqlite3.Error, BotoCoreError, ClientError):
        raise HTTPException(status_code=503, detail="Case storage unavailable")
    if case is None:
        # Use the same response for unknown IDs and cases owned by other users.
        raise HTTPException(status_code=404, detail="Case not found")
    return case

# Lambda handler for AWS API Gateway
from mangum import Mangum
handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
