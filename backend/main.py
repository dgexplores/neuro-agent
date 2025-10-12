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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

        return {"image_id": result["image_id"], "analysis": result["analysis"]}
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
