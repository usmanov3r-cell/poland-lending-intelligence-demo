import tempfile
import unittest
from pathlib import Path

from offline_market_demo import analyze, compare_price, load_data


class OfflineMarketDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.s = cls.data["miloan_observation_summaries"]

    def test_price_mismatch_rejected(self):
        value = compare_price(self.s["baseline"], self.s["mismatched_principal"])
        self.assertEqual(value["status"], "scenario_mismatch")
        self.assertIn("principal_pln", value["mismatch_fields"])
        self.assertFalse(value["candidate_price_change"])

    def test_matched_price_unchanged(self):
        self.assertEqual(compare_price(self.s["baseline"], self.s["matched_unchanged"])["status"], "no_change_observed")

    def test_synthetic_change_not_verified(self):
        result = compare_price(self.s["baseline"], self.s["synthetic_delta"])
        self.assertEqual(result["status"], "candidate_price_change")
        self.assertTrue(result["synthetic"])
        self.assertFalse(result["verified_repricing"])

    def test_customer_segment_blocks_comparison(self):
        changed = dict(self.s["baseline"], segment="confirmed_repeat")
        self.assertEqual(compare_price(self.s["baseline"], changed)["status"], "scenario_mismatch")

    def test_service_selection_blocks_comparison(self):
        changed = dict(self.s["baseline"], ancillary="insurance_selected")
        self.assertEqual(compare_price(self.s["baseline"], changed)["status"], "scenario_mismatch")

    def test_market_numbers(self):
        report = analyze(self.data)
        self.assertEqual(report["coverage"], "15/18")
        self.assertEqual(report["spl_range_pln"], ["239.83", "240.23"])
        self.assertEqual(report["inst_range_pln"], ["1159.0", "2236.07"])
        self.assertEqual(report["hoprata_gap_below_modelled_reference_pln"], "6.09")
        self.assertEqual(report["first_loan_promotion_terms_days"], [30, 61])

    def test_all_derived_statuses_have_zero_verified_changes(self):
        report = analyze(self.data)
        self.assertFalse(any(x["verified_repricing"] for x in report["monitoring"].values()))

    def test_synthetic_price_condition_not_reported_as_compliant(self):
        self.assertGreater(self.s["synthetic_delta"]["total_cost_pln"],
                           self.data["spl"]["statutory_scenario_reference_pln"])


if __name__ == "__main__":
    unittest.main()
