# TriageAI

### AI-assisted emergency triage with contactless vital signs, clinical reasoning, and real-time patient prioritization.

TriageAI is an emergency triage decision-support platform designed to help clinicians assess incoming patients, identify higher-risk cases, assign Emergency Severity Index (ESI) recommendations, and manage patient flow through a single interface.

Built for **VTHacks 14**.

**Sponsor Tracks:** Peraton and Impiricus

---

## Overview

Emergency departments can become overwhelmed quickly. Clinicians must evaluate patients with different symptoms, medical histories, vital signs, and levels of urgency while deciding who needs care first.

TriageAI helps organize that process.

The platform combines:

* AI-assisted ESI triage
* Contactless vital-sign collection
* Real-time patient prioritization
* Explainable clinical reasoning
* Clinician overrides
* Patient-flow analytics
* Cloud-hosted patient data

TriageAI is built as a **decision-support system**. It does not replace clinical judgment. The clinician always retains final authority over a patient's triage level.

---

## Inspiration

The idea for TriageAI came from watching *The Pitt*.

Throughout the show, the emergency department becomes increasingly crowded as more patients arrive. Triage nurses have to continuously determine which patients require immediate attention and which can safely wait.

That made us think about the difficulty of making those decisions at scale.

A patient who appears stable may still have signs of a serious condition, while another patient with more visible symptoms may be medically stable. During overcrowding, extreme weather, disasters, or mass-casualty events, making those decisions becomes even harder.

We wanted to build a system that could help clinicians organize patient information, recognize warning signs, and prioritize care without removing the human from the decision.

That became TriageAI.

---

## What TriageAI Does

### Patient Intake

Clinicians can record:

* Chief complaint
* Age and demographics
* Pain level
* Medical history
* Allergies
* Current medications
* Heart rate
* Blood pressure
* Temperature
* Respiratory rate
* Oxygen saturation
* Arrival method

---

### Contactless Vitals with Presage

TriageAI integrates Presage into the patient intake workflow.

The scanning interface can:

* Access the patient's camera
* Detect whether a patient is positioned in frame
* Monitor signal quality
* Perform an optical vital-sign scan
* Capture heart rate
* Capture respiratory rate
* Apply readings directly to the intake form

If the scan cannot produce a reliable measurement, the clinician can rescan or enter the vitals manually.

---

### Gemini-Powered Triage

Once a patient record is created, TriageAI sends the relevant information to the Google Gemini API.

Gemini analyzes the patient using the Emergency Severity Index framework and returns structured output containing:

* Recommended ESI level
* Confidence score
* Clinical reasoning
* Critical warning flags
* Recommended actions
* Estimated wait time
* Patient summary

Example response:

```json
{
  "esi_level": 2,
  "confidence": 0.94,
  "reasoning": [
    "Patient presents with high-risk symptoms",
    "Vital signs indicate possible deterioration"
  ],
  "recommended_actions": [
    "Immediate clinician evaluation",
    "Continuous vital-sign monitoring"
  ],
  "critical_flags": [
    "Abnormal respiratory status"
  ],
  "estimated_wait_minutes": 10,
  "brief_summary": "High-risk patient requiring rapid evaluation."
}
```

Using structured JSON instead of unrestricted text allows the AI output to directly drive the rest of the application.

---

## Emergency Severity Index

TriageAI uses the five-level Emergency Severity Index framework.

| ESI Level | Classification | Description                                   |
| --------- | -------------- | --------------------------------------------- |
| **1**     | Resuscitation  | Immediate life-saving intervention required   |
| **2**     | Emergent       | High-risk patient or severe distress          |
| **3**     | Urgent         | Stable but likely requires multiple resources |
| **4**     | Less Urgent    | Likely requires one resource                  |
| **5**     | Non-Urgent     | No major additional resources expected        |

---

## Real-Time Priority Queue

After triage, patients are added to a centralized queue.

The interface allows clinicians to:

* View patients by severity
* Identify higher-acuity patients quickly
* Monitor patient status
* Open complete patient records
* Review AI reasoning
* Update patient status
* Override AI-generated ESI levels

The goal is to turn a crowded waiting room into a clearer picture of who may need attention first.

---

## Human-in-the-Loop Design

TriageAI is intentionally designed so that AI does not make the final clinical decision.

The workflow is:

