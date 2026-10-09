# Datenstand und Lückenbericht

Erzeugt am 2026-10-09. Der Bestand umfasst **170 reguläre Folgen**.

## Abdeckung

| Feld | vorhanden | fehlt | fehlende Folgen |
|---|---:|---:|---|
| Titel | 170 | 0 | – |
| Beschreibung | 170 | 0 | – |
| Sprecher | 170 | 0 | – |
| Produktionsdaten | 170 | 0 | – |
| Erscheinungsjahr | 170 | 0 | – |
| Exaktes Erscheinungsdatum | 29 | 141 | 1–10, 12–21, 23–114, 116–136, 138–139, 145, 149, 156, 165–167 |
| Laufzeit | 169 | 1 | 134 |
| Trackpunkte | 0 | 170 | 1–170 |
| Ausgaben/EAN | 170 | 0 | – |

## Bekannte Lücken und Grenzen

- Komplett fehlende reguläre Folgen im Nummernbereich: **–**.
- Besetzung, Produktionscredits, Laufzeiten und Ausgaben stammen vorrangig aus den verlinkten KIDDINX-Shop-Produktkarten; Hoerspiele.de und HörNews ergänzen insbesondere ältere Folgen.
- Die offizielle Hörspielliste nennt überwiegend nur Erscheinungsjahre. Exakte Veröffentlichungstage werden nur übernommen, wenn sie in der jeweiligen Shop-Produktkarte ausdrücklich genannt sind.
- Belastbare Tracklisten und Kapitel-Zeitstempel wurden noch nicht importiert.
- Die Beschreibungen sind Quelltexte Dritter und nicht von der MIT-Lizenz des Codes umfasst.
- Specials, Bücher, Filme, Coverdateien, Streaming-IDs und MusicBrainz-IDs sind noch nicht modelliert/importiert.
- Schreibweisen von Rollen und Personen werden quellengetreu übernommen; Pseudonyme und Alias-Normalisierung fehlen noch.
- Konflikte zwischen Quellen werden noch nicht als eigene Datensätze gespeichert; die offizielle Seite hat bei Titel, Jahr und Beschreibung Vorrang.

## Quellenbilanz

- `www.benjaminbluemchen.de`: bei 170 Folgendatensätzen referenziert
- `www.hoernews.de`: bei 49 Folgendatensätzen referenziert
- `www.hoerspiele.de`: bei 114 Folgendatensätzen referenziert
- `www.kiddinx-shop.de`: bei 170 Folgendatensätzen referenziert
- `www.qobuz.com`: bei 1 Folgendatensätzen referenziert

## Sinnvolle nächste Schritte

1. Die noch fehlende Laufzeit von Folge 134 anhand eines offiziellen Inlays ergänzen.
2. Weitere exakte Veröffentlichungstage und Streaming-IDs aus offiziellen Katalogen ergänzen.
3. Specials und Sonderausgaben getrennt von der regulären Serie erfassen.
4. Personen- und Rollen-IDs samt Alias-Tabelle einführen, ohne abweichende Originalcredits zu verlieren.
5. Kapitel-Zeitstempel aus legal verfügbaren Medien oder MusicBrainz-Daten ergänzen.

Der Bericht wird mit `make report` bzw. bei jedem `make update` neu erzeugt.
