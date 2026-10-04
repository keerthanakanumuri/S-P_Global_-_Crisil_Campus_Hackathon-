# FinRisk AI — Real-Time Financial Risk Intelligence & Tactical Index Rebalancing

> Converts multi-source unstructured financial information into explainable, time-sensitive risk signals and directly translates those signals into tactical portfolio decisions.

---

## Architecture

```
Financial News (Google RSS)
Social Media   (Reddit API)
        ↓
  Data Ingestion
        ↓
  Text Preprocessing
        ↓
  FinBERT Sentiment  →  Event Classifier  →  Impact Engine
        ↓
  Risk Signal Aggregation  (source confidence × recency decay)
        ↓
  Tactical Rebalancing Engine
        ↓
  Interactive Dashboard  (single-file HTML, no build step)
```

---

## Project Structure

```
finrisk-ai/
├── backend/
│   ├── main.py                  ← FastAPI app (5 endpoints)
│   ├── requirements.txt
│   ├── data/
│   │   └── stocks.csv           ← 15-stock mock S&P index
│   └── services/
│       ├── ingestion.py         ← Google News RSS + Reddit
│       ├── sentiment.py         ← FinBERT (ProsusAI/finbert)
│       ├── event_classifier.py  ← Keyword-weighted classifier
│       ├── impact.py            ← Impact score 1-10
│       ├── risk_engine.py       ← Unified NLP pipeline
│       └── rebalancer.py        ← Tactical rebalancing engine
├── frontend/
│   └── index.html               ← Complete dashboard (CDN only)
├── data/
│   └── demo_signals.json        ← 30 pre-built demo signals
├── start.bat                    ← One-click Windows launcher
└── README.md
```

---

## Quick Start (Windows)

### Option 1 — One-click launcher
```
Double-click  start.bat
```
This creates the virtual environment, installs dependencies, and starts the backend automatically.

### Option 2 — Manual setup

**Step 1 — Backend**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Step 2 — Frontend**

Open `frontend/index.html` directly in any browser.  
No build step. No npm. No Node.js required.

---

## API Endpoints

| Method | Endpoint    | Description                                      |
|--------|-------------|--------------------------------------------------|
| GET    | `/`         | Health check                                     |
| GET    | `/ingest`   | Fetch live data + run full NLP pipeline          |
| GET    | `/signals`  | Return latest processed risk signals             |
| GET    | `/rebalance`| Return rebalanced portfolio weights              |
| GET    | `/summary`  | Aggregate market-level statistics                |
| GET    | `/demo`     | Load pre-built demo signals (offline fallback)   |

---

## NLP Risk Engine — Output Schema

```json
{
  "ticker":           "NVDA",
  "company":          "NVIDIA",
  "source":           "Financial News",
  "sentiment_label":  "negative",
  "sentiment_score":  -0.88,
  "event_type":       "Geopolitical",
  "impact_score":     9,
  "risk_level":       "Critical",
  "source_confidence": 1.0
}
```

### Sentiment Score
- Range: **-1.0 to +1.0**
- Model: **FinBERT** (ProsusAI/finbert)
- Negative = bearish, Positive = bullish, ~0 = neutral

### Event Classification
| Label | Description |
|---|---|
| Geopolitical | Wars, sanctions, trade restrictions |
| Macroeconomic | Fed rates, inflation, GDP, recession |
| Credit Event | Defaults, downgrades, bankruptcy |
| Merger/Acquisition | M&A, buyouts, IPOs |
| Product Launch | New products, AI breakthroughs |
| Earnings | Revenue, EPS, guidance |
| General Market | Uncategorised |

### Impact Score
| Range | Level |
|---|---|
| 1–3 | Low |
| 4–5 | Medium |
| 6–7 | High |
| 8–10 | Critical |

---

## Rebalancing Logic

```
Signal Score  =  Sentiment × Source Confidence × Recency Weight
Risk-Adjusted =  Signal Score × (1 − Impact / 15)
New Weight    =  Base Weight × (1 + Risk-Adjusted)
              → clamp [2%, 12%]
              → normalize to sum = 100%

Action:
  New Weight > Base × 1.05  →  INCREASE
  New Weight < Base × 0.95  →  REDUCE
  otherwise                 →  HOLD
```

**Source confidence weights:**
- Financial News → 1.0
- Social Media   → 0.6

**Recency decay:**
- < 1 hour  → 1.00
- 1–6 hours → 0.85
- 6–12 hours → 0.65
- 12–24 hours → 0.40

---

## Data Sources

| Source | Type | API |
|---|---|---|
| Google News RSS | Financial News | Free, no key |
| Reddit Search API | Social Media | Free, no key |
| demo_signals.json | Offline fallback | Bundled |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| NLP | FinBERT (HuggingFace Transformers), PyTorch |
| Data | Pandas, NumPy, Feedparser, Requests |
| Frontend | Vanilla JS, Tailwind CSS CDN, Chart.js CDN |
| Storage | In-memory (session state) |

---

## Demo Mode

If live APIs are unavailable during the presentation:

1. Click **📂 Demo Mode** in the dashboard
2. 30 pre-built realistic signals load instantly
3. Full dashboard, charts, and rebalancing work offline

---

## Submission Checklist

- [x] Two data sources (Financial News + Social Media)
- [x] Sentiment Score (−1.0 to +1.0, FinBERT)
- [x] Event Classification (7 categories)
- [x] Impact Score (1–10)
- [x] Structured JSON/API output
- [x] 15-stock mock index (S&P 100 subset)
- [x] Positive sentiment → INCREASE weight
- [x] Negative sentiment → REDUCE weight
- [x] Portfolio weights sum to ~100%
- [x] Dashboard visualises changing weights
- [x] Explainability panel per signal
- [x] Demo fallback mode
- [x] Single-file frontend (no build step)

---

## Live Demo Script (5 minutes)

| Time | Action |
|---|---|
| 0:00–0:30 | Explain the problem: unstructured news → portfolio risk |
| 0:30–1:15 | Click **Run Live Analysis** — show signals loading |
| 1:15–2:00 | Click **Explain ↗** on NVDA — show sentiment, event, impact |
| 2:00–3:00 | Show event chart + sentiment distribution |
| 3:00–4:00 | Click **Rebalance Portfolio** — show before/after weights |
| 4:00–4:40 | Show weight comparison bar chart |
| 4:40–5:00 | Closing: "End-to-end: unstructured text → portfolio action" |
