#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bbmeta.scrapers import (
    HOERNEWS_DETAIL_URL, HOERNEWS_INDEX_URLS,
    HOERSPIELE_DETAIL_URL, HOERSPIELE_LIST_URL, OFFICIAL_LIST_URL,
    empty_episode, merge_episode, parse_hoerspiele_detail,
    parse_hoerspiele_list, parse_hoernews_detail, parse_hoernews_index,
    parse_official_detail, parse_official_list, parse_shop_detail, parse_shop_url, source,
)

CACHE = ROOT / ".cache"
USER_AGENT = "benjaminmeta/0.1 (public metadata research; contact via repository)"
SHOP_URL_OVERRIDES = {
    45: "https://www.kiddinx-shop.de/benjamin-bluemchen-als-zirkusclown-folge-45.html",
    46: "https://www.kiddinx-shop.de/benjamin-bluemchen-hilft-den-tieren-folge-46.html",
    52: "https://www.kiddinx-shop.de/benjamin-bluemchen-der-weihnachtstraum-folge-52.html",
    105: "https://www.kiddinx-shop.de/benjamin-bluemchen-das-fleissige-faultier-folge-105.html",
    114: "https://www.kiddinx-shop.de/benjamin-blumchen-und-der-delfin-folge-114.html",
    115: "https://www.kiddinx-shop.de/benjamin-bluemchen-die-kleinen-katzchen-folge-115-cd.html",
    117: "https://www.kiddinx-shop.de/benjamin-blumchen-die-zoo-schwimmschule-folge-117.html",
    120: "https://www.kiddinx-shop.de/benjamin-blumchen-der-zeltausflug-folge-120.html",
    124: "https://www.kiddinx-shop.de/benjamin-bluemchen-im-tante-emma-laden-folge-124.html",
    138: "https://www.kiddinx-shop.de/benjamin-bluemchen-das-neue-muellauto-folge138.html",
}


def fetch(url: str, target: Path, refresh: bool, offline: bool, encoding: str = "utf-8") -> str:
    if target.exists() and not refresh:
        return target.read_text(encoding=encoding, errors="replace")
    if offline:
        raise FileNotFoundError(f"Nicht im Cache: {target}")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = response.read()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return payload.decode(encoding, errors="replace")


