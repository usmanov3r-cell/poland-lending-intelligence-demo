# Poland Lending Market Intelligence - offline demo

Competitor pricing research for Polish non-bank consumer lending:
short-term loans (SPL, PLN 2,000 / 30 days) and instalment loans
(INST, PLN 8,000 / 12 months).

**Key finding:** paid short-term loan prices sit within PLN 0.44 of the
legal cost limit (PLN 240.27), for new and repeat borrowers alike.
Lenders compete on free first loans, loan limits and speed, not on price.

## What is inside

- 18 lenders tracked; 15 with prices (11 SPL, 4 INST), captured 30-31 Oct 2026
  from public calculators.
- New and repeat borrower prices shown separately, never pooled.
- Price-change check: rejects different loan amounts, accepts unchanged
  prices, flags a test price change for review, never as verified.
- Legal cost-limit reference for each scenario.

## Pricing decision case (synthetic)

A competitor cuts its fee after an NBP rate cut. Should we copy it?
Fictional lenders, PLN 8,000 / 12 months, both options in the same month.

| Per 1,000 applications | A: Keep fee (1,400) | B: Copy (1,250) |
|---|---|---|
| Profit per loan | 1,074.56 | 924.56 |
| Loans taken | 350 | 380 (assumed) |
| **Profit** | **336,096** | **311,333** |

Copying loses PLN 24,763. It pays off only if take-up rises from 35% to 40.7%.
If the extra customers are riskier (PD 15%), the loss grows to PLN 31,513.
Full calculation: `output/decision_case.html`.

## Run it (2 minutes)

Needs Python 3.10+. No extra packages, no internet, no API key.

    python run_demo.py
    python -m unittest discover -s tests -q

Then open `output/index.html` (dashboard), `output/decision_case.html` (decision case)
and `output/demo_review.md` (summary).

## Limitations

- Public calculator prices are not approved offers; eligibility differs.
- Prices are a snapshot (30-31 Oct 2026), not live monitoring.
- No AI runs in this demo; the dashboard shows a saved result of an
  earlier evidence-gated AI review.
- The +PLN 1 price change and the decision case are synthetic, for illustration only.
- Legal limits use the NBP rate valid at capture date; they change with NBP decisions.
- Research prototype, not a production service.

## Read more

- [docs/FIVE_MINUTE_DEMO.md](docs/FIVE_MINUTE_DEMO.md) - 5-minute walkthrough
- [docs/METHODOLOGY_AND_SOURCES.md](docs/METHODOLOGY_AND_SOURCES.md) - methods and legal sources

Author: Ren - consumer lending product & compliance (Baltics, Poland).
