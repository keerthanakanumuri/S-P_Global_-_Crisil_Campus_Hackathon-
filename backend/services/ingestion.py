"""
ingestion.py — Data Ingestion Service
Sources:
  1. Google News RSS feeds (Financial News)
  2. Reddit JSON API (Social Media)
"""

import feedparser
import requests
from datetime import datetime, timezone

# ── Stock universe ────────────────────────────────────────────────────────────
STOCKS: dict[str, str] = {
    "AAPL":  "Apple",
    "MSFT":  "Microsoft",
    "NVDA":  "NVIDIA",
    "AMZN":  "Amazon",
    "GOOGL": "Alphabet",
    "META":  "Meta",
    "TSLA":  "Tesla",
    "JPM":   "JPMorgan",
    "V":     "Visa",
    "MA":    "Mastercard",
    "WMT":   "Walmart",
    "XOM":   "Exxon Mobil",
    "JNJ":   "Johnson Johnson",
    "PG":    "Procter Gamble",
    "HD":    "Home Depot",
}

# How many items to pull per ticker per source
NEWS_LIMIT = 5
REDDIT_LIMIT = 5


# ── Source 1: Financial News via Google News RSS ──────────────────────────────
def get_news() -> list[dict]:
    """Fetch recent financial news headlines for every ticker."""
    results: list[dict] = []

    for ticker, company in STOCKS.items():
        # Search Google News RSS for "<company> stock"
        url = (
            f"https://news.google.com/rss/search"
            f"?q={company.replace(' ', '+')}+stock"
            f"&hl=en-US&gl=US&ceid=US:en"
        )
        try:
            feed = feedparser.parse(url)
            for item in feed.entries[:NEWS_LIMIT]:
                title = item.get("title", "").strip()
                summary = item.get("summary", title).strip()
                # strip HTML tags from summary
                import re
                summary = re.sub(r"<[^>]+>", " ", summary)
                results.append(
                    {
                        "source": "Financial News",
                        "ticker": ticker,
                        "company": company,
                        "title": title,
                        "text": summary or title,
                        "url": item.get("link", ""),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
        except Exception as exc:
            # Non-fatal: skip this ticker if the feed fails
            print(f"[ingestion] News feed failed for {ticker}: {exc}")
            continue

    return results


# ── Source 2: Social Media via Reddit public JSON API ────────────────────────
def get_social_posts() -> list[dict]:
    """Fetch recent Reddit posts mentioning each ticker."""
    results: list[dict] = []
    headers = {"User-Agent": "FinRiskAI/1.0 (hackathon project)"}

    for ticker, company in STOCKS.items():
        # Search Reddit's public API — no key required
        url = (
            f"https://www.reddit.com/search.json"
            f"?q={ticker}&sort=new&limit={REDDIT_LIMIT}&type=link"
        )
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json()
            children = data.get("data", {}).get("children", [])
            for child in children:
                post = child.get("data", {})
                title = post.get("title", "").strip()
                body = post.get("selftext", "").strip()
                text = f"{title} {body}".strip() or title
                results.append(
                    {
                        "source": "Social Media",
                        "ticker": ticker,
                        "company": company,
                        "title": title,
                        "text": text[:600],  # cap length for NLP
                        "url": "https://reddit.com" + post.get("permalink", ""),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
        except Exception as exc:
            print(f"[ingestion] Reddit fetch failed for {ticker}: {exc}")
            continue

    return results


# ── Combined ingestion ────────────────────────────────────────────────────────
def ingest_all() -> list[dict]:
    """Return a unified list of raw items from all sources."""
    news = get_news()
    social = get_social_posts()
    print(f"[ingestion] Fetched {len(news)} news + {len(social)} social items")
    return news + social
