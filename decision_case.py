"""Synthetic pricing decision: a competitor cut its fee - should we copy it?

Offline and deterministic. Fictional lenders, hypothetical rate event.
Interest is calculated from the annuity formula, never taken as an input.
"""
from __future__ import annotations

import html
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE = Path(__file__).resolve().parent
CASE = BASE / "fixtures" / "synthetic_decision_case.json"
D = Decimal
CENT = D("0.01")
APPLICATIONS = D("1000")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def annuity_interest(principal: Decimal, nominal_pct: Decimal, months: int) -> Decimal:
    """Total interest of an equal-instalment loan (last instalment absorbs rounding)."""
    r = nominal_pct / D(100) / D(12)
    payment = principal * r / (1 - (1 + r) ** -months)
    return money(payment * months - principal)


def max_nominal_pct(reference_rate_pct: Decimal) -> Decimal:
    """Polish cap on contractual interest: 2 x (NBP reference rate + 3.5 pp)."""
    return D(2) * (reference_rate_pct + D("3.5"))


def max_fee_pln(principal: Decimal, months: int) -> Decimal:
    """Art. 36a non-interest cap: 10% K + 10% K x n/365 (n approximated as months/12), max 45% K."""
    cap = principal * D("0.10") + principal * D("0.10") * D(months) / D(12)
    return min(cap, principal * D("0.45"))


def per_loan(interest: Decimal, fee: Decimal, costs: dict, pd: Decimal) -> Decimal:
    expected_loss = pd * D(costs["lgd"]) * D(costs["ead_at_default_pln"])
    return money(interest + fee - D(costs["funding_cost_pln"]) - D(costs["servicing_cost_pln"])
                 - D(costs["origination_cost_pln"]) - expected_loss)


