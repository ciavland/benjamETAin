from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment, Tag


OFFICIAL_BASE = "https://www.benjaminbluemchen.de"
OFFICIAL_LIST_URL = OFFICIAL_BASE + "/hoerspielliste?page={page}&sort_by=field_ep_episode_value_1&sort_order=ASC"
HOERSPIELE_LIST_URL = "https://www.hoerspiele.de/hsp_serie.asp?serie=24"
HOERSPIELE_DETAIL_URL = "https://www.hoerspiele.de/hsp_anzeige.asp?code={code}"
HOERNEWS_INDEX_URLS = (
    "https://www.hoernews.de/Bluemchen/1bis100.html",
    "https://www.hoernews.de/Bluemchen/ab101.html",
)
HOERNEWS_DETAIL_URL = "https://www.hoernews.de/Bluemchen/{filename}"


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def empty_episode(number: int) -> dict[str, Any]:
    return {
        "number": number, "title": None, "description": None,
        "release_year": None, "release_date": None, "duration_seconds": None,
        "cast": [], "production": [], "tracks": [], "editions": [], "sources": [],
    }


def source(url: str, retrieved_at: str, fields: list[str]) -> dict[str, Any]:
    return {"url": url, "retrieved_at": retrieved_at, "fields": sorted(fields)}