```text
Patient Intake
      |
      v
Vitals Collection
      |
      v
AI Assessment
      |
      v
ESI Recommendation
      |
      v
Clinician Review
      |
      +---- Accept Recommendation
      |
      +---- Override Recommendation
      |
      v
Priority Queue
```

Clinicians can review the AI recommendation and reasoning before deciding how the patient should be prioritized.

---

## Analytics

TriageAI includes an operational dashboard for monitoring the current state of the emergency department.

The dashboard can surface information such as:

* Number of active patients
* ESI distribution
* Patient statuses
* Average wait times
* Patient-flow trends
* Current ER activity

---

## Architecture

```text
                    TriageAI

               React + Vite Frontend
                      |
                      |
                   REST API
                      |
                      v
                FastAPI Backend
                 /     |      \
                /      |       \
               v       v        v
         Tiger Data  Gemini   Analytics
         PostgreSQL    API
               ^
               |
            Presage
       Contactless Vitals
```

### Deployment Architecture

```text
User
 |
 v
Vercel
React Frontend
 |
 v
FastAPI Backend
Vultr
 |
 +--------------------+
 |                    |
 v                    v
Tiger Data          Gemini API
PostgreSQL
```

---

## Tech Stack

| Category               | Technology              |
| ---------------------- | ----------------------- |
| Frontend               | React 18                |
| Build Tool             | Vite                    |
| Backend                | Python                  |
| API Framework          | FastAPI                 |
| AI                     | Google Gemini API       |
| Database               | Tiger Data / PostgreSQL |
| Contactless Vitals     | Presage                 |
| Backend Infrastructure | Vultr                   |
| Frontend Deployment    | Vercel                  |
| Domain Infrastructure  | GoDaddy                 |
| ORM                    | SQLAlchemy              |
| PostgreSQL Drivers     | asyncpg, psycopg2       |
| HTTP Client            | Axios                   |
| Charts                 | Recharts                |
| Animation              | Framer Motion           |
| Icons                  | Lucide React            |
| Version Control        | GitHub                  |

---

## Sponsor Technology Integrations

### Tiger Data

Tiger Data provides the PostgreSQL database layer for TriageAI.

The backend stores information including:

* Patient demographics
* Symptoms
* Vital signs
* ESI results
* AI confidence
* AI reasoning
* Recommended actions
* Critical flags
* Patient status
* Clinician overrides
* Timestamps

The application also supports SQLite as a fallback for local development.

---

### Presage

Presage adds a contactless sensing layer to the intake process.

Instead of requiring every vital sign to be entered manually, TriageAI can use a camera-based workflow to capture heart rate and respiratory rate.

Presage readings become part of the same patient record used by the triage engine.

---

### Google Gemini

Gemini provides the reasoning layer behind TriageAI.

The model receives structured patient information and produces structured triage recommendations that can be directly consumed by the backend and frontend.

We use Gemini for:

* ESI recommendations
* Clinical reasoning
* Critical-flag detection
* Recommended actions
* Patient summaries
* Estimated wait times

---

### Vultr

Vultr hosts the TriageAI backend infrastructure.

Our FastAPI service handles:

* Patient APIs
* Triage requests
* Analytics
* Database communication
* Status updates
* Clinician overrides

---

### Vercel

Vercel hosts the React frontend.

API requests from the frontend are routed to the deployed backend, allowing the client and server to remain independently deployable.

---

### GoDaddy

GoDaddy provides domain infrastructure for the deployed application.

---

## Sponsor Tracks

### Peraton

For the Peraton track, TriageAI focuses on rapid decision support in high-pressure and resource-constrained environments.

Potential applications include:

* Mass-casualty incidents
* Disaster response
* Field hospitals
* Temporary medical facilities
* Large-scale emergency events

The system is designed to organize incomplete patient information and help medical teams identify higher-priority cases quickly.

### Impiricus

For the Impiricus track, TriageAI focuses on improving the clinician workflow.

Instead of replacing healthcare professionals, TriageAI reduces repetitive cognitive work by organizing information, surfacing warning signs, and presenting explainable recommendations while keeping clinicians in control.

---

## Project Structure

