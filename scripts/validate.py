#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    paths = sorted((ROOT / "data" / "episodes").glob("*.json"))
    episodes = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    numbers = [episode.get("number") for episode in episodes]
    if len(numbers) != len(set(numbers)):
        errors.append("doppelte Folgennummer")
    for path, episode in zip(paths, episodes):
        number = episode.get("number")
        if path.stem != f"{number:03d}":
            errors.append(f"{path}: Dateiname passt nicht zur Nummer")
        if not episode.get("title"):
            errors.append(f"{path}: Titel fehlt")
        if not episode.get("sources"):
            errors.append(f"{path}: Quellen fehlen")
        cast_pairs = [(item.get("role"), item.get("person")) for item in episode.get("cast", [])]
        if len(cast_pairs) != len(set(cast_pairs)):
            errors.append(f"{path}: doppelte Sprechrolle")

    bundle = json.loads((ROOT / "data" / "all.json").read_text(encoding="utf-8"))
    if bundle.get("episodes") != episodes:
        errors.append("data/all.json stimmt nicht mit den Einzelfolgen überein")
    with (ROOT / "data" / "index.csv").open(encoding="utf-8") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != len(episodes):
        errors.append("data/index.csv hat eine abweichende Zeilenzahl")

    if errors:
        print("Validierung fehlgeschlagen:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"OK: {len(episodes)} Folgen, {sum(len(e['cast']) for e in episodes)} Sprechrollen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

