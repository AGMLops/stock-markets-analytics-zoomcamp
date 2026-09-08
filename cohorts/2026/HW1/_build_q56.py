"""Build standalone Q5 / Q6 project notebooks. Run once."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def md(s: str) -> dict:
    lines = s.split("\n")
    source = [line + "\n" for line in lines[:-1]]
    if lines:
        source.append(lines[-1] + "\n")
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code(s: str) -> dict:
    lines = s.split("\n")
    source = [line + "\n" for line in lines[:-1]]
    if lines:
        source.append(lines[-1] + "\n")
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def write_nb(path: Path, cells: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.14.0"},
        },
        "cells": cells,
    }
    path.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print("Wrote", path, "cells=", len(cells))


# ---------------------------------------------------------------------------
# Q5
# ---------------------------------------------------------------------------
q5 = []
q5.append(
    md(
        """# Q5 project — AI infrastructure / Memory / Inference capstone

Standalone notebook (does **not** depend on `homework1.ipynb`).

**Thesis:** week-ahead *direction* model for listed names that build AI factories,
ship DRAM/HBM, or run inference — not a generic S&P 500 screen.

**Sleeves**
- **AI infrastructure** — GPUs, custom ASICs, foundry, equipment, racks, power, networking
- **Memory / RAM** — DRAM, HBM, NAND (the attach bottleneck)
- **Inference** — custom silicon, interconnect, hyperscalers that spend on serving tokens

**Target:** `1` if `Close[t+5] > Close[t]`, else `0`. Horizon = 5 trading days.

This notebook also builds a leakage-safe panel, trains baseline classifiers with
chronological validation, and evaluates a cost-aware long-only portfolio.
"""
    )
)
q5.append(md("## Setup"))
q5.append(
    code(
        """# SSL first, then HTTPS clients. Own kernel — run this cell first.
%pip install yfinance pandas matplotlib requests truststore curl_cffi pandas-datareader scikit-learn

import truststore
truststore.inject_into_ssl()

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import yfinance as yf
from curl_cffi import requests as curl_requests
import pandas_datareader as pdr
import matplotlib.pyplot as plt

yf_session = curl_requests.Session(impersonate="chrome", verify=False)
pd.set_option("display.float_format", lambda x: f"{x:,.4f}")
print("setup ok")
"""
    )
)
q5.append(md("## Universe (three sleeves)"))
q5.append(
    code(
        """UNIVERSE = [
    # AI infrastructure: compute, foundry, equipment, racks, power, networking
    {"ticker": "NVDA", "name": "NVIDIA", "segment": "AI infrastructure"},
    {"ticker": "AVGO", "name": "Broadcom", "segment": "AI infrastructure"},
    {"ticker": "AMD", "name": "AMD", "segment": "AI infrastructure"},
    {"ticker": "TSM", "name": "TSMC", "segment": "AI infrastructure"},
    {"ticker": "ASML", "name": "ASML", "segment": "AI infrastructure"},
    {"ticker": "AMAT", "name": "Applied Materials", "segment": "AI infrastructure"},
    {"ticker": "SMCI", "name": "Super Micro", "segment": "AI infrastructure"},
    {"ticker": "VRT", "name": "Vertiv", "segment": "AI infrastructure"},
    {"ticker": "ANET", "name": "Arista", "segment": "AI infrastructure"},
    # Memory / RAM / HBM / NAND
    {"ticker": "MU", "name": "Micron", "segment": "Memory / RAM"},
    {"ticker": "WDC", "name": "Western Digital", "segment": "Memory / RAM"},
    {"ticker": "SNDK", "name": "Sandisk", "segment": "Memory / RAM"},
    {"ticker": "000660.KS", "name": "SK Hynix", "segment": "Memory / RAM"},
    {"ticker": "005930.KS", "name": "Samsung Electronics", "segment": "Memory / RAM"},
    # Inference: custom silicon, interconnect, hyperscalers
    {"ticker": "MRVL", "name": "Marvell", "segment": "Inference"},
    {"ticker": "ARM", "name": "Arm Holdings", "segment": "Inference"},
    {"ticker": "ALAB", "name": "Astera Labs", "segment": "Inference"},
    {"ticker": "CRDO", "name": "Credo", "segment": "Inference"},
    {"ticker": "GOOGL", "name": "Alphabet", "segment": "Inference"},
    {"ticker": "MSFT", "name": "Microsoft", "segment": "Inference"},
    {"ticker": "AMZN", "name": "Amazon", "segment": "Inference"},
    {"ticker": "META", "name": "Meta", "segment": "Inference"},
]

