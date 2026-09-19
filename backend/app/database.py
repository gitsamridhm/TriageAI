"""
TriageAI - Database Setup
SQLAlchemy async setup — reads DATABASE_URL from environment (Tiger Data / PostgreSQL)
with SQLite fallback for local development.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, Text, DateTime
from datetime import datetime, timezone
from typing import Optional


_raw_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./triageai.db")

# Convert plain postgres:// / postgresql:// URLs to async driver format
if _raw_url.startswith("postgres://"):
    DATABASE_URL = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgresql://"):
    DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = _raw_url

# PostgreSQL needs different connect_args than SQLite
if DATABASE_URL.startswith("postgresql"):
    engine = create_async_engine(DATABASE_URL, echo=False)
else:
    engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Patient(Base):
    """Patient database model with triage information."""
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Demographics
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    chief_complaint: Mapped[str] = mapped_column(Text, nullable=False)
    pain_level: Mapped[int] = mapped_column(Integer, nullable=False)

    # Vital Signs — all Optional for degraded-comms / mass-casualty scenarios
    heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    blood_pressure_systolic: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    blood_pressure_diastolic: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    respiratory_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    spo2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Additional Info
    arrival_mode: Mapped[str] = mapped_column(String(20), default="Walk-in")
    allergies: Mapped[Optional[str]] = mapped_column(Text, default="")
    medical_history: Mapped[Optional[str]] = mapped_column(Text, default="")
    current_medications: Mapped[Optional[str]] = mapped_column(Text, default="")

    # Triage Results
    esi_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    triage_status: Mapped[str] = mapped_column(String(20), default="Pending")
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    critical_flags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_wait_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    brief_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Nurse Override
    nurse_override_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    nurse_override_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status & Timestamps
    status: Mapped[str] = mapped_column(String(20), default="Waiting")
    created_at: Mapped[str] = mapped_column(
        String(30),
        default=lambda: datetime.now(timezone.utc).isoformat()
    )
    triage_completed_at: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)


async def get_db():
    """Dependency that yields an async database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
