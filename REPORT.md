# Datenstand und Lückenbericht

Erzeugt am 2026-10-09. Der Bestand umfasst **170 reguläre Folgen**.

## Abdeckung

| Feld | vorhanden | fehlt | fehlende Folgen |
|---|---:|---:|---|
| Titel | 170 | 0 | – |
| Beschreibung | 170 | 0 | – |
| Sprecher | 111 | 59 | 109–110, 114–170 |
| Produktionsdaten | 111 | 59 | 59, 65, 67, 114–130, 132–170 |
| Erscheinungsjahr | 170 | 0 | – |
| Exaktes Erscheinungsdatum | 1 | 169 | 1–136, 138–170 |
| Laufzeit | 112 | 58 | 104, 113–130, 132–170 |
| Trackpunkte | 0 | 170 | 1–170 |
| Ausgaben/EAN | 0 | 170 | 1–170 |

## Bekannte Lücken und Grenzen

- Komplett fehlende reguläre Folgen im Nummernbereich: **–**.
- Besetzung und Produktionscredits stammen aus Hoerspiele.de und ergänzend aus den dort tatsächlich verlinkten HörNews-Detailseiten. Für neuere Folgen sind in diesen Quellen oft keine Einzelcredits vorhanden.
- Die offizielle Hörspielliste nennt überwiegend nur Erscheinungsjahre. Exakte Veröffentlichungstage werden nicht aus Händlerangaben oder Wiederveröffentlichungen abgeleitet.
- Belastbare Tracklisten und Kapitel-Zeitstempel wurden noch nicht importiert.
- Die Beschreibungen sind Quelltexte Dritter und nicht von der MIT-Lizenz des Codes umfasst.
- Specials, Bücher, Filme, Coverdateien, Streaming-IDs und MusicBrainz-IDs sind noch nicht modelliert/importiert.
- Schreibweisen von Rollen und Personen werden quellengetreu übernommen; Pseudonyme und Alias-Normalisierung fehlen noch.
- Konflikte zwischen Quellen werden noch nicht als eigene Datensätze gespeichert; die offizielle Seite hat bei Titel, Jahr und Beschreibung Vorrang.

## Quellenbilanz

- `www.benjaminbluemchen.de`: bei 170 Folgendatensätzen referenziert
- `www.hoernews.de`: bei 49 Folgendatensätzen referenziert
- `www.hoerspiele.de`: bei 114 Folgendatensätzen referenziert
- `www.qobuz.com`: bei 1 Folgendatensätzen referenziert

## Sinnvolle nächste Schritte

1. Die in der Tabelle genannten Folgen ohne Produktionsdaten anhand offizieller Inlays oder einer ausdrücklich nutzbaren Quelle ergänzen.
2. Exakte Veröffentlichungstage und Streaming-IDs aus offiziellen Katalogen ergänzen.
3. Specials und Sonderausgaben getrennt von der regulären Serie erfassen.
4. Personen- und Rollen-IDs samt Alias-Tabelle einführen, ohne abweichende Originalcredits zu verlieren.
5. Kapitel-Zeitstempel aus legal verfügbaren Medien oder MusicBrainz-Daten ergänzen.

Der Bericht wird mit `make report` bzw. bei jedem `make update` neu erzeugt.
