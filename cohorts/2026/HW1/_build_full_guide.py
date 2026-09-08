# -*- coding: utf-8 -*-
"""homework1-guide.html — Jupyter-style cells (In/Out), full source + outputs."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HW1 = ROOT / "homework1.ipynb"
Q5 = ROOT / "q5-ai-infra-capstone" / "q5_ai_infra_capstone.ipynb"
Q6 = ROOT / "q6-ai-metrics" / "q6_ai_metrics.ipynb"
OUT = ROOT / "homework1-guide.html"


def load_nb(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def src(cell: dict) -> str:
    return "".join(cell.get("source", []))


def md_to_html(text: str) -> str:
    """Very small markdown subset for notebook markdown cells."""
    lines = text.replace("\r\n", "\n").split("\n")
    out, para, in_code = [], [], False
    code_buf = []

    def flush_para():
        if para:
            out.append("<p>" + " ".join(para) + "</p>")
            para.clear()

    for line in lines:
        if line.startswith("```"):
            if in_code:
                out.append(f"<pre class='mdcode'>{html.escape(chr(10).join(code_buf))}</pre>")
                code_buf.clear()
                in_code = False
            else:
                flush_para()
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        if not line.strip():
            flush_para()
            continue
        if line.startswith("# "):
            flush_para()
            out.append(f"<h2>{inline(line[2:])}</h2>")
        elif line.startswith("## "):
            flush_para()
            out.append(f"<h3>{inline(line[3:])}</h3>")
        elif line.startswith("### "):
            flush_para()
            out.append(f"<h4>{inline(line[4:])}</h4>")
        elif line.startswith("- ") or line.startswith("* "):
            flush_para()
            out.append(f"<ul><li>{inline(line[2:])}</li></ul>")
        else:
            para.append(inline(line))
    flush_para()
    # merge adjacent ul
    merged = []
    for chunk in out:
        if merged and chunk.startswith("<ul>") and merged[-1].endswith("</ul>"):
            merged[-1] = merged[-1][:-5] + chunk[4:]
        else:
            merged.append(chunk)
    return "\n".join(merged) or "<p></p>"


def inline(s: str) -> str:
    import re

    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    return s


def outputs_html(cell: dict) -> str:
    chunks = []
    for o in cell.get("outputs", []) or []:
        ot = o.get("output_type")
        if ot == "stream":
            t = o.get("text", "")
            text = "".join(t) if isinstance(t, list) else t
            if text.strip():
                chunks.append(f"<pre class='stdout'>{html.escape(text)}</pre>")
        elif ot in ("execute_result", "display_data"):
            data = o.get("data") or {}
            if "image/png" in data:
                b64 = data["image/png"]
                if isinstance(b64, list):
                    b64 = "".join(b64)
                chunks.append(
                    f'<img class="plot" alt="figure" src="data:image/png;base64,{b64}"/>'
                )
            if "text/plain" in data:
                tp = data["text/plain"]
                text = "".join(tp) if isinstance(tp, list) else tp
                if text and not text.startswith("<Figure"):
                    chunks.append(f"<pre class='stdout'>{html.escape(text)}</pre>")
        elif ot == "error":
            chunks.append(
                f"<pre class='stderr'>{html.escape(o.get('ename','Error'))}: "
                f"{html.escape(o.get('evalue',''))}</pre>"
            )
    return "\n".join(chunks)


def render_notebook(nb: dict, indices: list[int] | None = None) -> str:
    cells = nb["cells"] if indices is None else [nb["cells"][i] for i in indices]
    parts = []
    exec_n = 0
    for cell in cells:
        kind = cell.get("cell_type")
        text = src(cell)
        if kind == "markdown":
            parts.append(
                f'<article class="jcell jmd"><div class="jprompt"></div>'
                f'<div class="jbody">{md_to_html(text)}</div></article>'
            )
        elif kind == "code":
            exec_n += 1
            n = cell.get("execution_count") or exec_n
            raw = text.rstrip() + "\n"
            out = outputs_html(cell)
            out_block = ""
            if out:
                out_block = (
                    f'<div class="jout">'
                    f'<div class="jprompt">Out&nbsp;[{n}]:</div>'
                    f'<div class="jbody">{out}</div></div>'
                )
            parts.append(
                f"""<article class="jcell jcode">
  <div class="jin">
    <div class="jprompt">In&nbsp;[{n}]:</div>
    <div class="jbody">
      <button type="button" class="copybtn">Copy cell</button>
      <pre class="jinput"><code>{html.escape(raw)}</code></pre>
    </div>
  </div>
  {out_block}
