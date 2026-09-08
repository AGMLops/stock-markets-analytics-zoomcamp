# Homework 1 — відповіді для форми

Форма: https://courses.datatalks.club/sma-zoomcamp-2026/homework/hw01  
Дедлайн: 14 September 2026 (Mon), 22:59  

Треба залогінитись. Нижче — що клікнути в Q1–Q4 і що вставити в Q5–Q6.

Пояснення розрахунків: [homework1-answers.md](homework1-answers.md).  
Ноутбук: [homework1.ipynb](homework1.ipynb).

Цифри з прогону ноутбука (Wikipedia + Yahoo Finance, кінець серпня 2026).

---

## Q1. Which year had the highest number of additions (starting from 2020)? (2 points)

**2025**

---

## Q2. How many indexes (out of 10) have better year-to-date returns than the US (S&P 500) as of August 21, 2026? (3 points)

**2**

---

## Q3. Median drawdown (in %) of significant market corrections in the S&P 500 index (3 points)

**8**

У ноутбуці median = 7.9864%. У формі найближчий варіант — 8.

---

## Q4. Calculate the median 2-day percentage change in stock prices following positive earnings surprise days. (2 points)

**0.35**

У ноутбуці median 2-day return = 0.003528, тобто +0.3528%. У формі найближчий варіант — 0.35.

---

## Q5. Idea for your capstone project (1 point)

Вставити цей текст:

```
I want to map where the next dollar of AI-infrastructure capital expenditure actually lands. The universe has four books: (A) 50 listed global builders and buyers outside mainland China; (B) a separate 20-name China hardware/cloud book; (C) listed power companies plus the ten largest dedicated generation projects; (D) the companies behind OpenRouter Value Leaders (MiniMax, GLM/Z.ai, Kimi/Moonshot, Qwen/Alibaba, Tencent, Xiaomi, DeepSeek). Public China model labs are tracked with HK tickers (0100.HK MiniMax, 2513.HK Z.AI, plus Alibaba, Tencent, Xiaomi). The investment question is which layer is the bottleneck this quarter (GPU, HBM, power, or the model lab) and whether that sleeve is invest, hold, or underweight.
```

Деталі: [q5-ai-infra-capstone/INFRA-CAPSTONE.md](q5-ai-infra-capstone/INFRA-CAPSTONE.md)

---

## Q6. Investigate new metrics (1 point)

Вставити цей текст:

```
For the AI-infrastructure capstone I will track how the large spenders allocate capital — Microsoft (working assumption: about $20 billion of infrastructure programmes, always checked against the latest 10-Q), plus Amazon, Google, Meta, Oracle, Apple and NVIDIA — and which listed contractors receive that spend (TSMC, SK Hynix, Vertiv, Constellation, Entergy, and the rest of the Q5 books). Metrics: trailing and quarterly CapEx, CapEx/sales, CapEx/depreciation, the share labelled cloud or data-center, a spender-to-contractor map, announced GW and FID status for power projects, plus ^SOX, FRED IPB53122S / VIXCLS / T10Y2Y / FEDFUNDS, earnings-surprise 2-day returns, Wikipedia GICS, and Yahoo info valuation gates. China model labs stay in a separate book (MiniMax 0100.HK, Z.AI 2513.HK; DeepSeek and Kimi via company blogs and HKEX/news, not a price series). Python: yfinance (history, get_earnings_dates, info, cashflow), pandas_datareader for FRED after truststore.inject_into_ssl(), and pandas.read_html for Wikipedia.
```

Деталі: [q6-ai-metrics/Q6-METRICS.md](q6-ai-metrics/Q6-METRICS.md)
