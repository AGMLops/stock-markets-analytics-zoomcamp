"""Execute Q5/Q6 notebooks without jupyter kernel (skip %pip)."""
from __future__ import annotations

import base64
import io
import os
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

os.environ["MPLBACKEND"] = "Agg"

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nbformat
from nbformat.v4 import new_output

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = [
    ROOT / "q5-ai-infra-capstone" / "q5_ai_infra_capstone.ipynb",
    ROOT / "q6-ai-metrics" / "q6_ai_metrics.ipynb",
]


def fig_outputs():
    outs = []
    for num in plt.get_fignums():
        fig = plt.figure(num)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        outs.append(
            new_output(
                "display_data",
                data={"image/png": b64, "text/plain": ["<Figure>"]},
                metadata={},
            )
        )
    plt.close("all")
    return outs


def run_notebook(path: Path) -> dict:
    nb = nbformat.read(path, as_version=4)
    ns: dict = {"__name__": "__main__"}
    n_ok = 0
    n_err = 0
    last_err = None
    exec_count = 0

    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        src = "".join(cell.source)
        lines = []
        for line in src.splitlines(keepends=True):
            if line.lstrip().startswith("%pip") or line.lstrip().startswith("%matplotlib"):
                lines.append("# " + line.lstrip() if not line.startswith("#") else line)
            else:
                lines.append(line)
        src = "".join(lines)
        exec_count += 1
        stdout = io.StringIO()
        stderr = io.StringIO()
        outs = []
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = exec(compile(src, str(path), "exec"), ns, ns)
            text = stdout.getvalue()
            err_text = stderr.getvalue()
            if text:
                outs.append(new_output("stream", name="stdout", text=text))
            if err_text:
                outs.append(new_output("stream", name="stderr", text=err_text))
            outs.extend(fig_outputs())
            cell["outputs"] = outs
            cell["execution_count"] = exec_count
            n_ok += 1
        except Exception as exc:
            n_err += 1
            last_err = f"{path.name} cell {exec_count}: {exc}"
            tb = traceback.format_exc()
            text = stdout.getvalue()
            if text:
                outs.append(new_output("stream", name="stdout", text=text))
            outs.append(
                new_output(
                    "error",
                    ename=type(exc).__name__,
                    evalue=str(exc),
                    traceback=tb.splitlines(),
                )
            )
            plt.close("all")
            cell["outputs"] = outs
            cell["execution_count"] = exec_count
            print("FAIL", last_err, file=sys.stderr)

    nbformat.write(nb, path)
    return {"path": str(path), "ok": n_ok, "err": n_err, "last_err": last_err}


if __name__ == "__main__":
    summary = []
    for nb_path in NOTEBOOKS:
        print("===", nb_path.name, flush=True)
        summary.append(run_notebook(nb_path))
    print("SUMMARY")
    for row in summary:
        print(row)