</article>"""
            )
    return "\n".join(parts)


TASKS = {
    "setup": "<p>Перша клітинка <code>homework1.ipynb</code>. Запусти її <b>першою</b>, потім Q1→Q4 зверху вниз у тому ж ядрі.</p>",
    "q1": "<p>Клітинка Q1 в <code>homework1.ipynb</code> (після Setup). Відповідь форми: <b>2025</b>.</p>",
    "q2": "<p>Клітинка Q2. yfinance <code>end</code> exclusive → <code>2026-08-22</code>. Відповідь: <b>2</b>.</p>",
    "q3": "<p>Клітинка Q3. Close, не Adj Close. Відповідь: <b>7.9864</b>.</p>",
    "q4": "<p>Дві клітинки: розрахунок AMZN + summary answers. Відповідь: <b>0.003528</b>.</p>",
    "q5": "<p>Окремий файл <code>q5-ai-infra-capstone/q5_ai_infra_capstone.ipynb</code>. Відкрий його і ганяй In[1]→In[8] по черзі. Свій Setup, не залежить від homework1.</p>",
    "q6": "<p>Окремий файл <code>q6-ai-metrics/q6_ai_metrics.ipynb</code>. Свій Setup + FRED. Ганяй In[1]→In[7].</p>",
}

EXPS = {
    "setup": "<p><code>truststore</code> до HTTPS. <code>yf_session verify=False</code> — обхід curl SSL на Windows.</p>",
    "q1": "<p>Survivorship-лічильник поточних членів. 2025 = 18, максимум серед повних років ≥ 2020. 224 імена &gt;20 років.</p>",
    "q2": "<p>S&amp;P YTD +11.9%. Б’ють лише Японія і Канада → 2. 3y/5y теж 2/10, 10y = 1/10.</p>",
    "q3": "<p>74 корекції ≥5%. Медіана глибини 7.99%. Топ-10 збігся з підказкою ДЗ.</p>",
    "q4": "<p>20 позитивних сюрпризів, медіана 2-day +0.35%. corr ≈ 0.22. Не став <code>limit=100</code>.</p>",
    "q5": "<p>Memory/RAM медіана YTD +155% vs SPX +12%. 18/22 б’ють індекс. Baseline P(up 5d) ~54–57%.</p>",
    "q6": "<p>SOX +59% YTD. VIX ~15, крива +0.39. Earnings 2-day часто мінус навіть після beat.</p>",
}

TITLES = {
    "setup": "Setup",
    "q1": "Q1 — S&amp;P 500 additions <span class='ans'>2025</span>",
    "q2": "Q2 — Indexes YTD <span class='ans'>2</span>",
    "q3": "Q3 — Corrections <span class='ans'>7.9864</span>",
    "q4": "Q4 — AMZN 2-day <span class='ans'>0.003528</span>",
    "q5": "Q5 — AI infra notebook",
    "q6": "Q6 — Metrics notebook",
}

hw, q5, q6 = load_nb(HW1), load_nb(Q5), load_nb(Q6)

# homework1.ipynb slices (include markdown headers so it reads as a notebook)
SLICES = {
    "setup": [0, 1, 2],
    "q1": [3, 4],
    "q2": [5, 6],
    "q3": [7, 8],
    "q4": [9, 10, 13, 14],
    "q5": list(range(len(q5["cells"]))),
    "q6": list(range(len(q6["cells"]))),
}
NBS = {"setup": hw, "q1": hw, "q2": hw, "q3": hw, "q4": hw, "q5": q5, "q6": q6}


def section(qid: str, active: bool = False) -> str:
    nb_html = render_notebook(NBS[qid], SLICES[qid])
    cls = "qpanel active" if active else "qpanel"
    src_file = {
        "q5": "q5-ai-infra-capstone/q5_ai_infra_capstone.ipynb",
        "q6": "q6-ai-metrics/q6_ai_metrics.ipynb",
    }.get(qid, "homework1.ipynb")
    return f"""
  <section class="{cls}" id="{qid}">
    <h2>{TITLES[qid]}</h2>
    <p class="filehint">Джерело: <code>{src_file}</code> · Copy cell → встав у Jupyter і Shift+Enter</p>
    <div class="itabs">
      <button class="itab" aria-selected="true" data-i="{qid}-nb">Ноутбук (клітинка за клітинкою)</button>
      <button class="itab" aria-selected="false" data-i="{qid}-task">Завдання</button>
      <button class="itab" aria-selected="false" data-i="{qid}-exp">Пояснення</button>
    </div>
    <div class="ipanel active" id="{qid}-nb">
      <div class="notebook">{nb_html}</div>
    </div>
    <div class="ipanel" id="{qid}-task">{TASKS[qid]}</div>
    <div class="ipanel" id="{qid}-exp">{EXPS[qid]}</div>
  </section>
