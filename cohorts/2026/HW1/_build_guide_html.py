# -*- coding: utf-8 -*-
"""Build homework1-guide.html — tabbed study sheet."""
from html import escape
from pathlib import Path

OUT = Path(__file__).with_name("homework1-guide.html")


def pre(s: str) -> str:
    return f"<pre><code>{escape(s.strip())}</code></pre>"


Q1_CODE = r'''
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
}
response = requests.get(url, headers=headers)
response.raise_for_status()

tables = pd.read_html(StringIO(response.text))
sp500 = tables[0].copy()
sp500["Date added"] = pd.to_datetime(sp500["Date added"], errors="coerce")
sp500["year_added"] = sp500["Date added"].dt.year

adds_by_year = sp500.dropna(subset=["year_added"]).groupby("year_added").size()
adds_2020_plus = adds_by_year[adds_by_year.index >= 2020]
q1_year = int(adds_2020_plus.idxmax())
q1_count = int(adds_2020_plus.max())

cutoff = pd.Timestamp(date.today()) - pd.DateOffset(years=20)
n_over_20y = int((sp500["Date added"].notna() & (sp500["Date added"] <= cutoff)).sum())
print(adds_2020_plus.sort_index())
print(f"Q1 answer: {q1_year} ({q1_count} additions)")
print(f"Additional >20y: {n_over_20y}")
'''

Q1_OUT = r'''
Additions by year (>=2020):
year_added
2020    10
2021    10
2022    15
2023    15
2024    16
2025    18
2026    13
dtype: int64

Q1 answer: 2025 (18 additions)
Additional: stocks with Date added >20y ago (dated only): 224
Additional: including undated original members: 224
'''

Q2_CODE = r'''
indexes = {
    "United States": "^GSPC", "China": "000001.SS", "Hong Kong": "^HSI",
    "Australia": "^AXJO", "India": "^NSEI", "Canada": "^GSPTSE",
    "Germany": "^GDAXI", "United Kingdom": "^FTSE", "Japan": "^N225",
    "Mexico": "^MXX", "Brazil": "^BVSP",
}
start_ytd = "2026-01-01"
end_inclusive = pd.Timestamp("2026-08-21")
end_download = "2026-08-22"   # yfinance end is exclusive

rows = []
for name, ticker in indexes.items():
    hist = yf.Ticker(ticker, session=yf_session).history(
        start=start_ytd, end=end_download, auto_adjust=False
    )
    hist.index = hist.index.tz_localize(None)
    hist = hist[hist.index <= end_inclusive]
    ret = hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1
    rows.append({"name": name, "ticker": ticker, "ytd_return": ret,
                 "start_date": hist.index[0].date(), "end_date": hist.index[-1].date()})

ytd = pd.DataFrame(rows).set_index("name")
us_ytd = ytd.loc["United States", "ytd_return"]
q2_count = int((ytd.drop(index="United States")["ytd_return"] > us_ytd).sum())
print(ytd.sort_values("ytd_return", ascending=False))
print(f"Q2 answer: {q2_count}")
'''

Q2_OUT = r'''
                   ticker  start_date    end_date  ytd_return
Japan               ^N225  2026-01-05  2026-08-21    0.273641
Canada            ^GSPTSE  2026-01-02  2026-08-21    0.148566
United States       ^GSPC  2026-01-02  2026-08-21    0.118962
United Kingdom      ^FTSE  2026-01-02  2026-08-21    0.086975
Brazil              ^BVSP  2026-01-02  2026-08-21    0.065361
Germany            ^GDAXI  2026-01-02  2026-08-21    0.065088
Australia           ^AXJO  2026-01-02  2026-08-21    0.037936
Mexico               ^MXX  2026-01-02  2026-08-21    0.024755
Hong Kong            ^HSI  2026-01-02  2026-08-21   -0.012492
China           000001.SS  2026-01-05  2026-08-21   -0.029382
India               ^NSEI  2026-01-01  2026-08-21   -0.072459

US YTD: 11.8962%
Q2 answer: 2 indexes beat S&P 500 YTD
Additional 3y: 2/10 beat US (US=74.4266%)
Additional 5y: 2/10 beat US (US=71.3209%)
Additional 10y: 1/10 beat US (US=251.6095%)
'''

Q3_CODE = r'''
spx = yf.Ticker("^GSPC", session=yf_session).history(start="1950-01-01", auto_adjust=False)
close = spx["Close"]
if getattr(close.index, "tz", None) is not None:
    close.index = close.index.tz_localize(None)

prev_max = close.cummax().shift(1)
is_ath = close > prev_max
is_ath.iloc[0] = True
ath_dates = close.index[is_ath]
ath_prices = close[is_ath]

corrections = []
for i in range(len(ath_dates) - 1):
    t0, t1 = ath_dates[i], ath_dates[i + 1]
    high = float(ath_prices.iloc[i])
    segment = close.loc[t0:t1].iloc[:-1]   # trough between ATHs
    trough_date = segment.idxmin()
    low = float(segment.min())
    dd = (high - low) / high * 100
    corrections.append({
        "ath_date": t0.date(), "trough_date": trough_date.date(),
        "drawdown_pct": dd, "duration_days": (trough_date - t0).days,
    })

sig = pd.DataFrame(corrections)
sig = sig[sig["drawdown_pct"] >= 5]
q3_median_dd = float(sig["drawdown_pct"].median())
print(sig["drawdown_pct"].quantile([0.25, 0.5, 0.75]))
print("Q3 answer:", q3_median_dd)
'''

