# Homework 1 (2026) — answers and explanations

Submit: https://courses.datatalks.club/sma-zoomcamp-2026/homework/hw01

Spec: [../homework1.md](../homework1.md)  
Main notebook: [homework1.ipynb](homework1.ipynb)

Numbers below come from a live run of `homework1.ipynb` (Wikipedia + Yahoo Finance as of 30 Aug 2026). Re-run the notebook before submitting if you want the freshest scrape.

---

Готовий файл лише для форми (кліки + тексти Q5/Q6): [homework1-form-answers.md](homework1-form-answers.md)

## Form answers (copy these)

| Question | Answer | Notes |
|---|---|---|
| Q1 | **2025** | 18 current S&P 500 names were added in 2025 (most among full years ≥ 2020) |
| Q2 | **2** | Japan (`^N225`) and Canada (`^GSPTSE`) beat `^GSPC` YTD as of 21 Aug 2026 |
| Q3 | **7.9864** | Median drawdown (%) of S&P 500 corrections with ≥ 5% drop from ATH. Form may also accept ~**7.99** or **8** |
| Q4 | **0.003528** | Median 2-day return after **positive** AMZN Surprise %. Same as **+0.3528%** |
| Q5 | see text below | Optional free text — AI infrastructure / memory / inference capstone |
| Q6 | see text below | Optional free text — extra series + how to pull them |

---

## Question 1 — S&P 500 additions

**Prompt:** Which year had the highest number of additions (starting from 2020)?

**Answer: 2025**

### What we did

1. `GET` [List of S&P 500 companies](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies) with the homework User-Agent (Wikipedia 403s without it).
2. `pd.read_html` on the HTML. First table = current constituents (`Symbol`, `Security`, `Date added`).
3. Parse `Date added` to datetime, extract year. Missing dates = original members → skip for yearly counts.
4. Count additions by year, keep `year >= 2020`, take `idxmax()`.

This is a **survivorship** count: only names still in the index today. A ticker added in 2022 and later removed does not appear.

### Yearly counts (current members)

| Year | Additions still in the index |
|---|---|
| 2020 | 10 |
| 2021 | 10 |
| 2022 | 15 |
| 2023 | 15 |
| 2024 | 16 |
| **2025** | **18** |
| 2026 (partial) | 13 |

2026 is not a full year, so even if it later exceeds 18 it would not be the intended “full year” answer.

### Additional (not the form field)

How many current S&P 500 stocks have been in the index **more than 20 years**?

- Dated `Date added <= today − 20 years`: **224**
- Same count after treating undated original members as long-tenure: **224** (no undated rows in this scrape)

---

## Question 2 — World indexes YTD vs S&P 500

**Prompt:** How many indexes (out of 10) have better YTD returns than the US (S&P 500) as of 21 August 2026?

**Answer: 2**

### What we did

YTD return = `Close_end / Close_start − 1` using **Close** (not Adj Close).

yfinance `end` is **exclusive**, so we downloaded `start="2026-01-01"`, `end="2026-08-22"` to include 21 Aug. If 1 Jan is a holiday, first available close in range is used; last close is the last session `<= 2026-08-21`.

FX ignored (homework instruction).

### YTD results (1 Jan–21 Aug 2026)

| Index | Ticker | Start used | End used | YTD |
|---|---|---|---|---|
| Japan | `^N225` | 2026-01-05 | 2026-08-21 | **+27.36%** |
| Canada | `^GSPTSE` | 2026-01-02 | 2026-08-21 | **+14.86%** |
| United States | `^GSPC` | 2026-01-02 | 2026-08-21 | **+11.90%** |
| United Kingdom | `^FTSE` | 2026-01-02 | 2026-08-21 | +8.70% |
| Brazil | `^BVSP` | 2026-01-02 | 2026-08-21 | +6.54% |
| Germany | `^GDAXI` | 2026-01-02 | 2026-08-21 | +6.51% |
| Australia | `^AXJO` | 2026-01-02 | 2026-08-21 | +3.79% |
| Mexico | `^MXX` | 2026-01-02 | 2026-08-21 | +2.48% |
| Hong Kong | `^HSI` | 2026-01-02 | 2026-08-21 | −1.25% |
| China | `000001.SS` | 2026-01-05 | 2026-08-21 | −2.94% |
| India | `^NSEI` | 2026-01-01 | 2026-08-21 | −7.25% |