meta = pd.DataFrame(UNIVERSE).set_index("ticker")
print(meta.groupby("segment").size())
meta
"""
    )
)
q5.append(md("## Download prices + build sleeve indexes"))
q5.append(
    code(
        """TICKERS = list(meta.index) + ["^GSPC", "^SOX"]
raw = yf.download(
    TICKERS,
    start="2023-01-01",
    end="2026-08-22",
    auto_adjust=False,
    group_by="ticker",
    threads=True,
    session=yf_session,
    progress=False,
)

closes = {}
for t in TICKERS:
    try:
        s = raw[t]["Close"].dropna()
    except Exception:
        s = pd.Series(dtype=float)
    if getattr(s.index, "tz", None) is not None:
        s.index = s.index.tz_localize(None)
    if s.empty:
        print("EMPTY", t)
        continue
    closes[t] = s

px = pd.DataFrame(closes).sort_index()
px = px.loc[: pd.Timestamp("2026-08-21")]
volumes = {}
for t in TICKERS:
    try:
        s = raw[t]["Volume"].dropna()
    except Exception:
        s = pd.Series(dtype=float)
    if getattr(s.index, "tz", None) is not None:
        s.index = s.index.tz_localize(None)
    volumes[t] = s.loc[: pd.Timestamp("2026-08-21")]
print("price panel", px.shape, px.index.min().date(), "->", px.index[-1].date())
print("missing shares:", sorted(set(TICKERS) - set(px.columns)))
"""
    )
)
q5.append(
    code(
        """def period_ret(s, start, end):
    w = s.loc[start:end].dropna()
    if len(w) < 2:
        return np.nan
    return float(w.iloc[-1] / w.iloc[0] - 1)


end = px.index.max()
ytd_start = pd.Timestamp("2026-01-01")
y1_start = end - pd.DateOffset(years=1)

rows = []
for t in meta.index:
    if t not in px.columns:
        continue
    s = px[t]
    w = s.dropna()
    peak = w.cummax()
    mdd = float(((w / peak) - 1).min())
    rows.append(
        {
            "ticker": t,
            "name": meta.loc[t, "name"],
            "segment": meta.loc[t, "segment"],
            "ytd": period_ret(s, ytd_start, end),
            "ret_1y": period_ret(s, y1_start, end),
            "max_dd": mdd,
            "last_close": float(w.iloc[-1]),
        }
    )

stats = pd.DataFrame(rows).set_index("ticker")
spx_ytd = period_ret(px["^GSPC"], ytd_start, end)
spx_1y = period_ret(px["^GSPC"], y1_start, end)
stats["ytd_vs_spx"] = stats["ytd"] - spx_ytd
stats["ret_1y_vs_spx"] = stats["ret_1y"] - spx_1y

print(f"S&P 500 YTD {spx_ytd:.2%} | 1y {spx_1y:.2%} | end {end.date()}")
print("\\nSleeve medians")
print(stats.groupby("segment")[["ytd", "ret_1y", "max_dd"]].median())
stats.sort_values(["segment", "ytd"], ascending=[True, False])
"""
    )
)
q5.append(md("## Equal-weight sleeves vs S&P 500"))
q5.append(
    code(
        """norm = px.dropna(how="all")
