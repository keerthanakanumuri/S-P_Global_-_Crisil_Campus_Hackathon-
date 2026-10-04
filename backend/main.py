"""
main.py — FinRisk AI FastAPI Application
Endpoints:
    GET /              → health check
    GET /ingest        → pull live data, run NLP pipeline, store signals
    GET /signals       → return latest processed risk signals
    GET /rebalance     → return current portfolio allocation
    GET /summary       → aggregate market-level stats
    GET /demo          → load demo_signals.json (fallback mode)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.ingestion import ingest_all
from services.risk_engine import process_all
from services.rebalancer import rebalance

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FinRisk AI",
    description="Real-Time Financial Risk Intelligence & Tactical Index Rebalancing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory state ───────────────────────────────────────────────────────────
_signals: list[dict] = []

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
STOCKS_CSV = BASE_DIR / "data" / "stocks.csv"
DEMO_FILE = BASE_DIR.parent / "data" / "demo_signals.json"


def _load_stocks() -> list[dict]:
    return pd.read_csv(STOCKS_CSV).to_dict("records")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root() -> dict:
    return {
        "service": "FinRisk AI",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/ingest", "/signals", "/rebalance", "/summary", "/demo"],
    }


@app.get("/ingest", tags=["Engine"])
def ingest() -> dict:
    """
    Fetch live data from all sources, run the full NLP pipeline,
    and store the processed signals in memory.
    """
    global _signals
    try:
        raw = ingest_all()
        _signals = process_all(raw)
        return {
            "status": "ok",
            "signal_count": len(_signals),
            "signals": _signals,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/signals", tags=["Engine"])
def get_signals() -> list[dict]:
    """Return the latest processed risk signals."""
    return _signals


@app.get("/rebalance", tags=["Module A"])
def get_rebalance() -> list[dict]:
    """Return portfolio allocation after applying current risk signals."""
    stocks = _load_stocks()
    return rebalance(stocks, _signals)


@app.get("/summary", tags=["Engine"])
def get_summary() -> dict[str, Any]:
    """Return aggregate market-level statistics."""
    if not _signals:
        return {
            "signal_count": 0,
            "avg_sentiment": 0.0,
            "avg_impact": 0.0,
            "high_risk_count": 0,
            "critical_count": 0,
            "event_distribution": {},
            "market_risk_score": 0.0,
        }

    sentiments = [s["sentiment_score"] for s in _signals]
    impacts = [s["impact_score"] for s in _signals]
    avg_sentiment = round(sum(sentiments) / len(sentiments), 4)
    avg_impact = round(sum(impacts) / len(impacts), 2)
    high_risk = sum(1 for s in _signals if s["risk_level"] in ("High", "Critical"))
    critical = sum(1 for s in _signals if s["risk_level"] == "Critical")

    event_dist: dict[str, int] = {}
    for s in _signals:
        ev = s["event_type"]
        event_dist[ev] = event_dist.get(ev, 0) + 1

    # Composite market risk score [0–10]
    market_risk = round(
        avg_impact * 0.5
        + abs(avg_sentiment) * 3
        + (high_risk / max(len(_signals), 1)) * 3,
        1,
    )
    market_risk = min(10.0, market_risk)

    return {
        "signal_count": len(_signals),
        "avg_sentiment": avg_sentiment,
        "avg_impact": avg_impact,
        "high_risk_count": high_risk,
        "critical_count": critical,
        "event_distribution": event_dist,
        "market_risk_score": market_risk,
    }


@app.get("/demo", tags=["Engine"])
def load_demo() -> dict:
    """
    Load pre-built demo signals from demo_signals.json.
    Use this as a fallback when live APIs are unavailable.
    """
    global _signals
    if not DEMO_FILE.exists():
        raise HTTPException(status_code=404, detail="demo_signals.json not found")
    with open(DEMO_FILE, "r", encoding="utf-8") as f:
        _signals = json.load(f)
    return {
        "status": "demo_mode",
        "signal_count": len(_signals),
        "signals": _signals,
    }
