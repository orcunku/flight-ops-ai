"""FlightOps AI — interactive demo entry point."""
from __future__ import annotations
import json
from schemas import FlightDisruption, DisruptionType
from agents.orchestrator import resolve
from utils.llm import TRACKER, _LIVE

SCENARIOS = [
    FlightDisruption(
        flight_no="DL1423", origin="JFK", destination="LAX",
        scheduled_dep="14:00", disruption_type=DisruptionType.CANCELLATION,
        delay_minutes=240, passengers=180, reason="winter storm"),
    FlightDisruption(
        flight_no="AA887", origin="LAX", destination="ATL",
        scheduled_dep="09:30", disruption_type=DisruptionType.DELAY,
        delay_minutes=75, passengers=140, reason="crew scheduling"),
]


def main():
    mode = "LIVE (Anthropic API)" if _LIVE else "MOCK (offline, set ANTHROPIC_API_KEY for live)"
    print("=" * 70)
    print(f"  FlightOps AI — Multi-Agent Disruption Management   [{mode}]")
    print("=" * 70)

    for scenario in SCENARIOS:
        result = resolve(scenario)
        print("\n📋 RESOLUTION")
        print(json.dumps(result.model_dump(), indent=2, default=str))
        print("\n" + "─" * 70)

    if _LIVE:
        print(f"\n💰 Run cost: ${TRACKER.est_cost_usd} "
              f"({TRACKER.input_tokens} in / {TRACKER.output_tokens} out tokens)")


if __name__ == "__main__":
    main()
