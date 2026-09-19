"""
TriageAI - AI Triage Engine
Integrates with Google Gemini API to provide intelligent triage assessments.
"""

import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.models import TriageResult

load_dotenv(override=True)

def get_api_key():
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

api_key = get_api_key()
if api_key:
    genai.configure(api_key=api_key)


TRIAGE_SYSTEM_PROMPT = """You are an expert Emergency Room triage nurse with 20 years of experience.
You use the Emergency Severity Index (ESI) 5-level triage system used in hospitals across the United States.

ESI Levels:
- ESI 1 (Resuscitation): Immediate life-threatening condition requiring aggressive interventions. Examples: cardiac arrest, severe respiratory distress, unresponsive patient, active hemorrhage with hemodynamic instability.
- ESI 2 (Emergent): High risk of deterioration, severe pain/distress, or confusion/lethargy. Examples: chest pain with cardiac risk factors, stroke symptoms (FAST criteria), severe allergic reaction, suicidal ideation with plan, high-mechanism trauma.
- ESI 3 (Urgent): Stable but likely needs multiple resources (labs, imaging, IV meds, specialist consult). Examples: abdominal pain needing labs + CT, moderate asthma exacerbation, complex lacerations, high fever with comorbidities.
- ESI 4 (Less Urgent): Needs one resource (simple X-ray, basic lab, simple procedure). Examples: simple laceration needing sutures, possible UTI needing urinalysis, ankle injury needing X-ray, earache needing exam only.
- ESI 5 (Non-Urgent): No resources needed beyond exam and possibly a prescription. Examples: prescription refill, minor cold symptoms, small abrasion, insect bite without allergic reaction.

CRITICAL VALUE THRESHOLDS (flag these):
- Heart Rate: <50 or >130 bpm
- Blood Pressure Systolic: <90 or >180 mmHg
- Blood Pressure Diastolic: >120 mmHg
- Temperature: <95°F or >104°F
- Respiratory Rate: <10 or >30 breaths/min
- SpO2: <92%
- Pain Level: 10/10 with acute onset

NORMAL RANGES (for reference):
- Heart Rate: 60-100 bpm
- Blood Pressure: 90-120/60-80 mmHg
- Temperature: 97.8-99.1°F
- Respiratory Rate: 12-20 breaths/min
- SpO2: 95-100%
"""


def build_patient_prompt(patient_data: dict) -> str:
    """Build the patient-specific prompt for triage assessment."""
    return f"""Analyze the following patient presenting to the Emergency Room and provide your triage assessment.

PATIENT DATA:
- Name: {patient_data.get('name', 'Unknown')}
- Age: {patient_data.get('age', 'Unknown')} years old
- Gender: {patient_data.get('gender', 'Unknown')}
- Chief Complaint: {patient_data.get('chief_complaint', 'Not specified')}
- Pain Level: {patient_data.get('pain_level', 0)}/10
- Vital Signs:
  - Heart Rate: {patient_data.get('heart_rate', 'N/A')} bpm
  - Blood Pressure: {patient_data.get('blood_pressure_systolic', 'N/A')}/{patient_data.get('blood_pressure_diastolic', 'N/A')} mmHg
  - Temperature: {patient_data.get('temperature', 'N/A')}°F
  - Respiratory Rate: {patient_data.get('respiratory_rate', 'N/A')} breaths/min
  - SpO2: {patient_data.get('spo2', 'N/A')}%
- Arrival Mode: {patient_data.get('arrival_mode', 'Walk-in')}
- Allergies: {patient_data.get('allergies', 'None reported')}
- Medical History: {patient_data.get('medical_history', 'None reported')}
- Current Medications: {patient_data.get('current_medications', 'None reported')}

Provide your assessment as a JSON object with EXACTLY this structure:
{{
  "esi_level": <integer 1-5>,
  "confidence": <float 0.0-1.0>,
  "reasoning": ["<specific clinical reasoning point 1>", "<point 2>", "<point 3>", "<point 4>"],
  "recommended_actions": ["<immediate action 1>", "<action 2>", "<action 3>"],
  "critical_flags": ["<critical value or concern, or empty list if none>"],
  "estimated_wait_minutes": <integer>,
  "brief_summary": "<one sentence clinical summary>"
}}

IMPORTANT:
- Provide at least 3-4 reasoning points referencing specific vital signs and clinical indicators
- Be specific about WHY each vital sign is concerning or reassuring
- Reference the patient's age, medical history, and medications in your reasoning
- estimated_wait_minutes should align with ESI level (ESI1=0, ESI2=10, ESI3=30, ESI4=60, ESI5=120)
- Respond with ONLY the JSON object, no additional text"""


async def assess_patient(patient_data: dict) -> TriageResult:
    """
    Use Gemini AI to assess a patient and return a triage recommendation.
    
    Args:
        patient_data: Dictionary containing patient information
        
    Returns:
        TriageResult with ESI level, reasoning, and recommendations
    """
    try:
        load_dotenv(override=True)
        current_key = get_api_key()
        if current_key:
            genai.configure(api_key=current_key)

        # Try models in order of availability for free tier keys
        models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-latest"]
        response = None
        last_exception = None

        prompt = build_patient_prompt(patient_data)

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=TRIAGE_SYSTEM_PROMPT,
                    generation_config=genai.GenerationConfig(
                        temperature=0.3,
                        response_mime_type="application/json",
                    )
                )
                response = model.generate_content(prompt)
                if response and response.text:
                    break
            except Exception as ex:
                last_exception = ex
                print(f"Model {model_name} failed: {ex}. Trying fallback...")
                continue

        if not response:
            raise last_exception or Exception("All Gemini models failed")

        # Parse the JSON response
        result_json = json.loads(response.text)

        return TriageResult(
            esi_level=result_json.get("esi_level", 3),
            confidence=result_json.get("confidence", 0.5),
            reasoning=result_json.get("reasoning", ["Assessment completed"]),
            recommended_actions=result_json.get("recommended_actions", ["Standard evaluation"]),
            critical_flags=result_json.get("critical_flags", []),
            estimated_wait_minutes=result_json.get("estimated_wait_minutes", 30),
            brief_summary=result_json.get("brief_summary", "Assessment complete"),
        )

    except json.JSONDecodeError as e:
        # If JSON parsing fails, return a safe default
        print(f"JSON Parse Error: {e}")
        print(f"Raw response: {response.text}")
        return TriageResult(
            esi_level=3,
            confidence=0.3,
            reasoning=["AI assessment encountered a parsing error", "Manual assessment recommended", "Patient data was submitted successfully"],
            recommended_actions=["Perform manual triage assessment", "Monitor vital signs"],
            critical_flags=["AI_PARSE_ERROR"],
            estimated_wait_minutes=30,
            brief_summary="AI assessment requires manual review due to parsing error",
        )

    except Exception as e:
        print(f"AI Engine Error: {e}")
        return TriageResult(
            esi_level=3,
            confidence=0.0,
            reasoning=[f"AI service temporarily unavailable: {str(e)}", "Manual triage assessment required"],
            recommended_actions=["Perform manual triage assessment", "Check AI service status"],
            critical_flags=["AI_SERVICE_ERROR"],
            estimated_wait_minutes=30,
            brief_summary="AI service error - manual assessment required",
        )
