"""Tiny in-memory RAG store over aviation passenger-rights regulations.

Uses keyword + token-overlap scoring so it runs with zero dependencies / offline.
Swap `retrieve` for a real embedding model (e.g. voyage-3) in production.
"""
from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class Doc:
    id: str
    title: str
    text: str


KNOWLEDGE_BASE = [
    Doc(
        id="EU261-Art7",
        title="EU261 Article 7 — Right to Compensation",
        text=("Under EU Regulation 261/2004, passengers are entitled to compensation of "
              "250 EUR for flights up to 1500 km, 400 EUR for intra-EU flights over 1500 km "
              "and other flights 1500-3500 km, and 600 EUR for all other flights, when a "
              "cancellation or long delay of 3 hours or more occurs and is within the "
              "carrier's control. Weather and other extraordinary circumstances exempt the "
              "carrier from compensation but not from the duty of care."),
    ),
    Doc(
        id="EU261-Art9",
        title="EU261 Article 9 — Right to Care",
        text=("Passengers facing delay are entitled to meals and refreshments, hotel "
              "accommodation when an overnight stay is required, transport between airport "
              "and accommodation, and two free communications. These care obligations apply "
              "even under extraordinary circumstances such as severe weather."),
    ),
    Doc(
        id="USDOT-Refund-2024",
        title="US DOT Automatic Refund Rule",
        text=("US Department of Transportation rules require airlines to provide automatic "
              "cash refunds when a flight is cancelled or significantly changed and the "
              "passenger does not accept rebooking. A significant delay is generally 3 hours "
              "domestic or 6 hours international. Compensation beyond refunds is not federally "
              "mandated for weather-related disruptions."),
    ),
    Doc(
        id="IATA-Reaccommodation",
        title="IATA Re-accommodation Guidance",
        text=("Carriers should re-accommodate passengers on the next available flight, "
              "including interline partners, prioritizing passengers with onward connections "
              "and those with reduced mobility. Cost minimization should not override duty of "
              "care obligations."),
    ),
]


def _tokens(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def retrieve(query: str, k: int = 2) -> list[Doc]:
    """Return top-k docs by token overlap (stand-in for vector similarity)."""
    q = _tokens(query)
    scored = []
    for doc in KNOWLEDGE_BASE:
        overlap = len(q & _tokens(doc.text + " " + doc.title))
        scored.append((overlap, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for score, d in scored[:k] if score > 0] or [KNOWLEDGE_BASE[0]]
