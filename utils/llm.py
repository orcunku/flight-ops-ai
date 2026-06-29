"""Thin Anthropic client wrapper.

Runs against the real API when ANTHROPIC_API_KEY is set; otherwise falls back to a
deterministic mock so the project is runnable in any environment (e.g. by a recruiter).
"""
from __future__ import annotations
import json
import os
from typing import Optional

MODEL = "claude-sonnet-4-6"
_LIVE = bool(os.environ.get("ANTHROPIC_API_KEY"))

try:
    from anthropic import Anthropic
    _client = Anthropic() if _LIVE else None
except Exception:
    _client = None
    _LIVE = False


class TokenTracker:
    """Lightweight observability: counts tokens/cost across the run."""
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0

    def add(self, usage):
        if usage:
            self.input_tokens += getattr(usage, "input_tokens", 0)
            self.output_tokens += getattr(usage, "output_tokens", 0)

    @property
    def est_cost_usd(self) -> float:
        # Sonnet pricing approximation
        return round(self.input_tokens / 1e6 * 3 + self.output_tokens / 1e6 * 15, 4)


TRACKER = TokenTracker()


def call(system: str, messages: list[dict], tools: Optional[list] = None,
         mock_fn=None) -> dict:
    """Single LLM turn. Returns {'text', 'tool_calls', 'stop_reason'}.

    mock_fn(system, messages) -> dict is used when offline.
    """
    if not _LIVE or _client is None:
        return mock_fn(system, messages) if mock_fn else {"text": "{}", "tool_calls": [], "stop_reason": "end_turn"}

    kwargs = dict(model=MODEL, max_tokens=1024, system=system, messages=messages)
    if tools:
        kwargs["tools"] = tools
    resp = _client.messages.create(**kwargs)
    TRACKER.add(resp.usage)

    text, tool_calls = "", []
    for block in resp.content:
        if block.type == "text":
            text += block.text
        elif block.type == "tool_use":
            tool_calls.append({"id": block.id, "name": block.name, "input": block.input})
    return {"text": text, "tool_calls": tool_calls, "stop_reason": resp.stop_reason}


def extract_json(text: str) -> dict:
    """Pull a JSON object out of an LLM text response."""
    text = text.strip().replace("```json", "").replace("```", "").strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return {}