# rebase each name to 100 at first valid print, then equal-weight inside sleeve
sleeve_nav = {}
for seg, tickers in meta.groupby("segment").groups.items():
    panel = norm[list(tickers)].copy()
    rebased = panel / panel.apply(lambda s: s.dropna().iloc[0])
    sleeve_nav[seg] = rebased.mean(axis=1) * 100
sleeve_nav["S&P 500"] = norm["^GSPC"] / norm["^GSPC"].dropna().iloc[0] * 100
nav = pd.DataFrame(sleeve_nav)

ax = nav.plot(figsize=(10, 5), title="Equal-weight sleeves vs S&P 500 (rebased=100)")
ax.set_ylabel("Index")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print("Total return since first common start:")
print((nav.iloc[-1] / nav.iloc[0] - 1).sort_values(ascending=False))
"""
    )
)
q5.append(md("## Cross-section: who is the bottleneck this year?"))
q5.append(
    code(
        """fig, axes = plt.subplots(1, 2, figsize=(12, 5))
order = stats.sort_values("ytd")
colors = {
    "AI infrastructure": "#1f77b4",
    "Memory / RAM": "#ff7f0e",
    "Inference": "#2ca02c",
}
bar_c = order["segment"].map(colors)
order["ytd"].plot.barh(ax=axes[0], color=bar_c, title="YTD return by name")
axes[0].axvline(spx_ytd, color="black", ls="--", lw=1, label="S&P 500")
axes[0].legend()
order["max_dd"].plot.barh(ax=axes[1], color=bar_c, title="Max drawdown (2023→now)")
plt.tight_layout()
plt.show()

print("Beat S&P 500 YTD:", int((stats["ytd"] > spx_ytd).sum()), "/", len(stats))
print(stats.sort_values("ytd", ascending=False)[["name", "segment", "ytd", "ytd_vs_spx"]].head(8))
"""
    )
)
q5.append(md("## Correlation — concentration risk"))
q5.append(
    code(
        """rets = px.pct_change()
core = [t for t in ["NVDA", "MU", "SKH", "000660.KS", "AVGO", "VRT", "MRVL", "GOOGL", "^GSPC"] if t in rets.columns]
# label SK Hynix
rename = {"000660.KS": "SK Hynix", "^GSPC": "SPX"}
corr = rets[core].corr().rename(index=rename, columns=rename)
print(corr.round(2))

# 5-day direction hit rate (naive: yesterday's sign predicts next 5d) — baseline only
fwd = px.shift(-5) / px - 1
hit = {}
for t in stats.index:
    y = (fwd[t] > 0).astype(float)
    hit[t] = float(y.mean())
print("\\nUnconditional P(up in 5d) — baseline a classifier must beat")
print(pd.Series(hit).sort_values(ascending=False).head(10))
"""
    )
)
q5.append(md("## Model-ready panel: Q6 metrics with point-in-time lags"))
q5.append(
    code(
        """# Q6 sources become model inputs here. Observation values are lagged
# before joining to prices, avoiding same-day publication look-ahead.
def fred_daily(series_id, lag_days):
    try:
        s = pdr.DataReader(series_id, "fred", start="2018-01-01")[series_id]
        s.index = pd.to_datetime(s.index).tz_localize(None)
        idx = s.index.union(px.index).sort_values()
        return s.reindex(idx).ffill().reindex(px.index).shift(lag_days)
    except Exception as exc:
        print(f"FRED unavailable for {series_id}: {exc}")
        return pd.Series(np.nan, index=px.index)


macro = pd.DataFrame(index=px.index)
macro["vix"] = fred_daily("VIXCLS", 1)
macro["curve_10y2y"] = fred_daily("T10Y2Y", 1)
macro["fedfunds"] = fred_daily("FEDFUNDS", 21)
macro["semi_ip"] = fred_daily("IPB53122S", 21)
macro["vix_change_5d"] = macro["vix"].pct_change(5)
macro["curve_change_20d"] = macro["curve_10y2y"].diff(20)
macro["semi_ip_yoy"] = macro["semi_ip"].pct_change(252)


