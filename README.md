# ✈️ FlightOps AI — Multi-Agent Flight Disruption Management System

[![CI](https://github.com/YOUR_USERNAME/flight-ops-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/flight-ops-ai/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/flight-ops-ai/blob/main/FlightOps_AI_Colab.ipynb)

> Replace `YOUR_USERNAME` in the badge URL above with your GitHub username after you push.

A production-style **3-agent system** that detects flight disruptions, assesses passenger
impact, and generates re-accommodation plans — built to showcase the skills recruiters
screen for in 2026: **agent orchestration, tool calling, RAG, structured outputs, and evals.**

## Why this matters (aviation context)
When a flight is delayed or cancelled, airlines must rebook passengers, honor regulations
(EU261 / US DOT), and minimize cost — fast. This system automates the triage loop.

## Architecture

```
                    ┌─────────────────────┐
   Disruption  ───► │   ORCHESTRATOR       │  (plans, routes, aggregates)
   event            └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
     ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
     │ DISRUPTION    │ │ REBOOKING     │ │ COMPLIANCE    │
     │ ANALYST       │ │ AGENT         │ │ AGENT         │
     │ (weather +    │ │ (search alt.  │ │ (RAG over     │
     │  flight tools)│ │  flights)     │ │  regulations) │
     └───────────────┘ └───────────────┘ └───────────────┘
```

> Max 3 specialist agents under one orchestrator (the orchestrator is coordination logic,
> not a 4th specialist).

## Skills demonstrated (the part recruiters scan)
- **Multi-agent orchestration** — planner/router that delegates to specialists
- **Tool / function calling** — typed tools (weather, flight search, rebooking)
- **RAG** — regulation retrieval over an embedded knowledge base
- **Structured outputs** — Pydantic schemas, validated JSON every turn
- **Evaluation harness** — automated test cases with pass/fail scoring
- **Observability** — per-agent tracing + token/cost logging

## Run — three ways

### 1. Google Colab (zero setup, best for demoing)
Open `FlightOps_AI_Colab.ipynb` in Colab and run all cells. It's fully self-contained
and runs offline in mock mode. To run live, add `ANTHROPIC_API_KEY` in Colab **Secrets**
(🔑 icon in the left sidebar) — the first cell picks it up automatically.

### 2. Local Python
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...        # optional: runs in mock mode without it
python main.py                          # interactive demo
python -m evals.run_evals               # eval suite
```

### 3. Docker (shows you can containerize / deploy)
```bash
docker build -t flightops-ai .
docker run --rm flightops-ai                              # demo, mock mode
docker run --rm -e ANTHROPIC_API_KEY=sk-... flightops-ai  # live
docker run --rm flightops-ai python -m evals.run_evals    # evals

# or with compose:
docker compose up flightops
docker compose run --rm evals
```

## Tech
Python · Anthropic API · Pydantic · in-memory vector store · Docker · Colab