Q3_OUT = r'''
Significant corrections (>=5%): 74
Drawdown percentiles:
0.25     6.234677
0.50     7.986358
0.75    14.019826
Duration percentiles:
0.25    22.00
0.50    40.50
0.75    86.25

Q3 answer (median drawdown %): 7.9864

Top 10 by drawdown:
  ath_date trough_date  drawdown_pct  duration_days
2007-10-09  2009-03-09     56.775388            517
2000-03-24  2002-10-09     49.146948            929
1973-01-11  1974-10-03     48.203593            630
1968-11-29  1970-05-26     36.061641            543
2020-02-19  2020-03-23     33.924960             33
1987-08-25  1987-12-04     33.509515            101
1961-12-12  1962-06-26     27.973568            196
1980-11-28  1982-08-12     27.113582            622
2022-01-03  2022-10-12     25.425097            282
1966-02-09  1966-10-07     22.177335            240
'''

Q4_CODE = r'''
ticker = "AMZN"
amzn = yf.Ticker(ticker, session=yf_session)
earnings = amzn.get_earnings_dates()
earnings = earnings.dropna(subset=["Reported EPS", "Surprise(%)"])

prices = amzn.history(period="max", auto_adjust=False)
closes = prices["Close"]
if getattr(closes.index, "tz", None) is not None:
    closes.index = closes.index.tz_localize(None)

# 2-day return when Day2 = i: Close[i+1] / Close[i-1] - 1
ret_2d = closes.shift(-1) / closes.shift(1) - 1

earn = earnings.copy()
earn.index = pd.to_datetime(earn.index).tz_localize(None).normalize()
earn["ret_2d"] = ret_2d.reindex(earn.index)

positive = earn[earn["Surprise(%)"] > 0].dropna(subset=["ret_2d"])
q4_median = float(positive["ret_2d"].median())
print("Q4 answer:", q4_median)
print(earn[["ret_2d", "Surprise(%)"]].dropna().corr())
'''

Q4_OUT = r'''
Earnings rows (reported): 24
... 2026-07-30 ... 2020-10-29 ...

Positive surprises with returns: 20
Q4 answer (median 2-day return): 0.003528 (0.3528%)

Correlation (all surprises):
               ret_2d  Surprise(%)
ret_2d       1.000000     0.219063
Surprise(%)  0.219063     1.000000
'''

SETUP_CODE = r'''
%pip install yfinance pandas lxml beautifulsoup4 requests truststore curl_cffi

import truststore
truststore.inject_into_ssl()   # BEFORE requests / yfinance / pandas_datareader

import requests
import pandas as pd
import numpy as np
import yfinance as yf
from curl_cffi import requests as curl_requests
from io import StringIO
from datetime import date

# Windows: yfinance 1.7 uses curl_cffi; OS CA store often fails.
yf_session = curl_requests.Session(impersonate="chrome", verify=False)
'''

Q5_CODE = r'''
# Скорочена версія з q5-ai-infra-capstone/q5_ai_infra_capstone.ipynb
UNIVERSE = [
    # AI infrastructure
    {"ticker": "NVDA", "segment": "AI infrastructure"},
    {"ticker": "AVGO", "segment": "AI infrastructure"},
    {"ticker": "AMD",  "segment": "AI infrastructure"},
    {"ticker": "TSM",  "segment": "AI infrastructure"},
    {"ticker": "SMCI", "segment": "AI infrastructure"},
    {"ticker": "VRT",  "segment": "AI infrastructure"},
    # Memory / RAM / HBM
    {"ticker": "MU", "segment": "Memory / RAM"},
    {"ticker": "WDC", "segment": "Memory / RAM"},
    {"ticker": "SNDK", "segment": "Memory / RAM"},
    {"ticker": "000660.KS", "segment": "Memory / RAM"},  # SK Hynix
    # Inference
    {"ticker": "MRVL", "segment": "Inference"},
    {"ticker": "ARM",  "segment": "Inference"},
    {"ticker": "ALAB", "segment": "Inference"},
    {"ticker": "GOOGL","segment": "Inference"},
]
# далі: yf.download → YTD / 1y / max DD vs ^GSPC, equal-weight sleeves
'''