def event_features(ticker):
    event = pd.Series(0.0, index=px.index)
    surprise = pd.Series(np.nan, index=px.index)
    try:
        earnings = yf.Ticker(ticker, session=yf_session).get_earnings_dates()
        earnings = earnings.dropna(subset=["Reported EPS", "Surprise(%)"])
        dates = pd.to_datetime(earnings.index)
        if getattr(dates, "tz", None) is not None:
            dates = dates.tz_localize(None)
        for dt, value in zip(dates.normalize(), earnings["Surprise(%)"]):
            sessions = px.index[px.index >= dt]
            if len(sessions):
                event.loc[sessions[0]] = 1.0
                surprise.loc[sessions[0]] = float(value)
    except Exception as exc:
        print(f"Earnings unavailable for {ticker}: {exc}")
    return event.shift(1).fillna(0), surprise.ffill().shift(1)


feature_rows = []
for ticker in meta.index:
    if ticker not in px:
        continue
    close = px[ticker].astype(float)
    ret = close.pct_change()
    volume = volumes.get(ticker, pd.Series(index=px.index, dtype=float)).reindex(px.index)
    event_lag, surprise_last = event_features(ticker)
    row = pd.DataFrame(index=px.index)
    row["ticker"] = ticker
    row["segment"] = meta.loc[ticker, "segment"]
    row["ret_1d"] = ret
    row["ret_5d"] = close.pct_change(5)
    row["ret_20d"] = close.pct_change(20)
    row["ret_60d"] = close.pct_change(60)
    row["vol_20d"] = ret.rolling(20).std()
    row["vol_60d"] = ret.rolling(60).std()
    row["ma20_gap"] = close / close.rolling(20).mean() - 1
    row["ma50_gap"] = close / close.rolling(50).mean() - 1
    row["ma200_gap"] = close / close.rolling(200).mean() - 1
    row["volume_z20"] = (volume - volume.rolling(20).mean()) / volume.rolling(20).std()
    row["rel_spx_20d"] = row["ret_20d"] - px["^GSPC"].pct_change(20)
    row["rel_sox_20d"] = row["ret_20d"] - px["^SOX"].pct_change(20)
    row["sox_ret_5d"] = px["^SOX"].pct_change(5)
    row["sox_ret_20d"] = px["^SOX"].pct_change(20)
    row["earnings_event_lag1"] = event_lag
    row["earnings_surprise_last"] = surprise_last
    for col in macro:
        row[col] = macro[col]
    for segment in meta["segment"].unique():
        key = "segment_" + segment.lower().replace(" / ", "_").replace(" ", "_")
        row[key] = float(meta.loc[ticker, "segment"] == segment)
    future_close = close.dropna().shift(-5)
    row["target_return_5d"] = future_close.reindex(px.index) / close - 1
    row["target"] = (row["target_return_5d"] > 0).astype(float)
    feature_rows.append(row.reset_index(names="date"))

dataset = pd.concat(feature_rows, ignore_index=True).sort_values(["date", "ticker"])
feature_cols = [
    "ret_1d", "ret_5d", "ret_20d", "ret_60d", "vol_20d", "vol_60d",
    "ma20_gap", "ma50_gap", "ma200_gap", "volume_z20", "rel_spx_20d",
    "rel_sox_20d", "sox_ret_5d", "sox_ret_20d", "vix", "vix_change_5d",
    "curve_10y2y", "curve_change_20d", "fedfunds", "semi_ip_yoy",
    "earnings_event_lag1", "earnings_surprise_last",
    "segment_ai_infrastructure", "segment_memory_ram", "segment_inference",
]
dataset[feature_cols] = dataset[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
dataset = dataset.dropna(subset=["target_return_5d"])
print("model panel", dataset.shape, "features", len(feature_cols))
"""
    )
)
q5.append(md("## Walk-forward training and five-day portfolio backtest"))
q5.append(
    code(
        """from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

train = dataset[dataset["date"] < "2025-01-01"]
valid = dataset[(dataset["date"] >= "2025-01-01") & (dataset["date"] < "2026-01-01")]
test = dataset[dataset["date"] >= "2026-01-01"].copy()
X_train, y_train = train[feature_cols], train["target"].astype(int)
X_valid, y_valid = valid[feature_cols], valid["target"].astype(int)
X_test, y_test = test[feature_cols], test["target"].astype(int)

models = {
    "logistic": make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=1000, random_state=42)),
    "hist_gradient_boosting": HistGradientBoostingClassifier(
        max_iter=150, learning_rate=0.05, max_leaf_nodes=15,
        l2_regularization=1.0, random_state=42,
    ),
}

