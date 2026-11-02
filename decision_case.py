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

    return {
        "classification": "SYNTHETIC_DEMO",
        "question": "A competitor cut its fee. Should we copy it?",
        "legal_caps_month2": {"max_nominal_pct": str(cap_rate), "max_fee_pln": str(money(cap_fee))},
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
    rows = [("Interest (annuity, 12 months)", "interest_pln"), ("Fee", "fee_pln"),
            ("Expected loss (PD x LGD x EAD)", "expected_loss_pln"), ("Contribution per loan", "contribution_per_loan_pln"),
            ("Take-up rate", "takeup_rate"), ("Loans per 1,000 applications", "loans_per_1000_applications"),
            ("Profit per 1,000 applications", "profit_per_1000_applications_pln")]
    def cell(key: str, value: str) -> str:
        if key == "takeup_rate":
            return f"{D(value) * 100:.0f}%"
        if key == "loans_per_1000_applications":
            return value
        return pln(value)
    table = "".join(f"<tr><th>{h(n)}</th><td>{h(cell(k, a[k]))}</td><td>{h(cell(k, b[k]))}</td></tr>" for n, k in rows)
    c1, c2 = r["competitor"]["month1"], r["competitor"]["month2"]
    st = r["stress_tests"]
    be = D(r["break_even_takeup_for_copy"]) * 100
    bullets = "".join(f"<li>{h(x)}</li>" for x in r["not_modelled"])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pricing Decision Case</title><style>
body{{max-width:980px;margin:28px auto;padding:0 16px;font:15px/1.55 -apple-system,"Segoe UI",Arial,sans-serif;color:#142a3c;background:#f5f8fb}}
section,header{{background:#fff;border:1px solid #dce5ed;border-radius:12px;padding:20px;margin:14px 0}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;border-bottom:1px solid #e7ecf2;text-align:left}}
td{{text-align:right;font-variant-numeric:tabular-nums}}thead th{{background:#f1f5f9}}.muted{{color:#607283}}
.big{{font-size:26px;font-weight:750}}.tag{{display:inline-block;background:#fbf5e7;color:#77551f;border:1px solid #efdbba;border-radius:6px;padding:3px 8px;font-size:12px;font-weight:700}}
</style></head><body>
<header><span class="tag">SYNTHETIC - FICTIONAL LENDERS, HYPOTHETICAL RATE EVENT</span>
<h1>{h(r['question'])}</h1><p class="muted">PLN 8,000 / 12 months, new customers. Both options are compared in the same month, so the rate cut affects them equally.</p></header>
<section><h2>1. What happened</h2><p>Hypothetical NBP cut: legal interest cap falls to {h(r['legal_caps_month2']['max_nominal_pct'])}%. Fee cap stays PLN {pln(r['legal_caps_month2']['max_fee_pln'])}.</p>
<p>{h('Competitor X (fictional)')}: Month 1 fee PLN {pln(c1['fee_pln'])} + interest PLN {pln(c1['interest_pln'])} at {h(c1['nominal_pct'])}%; Month 2 fee PLN {pln(c2['fee_pln'])} + interest PLN {pln(c2['interest_pln'])} at {h(c2['nominal_pct'])}%.</p></section>
<section><h2>2. Our two options</h2><table><thead><tr><th>Per loan / per 1,000 applications (PLN)</th><th>{h(a['label'])}</th><th>{h(b['label'])}</th></tr></thead>{table}</table>
<p class="muted">Costs per loan in both options: funding 300, servicing 110, origination 85. Marketing: PLN 40 per application. The take-up increase is an assumption, not a measured effect.</p>
<p>Difference (copy vs keep): <span class="big">PLN {pln(r['difference_copy_vs_keep_pln'])}</span> per 1,000 applications</p></section>
<section><h2>3. Break-even</h2><p>Copying pays off only if take-up rises from {D(a['takeup_rate'])*100:.0f}% to <b>{be:.1f}%</b>. Business question: will a PLN {pln(str(D(a['fee_pln'])-D(b['fee_pln'])))} lower fee bring that many more customers?</p></section>
<section><h2>4. Stress tests</h2><ul>
<li>Extra customers are riskier (PD {D(st['extra_customers_riskier']['pd_12m'])*100:.0f}% instead of 10%): copy vs keep = PLN {pln(st['extra_customers_riskier']['difference_vs_keep_pln'])}.</li>
<li>Keeping our fee loses customers (take-up {D(st['keep_fee_loses_customers']['takeup_rate'])*100:.0f}%): copy vs keep = PLN {pln(st['keep_fee_loses_customers']['difference_copy_vs_keep_pln'])}.</li></ul></section>
<section><h2>5. Decision</h2><p><b>{h(r['conclusion'])}</b></p><h3>Not modelled</h3><ul>{bullets}</ul></section>
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
