#!/usr/bin/env bash
# 高品質な楽器サンプルを取得する（リポジトリには入れず Tools/Music/.cache に置く）。
#
# Salamander Grand Piano V3（Alexander Holm、CC BY 3.0）
#   16 段階の強さ × 30 音（A・C・D#・F# ごと）＋ 鍵盤を離す音
#   npm の @audio-samples パッケージ（OGG）から取得する。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DEST="$ROOT/Tools/Music/.cache/salamander"
mkdir -p "$DEST"
cd "$DEST"
for name in $(seq -f "piano-velocity%g" 1 16) piano-release; do
  if [ -d "$name" ]; then continue; fi
  tgz=$(npm pack --silent "@audio-samples/$name@1.0.5")
  mkdir -p "$name"
  tar xzf "$tgz" -C "$name" --strip-components=1
  rm -f "$tgz"
  echo "fetched $name"
done