def scores(y_true, probability):
    prediction = (probability >= 0.5).astype(int)
    return {
        "accuracy": accuracy_score(y_true, prediction),
        "balanced_accuracy": balanced_accuracy_score(y_true, prediction),
        "roc_auc": roc_auc_score(y_true, probability),
        "brier": brier_score_loss(y_true, probability),
    }


validation_rows = []
for name, candidate in models.items():
    candidate.fit(X_train, y_train)
    validation_rows.append({"model": name, **scores(y_valid, candidate.predict_proba(X_valid)[:, 1])})
baseline = DummyClassifier(strategy="prior").fit(X_train, y_train)
validation_rows.append({"model": "prior_baseline", **scores(y_valid, baseline.predict_proba(X_valid)[:, 1])})
validation_results = pd.DataFrame(validation_rows).sort_values("roc_auc", ascending=False)
print("Validation results")
print(validation_results.round(4).to_string(index=False))

best_name = validation_results.loc[validation_results["model"] != "prior_baseline", "model"].iloc[0]
selected = clone(models[best_name])
selected.fit(pd.concat([X_train, X_valid]), pd.concat([y_train, y_valid]))
test["probability"] = selected.predict_proba(X_test)[:, 1]
test["prediction"] = (test["probability"] >= 0.5).astype(int)
print(f"Selected model: {best_name}")
print("Test results", {k: round(v, 4) for k, v in scores(y_test, test["probability"]).items()})


def portfolio_metrics(returns):
    nav = (1 + returns).cumprod()
    return {
        "total_return": nav.iloc[-1] - 1,
        "annualized_sharpe": np.sqrt(52) * returns.mean() / returns.std() if returns.std() else np.nan,
        "max_drawdown": (nav / nav.cummax() - 1).min(),
        "hit_rate": (returns > 0).mean(),
    }


portfolio_rows, previous_weights = [], {}
for dt in sorted(test["date"].unique())[::5]:
    day = test[test["date"] == dt].sort_values("probability", ascending=False)
    chosen, counts = [], {}
    for _, candidate in day.iterrows():
        sleeve = candidate["segment"]
        if counts.get(sleeve, 0) >= 2:
            continue
        chosen.append(candidate)
        counts[sleeve] = counts.get(sleeve, 0) + 1
        if len(chosen) == 6:
            break
    if not chosen:
        continue
    weights = {r["ticker"]: 1 / len(chosen) for r in chosen}
    turnover = sum(abs(weights.get(t, 0) - previous_weights.get(t, 0)) for t in set(weights) | set(previous_weights))
    gross = np.mean([r["target_return_5d"] for r in chosen])
    benchmark = day["target_return_5d"].mean()
    portfolio_rows.append({
        "date": dt, "gross_return": gross, "net_return": gross - 0.001 * turnover,
        "benchmark_return": benchmark, "turnover": turnover,
        "selected": ",".join(r["ticker"] for r in chosen),
    })
    previous_weights = weights

