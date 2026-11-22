#!/usr/bin/env python3
"""Generate all Steppe offline MP3s using a natural Russian neural voice.

This build-time tool uses an unofficial Microsoft Edge Read Aloud endpoint.
The Android app plays bundled files fully offline. No fallback to eSpeak.
"""
import asyncio
import json
import os
import random
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content.json'
AUDIO = ROOT / 'audio'
VOICE = 'ru-RU-SvetlanaNeural'
RATE = '-7%'
CONCURRENCY = 2


def items_to_speak():
    lessons = json.loads(CONTENT.read_text(encoding='utf-8'))
    result = [item for lesson in lessons for item in lesson['words'] + lesson['phrases']]
    assert len(result) == 320, f'Erwartet: 320 Einträge, gefunden: {len(result)}'
    assert len({item['id'] for item in result}) == len(result), 'Doppelte Audio-IDs'
    for item in result:
        assert item['term'].strip(), item['id']
    return result


async def generate(item, semaphore):
    destination = AUDIO / (item['id'] + '.mp3')
    if destination.exists() and destination.stat().st_size > 2500:
        return destination
    async with semaphore:
        for attempt in range(5):
            partial = AUDIO / (item['id'] + '.partial.mp3')
            try:
                partial.unlink(missing_ok=True)
                speech = edge_tts.Communicate(item['term'], VOICE, rate=RATE)
                await asyncio.wait_for(speech.save(str(partial)), timeout=55)
                data = partial.read_bytes()
                if len(data) < 2500 or not (data[:3] == b'ID3' or data[:2] in (b'\xff\xfb', b'\xff\xf3', b'\xff\xf2')):
                    raise ValueError(f'MP3 unvollständig/ungültig: {item["id"]} ({len(data)} Bytes)')
                os.replace(partial, destination)
                print(f'OK {item["id"]} {item["term"][:32]} ({len(data)} Bytes)', flush=True)
                return destination
            except Exception as exc:
                partial.unlink(missing_ok=True)
                print(f'Neural TTS Versuch {attempt + 1}/5 für {item["id"]}: {exc}', flush=True)
                if attempt == 4:
                    raise RuntimeError(f'Keine neuronale Audioausgabe für {item["term"]}') from exc
                await asyncio.sleep(min(30, 2 ** attempt * 2 + random.random()))


async def main():
    AUDIO.mkdir(exist_ok=True)
    items = items_to_speak()
    semaphore = asyncio.Semaphore(CONCURRENCY)
    await asyncio.gather(*(generate(item, semaphore) for item in items))
    files = [AUDIO / (item['id'] + '.mp3') for item in items]
    assert all(f.exists() and f.stat().st_size > 2500 for f in files)
    print(f'Alle {len(files)} neuronalen MP3s vorhanden, Gesamtgröße '
          f'{sum(f.stat().st_size for f in files) / 1024 / 1024:.2f} MiB; Stimme: {VOICE}', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
