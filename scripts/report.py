#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ranges(numbers: list[int]) -> str:
    if not numbers:
        return "–"
    groups = []
    start = previous = numbers[0]
    for number in numbers[1:]:
        if number == previous + 1:
            previous = number
            continue
        groups.append(str(start) if start == previous else f"{start}–{previous}")
        start = previous = number
    groups.append(str(start) if start == previous else f"{start}–{previous}")
    return ", ".join(groups)


def build_report(episodes: list[dict], target: Path, generated_at: str) -> None:
    fields = {
        "Titel": "title",
        "Beschreibung": "description",
        "Sprecher": "cast",
        "Produktionsdaten": "production",
        "Erscheinungsjahr": "release_year",
        "Exaktes Erscheinungsdatum": "release_date",
        "Laufzeit": "duration_seconds",
        "Trackpunkte": "tracks",
        "Ausgaben/EAN": "editions",
    }
    lines = [
        "# Datenstand und Lückenbericht",
        "",
        f"Erzeugt am {generated_at}. Der Bestand umfasst **{len(episodes)} reguläre Folgen**.",
        "",
        "## Abdeckung",
        "",
        "| Feld | vorhanden | fehlt | fehlende Folgen |",
        "|---|---:|---:|---|",
    ]
    for label, key in fields.items():
        missing = [episode["number"] for episode in episodes if not episode.get(key)]
        lines.append(f"| {label} | {len(episodes) - len(missing)} | {len(missing)} | {ranges(missing)} |")

    expected = set(range(1, max(e["number"] for e in episodes) + 1))
    absent = sorted(expected - {e["number"] for e in episodes})
    host_counts = Counter(
        source["url"].split("/", 3)[2]
        for episode in episodes
        for source in episode.get("sources", [])
    )
    lines += [
        "",
        "## Bekannte Lücken und Grenzen",
        "",
        f"- Komplett fehlende reguläre Folgen im Nummernbereich: **{ranges(absent)}**.",
        "- Besetzung, Produktionscredits, Laufzeiten und Ausgaben stammen vorrangig aus den verlinkten KIDDINX-Shop-Produktkarten; Hoerspiele.de und HörNews ergänzen insbesondere ältere Folgen.",
        "- Die offizielle Hörspielliste nennt überwiegend nur Erscheinungsjahre. Exakte Veröffentlichungstage werden nur übernommen, wenn sie in der jeweiligen Shop-Produktkarte ausdrücklich genannt sind.",
        "- Belastbare Tracklisten und Kapitel-Zeitstempel wurden noch nicht importiert.",
        "- Die Beschreibungen sind Quelltexte Dritter und nicht von der MIT-Lizenz des Codes umfasst.",
        "- Specials, Bücher, Filme, Coverdateien, Streaming-IDs und MusicBrainz-IDs sind noch nicht modelliert/importiert.",
        "- Schreibweisen von Rollen und Personen werden quellengetreu übernommen; Pseudonyme und Alias-Normalisierung fehlen noch.",
        "- Konflikte zwischen Quellen werden noch nicht als eigene Datensätze gespeichert; die offizielle Seite hat bei Titel, Jahr und Beschreibung Vorrang.",
        "",
        "## Quellenbilanz",
        "",
    ]
    for host, count in sorted(host_counts.items()):
        lines.append(f"- `{host}`: bei {count} Folgendatensätzen referenziert")
    lines += [
        "",
        "## Sinnvolle nächste Schritte",
        "",
        "1. Die noch fehlende Laufzeit von Folge 134 anhand eines offiziellen Inlays ergänzen.",
        "2. Weitere exakte Veröffentlichungstage und Streaming-IDs aus offiziellen Katalogen ergänzen.",
        "3. Specials und Sonderausgaben getrennt von der regulären Serie erfassen.",
        "4. Personen- und Rollen-IDs samt Alias-Tabelle einführen, ohne abweichende Originalcredits zu verlieren.",
        "5. Kapitel-Zeitstempel aus legal verfügbaren Medien oder MusicBrainz-Daten ergänzen.",
        "",
        "Der Bericht wird mit `make report` bzw. bei jedem `make update` neu erzeugt.",
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    bundle = json.loads((ROOT / "data" / "all.json").read_text(encoding="utf-8"))
    build_report(
        bundle["episodes"], ROOT / "REPORT.md", datetime.now(timezone.utc).date().isoformat()
    )


if __name__ == "__main__":
    main()