```text
TriageAI/
|
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   |
│   │   ├── routers/
│   │   │   ├── patients.py
│   │   │   ├── triage.py
│   │   │   └── analytics.py
│   │   |
│   │   └── services/
│   │       └── ai_engine.py
│   │
│   ├── seed_data.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── PatientIntakeForm.jsx
│   │   │   ├── PresageScanModal.jsx
│   │   │   ├── TriageAssessment.jsx
│   │   │   ├── PriorityQueue.jsx
│   │   │   ├── AnalyticsPanel.jsx
│   │   │   ├── PatientDetail.jsx
│   │   │   ├── Header.jsx
│   │   │   └── Sidebar.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── utils/
│   │   │   └── constants.js
│   │   │
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── vercel.json
└── README.md
```

---

## Running Locally

### Requirements

Make sure you have:

* Python 3.10+
* Node.js 18+
* A Google Gemini API key
* A Tiger Data/PostgreSQL connection string if using the cloud database

---

### Clone the Repository

```bash
git clone https://github.com/gitsamridhm/TriageAI.git
cd TriageAI
```

---

### Backend

```bash
cd backend

python -m venv venv
```

macOS/Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Add:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_tiger_data_postgresql_connection_string
```

If `DATABASE_URL` is not provided, TriageAI falls back to SQLite for local development.

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

FastAPI documentation will be available at:

```text
http://localhost:8000/docs
```

---

### Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local Vite URL shown in the terminal.

---

## API Endpoints

| Method   | Endpoint                      | Description              |
| -------- | ----------------------------- | ------------------------ |
| `GET`    | `/api/patients`               | Retrieve patients        |
| `POST`   | `/api/patients`               | Create a patient         |
| `GET`    | `/api/patients/{id}`          | Retrieve patient details |
| `PATCH`  | `/api/patients/{id}/status`   | Update patient status    |
| `PATCH`  | `/api/patients/{id}/override` | Override triage result   |
| `DELETE` | `/api/patients/{id}`          | Delete patient           |
| `POST`   | `/api/triage/{id}`            | Run AI triage            |
| `GET`    | `/api/analytics`              | Retrieve analytics       |
| `GET`    | `/health`                     | Backend health check     |

---

## Challenges

One of the most difficult parts of building TriageAI was integrating Presage.

Working with a live camera required handling problems that do not exist with normal API integrations, including:

* Camera permissions
* Live video streams
* Patient positioning
* Signal quality
* Failed scans
* Asynchronous sensor data

We also had to connect multiple independently deployed systems.

A feature working locally did not guarantee that it would work when the frontend, backend, database, AI service, and sensing workflow were running on different infrastructure.

We worked through issues involving:

* CORS
* Environment variables
* PostgreSQL connections
* Async database drivers
* Vercel routing
* Vultr networking
* Camera permissions
* API communication

---

## What We Learned

TriageAI taught us that building an AI product requires much more than connecting an application to an LLM.

The complete system requires:

```text
Reliable Data
     +
Sensor Input
     +
AI Reasoning
     +
Persistent Storage
     +
Failure Handling
     +
Human Oversight
     +
Usable Interface
```

We also learned how different software becomes when it interacts with the physical world.

Working with Presage required us to account for camera permissions, positioning, timing, signal quality, and real-world failure conditions.

Most importantly, we learned that high-stakes AI should provide understandable information while preserving human control.

---

## What's Next

Future versions of TriageAI could include:

* Secure clinician authentication
* Role-based access control
* EHR integration
* FHIR support
* Deeper Presage integration
* Offline emergency-response mode
* Ambulance-to-hospital handoffs
* Bed and resource allocation
* Multi-hospital dashboards
* Detailed audit logging
* Patient deterioration monitoring
* Additional clinical validation

We are particularly interested in expanding TriageAI beyond traditional emergency departments into disaster response, field hospitals, and other environments where medical teams need to rapidly prioritize patients with limited resources.

---

## Medical Disclaimer

TriageAI is a hackathon prototype and is **not a certified medical device**.

It is intended to demonstrate AI-assisted emergency triage and clinical workflow technology. It should not be used as a substitute for professional medical judgment, validated clinical protocols, or approved medical equipment.

---

## Built For

**VTHacks 14**
September 18–20, 2026

### Sponsor Tracks

* Peraton
* Impiricus

### Integrated Technologies

* Tiger Data
* Presage
* Vultr
* Google Gemini API
* GoDaddy
* Vercel

---

## Repository

https://github.com/gitsamridhm/TriageAI

---

## Team

TriageAI was built by:

- Samridh Mankala
- Saumit Guduguntla
- Dhruv Patel