Q5_OUT = r'''
S&P 500 YTD 11.90% | 1y 20.47% | end 2026-08-21

Sleeve medians
                     ytd   ret_1y  max_dd
AI infrastructure  0.412   0.843  -0.502
Inference          0.365   0.666  -0.444
Memory / RAM       1.555   6.061  -0.547

Beat S&P 500 YTD: 18 / 22
Leaders YTD: SNDK +480%, MU +207%, MRVL +165%, SK Hynix +156%

P(up in 5d) baseline: WDC 57.3%, NVDA 56.5%
'''

Q6_CODE = r'''
# Скорочена версія з q6-ai-metrics/q6_ai_metrics.ipynb
import pandas_datareader as pdr

vix  = pdr.DataReader("VIXCLS", "fred", start="2018-01-01")
curve = pdr.DataReader("T10Y2Y", "fred", start="2018-01-01")
ip   = pdr.DataReader("IPB53122S", "fred", start="2018-01-01")  # semi IP
sox  = yf.Ticker("^SOX", session=yf_session).history(start="2023-01-01")
earn = yf.Ticker("MU", session=yf_session).get_earnings_dates()

# Wikipedia GICS:
# requests.get(wiki_url, headers=UA) → pd.read_html(...)[0]
# Yahoo quality gates: yf.Ticker("NVDA").info  → forwardPE, profitMargins
'''

Q6_OUT = r'''
SOX YTD +59.4% | SPX +11.9% | MU +206% | SK Hynix +156%
SOX↔MU daily corr 0.78

FRED latest: VIX ~14.5–16; T10Y2Y +0.39 (не інвертована)

Median 2-day return after +surprise:
  AVGO +0.71% | NVDA -0.05% | AMD -0.53% | MU -1.77%
corr(surprise, ret_2d): MU 0.32, NVDA 0.31, AMD 0.11, AVGO -0.21

Wikipedia: 12 US names found. SMCI added 2024-03-18.
'''


def q_panel(qid, title, answer, task_en, task_ua, code, output, explain_ua, extra_html=""):
    return f"""
<section class="q-panel" id="panel-{qid}" role="tabpanel" hidden>
  <div class="q-head">
    <h2>{escape(title)}</h2>
    <span class="pill accent">Відповідь для форми: {escape(answer)}</span>
  </div>
  <div class="inner-tabs" role="tablist">
    <button class="inner-tab active" data-inner="{qid}-task" type="button">Завдання</button>
    <button class="inner-tab" data-inner="{qid}-code" type="button">Код</button>
    <button class="inner-tab" data-inner="{qid}-out" type="button">Результат</button>
    <button class="inner-tab" data-inner="{qid}-why" type="button">Пояснення</button>
  </div>
  <div class="inner-panel active" id="{qid}-task">
    <div class="callout">
      <b>EN task.</b>
      {task_en}
    </div>
    <div class="callout info">
      <b>Завдання українською.</b>
      {task_ua}
    </div>
    {extra_html}
  </div>
  <div class="inner-panel" id="{qid}-code">
    <p class="muted">Код з <code>homework1.ipynb</code> (або окремого проєкту Q5/Q6). Спочатку виконай Setup.</p>
    {pre(code)}
  </div>
  <div class="inner-panel" id="{qid}-out">
    <p class="muted">Живий вивід від 30 серпня 2026. При повторному запуску цифри можуть трохи змінитись.</p>
    {pre(output)}
  </div>
  <div class="inner-panel" id="{qid}-why">
    {explain_ua}
  </div>
</section>
"""


html = f"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>HW1 2026 — завдання, код, вивід, пояснення</title>
<style>
:root {{
  --ivory:#FAF9F5; --slate:#141413; --clay:#D97757; --oat:#E3DACC;
  --olive:#788C5D; --rust:#B04A3F; --white:#FFFFFF;
  --gray-100:#F0EEE6; --gray-300:#D1CFC5; --gray-500:#87867F; --gray-700:#3D3D3A;
  --serif: ui-serif, Georgia, 'Times New Roman', serif;
  --sans: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  --mono: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
  --border: 1.5px solid var(--gray-300);
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{
  background:var(--ivory); color:var(--gray-700);
  font-family:var(--sans); font-size:15.5px; line-height:1.65;
  padding:28px 18px 80px;
}}
.page {{ max-width:980px; margin:0 auto; }}
.eyebrow {{ font-family:var(--mono); font-size:11px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--gray-500); margin-bottom:8px; }}
h1 {{ font-family:var(--serif); font-weight:500; font-size:34px; color:var(--slate);
  letter-spacing:-.015em; margin-bottom:10px; }}
h2 {{ font-family:var(--serif); font-weight:500; font-size:24px; color:var(--slate); }}
h3 {{ font-family:var(--serif); font-weight:500; font-size:18px; color:var(--slate); margin:18px 0 8px; }}
p {{ margin-bottom:12px; }}
.muted {{ color:var(--gray-500); font-size:13.5px; }}
.lead {{ max-width:720px; margin-bottom:20px; }}
.pill {{ display:inline-flex; font-family:var(--mono); font-size:11px; letter-spacing:.04em;
  text-transform:uppercase; background:var(--gray-100); border:var(--border);
  border-radius:999px; padding:4px 10px; }}
