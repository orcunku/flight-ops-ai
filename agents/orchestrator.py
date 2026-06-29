"""Orchestrator — coordinates the 3 specialist agents into a final resolution.

This is the planner/router layer, not a 4th specialist: it sequences the agents,
passes state between them, and aggregates a single validated FinalResolution.
"""
from __future__ import annotations
import time
from schemas import FlightDisruption, FinalResolution
from agents import disruption_analyst, rebooking_agent, compliance_agent
from utils.llm import TRACKER


def _log(stage: str, t0: float):
    print(f"  [trace] {stage:<22} {(time.time()-t0)*1000:6.1f} ms")


def resolve(disruption: FlightDisruption) -> FinalResolution:
    print(f"\n🛫 Orchestrating resolution for {disruption.flight_no} "
          f"({disruption.origin}→{disruption.destination})")

    t0 = time.time()
    assessment = disruption_analyst.run(disruption)
    _log("disruption_analyst", t0)

    t0 = time.time()
    rebooking = rebooking_agent.run(disruption, assessment)
    _log("rebooking_agent", t0)

    t0 = time.time()
    compliance = compliance_agent.run(disruption, assessment)
    _log("compliance_agent", t0)

    total_cost = round(
        rebooking.estimated_cost_usd
        + compliance.compensation_per_pax_usd * disruption.passengers, 2)

    summary = (
        f"{disruption.disruption_type.value.title()} on {disruption.flight_no} rated "
        f"{assessment.severity.value.upper()} (cause: {assessment.root_cause}). "
        f"Recommend rebooking {disruption.passengers} pax onto {rebooking.recommended_flight_no}. "
        f"Compensation owed: {compliance.compensation_owed} "
        f"(${compliance.compensation_per_pax_usd:.0f}/pax). "
        f"Total estimated cost: ${total_cost:,.2f}.")

    return FinalResolution(
        disruption=disruption,
        assessment=assessment,
        rebooking=rebooking,
        compliance=compliance,
        total_estimated_cost_usd=total_cost,
        executive_summary=summary,
    )
