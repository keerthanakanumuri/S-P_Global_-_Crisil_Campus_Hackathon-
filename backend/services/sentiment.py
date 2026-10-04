"""
sentiment.py — Financial Sentiment Analysis using FinBERT
Model: ProsusAI/finbert
  Labels: positive | negative | neutral
  Output: score in [-1.0, +1.0]
"""

from __future__ import annotations

_pipeline = None  # lazy-loaded on first call


def _get_pipeline():
    """Lazy-load FinBERT so the server starts fast."""
    global _pipeline
    if _pipeline is None:
        from transformers import pipeline as hf_pipeline
        print("[sentiment] Loading FinBERT model (first call)…")
        _pipeline = hf_pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
            truncation=True,
            max_length=512,
        )
        print("[sentiment] FinBERT loaded.")
    return _pipeline


def analyze_sentiment(text: str) -> dict:
    """
    Analyse the financial sentiment of a text string.

    Returns:
        {
            "label": "positive" | "negative" | "neutral",
            "score": float  # range [-1.0, +1.0]
        }
    """
    if not text or not text.strip():
        return {"label": "neutral", "score": 0.0}

    try:
        clf = _get_pipeline()
        result = clf(text[:512])[0]
        label: str = result["label"].lower()
        confidence: float = float(result["score"])

        if label == "positive":
            score = round(confidence, 4)
        elif label == "negative":
            score = round(-confidence, 4)
        else:
            score = 0.0

        return {"label": label, "score": score}

    except Exception as exc:
        print(f"[sentiment] Error analysing text: {exc}")
        return {"label": "neutral", "score": 0.0}
