#!/usr/bin/env python3
"""Generate locally stored Russian pronunciation practice MP3s with eSpeak + FFmpeg.
The speech is synthetic and not a replacement for recordings by native speakers.
"""
import json, subprocess, tempfile, concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
words=[item for lesson in json.loads((ROOT/'content.json').read_text('utf-8')) for item in lesson['words']+lesson['phrases']]
audio_dir=ROOT/'audio';audio_dir.mkdir(exist_ok=True)

def make(item):
    out=audio_dir/(item['id']+'.mp3')
    if out.exists() and out.stat().st_size>500:return out.name
    with tempfile.TemporaryDirectory() as t:
        wav=str(Path(t)/'voice.wav')
        subprocess.run(['espeak','-v','ru','-s','137','-a','170','-w',wav,item['term']],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-i',wav,'-ac','1','-ar','24000','-codec:a','libmp3lame','-q:a','6',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    return out.name
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    names=list(pool.map(make,words))
print(f'{len(names)} MP3-Audios erstellt / geprüft; Gesamtgröße {sum(p.stat().st_size for p in audio_dir.glob("*.mp3"))//1024} KiB')
