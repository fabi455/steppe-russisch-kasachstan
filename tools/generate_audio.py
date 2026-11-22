#!/usr/bin/env python3
"""Generate all offline Russian MP3 clips with neural TTS and a reliable fallback.

Preferred existing audio: 128 Svetlana Neural samples from the previous verified APK.
New clips: offline Piper ru_RU-dmitri-medium neural model, no network throttling.
Only build tools need external services. Android playback is always offline.
"""
import asyncio
import json
import os
import random
import subprocess
import tempfile
import wave
from pathlib import Path

from edge_tts import Communicate

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "audio"
VOICE = "ru-RU-SvetlanaNeural"
RATE = "-7%"
PIPER_MODEL = ROOT / "voice" / "ru_RU-dmitri-medium.onnx"

def items_to_speak():
    lessons = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    result = [entry for lesson in lessons for entry in lesson["words"] + lesson["phrases"]]
    if len(lessons) < 20 or len(result) < 321:
        raise RuntimeError(f"Expected at least 20 lessons and 321 speech clips, found {len(lessons)} / {len(result)}")
    if len({w["id"] for w in result}) != len(result) or any(not w["term"].strip() for w in result):
        raise RuntimeError("Invalid/duplicated text-to-speech entry")
    return result

def valid_mp3(file):
    if not file.exists() or file.stat().st_size < 2200:
        return False
    h = file.read_bytes()[:3]
    return h == b"ID3" or (len(h) >= 2 and h[0] == 255 and (h[1] & 224) == 224)

_piper_voice = None
def piper_speech(item, out):
    """Offline deterministic neural synthesis when remote TTS is unavailable."""
    global _piper_voice
    from piper import PiperVoice
    if _piper_voice is None:
        if not PIPER_MODEL.is_file():
            raise RuntimeError(f"Fallback voice model missing: {PIPER_MODEL}")
        _piper_voice = PiperVoice.load(str(PIPER_MODEL))
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "speech.wav"
        with wave.open(str(wav), "wb") as audio_file:
            _piper_voice.synthesize_wav(item["term"], audio_file)
        subprocess.run(
            ["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
             "-i",str(wav),"-ac","1","-ar","24000",
             "-codec:a","libmp3lame","-q:a","5",str(out)],
            check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    if not valid_mp3(out):
        raise RuntimeError(f"Piper MP3 failed validation for {item['id']}")
    return out

async def one(item, sem):
    destination = AUDIO / (item["id"] + ".mp3")
    if valid_mp3(destination):
        return item["id"], "cached"
    async with sem:
        if os.environ.get("STEPPE_AUDIO_MODE", "").strip().lower() in ("local", "piper"):
            # Offline neural speaker. No network or external TTS throttling.
            await asyncio.to_thread(piper_speech, item, destination)
            print("Piper-Dmitri Neural", item["id"], item["term"][:36], flush=True)
            return item["id"], "PiperDmitri"
        part = AUDIO / (item["id"] + ".partial.mp3")
        for attempt in range(2):
            try:
                part.unlink(missing_ok=True)
                async with asyncio.timeout(50):
                    await Communicate(item["term"], VOICE, rate=RATE).save(str(part))
                if not valid_mp3(part):
                    raise RuntimeError("MP3 empty/invalid")
                os.replace(part, destination)
                print("Svetlana",item["id"],item["term"][:36],flush=True)
                await asyncio.sleep(0.6)
                return item["id"], "SvetlanaNeural"
            except Exception as exc:
                part.unlink(missing_ok=True)
                print(f"Edge TTS attempt {attempt+1}/2 for {item['id']}: {exc}",flush=True)
                await asyncio.sleep(1.2+random.random())
        # Never fall back to the old robotic eSpeak voice.
        await asyncio.to_thread(piper_speech, item, destination)
        print("Piper-Dmitri fallback",item["id"],item["term"][:36],flush=True)
        return item["id"], "PiperDmitri"

async def main():
    AUDIO.mkdir(exist_ok=True)
    entries = items_to_speak()
    sem = asyncio.Semaphore(1)
    results = await asyncio.gather(*(one(entry,sem) for entry in entries))
    clips = [AUDIO / (item["id"]+".mp3") for item in entries]
    if len(clips) != len(entries) or not all(valid_mp3(file) for file in clips):
        raise RuntimeError("One or more MP3 assets failed verification")
    sources = dict(results)
    (AUDIO / "sources.json").write_text(
        json.dumps({"source":"Neural synthesizers (not native speaker recordings)",
                    "primary":"ru-RU-SvetlanaNeural",
                    "fallback":"Piper ru_RU-dmitri-medium (CC0 speech data)",
                    "items":sources},ensure_ascii=False,indent=2),encoding="utf-8")
    fallback_count=sum(v=="PiperDmitri" for v in sources.values())
    print(f"SUCCESS: {len(clips)} valid Russian neural MP3s, "
          f"{sum(p.stat().st_size for p in clips)/1048576:.1f} MiB, "
          f"{fallback_count} local neural fallbacks",flush=True)

if __name__=="__main__":
    asyncio.run(main())
