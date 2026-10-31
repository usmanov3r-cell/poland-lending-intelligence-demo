# Five-minute interview demo — Head of Lending / Product Strategy

## 0:00–0:40 — Business problem

“Public lending prices are easy to collect and easy to misinterpret. A calculator can default to another principal, a first-loan promotion can depend on consents, and a cost ceiling can make lenders appear to copy each other. I built this agent to turn public observations into **auditable business questions**, not to automate unsupported market conclusions.”

**Show:** Dashboard header and coverage count (15/18).

## 0:40–1:50 — Commercial finding, not technology

“Across 11 selected paid SPL observations for PLN 2,000 / 30 days, disclosed costs cluster at PLN 239.83–240.23, close to a PLN 240.27 statutory reference. My interpretation is that the ceiling constrains visible price differentiation. The next questions are 0% acquisition, customer eligibility, limits, speed, and economics—not ‘who is cheapest by 40 groszy?’”

“On PLN 8,000 / 12-month instalments, Provident is the outlier at PLN 1,159, while Hoprata is at PLN 2,236.07. These public scenarios are not risk-matched; the investigation is to decompose economics rather than label one lender more profitable.”

**Show:** Both charts, ceiling markers, Provident, Hoprata.

## 1:50–2:50 — The real monitoring example

“On 31 October the live Miloan calculator initially showed PLN 3,000 rather than PLN 2,000. A naive monitor might report a 50% increase in cost. The matcher rejected it because principal differed. After selecting PLN 2,000, both the promotional PLN 0 and standard PLN 240.20 costs matched the archived observation.”

**Show:** Mismatch then matched-unchanged cards.

## 2:50–3:40 — Positive path, explicitly synthetic

“To test that the system does detect changes, I ran an in-memory +PLN 1 commission change. It becomes a *review candidate*, never a verified lender repricing. The amount is deliberately above the modelled legal reference, underscoring why this is a control test, not product guidance.”

**Show:** Synthetic label and candidate status.

## 3:40–4:30 — AI decision quality

“The AI only prioritizes finding IDs already in the evidence register. The accepted output selected F04 eligibility conflict, F01 SPL ceiling-cluster question and F02 instalment dispersion. There were zero actual new events. If AI invents an event ID, the gate rejects the response.”

**Show:** Executive investigations and quality-control cards.

## 4:30–5:00 — Practical value and honest boundaries

“This demonstrates where a lending product organization can spend analyst time: monitor contract/eligibility discrepancies and review actual changes, rather than produce unverified market alerts. It is a portfolio prototype: public observations are not approved offers, and I have not validated lender profitability or run a production-grade surveillance service.”

## Likely interview follow-ups

**Why not scrape all lenders daily?** Because repeatability, eligibility conditions, provenance and the event threshold matter more than the crawl count. Start with reliable comparable coverage and expand by business decision value.

**Why use AI?** To triage and prioritize supported investigations. Financial calculations, price-change classification and evidence requirements remain deterministic.

**Why 15/18, not 18/18?** Unresolved identity (Easypin), conflicting promotional eligibility (InstaFin), and conditional pricing (SuperGrosz) were excluded rather than forced into a precise-looking comparison.

**What comes next?** A cleared, reproducible offline sample and a real matched positive change observed over time; later, cohort-based unit economics using internal lender data where authorized.