def evaluate(case: dict) -> dict:
    if case.get("data_classification") != "SYNTHETIC_DEMO":
        raise ValueError("Only synthetic input is allowed")
    if case["event"].get("hypothetical") is not True:
        raise ValueError("The rate event must be labelled hypothetical")
    sc = case["scenario"]
    principal, months = D(sc["principal_pln"]), int(sc["months"])
    cap_rate = max_nominal_pct(D(case["event"]["reference_rate_month2_pct"]))
    cap_fee = max_fee_pln(principal, months)
    costs = case["our_costs_month2"]
    pd = D(costs["pd_12m"])
    marketing = APPLICATIONS * D(costs["marketing_cost_per_application_pln"])

    competitor = case["competitor"]
    for month, ref_key in (("month1", "reference_rate_month1_pct"), ("month2", "reference_rate_month2_pct")):
        offer = competitor[month]
        if D(offer["nominal_pct"]) > max_nominal_pct(D(case["event"][ref_key])):
            raise ValueError(f"Competitor {month} interest above legal cap")
        if D(offer["fee_pln"]) > cap_fee:
            raise ValueError(f"Competitor {month} fee above legal cap")

    options = {}
    for key, opt in case["options"].items():
        rate, fee, takeup = D(opt["nominal_pct"]), D(opt["fee_pln"]), D(opt["takeup_rate"])
        if rate > cap_rate:
            raise ValueError(f"{opt['label']}: interest above legal cap {cap_rate}%")
        if fee > cap_fee:
            raise ValueError(f"{opt['label']}: fee above legal cap {cap_fee}")
        if not D(0) < takeup <= D(1):
            raise ValueError("Take-up rate must be between 0 and 1")
        interest = annuity_interest(principal, rate, months)
        contribution = per_loan(interest, fee, costs, pd)
        loans = APPLICATIONS * takeup
        options[key] = {
            "label": opt["label"], "nominal_pct": str(rate), "fee_pln": str(money(fee)),
            "interest_pln": str(interest), "expected_loss_pln": str(money(pd * D(costs["lgd"]) * D(costs["ead_at_default_pln"]))),
            "contribution_per_loan_pln": str(contribution), "takeup_rate": str(takeup),
            "loans_per_1000_applications": f"{loans:.0f}",
            "profit_per_1000_applications_pln": str(money(loans * contribution - marketing)),
        }

    a, b = options["keep_fee"], options["copy_competitor"]
    a_profit, b_profit = D(a["profit_per_1000_applications_pln"]), D(b["profit_per_1000_applications_pln"])
    a_loans = D(a["loans_per_1000_applications"])
    break_even = (a_loans * D(a["contribution_per_loan_pln"])) / D(b["contribution_per_loan_pln"]) / APPLICATIONS

    st = case["stress_tests"]
    extra = D(b["loans_per_1000_applications"]) - a_loans
    risky = per_loan(D(b["interest_pln"]), D(b["fee_pln"]), costs, D(st["extra_customers_pd_12m"]))
    b_risky = money(a_loans * D(b["contribution_per_loan_pln"]) + extra * risky - marketing)
    a_lower = money(APPLICATIONS * D(st["keep_fee_takeup_if_customers_leave"]) * D(a["contribution_per_loan_pln"]) - marketing)
    # Take-up at which keeping our fee earns the same as copying (below it, copying wins).
    keep_floor = (b_profit + marketing) / D(a["contribution_per_loan_pln"]) / APPLICATIONS
    cap_rate_m1 = max_nominal_pct(D(case["event"]["reference_rate_month1_pct"]))
    interest_m1 = annuity_interest(principal, cap_rate_m1, months)
    for opt in (a, b):
        opt["customer_total_cost_pln"] = str(money(D(opt["interest_pln"]) + D(opt["fee_pln"])))

    return {
        "classification": "SYNTHETIC_DEMO",
        "question": "A competitor cut its fee. Should we copy it?",
        "legal_caps_month1": {"reference_rate_pct": case["event"]["reference_rate_month1_pct"],
                              "max_nominal_pct": str(cap_rate_m1), "interest_at_cap_pln": str(interest_m1)},
        "legal_caps_month2": {"reference_rate_pct": case["event"]["reference_rate_month2_pct"],
                              "max_nominal_pct": str(cap_rate), "max_fee_pln": str(money(cap_fee)),
                              "interest_at_cap_pln": str(annuity_interest(principal, cap_rate, months))},
        "interest_lost_per_loan_from_rate_cut_pln": str(money(interest_m1 - annuity_interest(principal, cap_rate, months))),
        "costs_per_loan": {k: costs[k] for k in ("funding_cost_pln", "servicing_cost_pln", "origination_cost_pln",
                                                 "pd_12m", "lgd", "ead_at_default_pln", "marketing_cost_per_application_pln")},
        "profit_change_copy_vs_keep_pct": str(((b_profit - a_profit) / a_profit * 100).quantize(D("0.1"), rounding=ROUND_HALF_UP)),
        "break_even_takeup_for_keep": str(keep_floor.quantize(D("0.0001"), rounding=ROUND_HALF_UP)),
        "competitor": {m: {**competitor[m], "interest_pln": str(annuity_interest(principal, D(competitor[m]["nominal_pct"]), months))}
                       for m in ("month1", "month2")},
        "options": options,
        "difference_copy_vs_keep_pln": str(money(b_profit - a_profit)),
        "break_even_takeup_for_copy": str(break_even.quantize(D("0.0001"), rounding=ROUND_HALF_UP)),
        "stress_tests": {
            "extra_customers_riskier": {"pd_12m": st["extra_customers_pd_12m"], "copy_profit_pln": str(b_risky),
                                        "difference_vs_keep_pln": str(money(b_risky - a_profit))},
            "keep_fee_loses_customers": {"takeup_rate": st["keep_fee_takeup_if_customers_leave"], "keep_profit_pln": str(a_lower),
                                         "difference_copy_vs_keep_pln": str(money(b_profit - a_lower))},
        },
        "conclusion": "Do not copy automatically. Copying pays off only if take-up reaches the break-even rate; test it in a controlled experiment and check the risk of the extra customers.",
        "not_modelled": case["not_modelled"],
    }


def pln(value: str) -> str:
    return f"{D(value):,.2f}"


