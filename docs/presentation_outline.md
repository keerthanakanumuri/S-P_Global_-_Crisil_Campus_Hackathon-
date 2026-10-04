# FinRisk AI — 7-Slide Presentation Outline
### S&P Global & Crisil Campus Hackathon 2026

> Use this as the exact content when building your PDF deck.  
> Tool: Google Slides / PowerPoint / Canva → Export as `presentation.pdf` → place in `docs/`

---

## SLIDE 1 — Title

**Title:** FinRisk AI  
**Subtitle:** Real-Time Financial Risk Intelligence & Tactical Index Rebalancing

**Candidate:** Keerthana Kanumuri  
**College:** [Your College Name]  
**Hackathon:** S&P Global & Crisil Campus Hackathon 2026  

*Visual suggestion: dark background (#0a0f1e), cyan accent title, simple clean layout*

---

## SLIDE 2 — Problem & Approach

**Title:** Financial Markets Are Information-Rich but Signal-Poor

**Problem (left panel):**
- Millions of financial articles + social posts generated daily
- Converting unstructured text → portfolio decisions is manual and slow
- Risk analysts spend hours reading before any action is taken
- Single articles can cause overreaction; aggregation is rarely done systematically

**Approach (right panel):**
```
Unstructured Text (News + Social)
           ↓
   AI/NLP Risk Engine
           ↓
  Sentiment + Event + Impact
           ↓
  Aggregated Risk Signals
           ↓
  Automatic Portfolio Action
```

**Key insight:** The gap is not data — it's structured signal extraction at speed.

---

## SLIDE 3 — System Design

**Title:** End-to-End Architecture

*Embed the architecture diagram: `docs/architecture.svg`*

**Callout boxes to highlight:**
- **2 data sources:** Google News RSS (confidence 1.0×) + Reddit API (confidence 0.6×)
- **3 NLP outputs per signal:** Sentiment Score · Event Type · Impact Score
- **1 rebalancing decision per stock:** INCREASE / HOLD / REDUCE
- **Recency decay:** signals lose weight over 24 hours (1.0 → 0.2×)
- **Zero external paid APIs** — fully reproducible

---

## SLIDE 4 — Implementation Highlights

**Title:** Key Modules & Technical Choices

| Module | Technology | Why |
|---|---|---|
| Sentiment Analysis | FinBERT (ProsusAI/finbert) | Financial-domain BERT — outperforms generic models on financial text |
| Event Classification | Weighted keyword rules | Fast, explainable, no training data required, 7 categories |
| Impact Scoring | Formula-based (sentiment + event + keywords) | Transparent, auditable, no black-box |
| Risk Aggregation | Source confidence × recency decay | Reduces noise from unreliable/stale social signals |
| API | FastAPI (Python) | Auto-docs, async, production-ready |
| Dashboard | Vanilla JS + Tailwind + Chart.js (CDN) | Zero build step — opens directly in browser during demo |

**Key differentiator:** Every portfolio action is **explainable** — the dashboard shows exactly why a weight changed (sentiment score, event type, source, recency).

---

## SLIDE 5 — Key Results

**Title:** From 30 Signals to Tactical Portfolio Actions

**Output sample (show as a table or cards):**

| Ticker | Event | Sentiment | Impact | Action |
|---|---|---|---|---|
| NVDA | Geopolitical | −0.88 | 9 / 10 | ▼ REDUCE 6.67% → 5.59% |
| MSFT | Earnings | +0.91 | 7 / 10 | ▲ INCREASE 6.67% → 8.73% |
| JPM | Credit Event | −0.72 | 8 / 10 | ▼ REDUCE 6.67% → 4.71% |
| TSLA | Product Launch | +0.83 | 6 / 10 | ▲ INCREASE 6.67% → 8.70% |
| PG | Earnings | +0.04 | 3 / 10 | — HOLD 6.67% → 6.37% |

**Portfolio metrics:**
- 30 signals processed · 15 stocks analysed · 6 event categories detected
- Market risk score: 5.1 / 10 · 5 Critical events · 14 High/Critical combined
- Portfolio weights: sum = 100% · all within [2%, 12%] constraints

*Visual: show the weight comparison bar chart screenshot from the dashboard*

---

## SLIDE 6 — Domain Impact

**Title:** Why This Matters for Financial Risk Management

**Use case relevance:**
- **S&P Global / Crisil context:** Index providers and credit rating agencies continuously monitor news for events that affect risk ratings and index compositions. FinRisk AI automates the first layer of that monitoring.
- **Speed advantage:** Sub-second signal generation vs. hours of manual analyst work
- **Consistency:** FinBERT removes human sentiment bias; the same news item always produces the same score
- **Auditability:** Every decision trace is logged (score + event + source + timestamp)
- **Scalability:** Extend from 15 stocks to 500+ with no architectural changes

**Business value chain:**
```
Real-world event
      ↓
News published (minutes)
      ↓
FinRisk AI detects + classifies (seconds)
      ↓
Risk signal generated + portfolio adjusted (seconds)
      ↓
Human analyst reviews explainable output (minutes)
```
vs. traditional: event → news → analyst reads → meeting → decision (hours/days)

---

## SLIDE 7 — Limitations & Next Steps

**Title:** Current Assumptions, Gaps & Future Work

**Current limitations:**
- Rebalancing formula is simplified — no transaction costs, no liquidity constraints
- Event classifier uses keyword rules — a fine-tuned classifier would be more robust on ambiguous text
- In-memory state — signals reset on server restart (no persistent database)
- 15 stocks only — S&P 500 coverage would require rate-limit management for live APIs
- Reddit as social proxy — Twitter/X API or Bloomberg Terminal would give better signal quality

**Next steps (if more time):**
1. Replace keyword event classifier with a fine-tuned zero-shot NLP model
2. Add SQLite/PostgreSQL persistence for signal history and backtesting
3. Integrate yfinance for real price data to measure actual portfolio P&L impact
4. Add Module B (stress testing) to complement the rebalancing module
5. Deploy backend to Render + frontend to Vercel for a fully live public URL
6. Add WebSocket support for true real-time dashboard updates without polling

---

## Presentation Tips

- Keep each slide to **1 key message**
- Use the dashboard **screenshots** on slides 5 and 6
- On slide 3, **embed the SVG diagram** — it renders clearly at any size
- Total talk time per slide (5-minute pitch): ~40 seconds per slide
- For live demo: have the backend running before you start presenting
