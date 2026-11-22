#!/usr/bin/env bash
# Reuse the 128 high-quality Svetlana MP3s from the verified Steppe 1.1 release.
# If that old artifact expires, the new generator can create ALL 320 locally.
set -Eeuo pipefail
mkdir -p audio
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
if ! gh run download 44756476911 \
    --repo fabi455/steppe-russisch-kasachstan \
    --name Steppe-Russisch-1.1-Neural-APK \
    --dir "$tmp"; then
  echo "Previous audio artifact unavailable; Piper will create all 320 clips instead."
  exit 0
fi
apk="$(find "$tmp" -type f -name '*.apk' -print -quit)"
if [[ -z "$apk" ]]; then
  echo "Previous artifact had no APK; Piper will create all 320 clips."
  exit 0
fi
unzip -j -o -q "$apk" 'assets/audio/*.mp3' -d audio
count="$(find audio -maxdepth 1 -type f -name '*.mp3' | wc -l)"
echo "Restored $count original Svetlana Neural audio samples."
if [[ "$count" -ne 128 ]]; then
  echo "Warning: fewer/more than 128 original audio samples; missing clips will be generated."
fi