def render(r: dict) -> str:
    h = lambda x: html.escape(str(x), quote=True)
    a, b = r["options"]["keep_fee"], r["options"]["copy_competitor"]
    m1, m2 = r["legal_caps_month1"], r["legal_caps_month2"]
    c1, c2 = r["competitor"]["month1"], r["competitor"]["month2"]
    co = r["costs_per_loan"]
    st = r["stress_tests"]
    pct = lambda v: f"{D(v) * 100:.0f}%"
    pct1 = lambda v: f"{D(v) * 100:.1f}%"
    fee_cut = pln(str(D(a["fee_pln"]) - D(b["fee_pln"])))
    marketing_total = str(D(co["marketing_cost_per_application_pln"]) * APPLICATIONS)
    extra = int(b["loans_per_1000_applications"]) - int(a["loans_per_1000_applications"])
    row = lambda name, va, vb, cls="": f'<tr class="{cls}"><th>{name}</th><td>{h(va)}</td><td>{h(vb)}</td></tr>'
    neg = lambda v: f"- {pln(v)}"
    per_loan_rows = "".join([
        row("Interest (annuity at the 14.0% cap)", pln(a["interest_pln"]), pln(b["interest_pln"])),
        row("Fee (non-interest cost)", pln(a["fee_pln"]), pln(b["fee_pln"])),
        row("Funding cost", neg(co["funding_cost_pln"]), neg(co["funding_cost_pln"])),
        row("Servicing cost", neg(co["servicing_cost_pln"]), neg(co["servicing_cost_pln"])),
        row("Origination cost", neg(co["origination_cost_pln"]), neg(co["origination_cost_pln"])),
        row(f"Expected loss (PD {pct(co['pd_12m'])} x LGD {pct(co['lgd'])} x EAD {pln(co['ead_at_default_pln'])})",
            neg(a["expected_loss_pln"]), neg(b["expected_loss_pln"])),
        row("Profit per loan", pln(a["contribution_per_loan_pln"]), pln(b["contribution_per_loan_pln"]), "total"),
    ])
    portfolio_rows = "".join([
        row("Take-up (loans per 100 applications)", pct(a["takeup_rate"]), pct(b["takeup_rate"]) + " (assumed)"),
        row("Loans", a["loans_per_1000_applications"], b["loans_per_1000_applications"]),
        row("Loans x profit per loan", pln(str(D(a["loans_per_1000_applications"]) * D(a["contribution_per_loan_pln"]))),
            pln(str(D(b["loans_per_1000_applications"]) * D(b["contribution_per_loan_pln"])))),
        row(f"Marketing (PLN {pln(co['marketing_cost_per_application_pln'])} per application)", neg(marketing_total), neg(marketing_total)),
        row("Profit", pln(a["profit_per_1000_applications_pln"]), pln(b["profit_per_1000_applications_pln"]), "total"),
    ])
    bullets = "".join(f"<li>{h(x)}</li>" for x in r["not_modelled"])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pricing Decision Case</title><style>