.pill.accent {{ background:var(--oat); border-color:var(--oat); color:var(--slate); }}
.stat-band {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; margin:18px 0 22px; }}
.stat-card {{ background:var(--white); border:var(--border); border-radius:12px; padding:14px 16px; }}
.stat-num {{ font-family:var(--serif); font-size:28px; color:var(--slate); line-height:1.1; }}
.stat-label {{ font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--gray-500); margin-top:4px; }}
.q-tabs {{ display:flex; flex-wrap:wrap; gap:6px; margin:8px 0 0; }}
.q-tab {{ font-family:var(--mono); font-size:12px; letter-spacing:.04em; text-transform:uppercase;
  background:transparent; border:var(--border); border-radius:999px; padding:7px 12px; cursor:pointer; color:var(--gray-700); }}
.q-tab.active {{ background:var(--slate); color:var(--ivory); border-color:var(--slate); }}
.q-panel {{ background:var(--white); border:var(--border); border-radius:12px; padding:22px 22px 26px; margin-top:14px; }}
.q-head {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; justify-content:space-between; margin-bottom:14px; }}
.inner-tabs {{ display:flex; flex-wrap:wrap; gap:4px; border-bottom:1.5px solid var(--gray-300); margin-bottom:16px; }}
.inner-tab {{ background:none; border:none; border-bottom:2px solid transparent; padding:8px 12px;
  font-family:var(--sans); font-size:14px; cursor:pointer; color:var(--gray-500); margin-bottom:-1.5px; }}
.inner-tab.active {{ color:var(--slate); border-bottom-color:var(--clay); font-weight:600; }}
.inner-panel {{ display:none; }}
.inner-panel.active {{ display:block; }}
.callout {{ border:var(--border); border-left:3px solid var(--clay); border-radius:0 10px 10px 0;
  background:var(--ivory); padding:14px 16px; margin:0 0 12px; }}
.callout.info {{ border-left-color:var(--olive); }}
.callout.warn {{ border-left-color:var(--clay); }}
ul, ol {{ margin:0 0 12px 20px; }}
li {{ margin-bottom:6px; }}
table {{ width:100%; border-collapse:separate; border-spacing:0; border:var(--border);
  border-radius:12px; overflow:hidden; margin:12px 0; background:var(--white); }}
th {{ text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.05em;
  color:var(--gray-500); background:var(--gray-100); padding:10px 12px; }}
td {{ padding:10px 12px; border-top:1px solid var(--gray-100); font-size:14px; vertical-align:top; }}
pre {{ background:var(--slate); color:#E8E6DE; border-radius:12px; padding:16px 18px;
  overflow-x:auto; font-family:var(--mono); font-size:12.4px; line-height:1.6; margin:10px 0; }}