portfolio = pd.DataFrame(portfolio_rows).set_index("date")
print("Portfolio metrics after 10 bp turnover cost")
print(pd.DataFrame({
    "model_portfolio": portfolio_metrics(portfolio["net_return"]),
    "equal_weight_universe": portfolio_metrics(portfolio["benchmark_return"]),
}).round(4))
print("Average turnover:", round(portfolio["turnover"].mean(), 4))
print(portfolio.tail(10).to_string())
"""
    )
)
q5.append(md("## Capstone write-up (Q5 answer)"))
q5.append(
    code(
        """print('''Q5 ANSWER
I want a week-ahead direction model for AI-infrastructure, memory/RAM, and inference
equities — not a generic large-cap screen.

Sleeves
  AI infrastructure: NVDA, AVGO, AMD, TSM, ASML, AMAT, SMCI, VRT, ANET
  Memory / RAM:      MU, WDC, SNDK, SK Hynix (000660.KS), Samsung (005930.KS)
  Inference:         MRVL, ARM, ALAB, CRDO, GOOGL, MSFT, AMZN, META

Target: Close[t+5] > Close[t]. Features from yfinance (returns, trend, volatility,
volume, SOX relative strength), FRED regime (FEDFUNDS, T10Y2Y, VIXCLS, semiconductor IP),
and lagged earnings events. Train regularized classifiers on the pooled panel with
sleeve dummies, use chronological validation, and simulate a long-only book with
sleeve caps and turnover costs.

Why: GPU attach is HBM-constrained, racks are power-constrained, inference is
ASIC/interconnect-constrained. Watching only NVDA misses the rotating bottleneck.
''')
print("\\nLive scoping snapshot")
print(f"  S&P 500 YTD: {spx_ytd:.2%}")
print(stats.groupby("segment")["ytd"].median().rename("median YTD"))
"""
    )
)

write_nb(ROOT / "q5-ai-infra-capstone" / "q5_ai_infra_capstone.ipynb", q5)


# ---------------------------------------------------------------------------
# Q6
# ---------------------------------------------------------------------------
q6 = []
q6.append(
    md(
        """# Q6 project — extra metrics for the AI / memory / inference book

Standalone notebook (does **not** depend on `homework1.ipynb` or the Q5 notebook).

**Job:** pull 4–5 series that the Q5 capstone actually needs, say *why*, and show the Python path.

| Metric | Source | Why |
|---|---|---|
| `^SOX` PHLX Semiconductor | yfinance | Cycle benchmark vs single-stock beta |
| `IPB53122S` semi industrial production | FRED | Real output, not just price |
| `VIXCLS`, `T10Y2Y`, `FEDFUNDS` | FRED | Vol / curve / policy regime |
| Earnings surprise + 2-day return | yfinance `get_earnings_dates` | Event features (same recipe as HW1 Q4) |
| Wikipedia GICS + Date added | Wikipedia | Sleeve dummies, index-inclusion flow |
| Yahoo `info` snapshot | yfinance | Forward PE / margin / mkt-cap gates |
"""
    )
)
q6.append(md("## Setup"))
q6.append(
    code(
        """%pip install yfinance pandas pandas-datareader lxml beautifulsoup4 requests truststore curl_cffi matplotlib

import truststore
truststore.inject_into_ssl()

import warnings
warnings.filterwarnings("ignore")

import requests
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader as pdr
from curl_cffi import requests as curl_requests
from io import StringIO
import matplotlib.pyplot as plt

# FRED: pandas_datareader opens its own Session — inject a post-truststore session.
_orig = pdr.DataReader

def DataReader(name, data_source, start=None, end=None, **kwargs):
    if data_source == "fred" and "session" not in kwargs:
        kwargs["session"] = requests.Session()
    return _orig(name, data_source, start=start, end=end, **kwargs)

pdr.DataReader = DataReader

yf_session = curl_requests.Session(impersonate="chrome", verify=False)
pd.set_option("display.float_format", lambda x: f"{x:,.4f}")
print("setup ok")
"""
    )
)
q6.append(md("## 1. Cycle: `^SOX` vs NVDA / MU / SK Hynix"))
q6.append(
    code(
        """cycle_tickers = ["^SOX", "NVDA", "MU", "000660.KS", "AVGO", "^GSPC"]
