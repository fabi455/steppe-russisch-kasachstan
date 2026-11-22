#!/usr/bin/env python3
"""Create an offline Russian–German lexicon from OpenRussian (CC BY-SA 4.0).

Source snapshot: Badestrand/russian-dictionary, commit 50e210c4803237779cb562bc1abcea529066031c.
The dictionary data and transformed derivative must retain CC BY-SA 4.0 attribution.
This script is used at BUILD TIME only; the published Android app needs no network.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISION = "50e210c4803237779cb562bc1abcea529066031c"
BASE_URL = "https://raw.githubusercontent.com/Badestrand/russian-dictionary/" + REVISION + "/"
SOURCES = (
    ("nouns", "c388f9e6dde51932832be8d7e9afdbe9f0acee72fcf70677f0fe25ea61293c84"),
    ("verbs", "8659de6799b949fb35f080b08088fb7d347ed300490954ebb380a31642646e1d"),
    ("adjectives", "89ab5d10dcd2f21f6b485de704aef372f32251468e3aa96f18b21e259f26b80a"),
    ("others", "9f22a16b17fc9a564298112168b667fced11aafb254ccebf5b7544fc37cdaa92"),
)


def download(name: str, digest: str) -> str:
    url = BASE_URL + name + ".csv"
    for n in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Steppe-Dictionary-Build/1.2"})
            with urllib.request.urlopen(req, timeout=50) as response:
                data = response.read()
            sha = hashlib.sha256(data).hexdigest()
            if sha != digest:
                raise RuntimeError(f"SHA-256 Prüfsumme unerwartet für {name}: {sha}")
            print(f"{name}: {len(data):,} Bytes geprüft", flush=True)
            return data.decode("utf-8-sig")
        except (TimeoutError, OSError, urllib.error.URLError) as exc:
            if n == 2:
                raise
            print(f"Download-Wiederholung für {name}: {exc}", flush=True)
            time.sleep(2 ** (n + 1))
    raise RuntimeError("Unreachable")


def normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def accent(value: str, bare: str) -> str:
    value = normalise(value)
    if not value or value == bare:
        return ""
    # OpenRussian marks stress using an apostrophe after a vowel.
    value = re.sub(r"([аеёиоуыэюяАЕЁИОУЫЭЮЯ])'", lambda m: m.group(1) + "\u0301", value)
    return value if len(value) <= 100 else ""


def build() -> None:
    unique = {}
    for part, (name, sha) in enumerate(SOURCES):
        source = io.StringIO(download(name, sha), newline="")
        reader = csv.DictReader(source, delimiter="\t")
        for entry in reader:
            ru = normalise(entry.get("bare") or "")
            de = normalise(entry.get("translations_de") or "")
            if not ru or not de or len(ru) > 80 or not re.search(r"[а-яА-ЯёЁ]", ru):
                continue
            de = de[:300].rstrip(" ;,")
            key = ru.casefold()
            existing = unique.get(key)
            if existing is None:
                unique[key] = [ru, accent(entry.get("accented") or "", ru), de, part]
            elif de and de not in existing[2]:
                existing[2] = (existing[2] + "; " + de)[:360]
    words = sorted(unique.values(), key=lambda r: r[0].casefold())
    if not 50000 <= len(words) <= 80000:
        raise RuntimeError(f"Unerwartete Wörterbuchgröße: {len(words)}")
    for word in ("привет", "спасибо", "город", "любить", "хороший", "Казахстан"):
        if not any(row[0].casefold() == word.casefold() for row in words):
            raise RuntimeError(f"Fehlender häufiger Eintrag: {word}")
    folder = ROOT / "dictionary"
    folder.mkdir(parents=True, exist_ok=True)
    data = json.dumps(words, ensure_ascii=False, separators=(",", ":"))
    metadata = json.dumps({"count": len(words), "source": "OpenRussian.org", "license": "CC BY-SA 4.0", "revision": REVISION}, ensure_ascii=False, separators=(",", ":"))
    output = folder / "ru-de.js"
    output.write_text("window.STEPPE_LEXICON=" + data + ";\nwindow.STEPPE_LEXICON_META=" + metadata + ";\n", encoding="utf-8")
    print(f"FERTIG: {len(words)} russisch-deutsche Stichwörter, {output.stat().st_size:,} Bytes ({output})", flush=True)


if __name__ == "__main__":
    build()
