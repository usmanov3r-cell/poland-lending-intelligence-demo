# Public portfolio demonstration. Offline, reproducible research example using sanitized observations and synthetic monitoring tests. Not a live lending-price monitoring service.

**Commercial research prototype | 31 October 2026 snapshot | Poland**

> **Lending insight:** 11 selected paid short-term-loan public observations of PLN 2,000/30 days cost PLN 239.83–240.23 versus a modelled PLN 240.27 scenario legal-cost reference. The narrow range is consistent with a price ceiling constraining *visible* standard pricing. Competitive investigation shifts toward first-loan acquisition promotions, eligibility, limits, servicing and repeat-customer economics. These are questions for further measurement, not measured drivers of profitability.

**15/18** lender brands have a recorded public scenario price in the frozen research roster; this is not market-share coverage. In 4 observed PLN 8,000/12-month instalment cases, Provident is the low-cost outlier at PLN 1,159 and Hoprata is PLN 6.09 below the *modelled* instalment reference. Borrower risk and eligibility are not matched.

## One-command offline demonstration

Requires Python 3.10+ only, **no pip installs, `.env`, private data, browser automation or API spend**.

```bash
python run_demo.py
python -m unittest discover -s tests -v
```

On Windows Git Bash, open the visual dashboard:

```bash
start "" "output/index.html"
```

Results:

- `output/index.html` — standalone **pre-rendered** executive dashboard (commercial narrative, pricing context, new vs returning customers, regulatory notes and monitoring logic).
- `output/demo_review.md` — generated commercial summary and control-test outcomes from supplied safe fixture.
- `output/results.json` — computed control classifications.
- `output/manifest.json` — SHA256 checksums for the supplied fixture and static dashboard.

## What is reproducible?

The control cases are computed from the shipped safe fixture, not hardcoded result labels:

1. **Different principal** — Miloan PLN 2,000 versus PLN 3,000: `scenario_mismatch` (not repricing).
2. **Same terms and price** — Miloan PLN 2,000 on two dates: `no_change_observed`.
3. **Artificial commission change** — +PLN 1: `candidate_price_change`, requiring human review; **not** a verified event or legally valid price example.

The HTML is a saved *snapshot*, not an output independently regenerated from raw primary lender evidence. This standalone pack is not the full private research agent. It demonstrates its public-facing findings and a self-contained subset of its deterministic monitoring logic. The private development project also includes browser capture, audit trails, and separately authorized AI prioritization, which **are not reproduced here**.

## Evidence boundaries

- Observed public pricing is not a personalized approved offer.
- Promo examples have lender-specific new-customer eligibility conditions; 61-day and 30-day campaigns cannot be treated as identical scenarios.
- Similar prices at one point in time do not prove imitation or a historical price-compression trend.
- Scenario legal-cost references depend on assumptions and then-current Polish law and are not universal price ceilings.
- The sanitized fixture contains manually summarized historical data, **not** the underlying screenshot/hash evidence or verified live offers.
- Market-price and regulatory statements are historical to 31 October 2026 and must be refreshed for later use.
- No AI inference, production collections or credit decisions occur in this released runner.

Read `docs/FIVE_MINUTE_DEMO.md` for the interview presentation and `docs/METHODOLOGY_AND_SOURCES.md` for methodology and reference links.

## Publication status

**Release candidate, not published.** Review the content, source rights and compliance implications before making a new GitHub repository public. Keep the original development repository private; its Git history may contain older research files.
