"""
risk_engine.py — Unified AI/NLP Risk Engine
Orchestrates the full pipeline:
  raw item → sentiment → event → impact → structured risk signal
"""

from __future__ import annotations

from datetime import datetime, timezone

from .sentiment import analyze_sentiment
from .event_classifier import classify_event
from .impact import calculate_impact, risk_level_from_impact

# Source confidence weights used downstream by the rebalancer
SOURCE_CONFIDENCE: dict[str, float] = {
    "Financial News": 1.0,
    "Social Media":   0.6,
}


def process_signal(item: dict) -> dict:
    """
    Convert a raw ingestion item into a full structured risk signal.

    Input keys expected:  source, ticker, company, title, text, url, timestamp
    Output adds:          sentiment_label, sentiment_score, event_type,
                          impact_score, risk_level, source_confidence,
                          processed_at
    """
    # Combine title + body for richer NLP context; cap at 512 tokens
    combined_text = f"{item.get('title', '')} {item.get('text', '')}".strip()

    # ── NLP pipeline ────────────────────────────────────────────────────────
    sentiment = analyze_sentiment(combined_text)
    event = classify_event(combined_text)
    impact = calculate_impact(sentiment["score"], event, combined_text)
    risk = risk_level_from_impact(impact)
    confidence = SOURCE_CONFIDENCE.get(item.get("source", ""), 0.7)

    return {
        # passthrough fields
        "source":           item.get("source", "Unknown"),
        "ticker":           item.get("ticker", ""),
        "company":          item.get("company", ""),
        "title":            item.get("title", ""),
        "text":             item.get("text", "")[:300],  # truncate for API response
        "url":              item.get("url", ""),
        "timestamp":        item.get("timestamp", datetime.now(timezone.utc).isoformat()),
        # generated fields
        "sentiment_label":  sentiment["label"],
        "sentiment_score":  sentiment["score"],
        "event_type":       event,
        "impact_score":     impact,
        "risk_level":       risk,
        "source_confidence": confidence,
        "processed_at":     datetime.now(timezone.utc).isoformat(),
    }


def process_all(raw_items: list[dict]) -> list[dict]:
    """Process a list of raw ingestion items and return risk signals."""
    signals = []
    for item in raw_items:
        try:
            signals.append(process_signal(item))
        except Exception as exc:
            print(f"[risk_engine] Skipping item for {item.get('ticker')}: {exc}")
    return signals
