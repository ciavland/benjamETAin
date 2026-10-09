import unittest

from bbmeta.scrapers import (
    empty_episode,
    merge_episode,
    parse_hoerspiele_detail,
    parse_hoerspiele_list,
    parse_official_detail,
    parse_official_list,
    parse_shop_detail,
    parse_shop_url,
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

    def test_shop_parser(self):
        official = '<a href="http://www.kiddinx-shop.de/folge-170.html">Zum Shop</a>'
        self.assertEqual(parse_shop_url(official), "https://www.kiddinx-shop.de/folge-170.html")
        html = '''<div class="product-info-secondary"><div class="medium-4">
        <div class="title">Folge 170 - in Australien</div><p>Eine Reise.</p>
        <table><tr><td>Spieldauer:</td><td>56 min</td></tr>
        <tr><td>Veröffentlicht:</td><td>22.05.2026</td></tr><tr><td>SKU:</td><td>425570</td></tr></table></div>
        <div class="secondary-toggle"><div class="title">Produktion</div>
        <p>Buch: Vincent Andreas<br>Regie: Ludwig Schultz</p>
        <div class="title">Sprecher</div><p>Benjamin Blümchen: M. Klemm<br>Otto: K. Primel<br>u.a.</p></div></div>
        <script>"ean":"4001504255701"</script>'''
        episode = parse_shop_detail(html, 170, "https://example.test/170", "2026-01-01")
        self.assertEqual(episode["release_date"], "2026-05-22")
        self.assertEqual(episode["duration_seconds"], 3360)
        self.assertEqual(len(episode["cast"]), 2)
        self.assertEqual(episode["production"][0]["credit"], "Buch")
        self.assertEqual(episode["editions"][0]["EAN"], ["4001504255701"])


if __name__ == "__main__":
    unittest.main()
