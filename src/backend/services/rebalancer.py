"""
rebalancer.py — Tactical Index Rebalancing Engine
Consumes structured risk signals and produces adjusted portfolio weights.

Rebalancing formula (per stock):
    signal_score = mean(sentiment_score * source_confidence * recency_weight)
    risk_adjusted = signal_score * (1 - impact_score / 15)
    new_weight = base_weight * (1 + risk_adjusted)
    → clamp to [MIN_WEIGHT, MAX_WEIGHT]
    → normalize so all weights sum to 1.0

Action thresholds:
    new_weight > base * 1.05  → INCREASE
    new_weight < base * 0.95  → REDUCE
    otherwise                 → HOLD
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd

MIN_WEIGHT = 0.02   # 2%  – prevent near-zero allocations
MAX_WEIGHT = 0.12   # 12% – prevent excessive concentration


def _recency_weight(timestamp_iso: str) -> float:
    """Return a decay factor based on how old the signal is."""
    try:
        ts = datetime.fromisoformat(timestamp_iso.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        age_hours = (now - ts).total_seconds() / 3600.0
    except Exception:
        return 0.5  # unknown age → moderate weight

    if age_hours < 1:
        return 1.00
    if age_hours < 6:
        return 0.85
    if age_hours < 12:
        return 0.65
    if age_hours < 24:
        return 0.40
    return 0.20


def rebalance(stocks: list[dict], signals: list[dict]) -> list[dict]:
    """
    Produce an updated allocation for every stock.

    Args:
        stocks:  list of dicts from stocks.csv  (ticker, name, sector, weight)
        signals: list of processed risk signals from risk_engine

    Returns:
        list of dicts with keys:
            ticker, name, sector, base_weight, new_weight, weight_change_pct,
            sentiment_score, impact_score, action, signal_count
    """
    df = pd.DataFrame(stocks)
    df["weight"] = df["weight"].astype(float)

    if not signals:
        # No signals – return unchanged allocation
        df["new_weight"] = df["weight"]
        df["weight_change_pct"] = 0.0
        df["sentiment_score"] = 0.0
        df["impact_score"] = 3.0
        df["action"] = "HOLD"
        df["signal_count"] = 0
        return df.to_dict("records")

    sig_df = pd.DataFrame(signals)

    # ── Per-signal effective score ───────────────────────────────────────────
    sig_df["recency"] = sig_df["timestamp"].apply(_recency_weight)
    sig_df["effective_score"] = (
        sig_df["sentiment_score"]
        * sig_df.get("source_confidence", pd.Series(1.0, index=sig_df.index))
        * sig_df["recency"]
    )

    # ── Aggregate per ticker ─────────────────────────────────────────────────
    agg = (
        sig_df.groupby("ticker")
        .agg(
            agg_sentiment=("effective_score", "mean"),
            agg_impact=("impact_score", "mean"),
            signal_count=("effective_score", "count"),
        )
        .reset_index()
    )

    df = df.merge(agg, on="ticker", how="left")
    df["agg_sentiment"] = df["agg_sentiment"].fillna(0.0)
    df["agg_impact"]    = df["agg_impact"].fillna(3.0)
    df["signal_count"]  = df["signal_count"].fillna(0).astype(int)

    # ── Risk-adjusted signal ─────────────────────────────────────────────────
    # High impact dampens the positive effect; extreme negative has full effect
    df["risk_adjusted_score"] = df["agg_sentiment"] * (1 - df["agg_impact"] / 15)

    # ── New weight ──────────────────────────────────────────────────────────
    df["new_weight"] = df["weight"] * (1 + df["risk_adjusted_score"])
    df["new_weight"] = df["new_weight"].clip(lower=MIN_WEIGHT, upper=MAX_WEIGHT)
    # Normalize to sum to 1.0
    total = df["new_weight"].sum()
    if total > 0:
        df["new_weight"] = df["new_weight"] / total

    # ── Change % ────────────────────────────────────────────────────────────
    df["weight_change_pct"] = ((df["new_weight"] - df["weight"]) / df["weight"] * 100).round(2)

    # ── Action ──────────────────────────────────────────────────────────────
    df["action"] = "HOLD"
    df.loc[df["new_weight"] > df["weight"] * 1.05, "action"] = "INCREASE"
    df.loc[df["new_weight"] < df["weight"] * 0.95, "action"] = "REDUCE"

    # ── Round for readability ────────────────────────────────────────────────
    df["new_weight"]      = df["new_weight"].round(6)
    df["agg_sentiment"]   = df["agg_sentiment"].round(4)
    df["agg_impact"]      = df["agg_impact"].round(2)

    return df.rename(columns={
        "weight":        "base_weight",
        "agg_sentiment": "sentiment_score",
        "agg_impact":    "impact_score",
    }).to_dict("records")
