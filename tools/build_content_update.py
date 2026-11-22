#!/usr/bin/env python3
"""Create the content-only offline update ZIP and its SHA-256 catalog.

Only data files are included: content.json, revision metadata and MP3s.
No JavaScript or Android executables are distributed by this mechanism.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REVISION = int(os.environ.get("GITHUB_RUN_NUMBER", "1"))

def create():
    if REVISION <= 0:
        raise ValueError("Revision must be a positive integer")
    lessons = json.loads((ROOT/"content.json").read_text("utf-8"))
    if len(lessons) < 20:
        raise ValueError("Missing course lessons")
    entries = [item for lesson in lessons for item in lesson["words"]+lesson["phrases"]]
    ids = [item["id"] for item in entries]
    if len(set(ids)) != len(ids) or len(ids) < 321:
        raise ValueError("Duplicate or missing audio IDs")
    files = [ROOT/"audio"/(id+".mp3") for id in ids]
    if not all(f.is_file() and f.stat().st_size > 1500 for f in files):
        raise ValueError("Some MP3s have not been produced")
    DIST.mkdir(parents=True, exist_ok=True)
    (ROOT/"updates").mkdir(exist_ok=True)
    revision_data = {"revision": REVISION, "schema": 1, "items": len(ids)}
    (ROOT/"updates"/"update-revision.json").write_text(
        json.dumps(revision_data,ensure_ascii=False,separators=(",",":"))+"\n", encoding="utf-8")
    package = DIST/"steppe-content.zip"
    with ZipFile(package,"w",compression=ZIP_DEFLATED,compresslevel=6) as z:
        z.write(ROOT/"content.json","content.json")
        z.write(ROOT/"updates"/"update-revision.json","update-revision.json")
        for f in files:
            z.write(f,"audio/"+f.name)
    bytes = package.read_bytes()
    catalog = {
        "schema":1,
        "revision":REVISION,
        "size":len(bytes),
        "sha256":hashlib.sha256(bytes).hexdigest(),
        "items":len(ids),
        "lessons":len(lessons),
        "updated_at":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "download": "https://github.com/fabi455/steppe-russisch-kasachstan/releases/download/content-latest/steppe-content.zip"
    }
    (DIST/"latest.json").write_text(
        json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Steppe content update r{REVISION}: {len(lessons)} lessons, {len(ids)} MP3 files, {len(bytes)} bytes, SHA-256 {catalog['sha256']}",flush=True)

if __name__ == "__main__":
    create()
