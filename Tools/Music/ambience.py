"""環境音のループを合成する（BGM とは別トラックで、常に薄く流す）。

使い方: python3 Tools/Music/ambience.py

- rain       雨（細かい雨音＋ときどき大きな雨粒＋遠いざわめき）
- waves      波（ゆっくり寄せて返すうねり＋泡のさざめき）
- highway    遠くのハイウェイ（低いうなり＋ときどき通り過ぎる車）。BlueNight の原風景
- crickets   夜の虫（コオロギ風の鳴き声が、何匹か重なる）

ループは「少し長めに作って、終わりを頭の直前の音へクロスフェード」してつなぐ。
"""

import json
import math
import os
import sys
import tempfile

import numpy as np
import pyloudnorm
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blue_song import ROOT, encode, equal_power_blend, write_wav  # noqa: E402

RATE = 48000
OUT = os.path.join(ROOT, "Assets", "006_Audio", "Ambient")
PREVIEW = os.path.join(ROOT, "Tools", "Music", "out", "preview")
XFADE = int(RATE * 1.0)


def bandpass(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=RATE, output="sos"), x, axis=0)


def lowpass(x, hz, order=2):
    return sosfilt(butter(order, hz, "low", fs=RATE, output="sos"), x, axis=0)


def stereo_noise(rng, n, corr=0.3):
    a = rng.standard_normal(n)
    b = rng.standard_normal(n)
    return np.stack([a, corr * a + (1 - corr) * b], axis=1)


def slow_lfo(n, seconds, cycles, phase=0.0):
    """ループの長さでちょうど cycles 回まわる、ゆっくりした揺れ（0〜1）。"""
    t = np.arange(n) / RATE
    return 0.5 + 0.5 * np.sin(2 * math.pi * cycles * t / seconds + phase)


def rain(seconds, rng):
    n = int(RATE * seconds) + XFADE
    hiss = bandpass(stereo_noise(rng, n, 0.2), 900, 9000) * 0.25
    body = bandpass(stereo_noise(rng, n, 0.5), 250, 1500) * 0.15
    swell = 0.8 + 0.2 * slow_lfo(n, seconds, 3)
    out = (hiss + body) * swell[:, None]
    # 大きめの雨粒（短い「ぽつっ」）
    drop_len = int(RATE * 0.03)
    env = np.exp(-np.linspace(0, 8, drop_len))
    for _ in range(int(seconds * 9)):
        at = rng.integers(0, n - drop_len)
        click = bandpass(rng.standard_normal(drop_len), 1500, 6000, order=1) * env * rng.uniform(0.15, 0.5)
        pan = rng.uniform(-0.8, 0.8)
        out[at:at + drop_len, 0] += click * (1 - pan) / 2
        out[at:at + drop_len, 1] += click * (1 + pan) / 2
    return out


def waves(seconds, rng):
    n = int(RATE * seconds) + XFADE
    base = lowpass(stereo_noise(rng, n, 0.6), 700) * 0.6
    foam = bandpass(stereo_noise(rng, n, 0.3), 1500, 7000) * 0.12
    # 寄せては返す：周期の違う揺れを重ねて、規則的すぎないうねりにする
    surge = (slow_lfo(n, seconds, 4) ** 2) * 0.7 + slow_lfo(n, seconds, 7, 1.3) * 0.3
    foam_env = np.clip(slow_lfo(n, seconds, 4, -0.6) - 0.4, 0, None) * 1.7
    return base * (0.25 + surge)[:, None] + foam * foam_env[:, None]


