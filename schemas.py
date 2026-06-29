"""Typed schemas — every agent returns validated structured output."""
from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    MINOR = "minor"          # < 1h delay
    MODERATE = "moderate"    # 1-3h delay
    SEVERE = "severe"        # 3h+ delay / cancellation


class DisruptionType(str, Enum):
    DELAY = "delay"
    CANCELLATION = "cancellation"
    DIVERSION = "diversion"


class FlightDisruption(BaseModel):
    flight_no: str
    origin: str
    destination: str
    scheduled_dep: str
    disruption_type: DisruptionType
    delay_minutes: int = 0
    passengers: int = Field(ge=0)
    reason: Optional[str] = None


class DisruptionAssessment(BaseModel):
    """Output of the Disruption Analyst agent."""
    severity: Severity
    root_cause: str
    weather_factor: bool
    estimated_resolution_minutes: int
    affected_passengers: int
    rationale: str


class AlternativeFlight(BaseModel):
    flight_no: str
    carrier: str
    dep_time: str
    arr_time: str
    seats_available: int
    extra_cost_usd: float


class RebookingPlan(BaseModel):
    """Output of the Rebooking agent."""
    alternatives: list[AlternativeFlight]
    recommended_flight_no: str
    rebooking_notes: str
    estimated_cost_usd: float


class ComplianceRuling(BaseModel):
    """Output of the Compliance agent (RAG-backed)."""
    regulation_id: str
    compensation_owed: bool
    compensation_per_pax_usd: float
    care_obligations: list[str]
    citation: str
    reasoning: str


class FinalResolution(BaseModel):
    """Orchestrator's aggregated output."""
    disruption: FlightDisruption
    assessment: DisruptionAssessment
    rebooking: RebookingPlan
    compliance: ComplianceRuling
    total_estimated_cost_usd: float
    executive_summary: str
