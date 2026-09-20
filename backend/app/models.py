"""
TriageAI - Pydantic Models
Defines all request/response schemas for the API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class ArrivalMode(str, Enum):
    WALK_IN = "Walk-in"
    AMBULANCE = "Ambulance"
    HELICOPTER = "Helicopter"
    POLICE = "Police"
    TRANSFER = "Transfer"


class PatientStatus(str, Enum):
    WAITING = "Waiting"
    IN_TREATMENT = "In Treatment"
    DISCHARGED = "Discharged"
    ADMITTED = "Admitted"


class TriageStatus(str, Enum):
    PENDING = "Pending"
    ASSESSED = "Assessed"
    OVERRIDDEN = "Overridden"


# ─── Request Models ────────────────────────────────────────

class PatientCreate(BaseModel):
    """Schema for creating a new patient record."""
    name: str = Field(..., min_length=1, max_length=100, description="Patient full name")
    age: int = Field(..., ge=0, le=150, description="Patient age in years")
    gender: Gender
    chief_complaint: str = Field(..., min_length=1, description="Primary reason for ER visit")
    pain_level: int = Field(..., ge=0, le=10, description="Pain scale 0-10")

    # Vital Signs — all Optional for degraded-comms / mass-casualty scenarios
    heart_rate: Optional[int] = Field(None, ge=0, le=300, description="Heart rate in bpm")
    blood_pressure_systolic: Optional[int] = Field(None, ge=0, le=300, description="Systolic BP in mmHg")
    blood_pressure_diastolic: Optional[int] = Field(None, ge=0, le=200, description="Diastolic BP in mmHg")
    temperature: Optional[float] = Field(None, ge=85.0, le=115.0, description="Temperature in °F")
    respiratory_rate: Optional[int] = Field(None, ge=0, le=80, description="Breaths per minute")
    spo2: Optional[float] = Field(None, ge=0, le=100, description="Oxygen saturation %")

    # Additional Info
    arrival_mode: ArrivalMode = ArrivalMode.WALK_IN
    allergies: Optional[str] = ""
    medical_history: Optional[str] = ""
    current_medications: Optional[str] = ""


class PatientStatusUpdate(BaseModel):
    """Schema for updating patient status."""
    status: PatientStatus


class NurseOverride(BaseModel):
    """Schema for nurse overriding the AI triage recommendation."""
    esi_level: int = Field(..., ge=1, le=5, description="Nurse-assigned ESI level")
    reason: str = Field(..., min_length=1, description="Reason for override")


# ─── Response Models ───────────────────────────────────────

class TriageResult(BaseModel):
    """AI triage assessment result."""
    esi_level: int = Field(..., ge=1, le=5)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: List[str] = []
    recommended_actions: List[str] = []
    critical_flags: List[str] = []
    estimated_wait_minutes: int = 0
    brief_summary: str = ""


class PatientResponse(BaseModel):
    """Full patient response with triage data."""
    id: int
    name: str
    age: int
    gender: str
    chief_complaint: str
    pain_level: int

    # Vitals
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    temperature: Optional[float] = None
    respiratory_rate: Optional[int] = None
    spo2: Optional[float] = None

    # Additional
    arrival_mode: str
    allergies: Optional[str] = ""
    medical_history: Optional[str] = ""
    current_medications: Optional[str] = ""

    # Triage Results
    esi_level: Optional[int] = None
    triage_status: str = "Pending"
    ai_confidence: Optional[float] = None
    ai_reasoning: Optional[str] = None
    recommended_actions: Optional[str] = None
    critical_flags: Optional[str] = None
    estimated_wait_minutes: Optional[int] = None
    brief_summary: Optional[str] = None

    # Nurse Override
    nurse_override_level: Optional[int] = None
    nurse_override_reason: Optional[str] = None

    # Status
    status: str = "Waiting"
    created_at: str
    triage_completed_at: Optional[str] = None

    treatment_started_at: Optional[str] = None
    discharged_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    """Dashboard analytics data."""
    total_patients: int = 0
    patients_by_esi: Dict[str, int] = {}
    patients_by_status: Dict[str, int] = {}
    ai_acceptance_rate: float = 0.0
    avg_triage_time_seconds: Optional[float] = None
    current_wait_times: Dict[str, int] = {}
    recent_patients: List[PatientResponse] = []
