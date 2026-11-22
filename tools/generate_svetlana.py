#!/usr/bin/env python3
"""Generate missing Steppe Russian MP3s with Svetlana Neural ONLY.

For reproducibility each of the independent GitHub Actions jobs takes one
shard of missing utterances. The preloaded verified files are immutable.
Every successful output uses edge-tts with voice ru-RU-SvetlanaNeural.
If the external service refuses a recording, fail the job; never fall back
to Piper, Dmitri, eSpeak or another speaker.
"""
import argparse
import asyncio
import json
import os
import random
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
VOICE = "ru-RU-SvetlanaNeural"
RATE = "-7%"


def valid_mp3(file: Path):
    if not file.is_file() or file.stat().st_size<2500:
        return False
    with file.open("rb") as f: header=f.read(3)
    return header==b"ID3" or len(header)>=2 and header[0]==255 and (header[1]&224)==224


async def one(item, folder):
    target=folder/(item["id"]+".mp3")
    if valid_mp3(target):return
    partial=folder/(item["id"]+".partial.mp3")
    for attempt in range(7):
        try:
            partial.unlink(missing_ok=True)
            talk=edge_tts.Communicate(item["term"],voice=VOICE,rate=RATE)
            await asyncio.wait_for(talk.save(str(partial)),timeout=55)
            if not valid_mp3(partial):
                raise ValueError("Neural TTS returned invalid/empty audio")
            os.replace(partial,target)
            print(f"OK {item['id']} {item['term'][:32]} {target.stat().st_size} B",flush=True)
            await asyncio.sleep(1.0+random.random())
            return
        except Exception as exc:
            partial.unlink(missing_ok=True)
            print(f"Retry {attempt+1}/7 {item['id']}: {exc}",flush=True)
            if attempt==6:raise RuntimeError(f"Svetlana not available for {item['id']}: {item['term']}") from exc
            await asyncio.sleep(min(24,(2**attempt)+random.random()*3))


async def main(args):
    lessons=json.loads((ROOT/"content.json").read_text("utf-8"))
    items=[w for l in lessons for w in l["words"]+l["phrases"]]
    if len(items)<321 or len(set(w["id"] for w in items))!=len(items):
        raise RuntimeError("Invalid course IDs")
    reused=Path(args.reused)
    missing=[w for w in items if not valid_mp3(reused/(w["id"]+".mp3"))]
    part=missing[args.part::args.parts]
    dest=Path(args.output)
    dest.mkdir(parents=True,exist_ok=True)
    print(f"All words: {len(items)}, verified Svetlana cache: {len(items)-len(missing)}, "
          f"missing: {len(missing)}, shard {args.part}/{args.parts}: {len(part)}",flush=True)
    for item in part:
        await one(item,dest)
    if not all(valid_mp3(dest/(w["id"]+".mp3")) for w in part):
        raise RuntimeError("Incomplete Svetlana audio shard")
    (dest/("voice-shard-"+str(args.part)+".json")).write_text(
        json.dumps({"voice":VOICE,"part":args.part,"parts":args.parts,
                    "items":[w["id"] for w in part]},ensure_ascii=False),encoding="utf-8")
    print(f"Verified Svetlana recordings: {len(part)} / {len(part)}",flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--reused",default="audio")
    p.add_argument("--output",default="generated")
    p.add_argument("--part",type=int,required=True)
    p.add_argument("--parts",type=int,required=True)
    opts=p.parse_args()
    if opts.parts<1 or opts.part<0 or opts.part>=opts.parts:sys.exit("Invalid shard number")
    asyncio.run(main(opts))
