"""Tools available to agents. Each has an Anthropic-style JSON schema + a callable.

In production these would hit real APIs (NOAA weather, GDS flight search, PSS rebooking).
Here they return deterministic mock data so the system runs offline.
"""
from __future__ import annotations
import random


# ---- Tool implementations -------------------------------------------------

def get_weather(airport_code: str) -> dict:
    conditions = {
        "JFK": {"condition": "snow", "visibility_km": 1.2, "wind_kts": 35, "severe": True},
        "ORD": {"condition": "thunderstorm", "visibility_km": 3.0, "wind_kts": 28, "severe": True},
        "LAX": {"condition": "clear", "visibility_km": 16.0, "wind_kts": 8, "severe": False},
        "ATL": {"condition": "rain", "visibility_km": 6.0, "wind_kts": 14, "severe": False},
    }
    return conditions.get(airport_code.upper(),
                          {"condition": "clear", "visibility_km": 16.0, "wind_kts": 6, "severe": False})


def search_alternative_flights(origin: str, destination: str, after_time: str) -> list[dict]:
    carriers = ["DL", "AA", "UA", "B6"]
    out = []
    base_hour = 14
    for i in range(3):
        out.append({
            "flight_no": f"{random.choice(carriers)}{random.randint(100, 999)}",
            "carrier": random.choice(carriers),
            "dep_time": f"{base_hour + i*2:02d}:30",
            "arr_time": f"{base_hour + i*2 + 4:02d}:45",
            "seats_available": random.randint(5, 60),
            "extra_cost_usd": round(random.uniform(0, 220), 2),
        })
    return out


def rebook_passengers(flight_no: str, passenger_count: int) -> dict:
    return {"status": "confirmed", "flight_no": flight_no,
            "rebooked": passenger_count, "confirmation": f"RBK{random.randint(10000, 99999)}"}


# ---- Anthropic tool schemas ----------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "get_weather",
        "description": "Get current weather conditions at an airport by IATA code.",
        "input_schema": {
            "type": "object",
            "properties": {"airport_code": {"type": "string", "description": "IATA code, e.g. JFK"}},
            "required": ["airport_code"],
        },
    },
    {
        "name": "search_alternative_flights",
        "description": "Search for alternative flights between two airports after a given time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "destination": {"type": "string"},
                "after_time": {"type": "string", "description": "HH:MM 24h"},
            },
            "required": ["origin", "destination", "after_time"],
        },
    },
    {
        "name": "rebook_passengers",
        "description": "Rebook a number of passengers onto a target flight.",
        "input_schema": {
            "type": "object",
            "properties": {
                "flight_no": {"type": "string"},
                "passenger_count": {"type": "integer"},
            },
            "required": ["flight_no", "passenger_count"],
        },
    },
]

TOOL_REGISTRY = {
    "get_weather": get_weather,
    "search_alternative_flights": search_alternative_flights,
    "rebook_passengers": rebook_passengers,
}


def dispatch(name: str, args: dict):
    """Execute a tool call by name."""
    if name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {name}")
    return TOOL_REGISTRY[name](**args)