def parse_official_list(html: str) -> dict[int, dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    result: dict[int, dict[str, Any]] = {}
    for teaser in soup.select(".audiobook__teaser"):
        number_node = teaser.select_one(".audio-number--audiobooklist")
        title_node = teaser.find("h2")
        link = teaser.find("a", href=True)
        if not number_node or not title_node or not link:
            continue
        match = re.search(r"\d+", clean(number_node.get_text()))
        if not match:
            continue
        number = int(match.group())
        year_match = re.search(r"\b(19|20)\d{2}\b", teaser.get_text(" ", strip=True))
        result[number] = {
            "number": number,
            "title": clean(title_node.get_text(" ", strip=True)),
            "release_year": int(year_match.group()) if year_match else None,
            "url": urljoin(OFFICIAL_BASE, link["href"]),
        }
    return result


def parse_official_detail(html: str, item: dict[str, Any], retrieved_at: str | None = None) -> dict[str, Any]:
    retrieved_at = retrieved_at or datetime.now(timezone.utc).date().isoformat()
    soup = BeautifulSoup(html, "html.parser")
    episode = empty_episode(item["number"])
    episode["title"] = item.get("title")
    episode["release_year"] = item.get("release_year")
    container = soup.select_one(".teaser-container-media-text--text")
    if container:
        title = container.find("h1")
        paragraph = next(
            (node for node in container.find_all("p") if clean(node.get_text(" ", strip=True))),
            None,
        )
        if title:
            episode["title"] = clean(title.get_text(" ", strip=True))
        if paragraph:
            episode["description"] = clean(paragraph.get_text(" ", strip=True))
    fields = [key for key in ("title", "description", "release_year") if episode[key]]
    episode["sources"] = [source(item["url"], retrieved_at, fields)]
    return episode


def parse_shop_url(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    link = soup.find("a", href=True, string=lambda value: value and "Zum Shop" in clean(value))
    if not link:
        return None
    return str(link["href"]).replace("http://www.kiddinx-shop.de/", "https://www.kiddinx-shop.de/")


def parse_shop_detail(html: str, number: int, url: str, retrieved_at: str | None = None) -> dict[str, Any] | None:
    retrieved_at = retrieved_at or datetime.now(timezone.utc).date().isoformat()
    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one(".product-info-secondary")
    if not container:
        return None
    title_node = container.select_one(".medium-4 .title")
    title_text = clean(title_node.get_text(" ", strip=True)) if title_node else ""
    product_number = re.search(r"Folge\s+(\d+)", title_text, re.I)
    if product_number and int(product_number.group(1)) != number:
        return None

    episode = empty_episode(number)
    episode["title"] = clean(re.sub(r"^Folge\s+\d+\s*[-–:]\s*", "", title_text)) or None
    description = title_node.find_next_sibling("p") if title_node else None
    if description:
        episode["description"] = clean(description.get_text(" ", strip=True))

    metadata: dict[str, str] = {}
    for row in container.select("table tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) == 2:
            metadata[clean(cells[0].get_text(" ", strip=True)).removesuffix(":")] = clean(cells[1].get_text(" ", strip=True))
    duration = re.search(r"(\d+)\s*min", metadata.get("Spieldauer", ""), re.I)
    if duration:
        episode["duration_seconds"] = int(duration.group(1)) * 60
    published = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{4})", metadata.get("Veröffentlicht", ""))
    if published:
        episode["release_date"] = f"{published.group(3)}-{published.group(2)}-{published.group(1)}"
        episode["release_year"] = int(published.group(3))

    toggle = container.select_one(".secondary-toggle")
    if toggle:
        sections = {clean(node.get_text(" ", strip=True)): node.find_next_sibling("p") for node in toggle.select(":scope > .title")}
        production_section = sections.get("Produktion")
        for line in production_section.get_text("\n", strip=True).splitlines() if production_section else []:
            line = clean(line)
            if ":" in line:
                credit, value = line.split(":", 1)
                if clean(credit) and clean(value):
                    episode["production"].append({"credit": clean(credit), "value": clean(value)})
        cast_section = sections.get("Sprecher")
        for line in cast_section.get_text("\n", strip=True).splitlines() if cast_section else []:
            line = clean(line)
            if ":" in line:
                role, person = line.split(":", 1)
                if clean(role) and clean(person):
                    episode["cast"].append({"role": clean(role), "person": clean(person)})
            elif line.startswith("Erzähler "):
                episode["cast"].append({"role": "Erzähler", "person": clean(line.removeprefix("Erzähler "))})

    edition: dict[str, Any] = {}
    for label in ("Erschienen bei", "Altersempfehlung", "SKU"):
        if metadata.get(label):
            edition[label] = metadata[label]
    eans = sorted(set(re.findall(r'"ean"\s*:\s*"(\d{8,14})"', html)))
    if eans:
        edition["EAN"] = eans
    if edition:
        episode["editions"] = [edition]

    fields = [key for key in ("title", "description", "release_year", "release_date", "duration_seconds", "cast", "production", "editions") if episode[key]]
    episode["sources"] = [source(url, retrieved_at, fields)]
    return episode


def parse_hoerspiele_list(html: str) -> dict[int, dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    result: dict[int, dict[str, str]] = {}
    for row in soup.find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 5:
            continue
        series = clean(cells[0].get_text(" ", strip=True))
        number_text = clean(cells[1].get_text(" ", strip=True))
        detail = cells[2].find("a", href=re.compile(r"hsp_anzeige\.asp\?code="))
        publisher = clean(cells[4].get_text(" ", strip=True))
        if series != "Benjamin Blümchen" or publisher != "Kiddinx" or not detail:
            continue
        if not re.fullmatch(r"\d{1,3}", number_text):
            continue
        number = int(number_text)
        if number < 1 or number in result:
            continue
        code_match = re.search(r"code=(\d+)", detail.get("href", ""))
        if code_match:
            result[number] = {"code": code_match.group(1), "title": clean(detail.get_text(" ", strip=True))}
    return result


def _value_after_bold(label: Tag) -> str:
    parts: list[str] = []
    for sibling in label.next_siblings:
        if isinstance(sibling, Tag) and sibling.name == "br":
            break
        parts.append(sibling.get_text(" ", strip=True) if isinstance(sibling, Tag) else str(sibling))
    return clean(" ".join(parts).lstrip(":"))


def parse_hoerspiele_detail(html: str, number: int, title: str, code: str, retrieved_at: str | None = None) -> dict[str, Any]:
    retrieved_at = retrieved_at or datetime.now(timezone.utc).date().isoformat()
    soup = BeautifulSoup(html, "html.parser")
    episode = empty_episode(number)
    episode["title"] = title
    description_label = soup.find(lambda tag: isinstance(tag, Tag) and tag.name == "span" and "t4_bold" in (tag.get("class") or []) and clean(tag.get_text()).startswith("Beschreibung"))
    if description_label:
        description = description_label.find_next("span", class_="t5")
        if description:
            episode["description"] = clean(description.get_text(" ", strip=True))
    text = soup.get_text(" ", strip=True)
    duration = re.search(r"Dauer:\s*(?:ca\.\s*)?(\d+)\s*Min", text, re.I)
    if duration:
        episode["duration_seconds"] = int(duration.group(1)) * 60
    wanted = {"Buch", "Regie", "Produktion", "Redaktion", "Ton", "Musik", "Manuskript"}
    seen = set()
    for bold in soup.find_all("b"):
        credit = clean(bold.get_text(" ", strip=True)).removesuffix(":")
        if credit not in wanted:
            continue
        value = _value_after_bold(bold)
        pair = (credit, value)
        if value and pair not in seen:
            seen.add(pair)
            episode["production"].append({"credit": credit, "value": value})
    marker = soup.find(string=lambda value: isinstance(value, Comment) and "Sprecher" in value)
    table = marker.find_next("table") if marker else None
    if table:
        for row in table.find_all("tr"):
            cells = row.find_all("td", recursive=False)
            if len(cells) != 4:
                continue
            role = clean(cells[1].get_text(" ", strip=True))
            person = clean(cells[3].get_text(" ", strip=True))
            if role and person and role != "Rolle" and person != "Sprecher/in":
                episode["cast"].append({"role": role, "person": person})
    url = HOERSPIELE_DETAIL_URL.format(code=code)
    fields = [key for key in ("title", "description", "duration_seconds", "cast", "production") if episode[key]]
    episode["sources"] = [source(url, retrieved_at, fields)]
    return episode


def parse_hoernews_index(html: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    return {
        link["href"].rsplit("/", 1)[-1]
        for link in soup.find_all("a", href=re.compile(r"(?:^|/)\d+\.html$"))
    }


def parse_hoernews_detail(html: str, filename: str, retrieved_at: str | None = None) -> dict[str, Any] | None:
    retrieved_at = retrieved_at or datetime.now(timezone.utc).date().isoformat()
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find("th", class_="tabellekopf")
    if not heading:
        return None
    heading_text = clean(heading.get_text(" ", strip=True))
    match = re.search(r"Benjamin Blümchen\s*\((\d+)\).*?[\"“](.*?)[\"”]", heading_text)
    if not match:
        return None
    number = int(match.group(1))
    episode = empty_episode(number)
    episode["title"] = clean(match.group(2))
    wanted = {"Buch", "Regie", "Produktion", "Redaktion", "Ton", "Musik", "Manuskript"}
    for bold in soup.find_all("b"):
        credit = clean(bold.get_text(" ", strip=True)).removesuffix(":")
        if credit in wanted:
            value = clean(bold.find_parent("td").find_next_sibling("td").get_text(" ", strip=True)) if bold.find_parent("td") and bold.find_parent("td").find_next_sibling("td") else ""
            if value:
                episode["production"].append({"credit": credit, "value": value})
    raw_text = soup.get_text(" ", strip=True)
    year = re.search(r"Herausgabe:\s*.*?((?:19|20)\d{2})", raw_text)
    if year:
        episode["release_year"] = int(year.group(1))
    duration = re.search(r"Länge:\s*(?:ca\.\s*)?(\d+)\s*Min", raw_text, re.I)
    if duration:
        episode["duration_seconds"] = int(duration.group(1)) * 60
    content_heading = soup.find(lambda tag: isinstance(tag, Tag) and tag.name in {"b", "u"} and clean(tag.get_text()) == "Inhalt")
    if content_heading:
        parent = content_heading.find_parent("td")
        if parent:
            text = parent.get_text(" ", strip=True)
            text = re.split(r"Besetzung", text, maxsplit=1)[0]
            episode["description"] = clean(text.removeprefix("Inhalt")) or None
    cast_heading = soup.find("th", string=lambda value: value and clean(value) == "Besetzung")
    if cast_heading:
        for row in cast_heading.find_parent("table").find_all("tr"):
            cells = row.find_all("td", recursive=False)
            if len(cells) == 2:
                role, person = (clean(cell.get_text(" ", strip=True)) for cell in cells)
                if role and person and role != "Rolle" and person != "Sprecher":
                    episode["cast"].append({"role": role, "person": person})
    url = HOERNEWS_DETAIL_URL.format(filename=filename)
    fields = [key for key in ("title", "description", "release_year", "duration_seconds", "cast", "production") if episode[key]]
    episode["sources"] = [source(url, retrieved_at, fields)]
    return episode


def merge_episode(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    number = primary.get("number") or secondary.get("number")
    merged = empty_episode(number)
    for key in ("title", "description", "release_year", "release_date", "duration_seconds"):
        merged[key] = primary.get(key) or secondary.get(key)
    for key in ("cast", "production", "tracks", "editions"):
        merged[key] = primary.get(key) or secondary.get(key) or []
        unique = []
        seen = set()
        for item in merged[key]:
            marker = json.dumps(item, ensure_ascii=False, sort_keys=True)
            if marker not in seen:
                seen.add(marker)
                unique.append(item)
        merged[key] = unique
    merged["sources"] = (primary.get("sources") or []) + (secondary.get("sources") or [])
    return merged
