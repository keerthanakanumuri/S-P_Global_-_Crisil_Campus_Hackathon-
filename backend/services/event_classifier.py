"""
event_classifier.py — Rule-based Event Classification
Classifies financial text into one of six event categories
using weighted keyword matching.
"""

from __future__ import annotations

# ── Keyword dictionary ────────────────────────────────────────────────────────
# Each key maps to a list of (keyword, weight) pairs.
# Higher-weight terms are stronger signals for that category.
EVENT_KEYWORDS: dict[str, list[tuple[str, float]]] = {
    "Geopolitical": [
        ("war", 2.0),
        ("sanction", 2.0),
        ("tariff", 1.5),
        ("geopolitical", 2.0),
        ("trade restriction", 2.0),
        ("embargo", 2.0),
        ("government", 0.5),
        ("regulation", 0.5),
        ("export control", 1.5),
        ("military", 1.0),
        ("invasion", 2.0),
        ("conflict", 1.5),
        ("nato", 1.0),
        ("diplomat", 0.5),
    ],
    "Macroeconomic": [
        ("inflation", 2.0),
        ("interest rate", 2.0),
        ("recession", 2.0),
        ("gdp", 1.5),
        ("economy", 1.0),
        ("federal reserve", 2.0),
        ("fed", 1.0),
        ("cpi", 1.5),
        ("unemployment", 1.5),
        ("stagflation", 2.0),
        ("monetary policy", 1.5),
        ("rate hike", 2.0),
        ("rate cut", 1.5),
        ("yield", 1.0),
        ("treasury", 1.0),
    ],
    "Credit Event": [
        ("debt", 1.5),
        ("default", 2.0),
        ("credit", 1.5),
        ("bankruptcy", 2.0),
        ("downgrade", 2.0),
        ("loan", 1.0),
        ("bond yield", 1.5),
        ("rating", 1.0),
        ("insolvency", 2.0),
        ("restructuring", 1.5),
        ("delinquency", 1.5),
        ("write-off", 1.5),
    ],
    "Merger/Acquisition": [
        ("merger", 2.0),
        ("acquisition", 2.0),
        ("acquire", 2.0),
        ("takeover", 2.0),
        ("deal", 0.5),
        ("buyout", 2.0),
        ("ipo", 1.5),
        ("spin-off", 1.5),
        ("divestiture", 1.5),
        ("partnership", 0.5),
        ("joint venture", 1.0),
        ("consolidation", 1.0),
    ],
    "Product Launch": [
        ("launch", 1.5),
        ("product", 1.0),
        ("release", 1.0),
        ("new model", 1.5),
        ("new device", 1.5),
        ("unveil", 1.5),
        ("announce", 0.5),
        ("innovation", 1.0),
        ("patent", 1.0),
        ("research", 0.5),
        ("development", 0.5),
        ("breakthrough", 1.5),
        ("technology", 0.5),
    ],
    "Earnings": [
        ("earnings", 2.0),
        ("revenue", 1.5),
        ("profit", 1.5),
        ("loss", 1.5),
        ("eps", 2.0),
        ("quarterly", 1.5),
        ("guidance", 1.5),
        ("beat", 1.5),
        ("miss", 1.5),
        ("forecast", 1.0),
        ("outlook", 1.0),
        ("dividend", 1.0),
        ("buyback", 1.0),
    ],
}


def classify_event(text: str) -> str:
    """
    Classify the primary event type of a financial text.

    Returns one of:
        Geopolitical | Macroeconomic | Credit Event |
        Merger/Acquisition | Product Launch | Earnings | General Market
    """
    if not text:
        return "General Market"

    text_lower = text.lower()
    scores: dict[str, float] = {}

    for event, pairs in EVENT_KEYWORDS.items():
        total = 0.0
        for keyword, weight in pairs:
            if keyword in text_lower:
                total += weight
        scores[event] = total

    best_event = max(scores, key=lambda k: scores[k])

    if scores[best_event] == 0.0:
        return "General Market"

    return best_event
