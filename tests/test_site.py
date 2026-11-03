import tempfile
import unittest
from pathlib import Path

from build_site import DASHBOARD, SITE, build


class SiteTests(unittest.TestCase):
    def test_published_site_is_up_to_date(self):
        """docs/ must match a fresh build; run `python build_site.py` if this fails."""
        with tempfile.TemporaryDirectory() as tmp:
            for fresh in build(Path(tmp)):
                published = SITE / fresh.name
                self.assertTrue(published.is_file(), f"missing {published}")
                self.assertEqual(published.read_bytes(), fresh.read_bytes(), f"{fresh.name} is out of date")

    def test_dashboard_is_bundled_snapshot(self):
        self.assertEqual((SITE / "dashboard.html").read_bytes(), DASHBOARD.read_bytes())

    def test_landing_links_and_labels(self):
        page = (SITE / "index.html").read_text(encoding="utf-8")
        for needed in ('href="dashboard.html"', 'href="decision_case.html"', "Synthetic", "not approved offers", "Keep the fee"):
            self.assertIn(needed, page)
        self.assertNotIn("—", page)


    def test_link_preview_image(self):
        page = (SITE / "index.html").read_text(encoding="utf-8")
        self.assertIn('property="og:image" content="https://usmanov3r-cell.github.io/poland-lending-intelligence-demo/og-image.png"', page)
        self.assertTrue((SITE / "og-image.png").is_file())

    def test_landing_numbers_match_data(self):
        page = (SITE / "index.html").read_text(encoding="utf-8")
        for needed in ("SPL: 99.8%", "INST: 48% gap", "PLN 1,159 to 2,236", "7% less profit"):
            self.assertIn(needed, page)

if __name__ == "__main__":
    unittest.main()
