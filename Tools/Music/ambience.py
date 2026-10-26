"""環境音のループを合成する（BGM とは別トラックで、常に薄く流す）。

使い方: python3 Tools/Music/ambience.py

ミックスの考え方
- 1 つのシーンにつき「主役」を 1 つだけ決め、ほかは空間を埋める「背景」として薄く重ねる。
- 素材にはできるだけ本物の録音（sources/、CC0・CC BY）を使う。短い録音は、ランダムな位置から切り出した断片を
  なめらかに重ねて（テクスチャ化）、繰り返しに聞こえない長い音にする。
- 波や車のような「出来事」は、録音の水音を材料にして、寄せる・崩れる・引くなどの形をつける。
- 録音が無い音（虫）だけは合成する。
- ホワイト／ピンク／ブラウンノイズは、そのまま大きく鳴らさず、主役の 20〜30% 程度の隠し味として背景に忍ばせる。
- 音を左右に散らす（主役は片側寄り、背景は広く）。リバーブは使わず、遠さはローパスと音量だけで表す。
- 層ごとの音量を測って、主役がいちばん大きく、背景は十分小さいことを確かめる。

ループは「円」で作る：ノイズは周波数領域で作って周期的にし、はみ出した出来事は頭へ回り込ませる。
そのため、ループの継ぎ目でクロスフェードせずに完全につながる。
"""

import json
import math
import os
import subprocess
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


# ---------------------------------------------------------------- 録音の素材

SOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources")
SOURCE_FILES = {
    "rain": "rain_mike_koenig.ogg",          # CC BY 3.0
    "river": "river_adam_newns.ogg",         # CC0
    "waterfall": "waterfall_leonard_graf.ogg",  # CC0
    "wind": "wind_0ad.ogg",                  # CC BY-SA 3.0（0 A.D.）
    "leaves1": "windleaves_0ad_1.ogg",       # CC BY-SA 3.0（0 A.D.）
    "leaves2": "windleaves_0ad_2.ogg",       # CC BY-SA 3.0（0 A.D.）
}
_active = {}


def active_starts(name, need):
    """断片を切り出してよい開始位置（録音の無音・ほぼ無音の部分にかからない位置）。"""
    key = (name, need)
    if key not in _active:
        src = source(name).mean(axis=1)
        block = int(RATE * 0.25)
        levels = np.array([np.sqrt(np.mean(src[i:i + block] ** 2)) for i in range(0, len(src) - block, block)])
        loud = levels > levels.max() * 10 ** (-30 / 20)  # いちばん大きい所から 30 dB 以内
        if loud.all():
            _active[key] = None  # 無音が無い録音は、どこから切り出してもよい
        else:
            starts = [i * block for i in range(len(loud)) if loud[i: i + need // block + 2].all() and i * block + need < len(src)]
            _active[key] = np.array(starts) if starts else None
    return _active[key]
_sources = {}


def source(name):
    if name not in _sources:
        path = os.path.join(SOURCES_DIR, SOURCE_FILES[name])
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(RATE), "-"],
                             check=True, capture_output=True).stdout
        audio = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)
        _sources[name] = audio / (np.sqrt(np.mean(audio ** 2)) + 1e-12)
    return _sources[name]


def texture(name, n, rng, grain_seconds, pitch_variation=0.03, channels=2):
    """
    短い録音から、繰り返しに聞こえない長い音を作る。
    録音のランダムな位置から断片を切り出し、少しだけ速さ（音程）を変えて、半分ずつ重ねながら並べる。
    重ねる窓は「足し合わせても音量が変わらない」形（サイン窓、50% 重ね）。左右は別々の断片で作るので広がりが出る。
    ループの終わりからはみ出した断片は頭へ回り込むので、継ぎ目なくループする。
    """
    src = source(name)
    grain = int(grain_seconds * RATE)
    hop = grain // 2
    window = np.sin(np.pi * (np.arange(grain) + 0.5) / grain)
    out = np.zeros((n, channels))
    for start in range(0, n, hop):
        for c in range(channels):
            ratio = 1.0 + rng.uniform(-pitch_variation, pitch_variation)
            need = int(grain * ratio) + 2
            starts = active_starts(name, need)
            offset = int(rng.integers(0, len(src) - need)) if starts is None else int(rng.choice(starts))
            segment = src[offset:offset + need, int(rng.integers(0, 2))]
            segment = np.interp(np.arange(grain) * ratio, np.arange(need), segment) * window
            column = np.zeros((n, 1))
            place(column, start, segment[:, None])
            out[:, c] += column[:, 0]
    return out