Only **Japan** and **Canada** beat the S&P 500 → **2**.

### Additional (3y / 5y / 10y ending 2026-08-21)

| Window | # of 10 that beat US | US total return |
|---|---|---|
| 3y | 2 | +74.43% |
| 5y | 2 | +71.32% |
| 10y | 1 | +251.61% |

Same short-horizon pattern (2/10) at 3y and 5y. Over 10y US dominates more (only 1/10 beats it). Local-currency, no FX hedge.

---

## Question 3 — S&P 500 corrections, median drawdown

**Prompt:** Median drawdown (in %) of significant market corrections (≥ 5% from most recent all-time high).

**Answer: 7.9864** (about **7.99%**)

### What we did

1. Daily `^GSPC` Close from 1950.
2. ATH day = Close exceeds all previous Closes (`close > close.cummax().shift(1)`; first day forced ATH).
3. For each consecutive ATH pair `(t_i, t_{i+1})`, take the min Close on `[t_i, t_{i+1})` (trough between highs, next ATH day excluded).
4. `drawdown_pct = (high − low) / high × 100`.
5. Keep `drawdown_pct >= 5`. Duration = calendar days `trough_date − ath_date`.

Used **Close**, not Adj Close (matches the homework hint table).

### Sample of corrections ≥ 5%

- Count: **74**
- Drawdown p25 / **p50** / p75: **6.23 / 7.99 / 14.02**
- Duration p25 / p50 / p75: **22 / 40.5 / 86.25** days

Typical ≥5% correction is about **8%** deep and lasts about **6 weeks** to the trough. The mean is pulled up by rare crashes; median is the right “typical dip” number.

### Top 10 vs homework hint (validation)

| ATH | Trough | Our DD | Hint DD | Days | Hint days |
|---|---|---|---|---|---|
| 2007-10-09 | 2009-03-09 | 56.78% | 56.8% | 517 | 517 |
| 2000-03-24 | 2002-10-09 | 49.15% | 49.1% | 929 | 929 |
| 1973-01-11 | 1974-10-03 | 48.20% | 48.2% | 630 | 630 |
| 1968-11-29 | 1970-05-26 | 36.06% | 36.1% | 543 | 543 |
| 2020-02-19 | 2020-03-23 | 33.92% | 33.9% | 33 | 33 |
| 1987-08-25 | 1987-12-04 | 33.51% | 33.5% | 101 | 101 |
| 1961-12-12 | 1962-06-26 | 27.97% | 28.0% | 196 | 196 |
| 1980-11-28 | 1982-08-12 | 27.11% | 27.1% | 622 | 622 |
| 2022-01-03 | 2022-10-12 | 25.43% | 25.4% | 282 | 282 |
| 1966-02-09 | 1966-10-07 | 22.18% | 22.2% | 240 | 240 |

Matches the hint list. Algorithm is correct.

---

## Question 4 — AMZN earnings surprise, 2-day return

**Prompt:** Median 2-day return after **positive** Surprise %.

**Answer: 0.003528** (**+0.3528%**)

### What we did

1. `yf.Ticker("AMZN").get_earnings_dates()` → 25 rows from 2020-10-29, including 1 future date.
2. Drop the future row with NaN Reported EPS / Surprise % → **24** reported prints.
3. Daily AMZN Close. For every 3 consecutive **trading** days `(d1, d2, d3)`: `ret = Close[d3] / Close[d1] − 1`.
4. Join earnings to `d2` (announcement session). After-close timestamps still map to that calendar session (tz stripped, date-normalized).
5. Keep `Surprise(%) > 0` → **20** events. Median of those 2-day returns.

### Results

| Metric | Value |
|---|---|
| Reported earnings rows | 24 (2020-10-29 → 2026-07-30) |
| Positive surprises with a 2-day return | 20 |
| **Median 2-day return (positive surprise)** | **+0.3528%** |
| corr(2-day return, Surprise %) — all surprises | **+0.219** |