"""


page = f"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HW1 2026 — Jupyter cells</title>
<style>
  :root {{
    --jp-in: #307FC1;
    --jp-out: #D84315;
    --jp-border: #e0e0e0;
    --jp-bg: #fff;
    --jp-code-bg: #f7f7f7;
    --ivory: #FAF9F5;
    --slate: #141413;
    --clay: #D97757;
    --olive: #788C5D;
    --sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    --serif: ui-serif, Georgia, serif;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--ivory); color:var(--slate); font-family:var(--sans); line-height:1.5; }}
  .wrap {{ max-width:980px; margin:0 auto; padding:24px 16px 72px; }}
  h1 {{ font-family:var(--serif); font-size:30px; margin:0 0 8px; }}
  h2 {{ font-family:var(--serif); font-size:22px; margin:0 0 6px; }}
  .eyebrow {{ font-family:var(--mono); font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--clay); }}
  .sub, .filehint {{ color:#666; font-size:14px; margin:0 0 12px; }}
  .tldr {{ background:#E3DACC; border-left:4px solid var(--clay); padding:10px 12px; margin:0 0 16px; }}
  .answers {{ display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin:0 0 16px; }}
  .card {{ background:#fff; border:1px solid var(--jp-border); padding:10px 12px; }}
  .card .k {{ font-family:var(--mono); font-size:11px; color:#666; }}
  .card .v {{ font-family:var(--serif); font-size:24px; }}
  .qtabs, .itabs {{ display:flex; flex-wrap:wrap; gap:6px; margin:0 0 10px; }}
  .qtab, .itab {{ border:1px solid #ccc; background:#fff; padding:7px 11px; cursor:pointer; font-size:13px; }}
  .qtab[aria-selected="true"] {{ background:var(--slate); color:#fff; border-color:var(--slate); }}
  .itab[aria-selected="true"] {{ background:var(--clay); color:#fff; border-color:var(--clay); }}
  .qpanel {{ display:none; background:#fff; border:1px solid var(--jp-border); padding:14px; }}
  .qpanel.active {{ display:block; }}
  .ipanel {{ display:none; }}
  .ipanel.active {{ display:block; }}
  .ans {{ background:var(--olive); color:#fff; padding:1px 7px; font-family:var(--mono); font-size:12px; }}
  .notebook {{ background:#fff; }}
  .jcell {{ display:flex; gap:8px; padding:8px 4px 10px; border-bottom:1px solid #f0f0f0; }}
  .jcell.jcode {{ flex-direction:column; gap:0; }}
  .jin, .jout {{ display:flex; gap:8px; width:100%; }}
  .jout {{ margin-top:4px; }}
  .jprompt {{ flex:0 0 72px; text-align:right; font-family:var(--mono); font-size:13px;
    padding-top:8px; user-select:none; }}
  .jcode .jin .jprompt {{ color:var(--jp-in); font-weight:600; }}
  .jout .jprompt {{ color:var(--jp-out); font-weight:600; }}
  .jbody {{ flex:1; min-width:0; position:relative; }}
  .jmd .jbody {{ padding:6px 8px 6px 0; }}
  .jmd h2 {{ font-size:22px; }}
  .jmd h3 {{ font-size:18px; margin:8px 0; }}
  .jmd p, .jmd li {{ margin:0 0 8px; }}
  pre.jinput {{ margin:0; padding:10px 12px; background:var(--jp-code-bg);
    border:1px solid var(--jp-border); border-radius:2px; overflow:auto;
    font-family:var(--mono); font-size:13px; line-height:1.45; white-space:pre; tab-size:4; }}
  pre.stdout, pre.stderr, pre.mdcode {{
    margin:0 0 8px; padding:8px 10px; overflow:auto; font-family:var(--mono);
    font-size:12.5px; line-height:1.4; white-space:pre; }}
  pre.stdout {{ background:#fff; }}
  pre.stderr {{ background:#fff5f5; color:#a33; }}
  img.plot {{ max-width:100%; height:auto; display:block; margin:6px 0; border:1px solid var(--jp-border); }}
  .copybtn {{ position:absolute; top:6px; right:8px; z-index:1; font-size:11px;
    border:1px solid #bbb; background:#fff; padding:3px 8px; cursor:pointer; }}
  .copybtn.ok {{ background:#e8f5e9; border-color:var(--olive); }}
  footer {{ margin-top:20px; color:#666; font-size:13px; }}
  @media (max-width:720px) {{ .answers {{ grid-template-columns:1fr 1fr; }} .jprompt {{ flex-basis:56px; font-size:11px; }} }}
</style>
</head>
<body>
<div class="wrap">
  <p class="eyebrow">SMA Zoomcamp 2026 · як у Jupyter</p>
  <h1>Homework 1 — клітинка за клітинкою</h1>
  <p class="sub">Формат як у notebook: <b>In [n]</b> повний код, під ним <b>Out [n]</b> повний вивід.
  Кнопка <b>Copy cell</b> — встав у свій .ipynb і Shift+Enter. Порядок: Setup → Q1 → Q2 → Q3 → Q4 в одному ядрі.
  Q5 і Q6 — окремі ноутбуки (свій Setup).</p>
  <div class="tldr">Форма: Q1=2025 · Q2=2 · Q3=7.9864 · Q4=0.003528</div>
  <div class="answers">
    <div class="card"><div class="k">Q1</div><div class="v">2025</div></div>
    <div class="card"><div class="k">Q2</div><div class="v">2</div></div>
    <div class="card"><div class="k">Q3</div><div class="v">7.9864</div></div>
    <div class="card"><div class="k">Q4</div><div class="v">0.003528</div></div>
  </div>
  <div class="qtabs">
    <button class="qtab" aria-selected="true" data-q="setup">Setup</button>
    <button class="qtab" aria-selected="false" data-q="q1">Q1</button>
    <button class="qtab" aria-selected="false" data-q="q2">Q2</button>
    <button class="qtab" aria-selected="false" data-q="q3">Q3</button>
    <button class="qtab" aria-selected="false" data-q="q4">Q4</button>
    <button class="qtab" aria-selected="false" data-q="q5">Q5 nb</button>
    <button class="qtab" aria-selected="false" data-q="q6">Q6 nb</button>
  </div>
{section("setup", True)}
{section("q1")}
{section("q2")}
{section("q3")}
{section("q4")}
{section("q5")}
{section("q6")}
  <footer>Клітинки 1:1 з .ipynb ·
  <code>homework1.ipynb</code> ·
  <code>q5-ai-infra-capstone/</code> ·
  <code>q6-ai-metrics/</code></footer>
</div>
<script>
(function () {{
  function activate(btns, panels, btn, attr) {{
    var key = btn.getAttribute(attr);
    btns.forEach(function (b) {{ b.setAttribute("aria-selected", b === btn ? "true" : "false"); }});
    panels.forEach(function (p) {{ p.classList.toggle("active", p.id === key); }});
  }}
  var qbtns = [].slice.call(document.querySelectorAll(".qtab"));
  var qpanels = [].slice.call(document.querySelectorAll(".qpanel"));
  qbtns.forEach(function (b) {{
    b.addEventListener("click", function () {{ activate(qbtns, qpanels, b, "data-q"); }});
  }});
  document.querySelectorAll(".qpanel").forEach(function (panel) {{
    var ib = [].slice.call(panel.querySelectorAll(".itab"));
    var ip = [].slice.call(panel.querySelectorAll(".ipanel"));
    ib.forEach(function (b) {{
      b.addEventListener("click", function () {{ activate(ib, ip, b, "data-i"); }});
    }});
  }});
  document.querySelectorAll(".copybtn").forEach(function (btn) {{
    btn.addEventListener("click", function () {{
      var code = btn.parentElement.querySelector("pre.jinput code");
      var t = code ? code.textContent : "";
      function done() {{ btn.textContent = "Copied"; btn.classList.add("ok");
        setTimeout(function () {{ btn.textContent = "Copy cell"; btn.classList.remove("ok"); }}, 1200); }}
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(t).then(done).catch(function () {{ fallback(t); done(); }});
      }} else {{ fallback(t); done(); }}
    }});
  }});
  function fallback(t) {{
    var ta = document.createElement("textarea");
    ta.value = t; document.body.appendChild(ta); ta.select();
    try {{ document.execCommand("copy"); }} catch (e) {{}}
    document.body.removeChild(ta);
  }}
}})();
</script>
</body>
</html>
"""

OUT.write_text(page, encoding="utf-8")
print("Wrote", OUT, "bytes", OUT.stat().st_size)
