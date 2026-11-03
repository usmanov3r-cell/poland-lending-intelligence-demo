"""Build the GitHub Pages site in docs/ (offline, deterministic).

docs/index.html          landing page
docs/dashboard.html      copy of the bundled market dashboard
docs/decision_case.html  synthetic pricing decision case
Run after any change to the dashboard or the decision case:  python build_site.py
"""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

from decision_case import CASE, evaluate, render

BASE = Path(__file__).resolve().parent
SITE = BASE / "docs"
DASHBOARD = BASE / "assets" / "dashboard_snapshot.html"
REPO = "https://github.com/usmanov3r-cell/poland-lending-intelligence-demo"


def landing(case: dict) -> str:
    a, b = case["options"]["keep_fee"], case["options"]["copy_competitor"]
    keep, copy = float(a["profit_per_1000_applications_pln"]), float(b["profit_per_1000_applications_pln"])
    less = f"{(keep - copy) / keep * 100:.0f}"
    fee_cut = f"{float(a['fee_pln']) - float(b['fee_pln']):,.0f}"
    e = lambda s: html.escape(s, quote=True)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Poland Lending Intelligence</title>
<meta name="description" content="Competitor pricing research for Polish non-bank consumer lending, with a pricing decision case.">
<style>
:root{{--ink:#142a3c;--muted:#5d7083;--line:#dce5ed;--paper:#f5f8fb;--accent:#2f6793;--amber:#77551f;--amberbg:#fbf5e7}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}
.wrap{{max-width:980px;margin:0 auto;padding:0 16px}}
header{{background:linear-gradient(113deg,#12283f,#1d3d5d);color:#fff;padding:28px 0 46px}}
.eyebrow{{font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#afc7d9;font-weight:700}}
h1{{font-size:clamp(24px,4vw,32px);line-height:1.15;letter-spacing:-.6px;margin:8px 0 0}}
.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:-30px}}
.fact,a.card{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px}}
.fact .v{{font-size:22px;font-weight:750;letter-spacing:-.4px}}.fact .k{{font-size:13px;color:var(--muted);margin-top:2px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;margin-top:14px}}
a.card{{display:block;color:inherit;text-decoration:none;padding:16px}}a.card:hover{{border-color:var(--accent)}}
a.card h3{{margin:6px 0 4px;font-size:17px}}a.card p{{margin:0;color:var(--muted);font-size:13px}}
.go{{display:inline-block;margin-top:8px;color:var(--accent);font-weight:700;font-size:13px}}
.tag{{display:inline-block;font-size:11px;font-weight:700;border-radius:6px;padding:2px 8px;background:#e9f1f7;color:#2f5d80}}
.tag.syn{{background:var(--amberbg);color:var(--amber)}}
.note{{font-size:12px;color:var(--muted);margin:14px 0 24px}}.note a{{color:var(--accent)}}
@media(max-width:600px){{header{{padding:20px 0 40px}}.eyebrow{{font-size:10px}}.facts,.cards{{gap:8px}}.cards{{margin-top:8px}}.fact{{padding:10px 14px}}.fact .v{{font-size:19px}}.fact .k{{font-size:12px}}a.card{{padding:12px 14px}}a.card h3{{font-size:16px;margin:4px 0 2px}}}}
</style></head><body>
<header><div class="wrap"><div class="eyebrow">Poland - non-bank consumer lending - Oct 2026</div>
<h1>The legal price cap shapes how Polish lenders compete.</h1></div></header>
<main class="wrap">
<div class="facts">
<div class="fact"><div class="v">99.8%</div><div class="k">of the legal maximum, or more: what all 11 paid short-term loans cost (PLN 2,000 / 30 days)</div></div>
<div class="fact"><div class="v">15 of 18</div><div class="k">lenders with a comparable price; new and repeat customers kept apart</div></div>
<div class="fact"><div class="v">Don't copy</div><div class="k">Matching a competitor's PLN {e(fee_cut)} fee cut brings more customers but {e(less)}% less profit. (Fictional case)</div></div>
</div>
<div class="cards">
<a class="card" href="dashboard.html"><span class="tag">Public calculator data</span><h3>Market dashboard &rarr;</h3>
<p>Prices of 15 lenders against the legal caps, first-loan promotions, and price-change checks.</p></a>
<a class="card" href="decision_case.html"><span class="tag syn">Synthetic</span><h3>Pricing decision case &rarr;</h3>
<p>A competitor cuts its fee after an NBP rate cut. Keep or copy? Step by step, with break-even and stress tests.</p></a>
</div>
<p class="note">Snapshot from public calculators, 30-31 Oct 2026 - not approved offers. Numbers come from code; AI only ranks existing evidence.
<a href="{REPO}">Code and method on GitHub</a> - Ren, consumer lending product &amp; compliance.</p>
</main></body></html>
"""


def build(site: Path = SITE) -> list[Path]:
    case = evaluate(json.loads(CASE.read_text(encoding="utf-8")))
    site.mkdir(exist_ok=True)
    shutil.copyfile(DASHBOARD, site / "dashboard.html")
    (site / "decision_case.html").write_text(render(case), encoding="utf-8")
    (site / "index.html").write_text(landing(case), encoding="utf-8")
    (site / ".nojekyll").write_text("", encoding="utf-8")
    return [site / n for n in ("index.html", "dashboard.html", "decision_case.html")]


if __name__ == "__main__":
    for path in build():
        print("Built:", path.relative_to(BASE))
    print("Push, then enable GitHub Pages: Settings > Pages > Branch main, folder /docs")
