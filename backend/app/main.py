"""
TriageAI - FastAPI Application Entry Point
AI-Powered Emergency Room Smart Triage System
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import create_tables, engine
from app.routers import patients, triage, analytics


async def run_migrations():
    """Add any missing columns to existing tables (safe to run on every startup)."""
    async with engine.begin() as conn:
        db_url = str(engine.url)
        is_sqlite = "sqlite" in db_url

        if is_sqlite:
            result = await conn.execute(text("PRAGMA table_info(patients)"))
            existing = {row[1] for row in result.fetchall()}
            if "treatment_started_at" not in existing:
                await conn.execute(text("ALTER TABLE patients ADD COLUMN treatment_started_at VARCHAR(30)"))
                print("✅ Added treatment_started_at column")
            if "discharged_at" not in existing:
                await conn.execute(text("ALTER TABLE patients ADD COLUMN discharged_at VARCHAR(30)"))
                print("✅ Added discharged_at column")
            if "vitals_source" not in existing:
                await conn.execute(text("ALTER TABLE patients ADD COLUMN vitals_source TEXT DEFAULT '{}'"))
                print("✅ Added vitals_source column")
        else:
            await conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='patients' AND column_name='treatment_started_at'
                    ) THEN
                        ALTER TABLE patients ADD COLUMN treatment_started_at VARCHAR(30);
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='patients' AND column_name='discharged_at'
                    ) THEN
                        ALTER TABLE patients ADD COLUMN discharged_at VARCHAR(30);
                    END IF;

                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='patients' AND column_name='vitals_source'
                    ) THEN
                        ALTER TABLE patients ADD COLUMN vitals_source TEXT DEFAULT '{}';
                    END IF;
                END $$;
            """))
            print("✅ PostgreSQL migration check complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await create_tables()
    await run_migrations()
    print("✅ Database tables created/migrated")
    print("🏥 TriageAI Backend is ready!")
    yield
    print("👋 TriageAI Backend shutting down")


app = FastAPI(
    title="TriageAI API",
    description="AI-Powered Emergency Room Smart Triage System. Uses Google Gemini AI to provide intelligent, explainable triage assessments based on the ESI 5-level system.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)
app.include_router(triage.router)
app.include_router(analytics.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "service": "TriageAI API",
        "version": "1.0.0",
        "description": "AI-Powered Emergency Room Smart Triage System",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "ai_engine": "ready",
    }
