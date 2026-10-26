"""Salamander Grand Piano V3（Alexander Holm、CC BY 3.0）を鳴らす、小さなサンプラー。

- 16 段階の強さ（ベロシティレイヤー）× A・C・D#・F# ごとに録音された音を使う
- 録音の無い音は、いちばん近い録音を ±1 半音だけ音程をずらして使う
- ダンパーペダル：踏んでいる間は鍵盤を離しても音が続き、ペダルを上げた瞬間に止まる
- 鍵盤を離すと弦が止まる（高音域の F6 より上はダンパーが無いので鳴り続ける）
- 鍵盤を離したときの小さな「コトッ」という音（リリース音）も鳴らす

サンプルは scripts/fetch_samples.sh で Tools/Music/.cache/salamander に取得する。
"""

import math
import os
import re
import subprocess
from functools import lru_cache

import numpy as np
from scipy.signal import resample

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache", "salamander")
RATE = 48000
NOTE_INDEX = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
NO_DAMPER_FROM = 89  # F6 より上はダンパーが無い


def available():
    # BLUENIGHT_NO_SALAMANDER=1 で、比較用に以前の音源（FluidSynth）へ戻せる
    if os.environ.get("BLUENIGHT_NO_SALAMANDER"):
        return False
    return os.path.isdir(os.path.join(CACHE, "piano-velocity16", "audio"))


def decode(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(RATE), "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


@lru_cache(maxsize=None)
def roots():
    """録音のある音（MIDI 番号）の一覧。"""
    found = []
    for name in os.listdir(os.path.join(CACHE, "piano-velocity8", "audio")):
        m = re.match(r"([A-G]#?)(\d)v8\.ogg$", name)
        if m:
            found.append(12 * (int(m.group(2)) + 1) + NOTE_INDEX[m.group(1)])
    return sorted(found)


def note_name(midi):
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{names[midi % 12]}{midi // 12 - 1}"


@lru_cache(maxsize=None)
def sample(root, layer, shift):
    """録音 1 つ（必要なら音程をずらしたもの）。同じ組み合わせは 1 回だけ作る。"""
    path = os.path.join(CACHE, f"piano-velocity{layer}", "audio", f"{note_name(root)}v{layer}.ogg")
    audio = decode(path)
    if shift == 0:
        return audio
    ratio = 2 ** (shift / 12.0)
    return resample(audio, int(round(len(audio) / ratio)), axis=0)


@lru_cache(maxsize=None)
def release_noise(midi):
    key = midi - 20  # A0 = 1
    path = os.path.join(CACHE, "piano-release", "audio", f"rel{key}.ogg")
    return decode(path) if os.path.exists(path) else np.zeros((1, 2))


def pick(pitch, velocity):
    layer = max(1, min(16, math.ceil(velocity / 8)))
    root = min(roots(), key=lambda r: (abs(r - pitch), r < pitch))
    return root, layer, pitch - root


def render(events, pedal_down, length):
    """
    events: (開始秒, 終了秒, MIDI 番号, 強さ) のリスト
    pedal_down: ペダルを踏んでいる区間 (始, 終) のリスト
    """
    out = np.zeros((length, 2))
    for start, end, pitch, velocity in events:
        root, layer, shift = pick(pitch, velocity)
        audio = sample(root, layer, shift)

        # ペダルを踏んでいる間に鍵盤を離した音は、ペダルを上げるまで続く
        release = end
        for a, b in pedal_down:
            if a <= end <= b:
                release = b
                break

        begin = int(start * RATE)
        if begin >= length:
            continue
        held = max(0, int((release - start) * RATE))
        if pitch >= NO_DAMPER_FROM:
            tau = 2.5
        else:
            tau = 0.07 + 0.25 * (NO_DAMPER_FROM - pitch) / 60.0  # 低い弦ほど止まるのに少し時間がかかる
        tail = int(tau * 6 * RATE)
        n = min(len(audio), held + tail, length - begin)
        env = np.ones(n)
        if held < n:
            env[held:] = np.exp(-np.arange(n - held) / (tau * RATE))
        # 発音の頭の小さなプチッを防ぐ
        env[: min(48, n)] *= np.linspace(0, 1, min(48, n))
        out[begin:begin + n] += audio[:n] * env[:, None]

        # 鍵盤を離したときの音（ダンパーが弦に触れる音）
        noise = release_noise(pitch)
        at = int(release * RATE)
        if pitch < NO_DAMPER_FROM and at < length:
            m = min(len(noise), length - at)
            out[at:at + m] += noise[:m] * (0.25 + 0.5 * velocity / 127)
    return out
