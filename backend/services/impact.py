"""
impact.py — Impact Score Calculation
Outputs a severity score from 1 (low) to 10 (critical)
based on sentiment magnitude, event type, and risk keywords.
"""

from __future__ import annotations

# Base scores by event type (how inherently market-moving the event is)
EVENT_BASE: dict[str, float] = {
    "Geopolitical":       2.5,
    "Macroeconomic":      2.5,
    "Credit Event":       2.5,
    "Merger/Acquisition": 1.5,
    "Earnings":           1.5,
    "Product Launch":     0.5,
    "General Market":     0.0,
}

# High-risk words that push the score up
HIGH_RISK_TERMS: list[tuple[str, float]] = [
    ("crisis",          0.8),
    ("default",         0.8),
    ("bankruptcy",      0.8),
    ("sanction",        0.8),
    ("collapse",        0.8),
    ("investigation",   0.5),
    ("lawsuit",         0.5),
    ("downgrade",       0.6),
    ("fraud",           0.8),
    ("recall",          0.5),
    ("warning",         0.4),
    ("risk",            0.3),
    ("concern",         0.3),
    ("volatility",      0.4),
    ("shock",           0.6),
]

# Positive amplifiers (strong positive news also creates impact)
POSITIVE_AMPLIFIERS: list[tuple[str, float]] = [
    ("record",          0.4),
    ("surge",           0.5),
    ("breakthrough",    0.5),
    ("boom",            0.4),
    ("soar",            0.5),
]


def calculate_impact(
    sentiment_score: float,
    event_type: str,
    text: str,
) -> int:
    """
    Calculate impact score in range [1, 10].

    Formula:
        base = 3
        + sentiment_magnitude * 4   (strong opinion → high impact)
        + event_base                 (inherent severity of event class)
        + keyword_bonus              (specific risk/amplifier words)

    Returns:
        int in [1, 10]
    """
    score: float = 3.0

    # Sentiment magnitude: strong positive OR negative both mean high impact
    magnitude = abs(sentiment_score)
    score += magnitude * 4.0

    # Event-type base
    score += EVENT_BASE.get(event_type, 0.0)

    # Keyword scan
    text_lower = text.lower()
    for term, bonus in HIGH_RISK_TERMS:
        if term in text_lower:
            score += bonus

    for term, bonus in POSITIVE_AMPLIFIERS:
        if term in text_lower:
            score += bonus

    # Clamp and round to integer
    return max(1, min(10, round(score)))


def risk_level_from_impact(impact: int) -> str:
    """Convert an impact integer to a human-readable risk level."""
    if impact >= 8:
        return "Critical"
    if impact >= 6:
        return "High"
    if impact >= 4:
        return "Medium"
    return "Low"