def highway(seconds, rng):
    n = int(RATE * seconds) + XFADE
    rumble = lowpass(stereo_noise(rng, n, 0.8), 180, order=3) * 1.2
    hum = lowpass(stereo_noise(rng, n, 0.7), 900) * 0.08
    out = rumble * (0.8 + 0.2 * slow_lfo(n, seconds, 2))[:, None] + hum
    # ときどき通り過ぎる車（遠くを左右に流れる）
    for _ in range(int(seconds / 7)):
        dur = int(RATE * rng.uniform(4, 7))
        at = rng.integers(0, n - dur)
        t = np.linspace(0, 1, dur)
        env = np.sin(math.pi * t) ** 2
        car = lowpass(rng.standard_normal(dur), rng.uniform(400, 800)) * env * rng.uniform(0.15, 0.3)
        direction = rng.choice([-1, 1])
        pan = direction * (t * 2 - 1) * 0.8
        out[at:at + dur, 0] += car * (1 - pan) / 2
        out[at:at + dur, 1] += car * (1 + pan) / 2
    return out


def crickets(seconds, rng):
    n = int(RATE * seconds) + XFADE
    out = np.zeros((n, 2))
    t = np.arange(n) / RATE
    for _ in range(4):
        freq = rng.uniform(3800, 4800)
        pulse_rate = rng.uniform(28, 40)       # 1 回の「リリ」の中の細かい震え
        chirp_period = rng.uniform(0.55, 0.9)  # 「リリリ、リリリ」の間隔
        chirp_len = chirp_period * rng.uniform(0.35, 0.5)
        offset = rng.uniform(0, chirp_period)
        carrier = np.sin(2 * math.pi * freq * t)
        trill = (np.sin(2 * math.pi * pulse_rate * t) > 0.2).astype(float)
        gate = (((t + offset) % chirp_period) < chirp_len).astype(float)
        gate = lowpass(gate, 60, order=1)
        voice = carrier * trill * gate * rng.uniform(0.03, 0.06)
        pan = rng.uniform(-0.7, 0.7)
        out[:, 0] += voice * (1 - pan) / 2
        out[:, 1] += voice * (1 + pan) / 2
    out += bandpass(stereo_noise(rng, n, 0.3), 2000, 8000) * 0.004  # 夜の空気
    return lowpass(out, 7000)


SOUNDS = [
    ("rain", "雨", rain, 40.0),
    ("waves", "波", waves, 40.0),
    ("highway", "遠くのハイウェイ", highway, 48.0),
    ("crickets", "夜の虫", crickets, 30.0),
]


def make_loop(raw, seconds):
    """頭の XFADE ぶんを「前の音」として、終わりへクロスフェードする。"""
    n = int(RATE * seconds)
    body = raw[XFADE:XFADE + n].copy()
    body[-XFADE:] = equal_power_blend(body[-XFADE:], raw[:XFADE])
    return body


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREVIEW, exist_ok=True)
    meter = pyloudnorm.Meter(RATE)
    entries = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, title, make, seconds in SOUNDS:
            rng = np.random.default_rng(sum(map(ord, name)))
            loop = make_loop(make(seconds, rng), seconds)
            # 環境音は BGM より十分小さく（BGM は -16 LUFS）
            loop = loop * 10 ** ((-26.0 - meter.integrated_loudness(loop)) / 20.0)
            loop *= min(1.0, 0.7 / (np.max(np.abs(loop)) + 1e-9))
            wav = os.path.join(tmp, f"{name}.wav")
            write_wav(wav, loop)
            encode(wav, os.path.join(OUT, f"ambient_{name}.ogg"))
            preview = np.concatenate([loop, loop])
            write_wav(wav, preview)
            encode(wav, os.path.join(PREVIEW, f"ambient_{name}.mp3"), mp3_kbps=96)
            entries.append({"name": name, "title": title, "file": f"ambient_{name}.ogg",
                            "loopSeconds": seconds, "loudnessLufs": round(meter.integrated_loudness(loop), 1)})
            print(f"ambient_{name:10s} {seconds:4.0f}s  {entries[-1]['loudnessLufs']} LUFS")
    with open(os.path.join(OUT, "ambient_manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"sounds": entries}, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