code {{ font-family:var(--mono); font-size:.9em; background:var(--gray-100); padding:1px 5px; border-radius:4px; }}
pre code {{ background:none; padding:0; color:inherit; }}
.kw {{ color:#E8C07A; }}
footer {{ margin-top:28px; font-size:13px; color:var(--gray-500); }}
a {{ color:var(--clay); }}
</style>
</head>
<body>
<div class="page">
  <p class="eyebrow">SMA Zoomcamp 2026 · Module 1 · файл для навчання</p>
  <h1>Homework 1 — завдання, код, вивід і пояснення</h1>
  <p class="lead">Кожне питання — окрема вкладка. Всередині: <b>Завдання</b> (EN + українською),
  <b>Код</b>, <b>Результат</b> і <b>Пояснення виводу</b> українською. Відкрий цей файл у браузері
  (подвійний клік). Сервер не потрібен.</p>

  <div class="stat-band">
    <div class="stat-card"><div class="stat-num">2025</div><div class="stat-label">Q1 рік</div></div>
    <div class="stat-card"><div class="stat-num">2</div><div class="stat-label">Q2 індекси &gt; США</div></div>
    <div class="stat-card"><div class="stat-num">7.99</div><div class="stat-label">Q3 медіана DD %</div></div>
    <div class="stat-card"><div class="stat-num">0.35%</div><div class="stat-label">Q4 медіана 2д</div></div>
  </div>

  <div class="q-tabs" role="tablist">
    <button class="q-tab active" data-q="setup" type="button">Setup</button>
    <button class="q-tab" data-q="q1" type="button">Q1</button>
    <button class="q-tab" data-q="q2" type="button">Q2</button>
    <button class="q-tab" data-q="q3" type="button">Q3</button>
    <button class="q-tab" data-q="q4" type="button">Q4</button>
    <button class="q-tab" data-q="q5" type="button">Q5</button>
    <button class="q-tab" data-q="q6" type="button">Q6</button>
  </div>

{q_panel(
    "setup",
    "Setup — бібліотеки і SSL",
    "не здається",
    "<p>Перша клітинка ноутбука. Встановити пакети, увімкнути системні сертифікати, імпортувати клієнти HTTPS.</p>",
    '''<p>На Windows Python часто не бачить файл сертифікатів OpenSSL. Тоді <code>requests</code> і FRED падають.
    <code>truststore.inject_into_ssl()</code> треба викликати <b>до</b> імпорту HTTPS-клієнтів.
    Yahoo Finance у yfinance 1.7 ходить через <code>curl_cffi</code> — окремий SSL.
    Тому створюємо <code>yf_session</code> з <code>verify=False</code>, інакше буде
    <code>CertificateVerifyError</code>.</p>''',
    SETUP_CODE,
    "setup ok\\n(пакети вже встановлені в середовищі)",
    '''
    <h3>Що саме робить код</h3>
    <ol>
      <li><code>%pip install ...</code> — ставить пакети в <b>поточне ядро</b> Jupyter, не в «якийсь Python на диску».</li>
      <li><code>truststore.inject_into_ssl()</code> — підсовує сертифікати Windows у стандартний SSL Python. Це лікує FRED / Wikipedia / <code>requests</code>.</li>
      <li><code>yf_session = Session(impersonate="chrome", verify=False)</code> — окремий обхід для Yahoo. Без цього <code>yf.Ticker("^GSPC").history()</code> на цій машині падає.</li>
    </ol>
    <div class="callout warn"><b>Правило.</b> Кожну наступну клітинку Q1–Q4 запускай у тому ж ядрі, після Setup.
    Інакше будуть <code>NameError: requests / yf_session</code>.</div>
    '''
)}

{q_panel(
    "q1",
    "Q1 — додавання в S&P 500",
    "2025",
    "<p><b>Which year had the highest number of additions (starting from 2020)?</b></p>"
    "<p>Scrape Wikipedia <i>List of S&amp;P 500 companies</i>, extract year from <code>Date added</code>, "
    "count additions per full year ≥ 2020, take the max year.</p>"
    "<p><i>Additional:</i> how many current members have been in the index more than 20 years?</p>",
    '''<p><b>Який рік (починаючи з 2020) має найбільше нових компаній у S&amp;P 500?</b></p>
    <p>Треба завантажити таблицю поточних учасників індексу з Вікіпедії, витягти рік з колонки
    <code>Date added</code> і порахувати, скільки тікерів додали в кожному повному році від 2020.
    Рік з максимумом — відповідь у форму.</p>
    <ul>
      <li>Без <code>User-Agent</code> Wikipedia часто дає <b>403</b>.</li>
      <li>Порожня дата = «оригінальний» учасник. Для річних лічильників такі рядки пропускаємо.</li>
      <li>2026 — неповний рік, його не беремо як «переможця», навіть якщо пізніше обжене 2025.</li>
    </ul>''',
    Q1_CODE,
    Q1_OUT,
    '''
    <h3>Як читати код по рядках</h3>
    <ol>
      <li><code>requests.get(..., headers=)</code> — качаємо HTML, ніби ми браузер.</li>
      <li><code>pd.read_html(StringIO(...))</code> — pandas знаходить усі HTML-таблиці. <b>Перша</b> = поточні 500 імен.</li>
      <li><code>to_datetime(..., errors="coerce")</code> — криві дати стають NaT, а не падають.</li>
      <li><code>groupby("year_added").size()</code> — скільки рядків на рік.</li>
      <li><code>idxmax()</code> — рік із найбільшим числом. Це і є <b>2025</b>.</li>
    </ol>
    <h3>Пояснення виводу</h3>
    <p>Таблиця — це <b>survivorship</b>: лише компанії, які <i>досі</i> в індексі. Тікер, який додали в 2022 і потім викинули, сюди не потрапить.</p>
    <table>
      <thead><tr><th>Рік</th><th>Скільки досі в індексі</th><th>Що це значить</th></tr></thead>
      <tbody>
        <tr><td>2020–2021</td><td>по 10</td><td>мало ротацій / COVID-епоха</td></tr>
        <tr><td>2022–2024</td><td>15–16</td><td>нормальна ротація</td></tr>
        <tr><td><b>2025</b></td><td><b>18</b></td><td>максимум → відповідь форми</td></tr>
        <tr><td>2026</td><td>13</td><td>рік ще йде, не «повний»</td></tr>
      </tbody>
    </table>
    <p><b>224</b> компанії мають <code>Date added</code> старшу за 20 років. Це додаткове питання, не поле форми.</p>
    <div class="callout info"><b>На форму пиши:</b> <code>2025</code></div>
    '''
)}

{q_panel(
    "q2",
    "Q2 — світові індекси YTD vs S&P 500",
    "2",
    "<p><b>How many of 10 non-US indexes beat S&amp;P 500 YTD as of 21 Aug 2026?</b></p>"
    "<p>YTD = last Close / first Close − 1. Use Close, ignore FX. "
    "yfinance <code>end</code> is exclusive → download through 2026-08-22.</p>",
    '''<p><b>Скільки з 10 неамериканських індексів обігнали S&amp;P 500 з 1 січня по 21 серпня 2026?</b></p>
    <p>Дохідність = <code>останній Close / перший Close − 1</code>. Беремо саме <b>Close</b>, не Adj Close.
    Валюту не конвертуємо (так написано в ДЗ).</p>
    <p>Пастка yfinance: параметр <code>end</code> <b>не включає</b> цей день. Щоб мати 21 серпня,
    качаємо <code>end="2026-08-22"</code>. Якщо 1 січня — свято, беремо перший доступний день.</p>''',
    Q2_CODE,
    Q2_OUT,
    '''
    <h3>Як читати код</h3>
    <ol>
      <li>Словник країна → тікер Yahoo.</li>
      <li>Для кожного тікера качаємо денні ціни через <code>yf_session</code>.</li>
      <li>Зрізаємо індекс до ≤ 21 серпня, рахуємо просту дохідність.</li>
      <li>Порівнюємо 10 індексів із рядком United States. Рахуємо, скільки <b>строго більше</b>.</li>
    </ol>
    <h3>Пояснення виводу</h3>
    <p>S&amp;P 500 YTD ≈ <b>+11.9%</b>. Вище нього лише два:</p>
    <ul>
      <li><b>Японія (^N225) +27.4%</b> — сильний рік для Nikkei.</li>
      <li><b>Канада (^GSPTSE) +14.9%</b> — ресурси / банки.</li>
    </ul>
    <p>Решта нижче США. Індія навіть у мінусі (−7.2%). Тому відповідь <b>2</b>, не «більшість світу обганяє США».</p>
    <p>Додатково (не форма): на 3р і 5р теж 2/10 б’ють США; на 10р лише 1/10 — довгий горизонт США домінує сильніше.</p>
    <div class="callout info"><b>На форму пиши:</b> <code>2</code></div>
    '''
)}

{q_panel(
    "q3",
    "Q3 — корекції S&P 500, медіана просадки",
    "7.9864",
    "<p><b>Median drawdown (%) of corrections ≥ 5% from the most recent all-time high.</b></p>"
    "<p>ATH = Close exceeds all previous Closes. Between consecutive ATHs take the min Close. "
    "Drawdown = (high−low)/high×100. Keep ≥ 5%. Report p25/p50/p75 for depth and duration.</p>",
    '''<p><b>Яка медіанна глибина (у %) значущих корекцій S&amp;P 500?</b></p>
    <p>Корекція = індекс впав щонайменше на <b>5%</b> від останнього історичного максимуму (ATH) по Close.</p>
    <ol>
      <li>Качаємо денний Close ^GSPC з 1950.</li>
      <li>День ATH: сьогоднішня ціна вища за всі попередні.</li>
      <li>Між двома сусідніми ATH шукаємо мінімум (дно).</li>
      <li>Просадка = (макс − мін) / макс × 100.</li>
      <li>Залишаємо лише події ≥ 5%. Медіана цих відсотків — відповідь.</li>
    </ol>
    <p>Тривалість = календарні дні від ATH до дна. Це <b>не</b> відповідь форми, але треба порахувати.</p>''',
    Q3_CODE,
    Q3_OUT,
    '''
    <h3>Як читати код</h3>
    <ul>
      <li><code>cummax().shift(1)</code> — максимальний Close <i>до</i> сьогодні. Якщо сьогодні вище — новий ATH.</li>
      <li><code>segment = close.loc[t0:t1].iloc[:-1]</code> — відрізок від ATH до дня <b>перед</b> наступним ATH (дно між піками).</li>
      <li><code>median()</code> стійкіша за середнє: рідкісні крахи (2008: −57%) не роздувають «типову» корекцію.</li>
    </ul>
    <h3>Пояснення виводу</h3>
    <p>Знайдено <b>74</b> корекції ≥ 5% з 1950 року.</p>
    <table>
      <thead><tr><th></th><th>p25</th><th>медіана (p50)</th><th>p75</th></tr></thead>
      <tbody>
        <tr><td>Глибина</td><td>6.23%</td><td><b>7.99%</b></td><td>14.02%</td></tr>
        <tr><td>Днів до дна</td><td>22</td><td>40.5</td><td>86</td></tr>
      </tbody>
    </table>
    <p>Типова «значуща» корекція — це приблизно <b>мінус 8%</b> і близько <b>6 тижнів</b> до дна. Не 2008 рік.</p>
    <p>Топ-10 збігся з підказкою в ДЗ (2007→2009: 56.8% / 517 днів). Отже алгоритм правильний. Брали Close, не Adj Close.</p>
    <div class="callout info"><b>На форму пиши:</b> <code>7.9864</code> (або 7.99 / 8 — як прийме поле)</div>
    '''
)}

{q_panel(
    "q4",
    "Q4 — сюрприз звітності AMZN, 2-денна дохідність",
    "0.003528",
    "<p><b>Median 2-day return after positive Surprise %.</b></p>"
    "<p>For trading days (d1, d2, d3): return = Close[d3]/Close[d1]−1. Align earnings to d2. "
    "Keep Surprise% &gt; 0. Also report corr(return, Surprise%).</p>",
    '''<p><b>Яка медіанна 2-денна дохідність AMZN після днів із <i>позитивним</i> сюрпризом EPS?</b></p>
    <p>Беремо <code>get_earnings_dates()</code> (~25 рядків від 2020-10-29, один майбутній рядок без EPS — викидаємо).</p>
    <p>Для трьох підряд торгових днів (день 1, день 2 = анонс, день 3):
    <code>Close[день3] / Close[день1] − 1</code>. Це «вікно навколо новини», не звичайний daily return.</p>
    <p>Фільтр: <code>Surprise(%) &gt; 0</code>. Медіана цих return — відповідь. Потім кореляція сюрпризу і return (всі сюрпризи, не лише плюс).</p>''',
    Q4_CODE,
    Q4_OUT,
    '''
    <h3>Як читати код</h3>
    <ul>
      <li><code>shift(-1) / shift(1) - 1</code> — для кожного дня <i>i</i> як Day2 рахує Close наступного / Close попереднього.</li>
      <li>Індекс звітності нормалізуємо до дати (прибираємо часовий пояс). Анонс після закриття все одно клеїться до цієї сесії.</li>
      <li>Майбутній рядок з NaN Reported EPS відсікається <code>dropna</code>.</li>
    </ul>
    <h3>Пояснення виводу</h3>
    <p>24 фактичні звіти, з них <b>20 позитивних сюрпризів</b>.</p>
    <p>Медіана 2-денної дохідності = <b>+0.3528%</b> (0.003528 у частках). Це дуже мало:
    «побив очікування» ≠ автоматичний стрибок акції. Ринок часто вже заложив beat у ціну.</p>
    <p>Кореляція сюрпризу і 2-денного руху ≈ <b>+0.22</b> — слабка додатна. Більший сюрприз трохи частіше дає кращий рух, але шуму багато.</p>
    <div class="callout info"><b>На форму пиши:</b> <code>0.003528</code> (або 0.35%, якщо поле у відсотках — читай підказку форми)</div>
    '''
)}

{q_panel(
    "q5",
    "Q5 — ідея капстоуну (AI infra / RAM / inference)",
    "вільний текст",
    "<p><b>Optional free text.</b> Describe a specific capstone: asset, horizon, features, model.</p>"
    "<p>Our project lives in <code>q5-ai-infra-capstone/q5_ai_infra_capstone.ipynb</code> — own kernel, own setup.</p>",
    '''<p><b>Необов’язкове.</b> Опиши конкретний капстоун: що торгуємо, який горизонт, які фічі, який модельний план.</p>
    <p>Ми звузили всесвіт не до всього S&amp;P 500, а до трьох рукавів:</p>
    <ul>
      <li><b>AI infrastructure</b> — NVDA, AVGO, AMD, TSM, ASML, AMAT, SMCI, VRT, ANET (чіпи, фабрики, стійки, живлення, мережа).</li>
      <li><b>Memory / RAM</b> — MU, WDC, SNDK, SK Hynix, Samsung (DRAM / HBM / NAND — вузьке місце GPU).</li>
      <li><b>Inference</b> — MRVL, ARM, ALAB, CRDO, GOOGL, MSFT, AMZN, META (кастомний силікон і гіперскейлери, які платять за інференс).</li>
    </ul>
    <p><b>Ціль моделі:</b> чи Close через 5 торгових днів буде вищим за сьогодні. Класифікатор (XGBoost) + лонг-онлі книга з лімітами на рукав.</p>''',
    Q5_CODE,
    Q5_OUT,
    '''
    <h3>Пояснення виводу скоупінг-прогону</h3>
    <p>Панель цін: 941 день, 23 тікери, без дірок. Кінець вікна — 21 серпня 2026, як у Q2.</p>
    <p>S&amp;P 500 YTD лише <b>+11.9%</b>. Медіана рукава Memory/RAM = <b>+155%</b>. Це не «ринок зріс» — це конкретний бум HBM/NAND (SNDK, MU, SK Hynix).</p>
    <p>AI-infra медіана +41%, inference +36% — теж б’ють індекс, але слабше за пам’ять. <b>18 з 22</b> імен вище SPX YTD. Теза «дивись лише NVDA» хибна: NVDA не лідер цього зрізу.</p>
    <p><code>P(up in 5d)</code> ≈ 53–57%. Наївний класифікатор «завжди лонг» уже правий більше ніж у половині випадків. Модель має бити <b>цю</b> базу, не 50/50.</p>
    <div class="callout warn"><b>NaN у «total return since first common start».</b> Рукави стартують у різні дати (ALAB, SNDK, корейські імена). Тому equal-weight NAV ламається на спільному старті. Дивись YTD / 1y таблицю — вона чесна.</div>
    <p>Текст для форми — у <code>homework1-answers.md</code> (секція Q5) і в останній клітинці ноутбука Q5.</p>
    '''
)}

{q_panel(
    "q6",
    "Q6 — додаткові метрики для AI-книги",
    "вільний текст",
    "<p><b>Optional.</b> Pull 2–4 extra series useful for the Q5 project. Say why and how in Python.</p>"
    "<p>Project: <code>q6-ai-metrics/q6_ai_metrics.ipynb</code>.</p>",
    '''<p><b>Необов’язкове.</b> Завантаж кілька рядів, які реально потрібні капстоуну. Коротко: навіщо і як тягнути в Python.</p>
    <ol>
      <li><code>^SOX</code> + FRED <code>IPB53122S</code> — цикл напівпровідників vs реальний випуск чіпів.</li>
      <li>FRED <code>VIXCLS</code>, <code>T10Y2Y</code>, <code>FEDFUNDS</code> — вола / крива / ставка для сайзингу.</li>
      <li><code>get_earnings_dates()</code> для NVDA/MU/AVGO/AMD — ті самі 2-денні вікна, що в Q4.</li>
      <li>Вікіпедія GICS + Date added — даммі сектора і «новий член індексу».</li>
      <li>Yahoo <code>info</code> — forward PE, маржа, капітал як фільтр якості.</li>
    </ol>''',
    Q6_CODE,
    Q6_OUT,
    '''
    <h3>Пояснення виводу</h3>
    <p><b>SOX +59% YTD</b> проти SPX +12%. MU і SK Hynix ще швидші за сам SOX — пам’ять зараз «гарячіша» за індекс чіпів. Кореляція SOX↔MU = 0.78: MU майже їде як бета на напівпровідниковий цикл.</p>
    <p><b>FRED.</b> VIX спокійний (~15). Спред 10y−2y = <b>+0.39</b> — крива не інвертована, режим не «рецесійний сигнал». <code>FEDFUNDS</code> і <code>IPB53122S</code> місячні: на останніх денних датах виглядають порожніми — це нормально, дивись попередній місяць.</p>
    <p><b>Звітності.</b> Після позитивного сюрпризу медіанний 2-денний хід: AVGO трохи плюс, NVDA майже нуль, AMD/MU навіть мінус. Ринок AI-імен часто продає новину. Кореляція сюрпризу і ціни слабка (макс ~0.31 у MU/NVDA) — як і в AMZN у Q4.</p>
    <p><b>Вікіпедія.</b> Усі 12 шуканих US-тікерів знайдені. SMCI в індексі лише з <b>2024-03-18</b> — свіжий inclusion-потік. TSM/ASML/ARM/корейці в S&amp;P 500 немає — для них цей фічер = 0.</p>
    <p><b>info.</b> NVDA ~$5.3T, маржа 64%; MU вже ~$1.05T і маржа 56%. Капітал SK Hynix у виводі — <b>вони</b> (KRW), не мішати з доларами.</p>
    <p>Текст для форми — у <code>homework1-answers.md</code> (секція Q6).</p>
    '''
)}

  <footer>
    Джерела: <code>homework1.ipynb</code>,
    <code>q5-ai-infra-capstone/q5_ai_infra_capstone.ipynb</code>,
    <code>q6-ai-metrics/q6_ai_metrics.ipynb</code>,
    <code>homework1-answers.md</code>.
    Форма: <a href="https://courses.datatalks.club/sma-zoomcamp-2026/homework/hw01">hw01</a>.
    Файл: <code>cohorts/2026/HW1/homework1-guide.html</code>
  </footer>
</div>
<script>
(function () {{
  const qTabs = document.querySelectorAll(".q-tab");
  const qPanels = document.querySelectorAll(".q-panel");
  function showQ(id) {{
    qTabs.forEach(b => b.classList.toggle("active", b.dataset.q === id));
    qPanels.forEach(p => {{
      const on = p.id === "panel-" + id;
      p.hidden = !on;
    }});
  }}
  qTabs.forEach(b => b.addEventListener("click", () => showQ(b.dataset.q)));
  showQ("setup");

  document.querySelectorAll(".inner-tab").forEach(btn => {{
    btn.addEventListener("click", () => {{
      const target = btn.dataset.inner;
      const panel = document.getElementById(target);
      if (!panel) return;
      const wrap = panel.parentElement;
      wrap.querySelectorAll(".inner-tab").forEach(t => t.classList.toggle("active", t === btn));
      wrap.querySelectorAll(".inner-panel").forEach(p => p.classList.toggle("active", p === panel));
    }});
  }});
}})();
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print("Wrote", OUT, "bytes", OUT.stat().st_size)
