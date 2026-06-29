"""Agent 2 — Rebooking Agent.

Searches alternative flights and proposes a re-accommodation plan that minimizes
cost while securing enough seats. Demonstrates: tool calling + cost optimization.
"""
from __future__ import annotations
from schemas import (FlightDisruption, DisruptionAssessment, RebookingPlan,
                     AlternativeFlight)
from tools import dispatch


def run(disruption: FlightDisruption,
        assessment: DisruptionAssessment) -> RebookingPlan:
    raw = dispatch("search_alternative_flights", {
        "origin": disruption.origin,
        "destination": disruption.destination,
        "after_time": disruption.scheduled_dep,
    })
    alts = [AlternativeFlight(**a) for a in raw]

    # Optimization: pick cheapest flight with enough seats; else most seats.
    viable = [a for a in alts if a.seats_available >= disruption.passengers]
    if viable:
        best = min(viable, key=lambda a: a.extra_cost_usd)
        notes = "Single flight covers all passengers at lowest incremental cost."
        cost = best.extra_cost_usd * disruption.passengers
    else:
        best = max(alts, key=lambda a: a.seats_available)
        notes = ("No single flight has enough seats; recommend splitting load across "
                 "flights, prioritizing connections and reduced-mobility passengers per IATA.")
        cost = sum(a.extra_cost_usd * a.seats_available for a in alts[:2])

    return RebookingPlan(
        alternatives=alts,
        recommended_flight_no=best.flight_no,
        rebooking_notes=notes,
        estimated_cost_usd=round(cost, 2),
    )
