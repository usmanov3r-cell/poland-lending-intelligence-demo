import copy
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from decision_case import CASE, annuity_interest, evaluate, max_fee_pln, max_nominal_pct, run


class DecisionCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads(CASE.read_text(encoding="utf-8"))
        cls.r = evaluate(cls.case)

    def test_interest_from_annuity_formula(self):
        self.assertEqual(annuity_interest(Decimal("8000"), Decimal("14.5"), 12), Decimal("642.16"))
        self.assertEqual(annuity_interest(Decimal("8000"), Decimal("14.0"), 12), Decimal("619.56"))

    def test_legal_caps(self):
        self.assertEqual(max_nominal_pct(Decimal("3.75")), Decimal("14.50"))
        self.assertEqual(max_nominal_pct(Decimal("3.50")), Decimal("14.00"))
        self.assertEqual(max_fee_pln(Decimal("8000"), 12), Decimal("1600"))

    def test_hand_calculation(self):
        a, b = self.r["options"]["keep_fee"], self.r["options"]["copy_competitor"]
        self.assertEqual(a["contribution_per_loan_pln"], "1074.56")
        self.assertEqual(b["contribution_per_loan_pln"], "924.56")
        self.assertEqual(a["profit_per_1000_applications_pln"], "336096.00")
        self.assertEqual(b["profit_per_1000_applications_pln"], "311332.80")
        self.assertEqual(self.r["difference_copy_vs_keep_pln"], "-24763.20")
        self.assertEqual(self.r["break_even_takeup_for_copy"], "0.4068")

    def test_stress_tests(self):
        st = self.r["stress_tests"]
        self.assertEqual(st["extra_customers_riskier"]["difference_vs_keep_pln"], "-31513.20")
        self.assertEqual(st["keep_fee_loses_customers"]["difference_copy_vs_keep_pln"], "-3272.00")

    def test_interest_above_new_cap_rejected(self):
        bad = copy.deepcopy(self.case)
        bad["options"]["copy_competitor"]["nominal_pct"] = "14.5"
        with self.assertRaises(ValueError):
            evaluate(bad)

    def test_competitor_above_cap_rejected(self):
        bad = copy.deepcopy(self.case)
        bad["competitor"]["month2"]["nominal_pct"] = "14.5"
        with self.assertRaises(ValueError):
            evaluate(bad)

    def test_fee_above_cap_rejected(self):
        bad = copy.deepcopy(self.case)
        bad["options"]["keep_fee"]["fee_pln"] = "1600.01"
        with self.assertRaises(ValueError):
            evaluate(bad)

    def test_only_synthetic_and_hypothetical(self):
        bad = copy.deepcopy(self.case)
        bad["data_classification"] = "REAL"
        with self.assertRaises(ValueError):
            evaluate(bad)
        bad = copy.deepcopy(self.case)
        bad["event"]["hypothetical"] = False
        with self.assertRaises(ValueError):
            evaluate(bad)

    def test_html_written_and_escaped(self):
        bad = copy.deepcopy(self.case)
        bad["not_modelled"] = ["<script>x</script>"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "case.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            run(Path(tmp), path)
            page = (Path(tmp) / "decision_case.html").read_text(encoding="utf-8")
        self.assertNotIn("<script>", page)
        self.assertIn("SYNTHETIC", page)


if __name__ == "__main__":
    unittest.main()