### How to read it

Positive surprises do **not** automatically produce a large 2-day pop. Median move is only about **+35 bp**. Correlation with surprise size is **weak-positive (~0.22)**: bigger beats tend to have better 2-day returns, but a lot of the reaction is already priced or reversed.

This is why the capstone (Q5) should not use raw Surprise % alone.

---

## Question 5 — capstone idea (optional)

**Focus:** where AI-infrastructure capital actually goes — four books of names, not a five-day NVIDIA forecast.

Full company tables (tickers, layers, energy projects): [q5-ai-infra-capstone/INFRA-CAPSTONE.md](q5-ai-infra-capstone/INFRA-CAPSTONE.md)  
Same file in the Head of portfolio: [../../projects/head_of/02-ai-infra-supply-chain/INFRA-CAPSTONE.md](../../projects/head_of/02-ai-infra-supply-chain/INFRA-CAPSTONE.md)

### Form text (paste this)

I want to map where the next dollar of AI-infrastructure capital expenditure actually lands. The universe has four books: (A) 50 listed global builders and buyers outside mainland China; (B) a separate 20-name China hardware/cloud book; (C) listed power companies plus the ten largest dedicated generation projects; (D) the companies behind OpenRouter Value Leaders (MiniMax, GLM/Z.ai, Kimi/Moonshot, Qwen/Alibaba, Tencent, Xiaomi, DeepSeek). Public China model labs are tracked with HK tickers (`0100.HK` MiniMax, `2513.HK` Z.AI, plus Alibaba, Tencent, Xiaomi). The investment question is which layer is the bottleneck this quarter (GPU, HBM, power, or the model lab) and whether that sleeve is invest, hold, or underweight.

### Why this universe

A GPU is useless without HBM, a rack, cooling, and gigawatts. Watching only NVIDIA misses the dollar moving into SK Hynix, Vertiv, or Constellation. China is a second supply chain (export controls and state procurement), so it stays in its own book.

---

## Question 6 — extra metrics (optional)

Which metrics to calculate, including the spender → contractor CapEx map: [q6-ai-metrics/Q6-METRICS.md](q6-ai-metrics/Q6-METRICS.md)

### Form text (paste this)

For the AI-infrastructure capstone I will track how the large spenders allocate capital — Microsoft (working assumption: about $20 billion of infrastructure programmes, always checked against the latest 10-Q), plus Amazon, Google, Meta, Oracle, Apple and NVIDIA — and which listed contractors receive that spend (TSMC, SK Hynix, Vertiv, Constellation, Entergy, and the rest of the Q5 books). Metrics: trailing and quarterly CapEx, CapEx/sales, CapEx/depreciation, the share labelled cloud or data-center, a spender-to-contractor map, announced GW and FID status for power projects, plus `^SOX`, FRED `IPB53122S` / `VIXCLS` / `T10Y2Y` / `FEDFUNDS`, earnings-surprise 2-day returns, Wikipedia GICS, and Yahoo `info` valuation gates. China names stay in a separate book. Python: `yfinance` (`history`, `get_earnings_dates`, `info`, `cashflow`), `pandas_datareader` for FRED after `truststore.inject_into_ssl()`, and `pandas.read_html` for Wikipedia.

---

## How to re-run

```text
cohorts/2026/HW1/homework1.ipynb                          # Q1–Q4 + form summary
cohorts/2026/HW1/q5-ai-infra-capstone/INFRA-CAPSTONE.md   # Q5 company books A/B/C
cohorts/2026/HW1/q6-ai-metrics/Q6-METRICS.md              # Q6 metrics + CapEx map
projects/head_of/02-ai-infra-supply-chain/               # same Infra Capstone in the portfolio
```

Windows note: Yahoo via `yfinance` 1.7 uses `curl_cffi`. If you hit `CertificateVerifyError`, the notebooks already use a shared `curl_cffi` session with `verify=False`. FRED still needs `truststore.inject_into_ssl()` **before** `pandas_datareader`.
