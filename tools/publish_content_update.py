#!/usr/bin/env python3
"""Publish verified Steppe content-only ZIP and its catalog using gh CLI.

Runs in a trusted GitHub Actions job with contents:write permission.
The GitHub Token remains in Actions, never in the APK.
"""
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REPO = os.environ.get("GITHUB_REPOSITORY","fabi455/steppe-russisch-kasachstan")
TAG = "content-latest"
CATALOG = "updates/latest.json"
PACKAGE = ROOT/"dist"/"steppe-content.zip"
MANIFEST = ROOT/"dist"/"latest.json"

def gh(*args, input_data=None, check=True):
    return subprocess.run(["gh",*args], input=input_data,text=True,capture_output=True,check=check)

def main():
    if not PACKAGE.is_file() or not MANIFEST.is_file():
        raise RuntimeError("Content package/catalog missing")
    latest = json.loads(MANIFEST.read_text("utf-8"))
    if latest["size"] != PACKAGE.stat().st_size:
        raise RuntimeError("Invalid package size")
    if gh("release","view",TAG,"--repo",REPO,check=False).returncode != 0:
        gh("release","create",TAG,"--repo",REPO,"--latest=false",
           "--title","Steppe – Lerninhalte (automatisch aktualisiert)",
           "--notes","Maschinenlesbare Kursdaten und Audio für die In-App-Aktualisierung. Keine ausführbare App-Datei.")
    gh("release","upload",TAG,str(PACKAGE),"--repo",REPO,"--clobber")
    # Publish the catalog only AFTER the exact checked package is online.
    previous = gh("api",f"repos/{REPO}/contents/{CATALOG}",check=False)
    payload = {
        "message":f"Inhalte r{latest['revision']} bereitstellen [skip ci]",
        "content":base64.b64encode(MANIFEST.read_bytes()).decode("ascii"),
        "branch":"main"
    }
    if previous.returncode == 0:
        payload["sha"] = json.loads(previous.stdout)["sha"]
    elif "404" not in (previous.stdout + previous.stderr):
        raise RuntimeError("Could not read current update catalog")
    with tempfile.NamedTemporaryFile("w",encoding="utf8",suffix=".json") as f:
        json.dump(payload,f,ensure_ascii=False);f.flush()
        gh("api","--method","PUT",f"repos/{REPO}/contents/{CATALOG}","--input",f.name)
    print(f"Published content package revision {latest['revision']} and matching manifest to {CATALOG}",flush=True)

if __name__=="__main__":
    main()
