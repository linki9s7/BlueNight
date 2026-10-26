"""環境音のループを合成する（BGM とは別トラックで、常に薄く流す）。

使い方: python3 Tools/Music/ambience.py

ミックスの考え方
- 1 つのシーンにつき「主役」を 1 つだけ決め、ほかは空間を埋める「背景」として薄く重ねる。
- 主役は面のノイズではなく「出来事」の積み重ねで作る（雨粒の 1 粒 1 粒、寄せては返す 1 つ 1 つの波、1 匹の虫の鳴き声）。
- ホワイト／ピンク／ブラウンノイズは、そのまま大きく鳴らさず、主役の 20〜30% 程度の隠し味として背景に忍ばせる。
- 音を左右に散らす（主役は片側寄り、背景は広く）。リバーブは使わず、遠さはローパスと音量だけで表す。
- 層ごとの音量を測って、主役がいちばん大きく、背景は十分小さいことを確かめる。

ループは「円」で作る：ノイズは周波数領域で作って周期的にし、はみ出した出来事は頭へ回り込ませる。
そのため、ループの継ぎ目でクロスフェードせずに完全につながる。
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
from blue_song import ROOT, encode, write_wav  # noqa: E402

RATE = 48000
OUT = os.path.join(ROOT, "Assets", "006_Audio", "Ambient")
PREVIEW = os.path.join(ROOT, "Tools", "Music", "out", "preview")
TARGET_LUFS = -26.0  # BGM（−16 LUFS）より十分小さく

METER = pyloudnorm.Meter(RATE)


# ---------------------------------------------------------------- 円（周期的）な音を作る道具

def freqs(n):
    return np.fft.rfftfreq(n, 1.0 / RATE)


def band_shape(f, lo=None, hi=None, order=2, color="white"):
    shape = np.ones_like(f)
    safe = np.maximum(f, 1.0)
    if color == "pink":
        shape /= np.sqrt(safe)
    elif color == "brown":
        shape /= safe
    if lo:
        shape /= np.sqrt(1 + (lo / safe) ** (2 * order))
    if hi:
        shape /= np.sqrt(1 + (safe / hi) ** (2 * order))
    shape[0] = 0.0
    return shape


def circular_noise(n, rng, lo=None, hi=None, color="white", width=0.7):
    """周期的なノイズ（ループの頭と終わりが自然につながる）。width は左右の広がり（0 = 真ん中、1 = 左右ばらばら）。"""
    f = freqs(n)
    shape = band_shape(f, lo, hi, color=color)
    chans = []
    for _ in range(2):
        spec = (rng.standard_normal(len(f)) + 1j * rng.standard_normal(len(f))) * shape
        chans.append(np.fft.irfft(spec, n))
    left, right = chans
    right = (1 - width) * left + width * right
    x = np.stack([left, right], axis=1)
    return x / (np.sqrt(np.mean(x ** 2)) + 1e-12)


def circular_filter(x, lo=None, hi=None, order=2):
    """ループを壊さないフィルター（周波数領域で掛ける）。"""
    f = freqs(len(x))
    shape = band_shape(f, lo, hi, order=order)
    shape[0] = 1.0 if lo is None else 0.0
    return np.stack([np.fft.irfft(np.fft.rfft(x[:, c]) * shape, len(x)) for c in range(2)], axis=1)


def circular_envelope(n, rng, rate_hz, floor=0.0):
    """ゆっくり不規則に揺れる 0〜1 の曲線（突風・雨脚の強弱など）。"""
    f = freqs(n)
    spec = (rng.standard_normal(len(f)) + 1j * rng.standard_normal(len(f))) * band_shape(f, hi=rate_hz, order=2)
    x = np.fft.irfft(spec, n)
    x = (x - x.min()) / (x.max() - x.min() + 1e-12)
    return floor + (1 - floor) * x


def pan(mono, position):
    """定位（−1 = 左、0 = 真ん中、1 = 右）。音量が変わらないカーブ。"""
    angle = (position + 1) * math.pi / 4
    return np.stack([mono * math.cos(angle), mono * math.sin(angle)], axis=1)


def place(buffer, start, sound):
    """出来事を置く。終わりからはみ出した分はループの頭へ回り込む。"""
    n = len(buffer)
    start %= n
    end = start + len(sound)
    if end <= n:
        buffer[start:end] += sound
    else:
        buffer[start:] += sound[: n - start]
        buffer[: end - n] += sound[n - start:]


def bandpass(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=RATE, output="sos"), x)


def lowpass(x, hz, order=2):
    return sosfilt(butter(order, hz, "low", fs=RATE, output="sos"), x)


# ---------------------------------------------------------------- 雨（第 2 章：雨の路地裏）

def rain_drop_bank(rng, count=64):
    """1 粒ぶんの音のバリエーション。硬いものに当たる「ぱちっ」と、ときどき水面の「ぽつ」。"""
    bank = []
    for _ in range(count):
        length = int(RATE * rng.uniform(0.003, 0.012))
        t = np.arange(length) / RATE
        tick = rng.standard_normal(length) * np.exp(-t / rng.uniform(0.0012, 0.004))
        center = rng.uniform(1800, 7000)
        tick = bandpass(np.concatenate([tick, np.zeros(64)]), center * 0.6, min(center * 1.6, 20000))
        if rng.random() < 0.25:
            ring = np.sin(2 * math.pi * rng.uniform(1500, 4200) * np.arange(len(tick)) / RATE)
            tick = tick + ring * np.exp(-np.arange(len(tick)) / (RATE * 0.004)) * 0.4
        bank.append(tick / (np.max(np.abs(tick)) + 1e-12))
    return bank


def rain_scene(seconds, rng):
    n = int(RATE * seconds)
    gust = circular_envelope(n, rng, 0.08, floor=0.55)  # 雨脚の強弱（十数秒で変わる）

    # 主役：雨粒。1 粒ずつ置く。大半は小さく、たまに大きな粒
    bank = rain_drop_bank(rng)
    drops = np.zeros((n, 2))
    block = int(RATE * 0.01)
    for b in range(n // block):
        density = 420 * gust[b * block]
        for _ in range(rng.poisson(density * 0.01)):
            at = b * block + int(rng.integers(0, block))
            amp = min(1.0, rng.lognormal(-2.2, 0.75)) * (0.7 + 0.3 * gust[at % n])
            place(drops, at, pan(bank[rng.integers(len(bank))] * amp, rng.uniform(-0.9, 0.9)))

    # 背景 1：ひさしから落ちるしずく（右寄り、ゆっくり不規則）
    drips = np.zeros((n, 2))
    t = 0.0
    while t < seconds:
        f0 = rng.uniform(900, 1500)
        length = int(RATE * 0.09)
        tt = np.arange(length) / RATE
        freq = f0 * (1 - 0.18 * tt / tt[-1])
        plink = np.sin(2 * math.pi * np.cumsum(freq) / RATE) * np.exp(-tt / 0.025)
        place(drips, int(t * RATE), pan(plink * rng.uniform(0.5, 1.0), rng.uniform(0.45, 0.7)))
        t += rng.uniform(0.6, 1.8)

    # 背景 2：遠くで降り続く雨のざわめき（広く、こもった音）
    wash = circular_noise(n, rng, lo=300, hi=2500, color="pink", width=0.9) * gust[:, None]
    # 隠し味：ブラウンノイズ（厚みと奥行き）
    spice = circular_noise(n, rng, lo=60, hi=400, color="brown", width=0.8)

    return [
        ("雨粒（主役）", drops, 0),
        ("しずく（背景）", drips, -11),
        ("遠くの雨（背景）", wash, -13),
        ("ノイズの隠し味", spice, -12),
    ]


# ---------------------------------------------------------------- 波（第 4 章：灯台と港）

def wave_event(rng):
    """寄せて、崩れて、引いていく 1 つの波（7〜10 秒）。"""
    length = rng.uniform(7.0, 10.0)
    n = int(RATE * length)
    t = np.arange(n) / RATE
    peak = rng.uniform(2.2, 3.4)
    after = np.maximum(t - peak, 0.0)
    swell = np.where(t < peak, (t / peak) ** 2, np.exp(-after / 1.8))
    # 崩れる音は一瞬で立ち上がらず、0.3 秒ほどかけてふくらむ
    crash = (1 - np.exp(-np.maximum(t - peak + 0.6, 0) / 0.3)) * np.exp(-after / rng.uniform(0.6, 1.0))
    # 寄せてくる間のざわめき（崩れる前から少しずつ大きくなる）
    approach = np.where(t < peak, (t / peak) ** 3, np.exp(-after / 0.8))
    wash = (1 - np.exp(-after / 0.5)) * np.exp(-after / rng.uniform(2.0, 3.2))
    # 波の終わりは途切れさせず、最後の 1.5 秒でなめらかに消す
    fade = np.clip((length - t) / 1.5, 0, 1) ** 2
    swell, crash, wash, approach = swell * fade, crash * fade, wash * fade, approach * fade

    low = bandpass(rng.standard_normal(n), 60, 450) * swell
    mid = bandpass(rng.standard_normal(n), 300, 2500) * crash * 0.9
    fizz = bandpass(rng.standard_normal(n), 2500, 9000) * wash * 0.35
    # 引き波の泡：細かい粒が消えていく
    bubbles = np.zeros(n)
    for _ in range(int(140 * length)):
        at = int(rng.integers(int(RATE * peak), n - 200))
        if rng.random() < wash[at]:
            bubbles[at:at + 120] += rng.standard_normal(120) * np.exp(-np.arange(120) / 25.0) * 0.5
    bubbles = bandpass(bubbles, 2000, 8000)
    body = bandpass(rng.standard_normal(n), 200, 1200) * swell * 0.5
    hiss = bandpass(rng.standard_normal(n), 1500, 6000) * approach * 0.3
    sound = low + body + hiss + mid + fizz + bubbles * 0.6
    return sound, peak


def buoy_bell(rng):
    """遠くのブイの鐘（倍音がずれた金属の響き）。"""
    f0 = rng.uniform(420, 520)
    length = int(RATE * 5.0)
    t = np.arange(length) / RATE
    partials = [(1.0, 1.0, 4.0), (2.0, 0.5, 3.0), (2.76, 0.55, 2.4), (5.4, 0.25, 1.4), (8.93, 0.12, 0.9)]
    bell = sum(a * np.sin(2 * math.pi * f0 * r * t) * np.exp(-t / d) for r, a, d in partials)
    return lowpass(bell * np.minimum(1, t / 0.004), 2500)  # 遠いので高音を落とす


def waves_scene(seconds, rng):
    n = int(RATE * seconds)

    # 主役：寄せては返す波。間隔は不規則に、左右も少しずつ変える
    waves = np.zeros((n, 2))
    t = 0.0
    while t < seconds:
        sound, _ = wave_event(rng)
        place(waves, int(t * RATE), pan(sound * rng.uniform(0.7, 1.0), rng.uniform(-0.35, 0.35)))
        t += rng.uniform(6.5, 10.5)

    # 背景 1：岸壁に当たる小さな水音（左寄り）
    lapping = np.zeros((n, 2))
    t = 0.0
    while t < seconds:
        length = int(RATE * rng.uniform(0.15, 0.35))
        tt = np.arange(length) / RATE
        env = np.minimum(1, tt / 0.02) * np.exp(-tt / (tt[-1] / 3))
        splash = bandpass(rng.standard_normal(length), 250, 1400) * env
        place(lapping, int(t * RATE), pan(splash * rng.uniform(0.4, 1.0), rng.uniform(-0.75, -0.45)))
        t += rng.uniform(0.9, 2.8)

    # 背景 2：遠くの海鳴り
    surf = circular_noise(n, rng, lo=45, hi=260, color="brown", width=0.9)
    # 背景 3：ずっと遠くのブイの鐘（ごくたまに）
    bells = np.zeros((n, 2))
    for k in range(max(1, int(seconds / 22))):
        place(bells, int(RATE * (k * 22 + rng.uniform(3, 15))), pan(buoy_bell(rng), 0.55))
    # 隠し味：ピンクノイズ
    spice = circular_noise(n, rng, lo=150, hi=6000, color="pink", width=0.8)

    return [
        ("波（主役）", waves, 0),
        ("岸壁の水音（背景）", lapping, -12),
        ("遠くの海鳴り（背景）", surf, -14),
        ("ブイの鐘（背景）", bells, -16),
        ("ノイズの隠し味", spice, -13),
    ]


# ---------------------------------------------------------------- 遠くのハイウェイ（BlueNight の原風景）

def passing_car(rng):
    """遠くを横切る 1 台。近づくと高い音、遠ざかると低い音（ドップラー）を、帯域の重みの変化で表す。"""
    length = rng.uniform(5.0, 9.0)
    n = int(RATE * length)
    t = np.linspace(0, 1, n)
    env = np.sin(math.pi * t) ** 2
    approach = np.clip(1.3 - t * 1.6, 0, 1)  # 前半ほど高い帯域が強い
    low = bandpass(rng.standard_normal(n), 90, 350)
    mid = bandpass(rng.standard_normal(n), 350, 900)
    tire = bandpass(rng.standard_normal(n), 1000, 3500)
    sound = (low * 1.0 + mid * (0.3 + 0.6 * approach) + tire * 0.25 * env) * env
    distance = rng.uniform(0.35, 1.0)
    sound = lowpass(sound, 900 + 2500 * distance) * distance
    direction = rng.choice([-1.0, 1.0])
    positions = direction * (t * 1.6 - 0.8)
    left = sound * np.cos((positions + 1) * math.pi / 4)
    right = sound * np.sin((positions + 1) * math.pi / 4)
    return np.stack([left, right], axis=1)


def highway_scene(seconds, rng):
    n = int(RATE * seconds)

    # 主役：ときどき通り過ぎる車。間があいたり、2 台続いたりする
    cars = np.zeros((n, 2))
    t = rng.uniform(0, 2)
    while t < seconds:
        place(cars, int(t * RATE), passing_car(rng))
        t += rng.choice([rng.uniform(1.5, 3.0), rng.uniform(4.0, 9.0), rng.uniform(4.0, 9.0)])

    # 背景：街全体の低いうなり（ゆっくり強弱）
    drone = circular_noise(n, rng, lo=45, hi=160, color="brown", width=0.8)
    drone *= circular_envelope(n, rng, 0.05, floor=0.7)[:, None]
    # 隠し味：夜の空気（ピンクノイズ）
    spice = circular_noise(n, rng, lo=200, hi=5000, color="pink", width=0.9)

    return [
        ("通り過ぎる車（主役）", cars, 0),
        ("街のうなり（背景）", drone, -13),
        ("ノイズの隠し味", spice, -14),
    ]


# ---------------------------------------------------------------- 夜の虫

def cricket_chirp(rng, f0, pulses):
    """コオロギの 1 回の「リリリ」：細かい脈の連なり。脈ごとに少し音程が下がる。"""
    pulse_len = int(RATE * 0.017)
    gap = int(RATE * rng.uniform(0.032, 0.038))
    out = np.zeros(gap * pulses + pulse_len)
    tt = np.arange(pulse_len) / RATE
    env = np.sin(math.pi * np.arange(pulse_len) / pulse_len) ** 2
    for k in range(pulses):
        freq = f0 * (1 - 0.012 * tt / tt[-1]) * rng.uniform(0.997, 1.003)
        phase = 2 * math.pi * np.cumsum(freq) / RATE
        pulse = (np.sin(phase) + 0.06 * np.sin(2 * phase)) * env * rng.uniform(0.8, 1.0)
        out[k * gap:k * gap + pulse_len] += pulse
    return out


def cricket_song(n, rng, f0, period, position, distance=1.0):
    """1 匹ぶん。しばらく鳴いては休む。"""
    voice = np.zeros((n, 2))
    seconds = n / RATE
    t = rng.uniform(0, 1)
    bout_end = t + rng.uniform(5, 14)
    while t < seconds:
        if t > bout_end:
            t += rng.uniform(1.0, 4.0)        # ひと休み
            bout_end = t + rng.uniform(5, 14)
            continue
        chirp = cricket_chirp(rng, f0, int(rng.choice([3, 4, 4, 5])))
        place(voice, int(t * RATE), pan(chirp * distance * rng.uniform(0.85, 1.0), position))
        t += period * rng.uniform(0.92, 1.08)
    return voice


def crickets_scene(seconds, rng):
    n = int(RATE * seconds)

    # 主役：近くの 1 匹（少し右寄り）
    main = cricket_song(n, rng, f0=4600, period=0.62, position=0.3)
    # 背景 1：少し離れたもう 1 匹（左寄り、小さく）
    second = cricket_song(n, rng, f0=4150, period=0.78, position=-0.45)
    # 背景 2：遠くの虫の合唱（たくさん、こもった音）
    chorus = np.zeros((n, 2))
    for _ in range(18):
        chorus += cricket_song(n, rng, f0=rng.uniform(3600, 5200), period=rng.uniform(0.4, 1.1),
                               position=rng.uniform(-0.9, 0.9), distance=rng.uniform(0.3, 1.0))
    chorus = circular_filter(chorus, hi=3800, order=2)
    # 隠し味：夜の空気
    spice = circular_noise(n, rng, lo=150, hi=4000, color="pink", width=0.9)

    return [
        ("近くの虫（主役）", main, 0),
        ("もう 1 匹（背景）", second, -10),
        ("遠くの合唱（背景）", chorus, -14),
        ("ノイズの隠し味", spice, -15),
    ]


SCENES = [
    ("rain", "雨（第2章 雨の路地裏）", rain_scene, 60.0),
    ("waves", "波（第4章 灯台と港）", waves_scene, 60.0),
    ("highway", "遠くのハイウェイ", highway_scene, 60.0),
    ("crickets", "夜の虫", crickets_scene, 45.0),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREVIEW, exist_ok=True)
    entries = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, title, make, seconds in SCENES:
            rng = np.random.default_rng(sum(map(ord, name)) * 7919)
            layers = []
            for label, signal, relative_db in make(seconds, rng):
                # 層ごとに「主役から何 dB 下か」を、実際の聞こえ方の音量（LUFS）でそろえる
                signal = signal * 10 ** ((TARGET_LUFS + relative_db - METER.integrated_loudness(signal)) / 20.0)
                layers.append((label, signal))
            scene = sum(layer for _, layer in layers)
            gain = 10 ** ((TARGET_LUFS - METER.integrated_loudness(scene)) / 20.0)
            scene *= gain
            peak = np.max(np.abs(scene))
            if peak > 0.7:
                scene *= 0.7 / peak
                gain *= 0.7 / peak

            print(f"ambient_{name}  {seconds:.0f}s  {METER.integrated_loudness(scene):.1f} LUFS")
            report = []
            main_level = METER.integrated_loudness(layers[0][1] * gain)
            for label, layer in layers:
                level = METER.integrated_loudness(layer * gain)
                report.append({"layer": label, "lufs": round(level, 1), "relativeToMainDb": round(level - main_level, 1)})
                print(f"    {label:16s} {level:6.1f} LUFS  （主役から {level - main_level:+.1f} dB）")

            wav = os.path.join(tmp, f"{name}.wav")
            write_wav(wav, scene)
            encode(wav, os.path.join(OUT, f"ambient_{name}.ogg"))
            write_wav(wav, np.concatenate([scene, scene]))
            encode(wav, os.path.join(PREVIEW, f"ambient_{name}.mp3"), mp3_kbps=128)
            entries.append({"name": name, "title": title, "file": f"ambient_{name}.ogg", "loopSeconds": seconds,
                            "loudnessLufs": round(METER.integrated_loudness(scene), 1), "layers": report})
    with open(os.path.join(OUT, "ambient_manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"sounds": entries}, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
