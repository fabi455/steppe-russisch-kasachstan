#!/usr/bin/env python3
"""Build a portable single HTML page with the complete Steppe 1.2 lexicon and audio."""
from __future__ import annotations
import base64
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
html = (root / "index.html").read_text(encoding="utf-8")
required = [
    ("<link rel=\"manifest\" href=\"manifest.webmanifest\"/>", ""),
    ("<link rel=\"icon\" type=\"image/png\" href=\"icons/icon-192.png\"/>", ""),
    ("<link rel=\"stylesheet\" href=\"style.css\"/>",
     "<style>\n" + (root / "style.css").read_text("utf-8") + "\n</style>"),
    ("<script src=\"content.js\"></script>",
     "<script>\n" + (root / "content.js").read_text("utf-8") + "\n</script>"),
    ("<script src=\"dictionary/ui.js\"></script>",
     "<script>\n" + (root / "dictionary/ui.js").read_text("utf-8") + "\n</script>"),
    ("<script src=\"adaptive.js\"></script>",
     "<script>\\n" + (root / "adaptive.js").read_text("utf-8") + "\\n</script>"),
    ("<script src=\"app.js\"></script>",
     "<script>\n" + (root / "app.js").read_text("utf-8") + "\n</script>"),
]
for before, after in required:
    if before not in html:
        raise RuntimeError("HTML-Einbindung nicht gefunden: " + before)
    html = html.replace(before, after)
js = (root / "dictionary/ru-de.js").read_text("utf-8")
if not "window.STEPPE_LEXICON=" in js:
    raise RuntimeError("Wörterbuch wurde nicht generiert")
html = html.replace("<!-- EMBED_DICTIONARY -->", "<script>\n" + js + "\n</script>")
if "window.STEPPE_LEXICON=" not in html:
    html = html.replace("<script>\n/* Steppe 1.2 –", "<script>\n" + js + "\n</script>\n<script>\n/* Steppe 1.2 –", 1)
clips = {}
for mp3 in sorted((root / "audio").glob("*.mp3")):
    clips[mp3.stem] = "data:audio/mpeg;base64," + base64.b64encode(mp3.read_bytes()).decode("ascii")
if len(clips) != 321:
    raise RuntimeError(f"Erwartet 321 Hörproben, gefunden {len(clips)}")
if "<script>/* EMBED_AUDIO */</script>" not in html:
    raise RuntimeError("Audiomarker fehlt")
html = html.replace("<script>/* EMBED_AUDIO */</script>",
                    "<script>window.STEPPE_EMBED_AUDIO=" +
                    json.dumps(clips, ensure_ascii=False, separators=(",", ":")) + ";</script>")
html = html.replace("</head>", '<meta name="offline-version" content="Steppe 1.2: full dictionary + audio"/>\n</head>')
out = root / "dist" / "Steppe-Russisch-1.3.1-Offline.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"Offline-App: {out.stat().st_size:,} Bytes, {len(clips)} Audios und Wörterbuch eingebettet")
