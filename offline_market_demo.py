"""Deterministic, safe demonstration based on summarized public observations.

This is a miniature standalone release harness, NOT the original evidence
capture or AI integration pipeline. No network, private data or API access.
"""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

BASE = Path(__file__).resolve().parent
FIXTURE = BASE / "fixtures" / "sanitized_market_snapshot.json"
MATCH_KEYS = (
    "principal_pln", "duration_days", "price_column", "segment",
    "ancillary", "offer_conditions",
)
PRICE_KEYS = ("interest_pln", "commission_pln", "total_cost_pln", "rrso_percent")


def load_data(path: Path = FIXTURE) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def d(value: object) -> Decimal:
    return Decimal(str(value))


def compare_price(baseline: dict, current: dict) -> dict:
    """No repricing conclusion without an identical scenario and conditions."""
    differences = [key for key in MATCH_KEYS if baseline.get(key) != current.get(key)]
    if differences:
        return {"status": "scenario_mismatch", "mismatch_fields": differences,
                "candidate_price_change": False, "verified_repricing": False}
    changed = [key for key in PRICE_KEYS if d(baseline[key]) != d(current[key])]
    if changed:
        return {"status": "candidate_price_change", "changed_fields": changed,
                "candidate_price_change": True, "verified_repricing": False,
                "synthetic": bool(current.get("synthetic"))}
    return {"status": "no_change_observed", "changed_fields": [],
            "candidate_price_change": False, "verified_repricing": False}


def analyze(data: dict) -> dict:
    assert data["dataset_type"] == "sanitized_summary_from_archived_public_observations"
    spl = data["spl"]["paid_observations"]
    inst = data["inst"]["observations"]
    assert len(spl) == 11 and len(inst) == 4
    assert data["roster_brands"] == 18 and data["priced_brands"] == 15
    assert len({x["brand"] for x in spl + inst}) == 15
    spl_costs = [d(x["borrow_cost_pln"]) for x in spl]
    inst_costs = [d(x["borrow_cost_pln"]) for x in inst]
    reference_spl = d(data["spl"]["statutory_scenario_reference_pln"])
    reference_inst = d(data["inst"]["modelled_annuity_reference_pln"])
    assert min(spl_costs) <= max(spl_costs) <= reference_spl
    assert min(inst_costs) <= max(inst_costs) <= reference_inst
    observed = data["miloan_observation_summaries"]
    results = {
        "mismatched_principal": compare_price(observed["baseline"], observed["mismatched_principal"]),
        "matched_unchanged": compare_price(observed["baseline"], observed["matched_unchanged"]),
        "synthetic_delta": compare_price(observed["baseline"], observed["synthetic_delta"]),
    }
    assert [results[k]["status"] for k in results] == [
        "scenario_mismatch", "no_change_observed", "candidate_price_change"
    ]
    assert all(not x["verified_repricing"] for x in results.values())
    assert results["synthetic_delta"]["synthetic"] is True
    return {
        "market": data["market"],
        "as_of": data["snapshot_date"],
        "coverage": f'{data["priced_brands"]}/{data["roster_brands"]}',
        "spl_count": len(spl),
        "spl_range_pln": [str(min(spl_costs)), str(max(spl_costs))],
        "spl_scenario_reference_pln": str(reference_spl),
        "inst_count": len(inst),
        "inst_range_pln": [str(min(inst_costs)), str(max(inst_costs))],
        "inst_modelled_reference_pln": str(reference_inst),
        "provident_cost_pln": str(next(d(x["borrow_cost_pln"]) for x in inst if x["brand"] == "Provident")),
        "hoprata_gap_below_modelled_reference_pln": str(reference_inst - next(d(x["borrow_cost_pln"]) for x in inst if x["brand"] == "Hoprata")),
        "first_loan_promotion_terms_days": sorted(set(x["advertised_term_days"] for x in data["first_loan_promotions"])),
        "monitoring": results,
        "verified_market_price_changes": 0,
        "note": "Fixture-only reproduction; the original private archived evidence and paid AI run are not included."
    }