def write_outputs(episodes: list[dict], generated_at: str) -> None:
    episode_dir = ROOT / "data" / "episodes"
    episode_dir.mkdir(parents=True, exist_ok=True)
    expected = set()
    for episode in episodes:
        path = episode_dir / f"{episode['number']:03d}.json"
        expected.add(path.name)
        path.write_text(json.dumps(episode, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for stale in episode_dir.glob("*.json"):
        if stale.name not in expected:
            stale.unlink()
    bundle = {"meta": {"generated_at": generated_at, "episode_count": len(episodes)}, "episodes": episodes}
    (ROOT / "data" / "all.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (ROOT / "data" / "index.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["number", "title", "release_year", "duration_seconds", "cast_count"])
        for episode in episodes:
            writer.writerow([episode["number"], episode["title"], episode["release_year"], episode["duration_seconds"], len(episode["cast"])])


def main() -> int:
    parser = argparse.ArgumentParser(description="Benjamin-Blümchen-Metadaten aktualisieren")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if args.refresh and args.offline:
        parser.error("--refresh und --offline schließen sich aus")
    today = datetime.now(timezone.utc).date().isoformat()

    official_index: dict[int, dict] = {}
    for page in range(5):
        html = fetch(OFFICIAL_LIST_URL.format(page=page), CACHE / "official" / f"list-{page}.html", args.refresh, args.offline)
        official_index.update(parse_official_list(html))
    print(f"Offizielle Liste: {len(official_index)} Folgen")

    hsp_html = fetch(HOERSPIELE_LIST_URL, CACHE / "hoerspiele.de" / "list.html", args.refresh, args.offline, "cp1252")
    hsp_index = parse_hoerspiele_list(hsp_html)
    print(f"Hoerspiele.de: {len(hsp_index)} reguläre Detailseiten")

    hoernews_files: set[str] = set()
    for index, url in enumerate(HOERNEWS_INDEX_URLS):
        html = fetch(url, CACHE / "hoernews.de" / f"list-{index}.html", args.refresh, args.offline, "cp1252")
        hoernews_files.update(parse_hoernews_index(html))
    print(f"HörNews: {len(hoernews_files)} verlinkte Detailseiten")

    official: dict[int, dict] = {}
    hsp: dict[int, dict] = {}
    hoernews: dict[int, dict] = {}
    shop: dict[int, dict] = {}
    failures: list[str] = []

    def official_job(item: dict) -> tuple[str, int, dict]:
        number = item["number"]
        html = fetch(item["url"], CACHE / "official" / f"{number:03d}.html", args.refresh, args.offline)
        return "official", number, parse_official_detail(html, item, today)

    def hsp_job(number: int, item: dict) -> tuple[str, int, dict]:
        code = item["code"]
        html = fetch(HOERSPIELE_DETAIL_URL.format(code=code), CACHE / "hoerspiele.de" / f"{number:03d}-{code}.html", args.refresh, args.offline, "cp1252")
        return "hsp", number, parse_hoerspiele_detail(html, number, item["title"], code, today)

    def hoernews_job(filename: str) -> tuple[str, int, dict] | None:
        html = fetch(HOERNEWS_DETAIL_URL.format(filename=filename), CACHE / "hoernews.de" / filename, args.refresh, args.offline, "cp1252")
        episode = parse_hoernews_detail(html, filename, today)
        return ("hoernews", episode["number"], episode) if episode else None

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        jobs = [executor.submit(official_job, item) for item in official_index.values()]
        jobs += [executor.submit(hsp_job, number, item) for number, item in hsp_index.items() if number <= 170]
        jobs += [executor.submit(hoernews_job, filename) for filename in hoernews_files]
        for future in as_completed(jobs):
            try:
                result = future.result()
                if not result:
                    continue
                kind, number, episode = result
                {"official": official, "hsp": hsp, "hoernews": hoernews}[kind][number] = episode
            except (OSError, urllib.error.URLError, ValueError) as error:
                failures.append(str(error))

    shop_urls: dict[int, str] = {}
    for number, item in official_index.items():
        html = fetch(item["url"], CACHE / "official" / f"{number:03d}.html", args.refresh, args.offline)
        if shop_url := parse_shop_url(html):
            shop_urls[number] = shop_url
    shop_urls.update(SHOP_URL_OVERRIDES)
    print(f"KIDDINX-Shop: {len(shop_urls)} verlinkte Produktseiten")

    def shop_job(number: int, url: str) -> tuple[int, dict | None]:
        html = fetch(url, CACHE / "kiddinx-shop.de" / f"{number:03d}.html", args.refresh, args.offline)
        return number, parse_shop_detail(html, number, url, today)

    with ThreadPoolExecutor(max_workers=min(3, max(1, args.workers))) as executor:
        jobs = [executor.submit(shop_job, number, url) for number, url in shop_urls.items()]
        for future in as_completed(jobs):
            try:
                number, episode = future.result()
                if episode:
                    shop[number] = episode
            except (OSError, urllib.error.URLError, ValueError) as error:
                failures.append(str(error))

    numbers = sorted(set(official_index) | {number for number in hsp_index if number <= 170})
    episodes = []
    for number in numbers:
        base = official.get(number) or empty_episode(number)
        if not base.get("title") and number in official_index:
            base.update({key: official_index[number].get(key) for key in ("title", "release_year")})
        combined = merge_episode(base, hsp.get(number) or empty_episode(number))
        combined = merge_episode(combined, hoernews.get(number) or empty_episode(number))
        episodes.append(merge_episode(combined, shop.get(number) or empty_episode(number)))
    episode_137 = next(episode for episode in episodes if episode["number"] == 137)
    if not episode_137["release_year"]:
        episode_137["release_year"] = 2017
        episode_137["release_date"] = "2017-11-10"
        episode_137["sources"].append(source(
            "https://www.qobuz.com/de-de/album/folge-137-ein-torooo-fur-alle-falle-benjamin-blumchen/0190295720445",
            today,
            ["release_date", "release_year"],
        ))
    write_outputs(episodes, today)
    print(f"Geschrieben: {len(episodes)} Folgen; Abruffehler: {len(failures)}")
    for error in failures[:10]:
        print(f"  {error}")

    from scripts.report import build_report
    build_report(episodes, ROOT / "REPORT.md", today)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
