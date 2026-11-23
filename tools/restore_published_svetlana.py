#!/usr/bin/env python3
"""Restore only complete, published Svetlana Neural audio for Steppe Android.

The published ZIP must match the manifest SHA-256, have voice set to
ru-RU-SvetlanaNeural, contain all course IDs and equal the bundled lesson JSON.
A missing/invalid release blocks the build instead of silently adding Dmitri.
"""
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = os.getenv("GITHUB_REPOSITORY", "fabi455/steppe-russisch-kasachstan")
VOICE = "ru-RU-SvetlanaNeural"


def main():
    catalog=json.loads((ROOT/"updates/latest.json").read_text("utf-8"))
    if catalog.get("voice") != VOICE:
        raise RuntimeError("The published update has not been verified as all-Svetlana audio")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["gh","release","download","content-latest","--repo",REPO,
             "--pattern","steppe-content.zip","--dir",tmp],
            check=True
        )
        data=(Path(tmp)/"steppe-content.zip").read_bytes()
        if len(data)!=catalog["size"] or hashlib.sha256(data).hexdigest()!=catalog["sha256"]:
            raise RuntimeError("The current audio package does not match the verified SHA-256 catalog")
        current=json.loads((ROOT/"content.json").read_text("utf-8"))
        course={w["id"]:w["term"] for l in current for w in l["words"]+l["phrases"]}
        if len(course)!=catalog["items"]:
            raise RuntimeError("Published audio count differs from the bundled course")
        audio_dir=ROOT/"audio"
        audio_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(Path(tmp)/"steppe-content.zip") as z:
            stored=json.loads(z.read("content.json"))
            if stored!=current:
                raise RuntimeError("The published audio package belongs to different lesson texts")
            meta=json.loads(z.read("update-revision.json"))
            if meta.get("revision")!=catalog["revision"]:
                raise RuntimeError("Published package revision mismatch")
            expected={"content.json","update-revision.json"}|{f"audio/{id}.mp3" for id in course}
            if set(z.namelist())!=expected:
                raise RuntimeError("Unexpected, duplicated or missing content pack entries")
            for id in course:
                blob=z.read("audio/"+id+".mp3")
                if len(blob)<2500 or not (blob.startswith(b"ID3") or (blob[0]==255 and (blob[1]&224)==224)):
                    raise RuntimeError("Invalid Svetlana MP3: "+id)
                (audio_dir/(id+".mp3")).write_bytes(blob)
        print(f"VERIFIED: {len(course)} MP3s; only {VOICE}; SHA256={catalog['sha256']}",flush=True)


if __name__=="__main__":
    main()
