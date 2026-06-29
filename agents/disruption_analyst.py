"""Agent 1 — Disruption Analyst.

Uses weather tools to assess root cause + severity of a flight disruption.
Demonstrates: tool calling loop + structured output.
"""
from __future__ import annotations
from schemas import FlightDisruption, DisruptionAssessment, Severity
from tools import TOOL_SCHEMAS, dispatch
from utils.llm import call, extract_json

SYSTEM = (
    "You are a Disruption Analyst for an airline operations center. "
    "Given a flight disruption, call get_weather for the origin airport, then assess "
    "severity and root cause. Respond ONLY with JSON matching: "
    '{"severity": "minor|moderate|severe", "root_cause": str, "weather_factor": bool, '
    '"estimated_resolution_minutes": int, "affected_passengers": int, "rationale": str}'
)


def _mock(system, messages):
    """Deterministic fallback when offline."""
    last = messages[-1]
    content = last["content"]
    if isinstance(content, list):  # tool result present -> emit final JSON
        text = str(content)
        weather_severe = "snow" in text or "thunderstorm" in text or "'severe': True" in text
        return {"text": "", "tool_calls": [], "stop_reason": "end_turn",
                "_final": {"weather_factor": weather_severe}}
    return {"text": "", "stop_reason": "tool_use",
            "tool_calls": [{"id": "t1", "name": "get_weather",
                            "input": {"airport_code": "JFK"}}]}


def run(disruption: FlightDisruption) -> DisruptionAssessment:
    messages = [{"role": "user", "content":
                 f"Disruption: {disruption.model_dump_json()}. Assess it."}]

    # tool-use loop (max 3 hops)
    weather = None
    for _ in range(3):
        resp = call(SYSTEM, messages, tools=TOOL_SCHEMAS,
                    mock_fn=lambda s, m: _mock(s, m))
        if resp.get("tool_calls"):
            tc = resp["tool_calls"][0]
            # default airport to actual origin in mock
            if tc["name"] == "get_weather":
                tc["input"]["airport_code"] = disruption.origin
            result = dispatch(tc["name"], tc["input"])
            weather = result if tc["name"] == "get_weather" else weather
            messages.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": tc["id"], "name": tc["name"], "input": tc["input"]}]})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tc["id"], "content": str(result)}]})
            continue
        break

    data = extract_json(resp.get("text", ""))
    if not data:  # build from tool data deterministically (mock path)
        weather = weather or dispatch("get_weather", {"airport_code": disruption.origin})
        wx_factor = weather.get("severe", False)
        mins = disruption.delay_minutes
        sev = Severity.SEVERE if mins >= 180 or disruption.disruption_type.value == "cancellation" \
            else Severity.MODERATE if mins >= 60 else Severity.MINOR
        data = {
            "severity": sev.value,
            "root_cause": f"{weather['condition']} at {disruption.origin}" if wx_factor
                          else (disruption.reason or "operational"),
            "weather_factor": wx_factor,
            "estimated_resolution_minutes": max(mins, 90 if wx_factor else 45),
            "affected_passengers": disruption.passengers,
            "rationale": f"{disruption.delay_minutes}min disruption; weather severe={wx_factor}.",
        }
    return DisruptionAssessment(**data)
