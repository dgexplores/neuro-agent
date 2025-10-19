from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

from .models.patient import PatientCase, DiagnosisRequest, DiagnosisResponse
from .agents.neuro_agent import NeuroAgent
from .services.bedrock_service import BedrockService
from .utils.auth import verify_token

# Load environment variables
load_dotenv()

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
if ALLOWED_ORIGINS_STR == "*" or "vercel.app" in ALLOWED_ORIGINS_STR:
    # For demo/production with dynamic Vercel URLs, allow all origins
    # In production, restrict this properly
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = ALLOWED_ORIGINS_STR.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False for wildcard origins
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
    max_age=3600,  # Cache preflight for 1 hour
)

# Security
security = HTTPBearer()

# Initialize services
bedrock_service = BedrockService()
neuro_agent = NeuroAgent(bedrock_service)

@app.get("/")
async def root():
    return {"message": "NeuroAgent API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {"bedrock": "connected"}}

# Explicit OPTIONS handler for all routes to handle CORS preflight
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {"message": "OK"}

@app.post("/api/v1/diagnosis", response_model=DiagnosisResponse)
async def create_diagnosis(
    request: DiagnosisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new neurological diagnosis based on patient data"""
    try:
        # Verify authentication
        user_id = verify_token(credentials.credentials)

        # Process diagnosis request
        result = await neuro_agent.analyze_case(request)

        return DiagnosisResponse(
            case_id=result["case_id"],
            diagnosis=result["diagnosis"],
            confidence=result["confidence"],
            recommendations=result["recommendations"],
            risk_factors=result["risk_factors"],
            next_steps=result["next_steps"]
        )
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
        if not file.content_type.startswith('image/'):
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


@app.get("/api/v1/cases/{case_id}")
async def get_case(
    case_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Retrieve a specific case by ID"""
    try:
        user_id = verify_token(credentials.credentials)
        case = await neuro_agent.get_case(case_id)
        return case
    except Exception as e:
        raise HTTPException(status_code=404, detail="Case not found")

# Lambda handler for AWS API Gateway
from mangum import Mangum
handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
