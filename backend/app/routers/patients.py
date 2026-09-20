"""
TriageAI - Patient CRUD Routes
Handles patient creation, listing, status updates, and nurse overrides.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime, timezone

from app.database import get_db, Patient
from app.models import PatientCreate, PatientResponse, PatientStatusUpdate, NurseOverride

router = APIRouter(prefix="/api/patients", tags=["Patients"])


def patient_to_response(patient: Patient) -> PatientResponse:
    """Convert a database Patient to a PatientResponse."""
    return PatientResponse(
        id=patient.id,
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        chief_complaint=patient.chief_complaint,
        pain_level=patient.pain_level,
        heart_rate=patient.heart_rate,
        blood_pressure_systolic=patient.blood_pressure_systolic,
        blood_pressure_diastolic=patient.blood_pressure_diastolic,
        temperature=patient.temperature,
        respiratory_rate=patient.respiratory_rate,
        spo2=patient.spo2,
        arrival_mode=patient.arrival_mode,
        allergies=patient.allergies,
        medical_history=patient.medical_history,
        current_medications=patient.current_medications,
        esi_level=patient.esi_level,
        triage_status=patient.triage_status,
        ai_confidence=patient.ai_confidence,
        ai_reasoning=patient.ai_reasoning,
        recommended_actions=patient.recommended_actions,
        critical_flags=patient.critical_flags,
        estimated_wait_minutes=patient.estimated_wait_minutes,
        brief_summary=patient.brief_summary,
        nurse_override_level=patient.nurse_override_level,
        nurse_override_reason=patient.nurse_override_reason,
        status=patient.status,
        created_at=patient.created_at,
        triage_completed_at=patient.triage_completed_at,
        treatment_started_at=patient.treatment_started_at,
        discharged_at=patient.discharged_at,
    )


@router.post("", response_model=PatientResponse)
async def create_patient(patient_data: PatientCreate, db: AsyncSession = Depends(get_db)):
    """Create a new patient record in the system."""
    new_patient = Patient(
        name=patient_data.name,
        age=patient_data.age,
        gender=patient_data.gender.value,
        chief_complaint=patient_data.chief_complaint,
        pain_level=patient_data.pain_level,
        heart_rate=patient_data.heart_rate,
        blood_pressure_systolic=patient_data.blood_pressure_systolic,
        blood_pressure_diastolic=patient_data.blood_pressure_diastolic,
        temperature=patient_data.temperature,
        respiratory_rate=patient_data.respiratory_rate,
        spo2=patient_data.spo2,
        arrival_mode=patient_data.arrival_mode.value,
        allergies=patient_data.allergies or "",
        medical_history=patient_data.medical_history or "",
        current_medications=patient_data.current_medications or "",
    )

    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)

    return patient_to_response(new_patient)


@router.get("", response_model=List[PatientResponse])
async def list_patients(
    status: str = None,
    esi_level: int = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all patients, sorted by ESI level (most critical first),
    then by arrival time (earliest first).
    """
    query = select(Patient)

    if status:
        query = query.where(Patient.status == status)
    if esi_level:
        query = query.where(Patient.esi_level == esi_level)

    # Sort: ESI level ascending (1=most critical first), nulls last, then by created_at
    query = query.order_by(
        Patient.esi_level.asc().nullslast(),
        Patient.created_at.asc(),
    )

    result = await db.execute(query)
    patients = result.scalars().all()

    return [patient_to_response(p) for p in patients]


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single patient by ID."""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient_to_response(patient)


@router.patch("/{patient_id}/status", response_model=PatientResponse)
async def update_patient_status(
    patient_id: int,
    status_update: PatientStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a patient's status and record timestamps for treatment start and discharge."""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    now = datetime.now(timezone.utc).isoformat()
    patient.status = status_update.status.value

    if status_update.status.value == "In Treatment":
        patient.treatment_started_at = now
    elif status_update.status.value in ("Discharged", "Admitted"):
        patient.discharged_at = now

    await db.commit()
    await db.refresh(patient)

    return patient_to_response(patient)


@router.patch("/{patient_id}/override", response_model=PatientResponse)
async def nurse_override(
    patient_id: int,
    override: NurseOverride,
    db: AsyncSession = Depends(get_db),
):
    """Allow a nurse to override the AI triage recommendation."""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient.nurse_override_level = override.esi_level
    patient.nurse_override_reason = override.reason
    patient.esi_level = override.esi_level
    patient.triage_status = "Overridden"

    await db.commit()
    await db.refresh(patient)

    return patient_to_response(patient)


@router.delete("/{patient_id}")
async def delete_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a patient record (for demo/testing purposes)."""
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    await db.delete(patient)
    await db.commit()

    return {"message": f"Patient {patient_id} deleted"}