raw = yf.download(
    cycle_tickers,
    start="2023-01-01",
    end="2026-08-22",
    auto_adjust=False,
    group_by="ticker",
    threads=True,
    session=yf_session,
    progress=False,
)

def close_of(t):
    s = raw[t]["Close"].dropna()
    if getattr(s.index, "tz", None) is not None:
        s.index = s.index.tz_localize(None)
    return s.loc[: pd.Timestamp("2026-08-21")]

cycle = pd.DataFrame({t: close_of(t) for t in cycle_tickers}).dropna(how="all")
cycle = cycle.rename(columns={"000660.KS": "SK Hynix", "^SOX": "SOX", "^GSPC": "SPX"})
rebased = cycle / cycle.apply(lambda s: s.dropna().iloc[0]) * 100
ax = rebased.plot(figsize=(10, 5), title="SOX vs AI / memory names (rebased=100)")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print("corr of daily returns")
print(cycle.pct_change().corr().round(2))
print("\\nYTD 2026")
ytd = cycle.loc["2026-01-01":]
print((ytd.iloc[-1] / ytd.apply(lambda s: s.dropna().iloc[0]) - 1).sort_values(ascending=False))
"""
    )
)
q6.append(md("## 2. FRED regime + semiconductor industrial production"))
q6.append(
    code(
        """fred_ids = {
    "VIXCLS": "VIX",
    "T10Y2Y": "10y-2y spread",
    "FEDFUNDS": "Fed funds",
    "IPB53122S": "Semi industrial production",
}
fred = pd.concat(
    {lab: pdr.DataReader(sid, "fred", start="2018-01-01")[sid] for sid, lab in fred_ids.items()},
    axis=1,
)
print(fred.tail(8))
print("\\nlatest")
print(fred.dropna(how="all").iloc[-1])

fig, axes = plt.subplots(4, 1, figsize=(10, 9), sharex=True)
for ax, col in zip(axes, fred.columns):
    fred[col].plot(ax=ax, title=col)
    ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print('''WHY
  VIX            — change size when vol spikes (AI names are high-beta).
  T10Y2Y         — inverted curve historically precedes risk-off in cyclicals/semis.
  FEDFUNDS       — discount-rate regime for long-duration AI winners.
  IPB53122S      — real chip output. If prices run and IP stalls, squeeze risk.
''')
"""
    )
)
q6.append(md("## 3. Earnings surprise + 2-day return (NVDA, MU, AVGO, AMD)"))
q6.append(
    code(
        """def two_day_after_earnings(ticker: str) -> pd.DataFrame:
    obj = yf.Ticker(ticker, session=yf_session)
    earn = obj.get_earnings_dates().copy()
    earn = earn.dropna(subset=["Reported EPS", "Surprise(%)"])
    px = obj.history(period="max", auto_adjust=False)
    if getattr(px.index, "tz", None) is not None:
        px.index = px.index.tz_localize(None)
    closes = px["Close"]
    ret_2d = closes.shift(-1) / closes.shift(1) - 1
    earn.index = pd.to_datetime(earn.index)
    if getattr(earn.index, "tz", None) is not None:
        earn.index = earn.index.tz_localize(None)
    earn.index = earn.index.normalize()
    earn = earn[~earn.index.duplicated(keep="first")]
    earn["ret_2d"] = ret_2d.reindex(earn.index)
    missing = earn["ret_2d"].isna()
    for dt in earn.index[missing]:
        later = closes.index[closes.index >= dt]
        if len(later):
            earn.loc[dt, "ret_2d"] = ret_2d.get(later[0], np.nan)
    earn["ticker"] = ticker
    return earn


event_names = ["NVDA", "MU", "AVGO", "AMD"]
events = pd.concat([two_day_after_earnings(t) for t in event_names])
pos = events[events["Surprise(%)"] > 0]