:root{{--ink:#142a3c;--muted:#5d7083;--line:#dce5ed;--paper:#f5f8fb;--accent:#2f6793;--good:#14675d;--goodbg:#e9f5f2;--amber:#77551f;--amberbg:#fbf5e7}}
*{{box-sizing:border-box}}body{{max-width:980px;margin:24px auto;padding:0 16px;font:15px/1.55 -apple-system,"Segoe UI",Arial,sans-serif;color:var(--ink);background:var(--paper)}}
section,header{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px;margin:14px 0}}
h1{{font-size:clamp(24px,4vw,32px);line-height:1.2;margin:10px 0 8px}}h2{{font-size:18px;margin:0 0 10px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{padding:8px;border-bottom:1px solid #e7ecf2;text-align:left;font-weight:400}}
td{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}thead th{{background:#f1f5f9;font-weight:700}}
tr.total th,tr.total td{{font-weight:750;border-top:2px solid var(--line)}}
.muted{{color:var(--muted);font-size:14px}}.big{{font-size:26px;font-weight:750}}
.tag{{display:inline-block;background:var(--amberbg);color:var(--amber);border:1px solid #efdbba;border-radius:6px;padding:3px 8px;font-size:12px;font-weight:700}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}
.box{{border:1px solid var(--line);border-radius:10px;padding:14px}}.box b{{display:block;font-size:20px;margin:4px 0}}
.decision{{background:var(--goodbg);border-color:#b6dcd2}}.decision h2{{color:var(--good)}}
.scroll{{overflow-x:auto}}a{{color:var(--accent)}}
</style></head><body>
<header><span class="tag">SYNTHETIC - FICTIONAL LENDERS, HYPOTHETICAL RATE CUT</span>
<h1>{h(r['question'])}</h1>
<p class="muted">Instalment loan, PLN 8,000 / 12 months, new customers. We compare two options in the same month, so the rate cut affects both equally.</p></header>

<section><h2>1. Why this matters in Poland</h2>
<p>Polish law caps the price of consumer loans in two ways:</p>
<ul><li><b>Interest</b> - at most 2 x (NBP reference rate + 3.5 pp). When the NBP cuts its rate, the cap falls for every lender right away.</li>
<li><b>Fees and other non-interest costs</b> - at most 10% of the loan + 10% per year, never above 45% (Art. 36a); here PLN {pln(m2['max_fee_pln'])}. Not linked to the NBP rate.</li></ul>
<p class="muted">Most non-bank lenders already price at or near these caps, so a rate cut lowers their income without any decision on their part.</p></section>

<section><h2>2. What happened</h2>
<div class="grid">
<div class="box"><span class="muted">NBP reference rate (hypothetical)</span><b>{h(m1['reference_rate_pct'])}% &rarr; {h(m2['reference_rate_pct'])}%</b>
<span class="muted">Interest cap {h(m1['max_nominal_pct'])}% &rarr; {h(m2['max_nominal_pct'])}%. Interest on the loan at the cap: PLN {pln(m1['interest_at_cap_pln'])} &rarr; {pln(m2['interest_at_cap_pln'])} (<b style="display:inline;font-size:inherit">- PLN {pln(r['interest_lost_per_loan_from_rate_cut_pln'])}</b> per loan, for everyone).</span></div>
<div class="box"><span class="muted">Competitor X (fictional)</span><b>Fee PLN {pln(c1['fee_pln'])} &rarr; {pln(c2['fee_pln'])}</b>
<span class="muted">On top of the lower interest, it cut its fee by PLN {fee_cut} to win customers. Customer pays PLN {pln(b['customer_total_cost_pln'])} instead of our PLN {pln(a['customer_total_cost_pln'])}.</span></div>
</div>
<p><b>The question:</b> keep our fee at PLN {pln(a['fee_pln'])}, or match the competitor at PLN {pln(b['fee_pln'])}?</p></section>

<section><h2>3. Profit per loan</h2><div class="scroll"><table>
<thead><tr><th>PLN per loan</th><th>{h(a['label'])}</th><th>{h(b['label'])}</th></tr></thead>{per_loan_rows}</table></div>
<p class="muted">Copying gives up PLN {fee_cut} on every loan. Interest and costs are the same in both options.</p></section>

<section><h2>4. Profit per 1,000 applications</h2><div class="scroll"><table>
<thead><tr><th>PLN per 1,000 applications</th><th>{h(a['label'])}</th><th>{h(b['label'])}</th></tr></thead>{portfolio_rows}</table></div>
<p>Copying brings {extra} more loans but <span class="big">PLN {pln(str(-D(r['difference_copy_vs_keep_pln'])))}</span> ({h(str(-D(r['profit_change_copy_vs_keep_pct'])))}%) less profit.</p>
<p class="muted">The extra take-up is an assumption, not a measured effect.</p></section>

<section><h2>5. When would the answer change?</h2><div class="grid">
<div class="box"><span class="muted">Copying wins if take-up rises above</span><b>{pct1(r['break_even_takeup_for_copy'])}</b><span class="muted">We assumed {pct(b['takeup_rate'])}. Will a PLN {fee_cut} lower fee bring that many more customers?</span></div>
<div class="box"><span class="muted">Copying also wins if keeping our fee drops take-up below</span><b>{pct1(r['break_even_takeup_for_keep'])}</b><span class="muted">Today {pct(a['takeup_rate'])}. Watch our own take-up after the competitor's move.</span></div>
</div>
<h3 style="font-size:15px;margin:16px 0 6px">Stress tests</h3><ul>
<li>The {extra} extra customers are riskier (PD {pct(st['extra_customers_riskier']['pd_12m'])} instead of {pct(co['pd_12m'])}): copying loses PLN {pln(str(-D(st['extra_customers_riskier']['difference_vs_keep_pln'])))}.</li>
<li>Keeping our fee loses some customers (take-up {pct(st['keep_fee_loses_customers']['takeup_rate'])}): keeping still earns PLN {pln(str(-D(st['keep_fee_loses_customers']['difference_copy_vs_keep_pln'])))} more.</li></ul></section>

<section class="decision"><h2>6. Decision</h2>
<p><b>Don't copy automatically.</b> Test the lower fee on a share of new applications and measure take-up and early defaults.</p>
<ul><li>Copy only if take-up rises above {pct1(r['break_even_takeup_for_copy'])} and the extra customers do not default more.</li>
<li>Reconsider if our own take-up falls below {pct1(r['break_even_takeup_for_keep'])} while we keep the fee.</li></ul>
<h3 style="font-size:15px;margin:14px 0 6px">Not modelled</h3><ul class="muted">{bullets}</ul></section>
<p class="muted">Fictional lenders and a hypothetical rate cut. Interest is calculated from the annuity formula; every option is checked against both legal caps. <a href="index.html">Back to overview</a></p>
</body></html>"""


def run(out_dir: Path, case_path: Path = CASE) -> dict:
    report = evaluate(json.loads(case_path.read_text(encoding="utf-8")))
    out_dir.mkdir(exist_ok=True)
    (out_dir / "decision_case.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (out_dir / "decision_case.html").write_text(render(report), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = run(BASE / "output")
    print("SYNTHETIC DECISION CASE | copy vs keep PLN", result["difference_copy_vs_keep_pln"],
          "| break-even take-up", result["break_even_takeup_for_copy"])
