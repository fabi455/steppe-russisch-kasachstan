#!/usr/bin/env bash
# Reuse all 320 verified neural Russian MP3s from Steppe 1.3 and build only new clips.
# Fall back to the 128 Svetlana clips from 1.1 if the new artifact is unavailable.
set -Eeuo pipefail
mkdir -p audio
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

retrieve() {
  local run="$1" artifact="$2" expected="$3"
  rm -rf "$tmp"/*
  if ! gh run download "$run" --repo fabi455/steppe-russisch-kasachstan --name "$artifact" --dir "$tmp"; then
    echo "Optional audio artifact '$artifact' unavailable."
    return 1
  fi
  local apk
  apk="$(find "$tmp" -type f -name '*.apk' -print -quit)"
  if [[ -z "$apk" ]]; then
    echo "Artifact '$artifact' does not contain an APK."
    return 1
  fi
  unzip -j -o -q "$apk" 'assets/audio/*.mp3' -d audio
  local count
  count="$(find audio -maxdepth 1 -type f -name '*.mp3' | wc -l)"
  echo "Restored $count MP3s from '$artifact' (expected $expected)."
  [[ "$count" -eq "$expected" ]]
}

if retrieve 45064634129 Steppe-Russisch-1.3-Adaptiv-APK 320; then
  echo "Only the new phrase Понаехали! needs speech synthesis."
  exit 0
fi
if retrieve 44756476911 Steppe-Russisch-1.1-Neural-APK 128; then
  echo "Older audio recovered; Piper will generate any other missing clips."
  exit 0
fi
echo "No previous APK available. Piper will synthesize all 321 clips."