print("median 2-day return after +surprise")
print(pos.groupby("ticker")["ret_2d"].median())
print("\\ncorr(ret_2d, Surprise%) by name")
print(
    events.groupby("ticker").apply(
        lambda d: d[["ret_2d", "Surprise(%)"]].dropna().corr().iloc[0, 1]
    )
)
print("\\nlast 3 prints per name")
print(
    events.sort_index()
    .groupby("ticker")
    .tail(3)[["ticker", "Reported EPS", "Surprise(%)", "ret_2d"]]
)
"""
    )
)
q6.append(md("## 4. Wikipedia GICS / Date added (index-inclusion feature)"))
q6.append(
    code(
        """url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
}
html = requests.get(url, headers=headers)
html.raise_for_status()
spx = pd.read_html(StringIO(html.text))[0]
spx["Date added"] = pd.to_datetime(spx["Date added"], errors="coerce")

want = [
    "NVDA", "AVGO", "AMD", "AMAT", "MU", "WDC", "ANET",
    "GOOGL", "MSFT", "AMZN", "META", "SMCI",
]
wiki = spx[spx["Symbol"].isin(want)][
    ["Symbol", "Security", "GICS Sector", "GICS Sub-Industry", "Date added"]
].sort_values("Symbol")
print(wiki.to_string(index=False))
print("\\nWHY: GICS dummies + years-in-index. New members get forced buying from index funds.")
print("Not in S&P 500 (still in the book): TSM, ASML, ARM, ALAB, CRDO, SK Hynix, Samsung, SNDK, VRT, MRVL (check live).")
print("Missing from this scrape:", sorted(set(want) - set(wiki["Symbol"])))
"""
    )
)
q6.append(md("## 5. Yahoo `info` snapshot — valuation / quality gates"))
q6.append(
    code(
        """snap_tickers = [
    "NVDA", "AVGO", "AMD", "TSM", "MU", "000660.KS", "VRT",
    "MRVL", "ALAB", "CRDO", "GOOGL", "SMCI",
]
rows = []
for t in snap_tickers:
    info = yf.Ticker(t, session=yf_session).info or {}
    rows.append(
        {
            "ticker": t,
            "name": info.get("shortName"),
            "mkt_cap_b": (info.get("marketCap") or np.nan) / 1e9,
            "fwd_pe": info.get("forwardPE"),
            "trail_pe": info.get("trailingPE"),
            "profit_margin": info.get("profitMargins"),
            "beta": info.get("beta"),
        }
    )
snap = pd.DataFrame(rows).set_index("ticker")
print(snap)
print('''\\nWHY
  forward PE / margin / beta are hard gates: skip names with no earnings
  or extreme beta unless the sleeve overlay says "bottleneck".
  Pull: yf.Ticker(t).info  (same SSL session as prices).
''')
"""
    )
)
q6.append(md("## Q6 write-up (form answer)"))
q6.append(
    code(
        """print('''Q6 ANSWER
For the AI-infra / memory / inference book I add:

1. ^SOX + FRED IPB53122S — semiconductor cycle vs real chip output.
2. FRED VIXCLS, T10Y2Y, FEDFUNDS — vol, curve, policy regime for position size.
3. get_earnings_dates() 2-day returns for NVDA/MU/AVGO/AMD — event features.
4. Wikipedia S&P 500 GICS + Date added — sleeve / inclusion dummies.
5. Yahoo info (fwd PE, margin, mkt cap) — valuation/quality gates.

How to pull
  import pandas_datareader as pdr
  vix = pdr.DataReader("VIXCLS", "fred", start="2018-01-01")
  ip  = pdr.DataReader("IPB53122S", "fred", start="2018-01-01")
  sox = yf.Ticker("^SOX").history(start="2023-01-01")
  earn = yf.Ticker("MU").get_earnings_dates()
  # Wikipedia: requests.get + pd.read_html (User-Agent required)
''')
"""
    )
)

write_nb(ROOT / "q6-ai-metrics" / "q6_ai_metrics.ipynb", q6)
