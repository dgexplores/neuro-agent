from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class SeverityEnum(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

class PatientInfo(BaseModel):
    age: int = Field(..., ge=0, le=120)
    gender: GenderEnum
    weight: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    medical_history: List[str] = []
    current_medications: List[str] = []
    allergies: List[str] = []

class Symptom(BaseModel):
    name: str
    severity: SeverityEnum
    duration_days: int = Field(..., ge=0)
    description: Optional[str] = None

class DiagnosisRequest(BaseModel):
    patient_info: PatientInfo
    symptoms: List[Symptom]
    vital_signs: Dict[str, float] = {}
    lab_results: Dict[str, Any] = {}
    imaging_studies: List[str] = []
    chief_complaint: str
    history_present_illness: str

class DiagnosisResponse(BaseModel):
    case_id: str
    diagnosis: List[Dict[str, Any]]
    confidence: float = Field(..., ge=0.0, le=1.0)
    recommendations: List[str]
    risk_factors: List[str]
    next_steps: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)

class PatientCase(BaseModel):
    case_id: str
    patient_info: PatientInfo
    request: DiagnosisRequest
    response: Optional[DiagnosisResponse] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str = "pending"
