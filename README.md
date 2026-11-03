# AI market discovery for non-bank consumer lending - Poland example

Finds and compares competitor offers from public sources: prices, promotions,
new vs repeat customers. Every price change is checked against evidence before
it is reported, and findings are turned into pricing decisions.

Built for Poland first. The method - fixed loan scenarios, evidence checks,
legal-cap reference - can be adapted to other markets (see below).

Poland scenarios: short-term loans (SPL, PLN 2,000 / 30 days) and instalment
loans (INST, PLN 8,000 / 12 months).

**Live demo (no install):** https://usmanov3r-cell.github.io/poland-lending-intelligence-demo/

**Key finding:** all 11 paid short-term loans cost 99.8% of the legal maximum
(PLN 240.27) or more, for new and repeat borrowers alike. Lenders compete on
free first loans, loan limits and speed, not on price.

## What is inside

- 18 lenders tracked; 15 with prices (11 SPL, 4 INST), captured 30-31 Oct 2026
  from public calculators.
- New and repeat borrower prices shown separately, never pooled.
- Price-change check: rejects different loan amounts, accepts unchanged
  prices, flags a test price change for review, never as verified.
- Legal cost-limit reference for each scenario.
- AI-assisted: AI ranks and explains evidence; code does every calculation.

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

## Adapting to another market

The checks and the decision case are generic. To run it for another market, change:

- **Lender list** - brands, products, official websites.
- **Loan scenarios** - the standard amount and term to compare.
- **Legal caps** - the local interest and fee limits (Poland: 2 x (NBP rate + 3.5 pp) and Art. 36a).
- **Sources** - local regulator and central-bank pages for news and rate changes.

## Read more

- [docs/FIVE_MINUTE_DEMO.md](docs/FIVE_MINUTE_DEMO.md) - 5-minute walkthrough
- [docs/METHODOLOGY_AND_SOURCES.md](docs/METHODOLOGY_AND_SOURCES.md) - methods and legal sources

Author: Ren - consumer lending product & compliance.
