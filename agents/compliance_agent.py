"""Agent 3 — Compliance Agent (RAG).

Retrieves the relevant passenger-rights regulation and determines compensation +
duty-of-care obligations. Demonstrates: retrieval-augmented generation + grounded reasoning.
"""
from __future__ import annotations
from schemas import (FlightDisruption, DisruptionAssessment, ComplianceRuling)
from data.regulations import retrieve
from utils.llm import call, extract_json

SYSTEM = (
    "You are an airline Compliance Officer. Using ONLY the provided regulation excerpts, "
    "determine whether compensation is owed and what care obligations apply. "
    "Weather/extraordinary circumstances exempt compensation but NOT duty of care. "
    "Respond ONLY with JSON: "
    '{"regulation_id": str, "compensation_owed": bool, "compensation_per_pax_usd": number, '
    '"care_obligations": [str], "citation": str, "reasoning": str}'
)


def run(disruption: FlightDisruption,
        assessment: DisruptionAssessment) -> ComplianceRuling:
    query = (f"{disruption.disruption_type.value} delay "
             f"{disruption.delay_minutes} minutes weather {assessment.weather_factor} compensation care")
    docs = retrieve(query, k=2)
    context = "\n\n".join(f"[{d.id}] {d.title}\n{d.text}" for d in docs)

    messages = [{"role": "user", "content":
                 f"Regulations:\n{context}\n\nDisruption: {disruption.model_dump_json()}\n"
                 f"Weather-caused: {assessment.weather_factor}, "
                 f"delay: {disruption.delay_minutes}min. Rule on it."}]

    resp = call(SYSTEM, messages, mock_fn=lambda s, m: {"text": "", "stop_reason": "end_turn"})
    data = extract_json(resp.get("text", ""))

    if not data:  # deterministic grounded fallback
        long_delay = disruption.delay_minutes >= 180 or \
            disruption.disruption_type.value == "cancellation"
        owed = long_delay and not assessment.weather_factor
        comp = 600.0 if owed else 0.0  # EU261 long-haul tier (USD approx)
        care = (["meals/refreshments", "hotel if overnight", "ground transport",
                 "two free communications"] if disruption.delay_minutes >= 120 else [])
        data = {
            "regulation_id": docs[0].id,
            "compensation_owed": owed,
            "compensation_per_pax_usd": comp,
            "care_obligations": care,
            "citation": f"{docs[0].id}: {docs[0].title}",
            "reasoning": (
                f"{'Long delay/cancellation' if long_delay else 'Short delay'}; "
                f"weather_factor={assessment.weather_factor}. "
                f"{'Compensation exempt due to extraordinary circumstances, ' if assessment.weather_factor and long_delay else ''}"
                f"duty of care {'applies' if care else 'not triggered'}."),
        }
    return ComplianceRuling(**data)