def mono_texture(name, n, rng, grain_seconds, pitch_variation=0.03):
    return texture(name, n, rng, grain_seconds, pitch_variation, channels=1)[:, 0]


# ---------------------------------------------------------------- 雨（第 2 章：雨の路地裏）

def rain_scene(seconds, rng):
    n = int(RATE * seconds)
    gust = circular_envelope(n, rng, 0.06, floor=0.55)  # 雨脚の強弱（十数秒で変わる）

    # 主役：録音の雨。断片をつないで長くし、雨脚に合わせて少しだけ強弱をつける
    rain = texture("rain", n, rng, grain_seconds=1.2, pitch_variation=0.04) * (0.8 + 0.2 * gust)[:, None]
    # 背景：雨どいを流れる水（録音の川の音を細く、右寄りに）
    gutter = circular_filter(texture("river", n, rng, grain_seconds=2.5, pitch_variation=0.05), lo=200, hi=3500)
    gutter *= np.array([0.45, 1.0])
    # 隠し味：ブラウンノイズ（厚みと奥行き）
    spice = circular_noise(n, rng, lo=60, hi=400, color="brown", width=0.8)

    return [
        ("雨（録音・主役）", rain, 0),
        ("雨どいの水音（録音・背景）", gutter, -14),
        ("ノイズの隠し味", spice, -18),
    ]


# ---------------------------------------------------------------- 波（第 4 章：灯台と港）

def fresh(name, n, rng):
    """出来事 1 つぶんの材料を、毎回新しく作る（同じ断片が別の出来事に使い回されないように）。"""
    if n < RATE * 0.8:
        # 短い音は、録音から直接ランダムに切り出し、少し速さを変える
        src = source(name)
        ratio = 1.0 + rng.uniform(-0.08, 0.08)
        need = int(n * ratio) + 2
        start = int(rng.integers(0, len(src) - need))
        return np.interp(np.arange(n) * ratio, np.arange(need), src[start:start + need, int(rng.integers(0, 2))])
    return mono_texture(name, n, rng, grain_seconds=min(1.2, n / RATE / 2), pitch_variation=0.07)


def wave_event(rng):
    """寄せて、崩れて、引いていく 1 つの波（7〜10 秒）。材料は録音の滝と川の音（波ごとに新しく作る）。"""
    length = rng.uniform(7.0, 10.0)
    n = int(RATE * length)
    t = np.arange(n) / RATE
    peak = rng.uniform(2.2, 3.4)
    after = np.maximum(t - peak, 0.0)
    swell = np.where(t < peak, (t / peak) ** 2, np.exp(-after / 1.8))
    # 崩れる音は一瞬で立ち上がらず、0.3 秒ほどかけてふくらむ
    crash = (1 - np.exp(-np.maximum(t - peak + 0.6, 0) / 0.3)) * np.exp(-after / rng.uniform(0.6, 1.0))
    approach = np.where(t < peak, (t / peak) ** 3, np.exp(-after / 0.8))
    wash = (1 - np.exp(-after / 0.5)) * np.exp(-after / rng.uniform(2.0, 3.2))
    # 波の終わりは途切れさせず、最後の 1.5 秒でなめらかに消す
    fade = np.clip((length - t) / 1.5, 0, 1) ** 2

    low = bandpass(fresh("waterfall", n, rng), 60, 500) * swell * fade
    body = bandpass(fresh("waterfall", n, rng), 200, 1200) * swell * 0.5 * fade
    hiss = bandpass(fresh("waterfall", n, rng), 1500, 6000) * approach * 0.3 * fade
    crash_sound = bandpass(fresh("waterfall", n, rng), 300, 4000) * crash * 0.9 * fade
    fizz = bandpass(fresh("river", n, rng), 1500, 9000) * wash * 0.7 * fade  # 引き波の泡は川のせせらぎから
    return low + body + hiss + crash_sound + fizz


