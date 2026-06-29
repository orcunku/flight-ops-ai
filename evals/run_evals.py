"""Evaluation harness — automated correctness checks on agent behavior.

Recruiters love this: it shows you treat agents like software, not magic.
Run: python -m evals.run_evals
"""
from __future__ import annotations
from schemas import FlightDisruption, DisruptionType, Severity
from agents.orchestrator import resolve

CASES = [
    {
        "name": "weather_cancellation_no_compensation",
        "input": FlightDisruption(
            flight_no="DL1423", origin="JFK", destination="LAX", scheduled_dep="14:00",
            disruption_type=DisruptionType.CANCELLATION, delay_minutes=240,
            passengers=180, reason="winter storm"),
        # Weather = extraordinary circumstance -> no compensation, but care applies.
        "expect": lambda r: (r.assessment.severity == Severity.SEVERE
                             and r.assessment.weather_factor is True
                             and r.compliance.compensation_owed is False
                             and len(r.compliance.care_obligations) > 0),
    },
    {
        "name": "non_weather_long_delay_owes_compensation",
        "input": FlightDisruption(
            flight_no="UA200", origin="LAX", destination="ATL", scheduled_dep="08:00",
            disruption_type=DisruptionType.DELAY, delay_minutes=200,
            passengers=120, reason="crew scheduling"),
        "expect": lambda r: (r.compliance.compensation_owed is True
                             and r.compliance.compensation_per_pax_usd > 0),
    },
    {
        "name": "minor_delay_no_obligations",
        "input": FlightDisruption(
            flight_no="AA887", origin="LAX", destination="ATL", scheduled_dep="09:30",
            disruption_type=DisruptionType.DELAY, delay_minutes=40,
            passengers=140, reason="late inbound aircraft"),
        "expect": lambda r: (r.assessment.severity == Severity.MINOR
                             and r.compliance.compensation_owed is False),
    },
    {
        "name": "rebooking_recommends_valid_flight",
        "input": FlightDisruption(
            flight_no="B655", origin="JFK", destination="LAX", scheduled_dep="12:00",
            disruption_type=DisruptionType.DELAY, delay_minutes=190,
            passengers=30, reason="mechanical"),
        "expect": lambda r: (r.rebooking.recommended_flight_no in
                             [a.flight_no for a in r.rebooking.alternatives]
                             and r.total_estimated_cost_usd >= 0),
    },
]


def run():
    passed = 0
    print("\nRunning eval suite...\n")
    for case in CASES:
        try:
            result = resolve(case["input"])
            ok = bool(case["expect"](result))
        except Exception as e:
            ok = False
            print(f"  ERROR in {case['name']}: {e}")
        passed += ok
        print(f"  {'✅ PASS' if ok else '❌ FAIL'}  {case['name']}")
    print(f"\n{passed}/{len(CASES)} cases passed "
          f"({100*passed/len(CASES):.0f}%)\n")
    return passed == len(CASES)


if __name__ == "__main__":
    import sys
    sys.exit(0 if run() else 1)
