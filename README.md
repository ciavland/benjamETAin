# BenjaminMeta

Offene, maschinenlesbare Metadaten zur regulären Benjamin-Blümchen-Hörspielserie – mit durchsuchbarer Website und statischer JSON-API.

Der aktuelle Import enthält die regulären Folgen 1–170. Im Mittelpunkt stehen Beschreibung, Sprechrollen und Produktionsdaten. Jede Angabe bleibt über `sources` auf ihre Herkunft zurückführbar; fehlende Werte werden nicht geraten.

## Daten

- `data/episodes/NNN.json`: ein Datensatz pro Folge
- `data/all.json`: alle Folgen als Gesamtausgabe
- `data/index.csv`: flacher Index
- `REPORT.md`: automatisch erzeugter Lückenbericht
- `schema/episode.schema.json`: JSON Schema

## Statische API

Beim Build entstehen folgende Endpunkte:

```text
GET /api/v1/episodes.json
GET /api/v1/episodes/index.json
GET /api/v1/episodes/001.json
GET /api/v1/status.json
GET /api/openapi.json
```

## Aktualisieren und prüfen

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
make update
make validate
make test
make build
make serve
```

Der HTTP-Cache liegt in `.cache/`. `python3 scripts/update.py --refresh` lädt alle Quellen neu; `--offline` wertet nur den vorhandenen Cache aus.

## Quellen und Abgrenzung

Der Import kombiniert die offizielle [Hörspielliste](https://www.benjaminbluemchen.de/hoerspielliste) mit Detaildaten von [Hoerspiele.de](https://www.hoerspiele.de/hsp_serie.asp?serie=24) und [HörNews](https://www.hoernews.de/Bluemchen/). Specials, Filme, Bücher, Coverbilder und Streaming-IDs sind vorerst nicht enthalten. Den exakten Stand dokumentiert `REPORT.md`.

Die MIT-Lizenz gilt nur für den Code. Für importierte Texte und Marken gelten die Hinweise in [DATA-LICENSE.md](DATA-LICENSE.md).

