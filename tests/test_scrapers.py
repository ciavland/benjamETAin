import unittest

from bbmeta.scrapers import (
    empty_episode,
    merge_episode,
    parse_hoerspiele_detail,
    parse_hoerspiele_list,
    parse_official_detail,
    parse_official_list,
)


class ScraperTests(unittest.TestCase):
    def test_official_list(self):
        html = '''<div class="audiobook__teaser"><a href="/hoerspiele/nr-1/wetterelefant">
        <span class="audio-number--audiobooklist">1</span><h2>... als Wetterelefant</h2>
        <div class="audiobook-text"><p>1977</p></div></a></div>'''
        item = parse_official_list(html)[1]
        self.assertEqual(item["release_year"], 1977)
        self.assertTrue(item["url"].endswith("/wetterelefant"))

    def test_official_detail(self):
        item = {"number": 1, "title": "Titel", "release_year": 1977, "url": "https://example.test/1"}
        html = '<div class="teaser-container-media-text--text"><h1>Wetterelefant</h1><p>Benjamin hilft.</p></div>'
        episode = parse_official_detail(html, item, "2026-01-01")
        self.assertEqual(episode["description"], "Benjamin hilft.")

    def test_hoerspiele_list(self):
        html = '''<table><tr><td>Benjamin Blümchen</td><td>1</td>
        <td><a href="hsp_anzeige.asp?code=4375">Wetterelefant</a></td><td></td><td>Kiddinx</td></tr></table>'''
        self.assertEqual(parse_hoerspiele_list(html)[1]["code"], "4375")

    def test_hoerspiele_detail_and_merge(self):
        html = '''<span class="t4_bold">Beschreibung:</span><span class="t5">Eine Geschichte.</span>
        <span>Dauer: ca. 45 Minuten</span><b>Buch:</b> Elfie Donnelly<br>
        <!-- Sprecher --><table><tr><td></td><td>Benjamin</td><td></td><td>Edgar Ott</td></tr></table>'''
        detail = parse_hoerspiele_detail(html, 1, "Wetterelefant", "4375", "2026-01-01")
        official = empty_episode(1)
        official.update({"title": "... als Wetterelefant", "release_year": 1977})
        merged = merge_episode(official, detail)
        self.assertEqual(merged["duration_seconds"], 2700)
        self.assertEqual(merged["cast"][0]["person"], "Edgar Ott")


if __name__ == "__main__":
    unittest.main()
