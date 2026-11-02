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

## Run it (2 minutes)

Needs Python 3.10+. No extra packages, no internet, no API key.

    python run_demo.py
    python -m unittest discover -s tests -q

Then open `output/index.html` (dashboard) and `output/demo_review.md` (summary).

## Limitations

- Public calculator prices are not approved offers; eligibility differs.
- Prices are a snapshot (30-31 Oct 2026), not live monitoring.
- No AI runs in this demo; the dashboard shows a saved result of an
  earlier evidence-gated AI review.
- The +PLN 1 price change is synthetic, for testing only.
- Legal limits use the NBP rate valid at capture date; they change with NBP decisions.
- Research prototype, not a production service.

## Read more

- [docs/FIVE_MINUTE_DEMO.md](docs/FIVE_MINUTE_DEMO.md) - 5-minute walkthrough
- [docs/METHODOLOGY_AND_SOURCES.md](docs/METHODOLOGY_AND_SOURCES.md) - methods and legal sources

Author: Ren - consumer lending product & compliance (Baltics, Poland).