def waves_scene(seconds, rng):
    n = int(RATE * seconds)
    # 主役：寄せては返す波。間隔は不規則に、左右も少しずつ変える
    waves = np.zeros((n, 2))
    t = 0.0
    while t < seconds:
        place(waves, int(t * RATE), pan(wave_event(rng) * rng.uniform(0.7, 1.0), rng.uniform(-0.35, 0.35)))
        t += rng.uniform(6.5, 10.5)

    # 背景 1：岸壁に当たる小さな水音（川の録音の短い断片、左寄り）
    lapping = np.zeros((n, 2))
    t = 0.0
    while t < seconds:
        length = int(RATE * rng.uniform(0.2, 0.45))
        tt = np.arange(length) / RATE
        env = np.minimum(1, tt / 0.03) * np.exp(-tt / (tt[-1] / 3))
        splash = bandpass(fresh("river", length, rng), 250, 2500) * env
        place(lapping, int(t * RATE), pan(splash * rng.uniform(0.5, 1.0), rng.uniform(-0.75, -0.45)))
        t += rng.uniform(0.9, 2.8)

    # 背景 2：遠くの海鳴り（滝の録音を低い音だけにして、遠くに置く）
    surf = circular_filter(texture("waterfall", n, rng, grain_seconds=2.0), lo=40, hi=350)
    # 隠し味：ピンクノイズ
    spice = circular_noise(n, rng, lo=150, hi=6000, color="pink", width=0.8)

    return [
        ("波（録音の水音から・主役）", waves, 0),
        ("岸壁の水音（録音・背景）", lapping, -12),
        ("遠くの海鳴り（録音・背景）", surf, -14),
        ("ノイズの隠し味", spice, -18),
    ]


# ---------------------------------------------------------------- 遠くのハイウェイ（BlueNight の原風景）

def passing_car(rng):
    """遠くを横切る 1 台。タイヤの音は録音の滝の音を材料にする。近づくと高く、遠ざかると低く聞こえる。"""
    length = rng.uniform(5.0, 9.0)
    n = int(RATE * length)
    t = np.linspace(0, 1, n)
    env = np.sin(math.pi * t) ** 2
    approach = np.clip(1.3 - t * 1.6, 0, 1)  # 前半ほど高い帯域が強い
    low = bandpass(fresh("waterfall", n, rng), 90, 350)
    mid = bandpass(fresh("waterfall", n, rng), 350, 900)
    tire = bandpass(fresh("waterfall", n, rng), 1000, 3500)
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

    # 背景：街全体の低いうなり（滝の録音のいちばん低い音だけ。ゆっくり強弱）
    drone = circular_filter(texture("waterfall", n, rng, grain_seconds=2.5), lo=40, hi=170)
    drone *= circular_envelope(n, rng, 0.05, floor=0.7)[:, None]
    # 背景：夜風（録音）。ノイズの隠し味の代わりに、本物の空気の流れを薄く敷く
    wind = texture("wind", n, rng, grain_seconds=3.0, pitch_variation=0.04)

    return [
        ("通り過ぎる車（録音の水音から・主役）", cars, 0),
        ("街のうなり（録音・背景）", drone, -13),
        ("夜風（録音・背景）", wind, -15),
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
    # 背景 3：夜風（録音）
    wind = texture("wind", n, rng, grain_seconds=3.0, pitch_variation=0.04)
    # 背景 4：ときどき風で葉がそよぐ（録音、左右どこかから）
    leaves = np.zeros((n, 2))
    t = rng.uniform(2, 6)
    while t < seconds:
        clip = source(rng.choice(["leaves1", "leaves2"])).mean(axis=1)
        length = int(RATE * rng.uniform(2.0, 4.0))
        start = int(rng.integers(0, len(clip) - length))
        env = np.sin(np.pi * np.arange(length) / length) ** 2
        place(leaves, int(t * RATE), pan(clip[start:start + length] * env, rng.uniform(-0.8, 0.8)))
        t += rng.uniform(7, 16)

    return [
        ("近くの虫（主役）", main, 0),
        ("もう 1 匹（背景）", second, -10),
        ("遠くの合唱（背景）", chorus, -14),
        ("夜風（録音・背景）", wind, -16),
        ("葉のそよぎ（録音・背景）", leaves, -15),
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
