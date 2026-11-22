#!/usr/bin/env python3
"""Restore ONLY verifiably Svetlana-synthesized MP3s for the Steppe course.

Input 1: last released content pack IF it declares the Svetlana voice, and
its SHA-256 and declared size match the checked-in catalog.
Input 2: legacy Steppe 1.1 build containing 128 original Svetlana clips.

A clip is reused only if its word ID and Russian text remain unchanged.
The script never reuses Piper/Dmitri MP3s or silently substitutes a voice.
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT/"audio"
REPO = os.getenv("GITHUB_REPOSITORY","fabi455/steppe-russisch-kasachstan")
LEGACY_RUN = "44756476911"
LEGACY_ARTIFACT = "Steppe-Russisch-1.1-Neural-APK"
VOICE = "ru-RU-SvetlanaNeural"


def run(*args: str) -> bool:
    command = subprocess.run(["gh",*args],text=True,capture_output=True)
    if command.returncode != 0:
        print("Optional audio lookup failed:",command.stderr.strip()[:500],flush=True)
    return command.returncode == 0


def read_ids(lessons):
    return {x["id"]: x["term"] for l in lessons for x in l["words"]+l["phrases"]}


def valid_mp3(data: bytes):
    return len(data)>2500 and (data.startswith(b"ID3") or data[:1]==b"\xff" and len(data)>1 and data[1]&224==224)


def restore_mp3(path: Path, data: bytes):
    if not valid_mp3(data):
        raise RuntimeError(f"Invalid MP3: {path}")
    path.write_bytes(data)


def released_pack(current):
    catalog_path=ROOT/"updates/latest.json"
    if not catalog_path.is_file():
        return 0
    catalog=json.loads(catalog_path.read_text("utf-8"))
    if catalog.get("voice")!=VOICE:
        print("Existing content release uses mixed/unknown voices. Not reused.",flush=True)
        return 0
    with tempfile.TemporaryDirectory() as d:
        if not run("release","download","content-latest","--repo",REPO,
                   "--pattern","steppe-content.zip","--dir",d):
            return 0
        pack=Path(d)/"steppe-content.zip"
        blob=pack.read_bytes()
        if len(blob)!=catalog["size"] or hashlib.sha256(blob).hexdigest()!=catalog["sha256"]:
            raise RuntimeError("Published Svetlana audio ZIP does not match SHA-256 catalog")
        count=0
        with zipfile.ZipFile(pack) as z:
            from_pack=read_ids(json.loads(z.read("content.json")))
            for id,term in current.items():
                if from_pack.get(id)!=term:
                    continue
                member="audio/"+id+".mp3"
                if member not in z.namelist():
                    continue
                raw=z.read(member)
                if valid_mp3(raw):
                    restore_mp3(AUDIO/(id+".mp3"),raw)
                    count+=1
        print("Restored",count,"matching previously verified Svetlana clips",flush=True)
        return count


def legacy_pack(current):
    # Steppe 1.1's first eight lessons have been kept unchanged since launch.
    with tempfile.TemporaryDirectory() as d:
        if not run("run","download",LEGACY_RUN,"--repo",REPO,
                   "--name",LEGACY_ARTIFACT,"--dir",d):
            raise RuntimeError("Original 128 Svetlana recordings are unavailable. Refusing a mixed-voice release.")
        apk=next(iter(Path(d).rglob("*.apk")),None)
        if apk is None: raise RuntimeError("Legacy artifact contained no APK")
        with zipfile.ZipFile(apk) as z:
            # Read the exact content that was spoken, not only the IDs.
            source="assets/content.json"
            if source not in z.namelist():raise RuntimeError("Legacy APK missing lesson data")
            old=read_ids(json.loads(z.read(source)))
            count=0
            for id,term in current.items():
                if old.get(id)!=term: continue
                member="assets/audio/"+id+".mp3"
                if member in z.namelist():
                    restore_mp3(AUDIO/(id+".mp3"),z.read(member));count+=1
        print("Restored",count,"originally recorded Svetlana clips",flush=True)
        if count<120:raise RuntimeError("Too few original Svetlana samples")
        return count


if __name__=="__main__":
    AUDIO.mkdir(parents=True,exist_ok=True)
    current=read_ids(json.loads((ROOT/"content.json").read_text("utf-8")))
    if not released_pack(current):
        legacy_pack(current)
    print("Trusted Svetlana audio files:",len(list(AUDIO.glob("*.mp3"))),flush=True)
