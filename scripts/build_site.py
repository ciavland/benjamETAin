#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "web", DIST)
    shutil.copytree(ROOT / "schema", DIST / "schema")
    shutil.copy2(ROOT / "DATA-LICENSE.md", DIST / "DATA-LICENSE.md")
    (DIST / ".nojekyll").touch()

    bundle = json.loads((ROOT / "data" / "all.json").read_text(encoding="utf-8"))
    episodes = bundle["episodes"]
    api = DIST / "api" / "v1"
    episode_dir = api / "episodes"
    episode_dir.mkdir(parents=True, exist_ok=True)

    public_bundle = {"meta": bundle["meta"], "episodes": episodes}
    (api / "episodes.json").write_text(
        json.dumps(public_bundle, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    index = [
        {
            "number": item["number"],
            "title": item["title"],
            "release_year": item["release_year"],
            "duration_seconds": item["duration_seconds"],
        }
        for item in episodes
    ]
    (episode_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    for episode in episodes:
        (episode_dir / f"{episode['number']:03d}.json").write_text(
            json.dumps(episode, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

    status = {
        "api_version": "1.0.0",
        "data_version": bundle["meta"]["generated_at"],
        "episode_count": len(episodes),
        "coverage": {
            "description": sum(bool(item["description"]) for item in episodes),
            "cast": sum(bool(item["cast"]) for item in episodes),
            "production": sum(bool(item["production"]) for item in episodes),
            "tracks": sum(bool(item["tracks"]) for item in episodes),
        },
    }
    (api / "status.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    openapi = {
        "openapi": "3.1.0",
        "info": {
            "title": "BenjaminMeta API",
            "version": "1.0.0",
            "description": "Statische, quelloffene Metadaten zur regulären Benjamin-Blümchen-Hörspielserie.",
        },
        "servers": [{"url": "https://ciavland.github.io/benjamETAin/api/v1"}],
        "paths": {
            "/episodes.json": {
                "get": {
                    "summary": "Alle Folgen",
                    "responses": {"200": {"description": "Gesamter Folgenbestand"}},
                }
            },
            "/episodes/{number}.json": {
                "get": {
                    "summary": "Eine Folge",
                    "parameters": [{"name": "number", "in": "path", "required": True, "schema": {"type": "string", "pattern": "^[0-9]{3}$"}}],
                    "responses": {"200": {"description": "Folgendatensatz"}, "404": {"description": "Folge nicht gefunden"}},
                }
            },
            "/status.json": {"get": {"summary": "Datenstatus", "responses": {"200": {"description": "Version und Abdeckung"}}}},
        },
    }
    (DIST / "api" / "openapi.json").write_text(
        json.dumps(openapi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Site gebaut: {len(episodes)} Folgen, {sum(1 for _ in DIST.rglob('*'))} Dateien")


if __name__ == "__main__":
    main()
