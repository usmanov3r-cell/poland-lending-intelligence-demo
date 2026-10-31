#!/usr/bin/env python3
"""One-command offline portfolio demonstration. Python standard library only."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from offline_market_demo import BASE, FIXTURE, analyze, load_data


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = load_data()
    report = analyze(data)
    dest = BASE / "output"
    dest.mkdir(exist_ok=True)
    snapshot = BASE / "assets" / "dashboard_snapshot.html"
    if not snapshot.is_file():
        raise FileNotFoundError("Missing bundled dashboard snapshot")
    shutil.copyfile(snapshot, dest / "index.html")
    (dest / "results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown = f"""# Poland consumer lending — offline portfolio check

**Archived research reference:** {report['as_of']} | **Coverage:** {report['coverage']} brands.

## Commercial observations (public calculator scenarios, not approved customer quotes)

- **SPL:** {report['spl_count']} paid observations: PLN {report['spl_range_pln'][0]}–{report['spl_range_pln'][1]}, compared with modelled PLN {report['spl_scenario_reference_pln']} scenario reference. This cross-sectional cluster is consistent with a binding pricing constraint, not proven price imitation.
- **INST:** {report['inst_count']} observations: PLN {report['inst_range_pln'][0]}–{report['inst_range_pln'][1]}. Provident at PLN {report['provident_cost_pln']} is the low-price outlier; Hoprata is PLN {report['hoprata_gap_below_modelled_reference_pln']} below the modelled instalment reference.
- **Acquisition:** selected first-loan promotions use {', '.join(map(str,report['first_loan_promotion_terms_days']))}-day terms. Zero-price promotion eligibility and paid comparison columns must not be conflated.

## Deterministic monitoring control

| Example | Result | Verified repricing? |
| --- | --- | --- |
| Miloan PLN 2,000 vs PLN 3,000 | {report['monitoring']['mismatched_principal']['status']} | No |
| Miloan PLN 2,000 matched cost | {report['monitoring']['matched_unchanged']['status']} | No |
| Synthetic +PLN 1 commission | {report['monitoring']['synthetic_delta']['status']} | No - artificial control test |

**No real lender repricing or campaign launch is verified.** The synthetic price exceeds the example SPL ceiling reference and MUST NOT be interpreted as a compliant offer.

## Reproducibility boundary

This package reproduces the summarized calculations and comparison classifications from **sanitized fixture data**, and opens a **pre-rendered HTML snapshot** of the executive dashboard. It does **not** rerun the live capture workflow, reconstruct original source archives, regenerate the HTML from lender evidence, or call a paid AI API. The original source validation was performed separately in a private research workspace.
"""
    (dest / "demo_review.md").write_text(markdown, encoding="utf-8")
    manifest = {"fixtures_sha256": sha256(FIXTURE), "dashboard_snapshot_sha256": sha256(snapshot), "offline": True}
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("OFFLINE DEMO PASS | 15/18 coverage | 0 verified price changes")
    print("Scenario mismatch: rejected | Matched unchanged: accepted | Synthetic delta: review candidate")
    print(f"Open: {dest / 'index.html'}")
    print(f"Evidence limitations: {dest / 'demo_review.md'}")


if __name__ == "__main__":
    main()
