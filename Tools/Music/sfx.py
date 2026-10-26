"""BlueNight の効果音を作る。

使い方: python3 Tools/Music/sfx.py

方針
- 現実の物の音（足音・ランタン・スイッチ）は、録音（sources/、パブリックドメイン・CC0・CC BY）を材料に組み立てる。
  例：足音 =「かかと」（木を叩く録音を小さく硬くしたもの）＋「つま先」＋「靴底のこすれ」（雨粒の録音）。
- 同じ音の連続が機械的に聞こえないよう、足音などは 1 種類につき 6 パターン作り、ゲーム側で順番を変えて鳴らす。
- 影の音は、水の録音を逆再生したり低くしたりして「この世のものではない」感じを出す。
- 電灯のうなりのような電気の音だけは合成する（もともと単純な音なので不自然になりにくい）。
- UI の音は uisfx の dreamy セット（CC0）を使い、余韻の後ろの無音を詰めて音量をそろえる。

出力：Assets/006_Audio/SE/<種類>/*.ogg と se_manifest.json、試聴用 Tools/Music/out/preview/se_*.mp3
"""

import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from blue_song import ROOT, encode, write_wav  # noqa: E402

RATE = 48000
SRC = os.path.join(HERE, "sources")
OUT = os.path.join(ROOT, "Assets", "006_Audio", "SE")
PREVIEW = os.path.join(ROOT, "Tools", "Music", "out", "preview")
VARIATIONS = 6


# ---------------------------------------------------------------- 道具

def load(name):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(SRC, name), "-f", "f32le", "-ac", "1",
                          "-ar", str(RATE), "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def seconds(s):
    return int(round(s * RATE))


def lowpass(x, hz, order=2):
    return sosfilt(butter(order, hz, "low", fs=RATE, output="sos"), x)


def highpass(x, hz, order=2):
    return sosfilt(butter(order, hz, "high", fs=RATE, output="sos"), x)


def bandpass(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=RATE, output="sos"), x)


def speed(x, ratio):
    """速さ（＝音の高さ）を変える。ratio > 1 で高く短く。"""
    n = int(len(x) / ratio)
    return np.interp(np.arange(n) * ratio, np.arange(len(x)), x)


def decay(n, tau):
    return np.exp(-np.arange(n) / (tau * RATE))


def fade(x, fade_in=0.002, fade_out=0.02):
    x = x.copy()
    a, b = min(len(x), seconds(fade_in)), min(len(x), seconds(fade_out))
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b) ** 2
    return x


def onsets(x, min_gap=0.06, threshold=0.3):
    """録音の中の「打撃」の始まりの位置（ノックの 1 回 1 回など）。"""
    block = seconds(0.001)
    env = np.array([np.abs(x[i:i + block]).max() for i in range(0, len(x) - block, block)])
    peak = env.max()
    found, last = [], -10 ** 9
    for i in range(1, len(env)):
        if env[i] > peak * threshold and env[i] >= env[i - 1] and (i + 1 >= len(env) or env[i] >= env[i + 1]):
            j = i
            while j > 0 and env[j - 1] > env[i] * 0.1 and i - j < 20:
                j -= 1
            if (j - last) * block > seconds(min_gap):
                found.append(j * block)
                last = j
    return found


def slices(x, length, **kw):
    return [x[s:s + seconds(length)] for s in onsets(x, **kw) if s + seconds(length) <= len(x)]


def mix(length, *parts):
    """(音, 開始秒, 音量) を重ねる。"""
    out = np.zeros(seconds(length))
    for sound, at, gain in parts:
        sound = fade(sound, fade_in=0.001, fade_out=0.004)  # 部品の頭と終わりの「プチッ」を防ぐ
        start = seconds(at)
        n = min(len(sound), len(out) - start)
        if n > 0:
            out[start:start + n] += sound[:n] * gain
    return out


def random_slice(x, length, rng):
    n = seconds(length)
    start = int(rng.integers(0, len(x) - n))
    return x[start:start + n]


def peak_to(x, db):
    return x * (10 ** (db / 20.0) / (np.max(np.abs(x)) + 1e-12))


def stereo(x, pan=0.0):
    angle = (pan + 1) * math.pi / 4
    return np.stack([x * math.cos(angle), x * math.sin(angle)], axis=1)


def trim_tail(x, floor_db=-60.0):
    """後ろの無音を詰める。"""
    level = np.abs(x) if x.ndim == 1 else np.abs(x).max(axis=1)
    loud = np.where(level > np.max(level) * 10 ** (floor_db / 20.0))[0]
    return x[: loud[-1] + seconds(0.01)] if len(loud) else x


# ---------------------------------------------------------------- 材料

class Materials:
    def __init__(self):
        self.knocks = slices(load("knock_wood_stephan.ogg"), 0.16)        # 木を叩く 1 回ずつ
        self.ticks = slices(load("clock_ticking_natalie.ogg"), 0.07)      # 時計の「カチ」1 回ずつ
        self.clangs = slices(load("metal_clang.ogg"), 0.8, threshold=0.2)  # 金属を打つ 1 回ずつ
        plop = load("plop_pacomav.ogg")
        self.plop = plop[max(0, onsets(plop)[0] - seconds(0.002)):]  # 頭の無音を詰める
        self.rain = load("rain_mike_koenig.ogg")
        self.river = load("river_adam_newns.ogg")
        self.waterfall = load("waterfall_leonard_graf.ogg")

    def pick(self, items, rng):
        return items[int(rng.integers(len(items)))]


# ---------------------------------------------------------------- 足音

def step_stone(m, rng):
    """石畳・アスファルト：硬く短いかかと＋小さなつま先＋靴底のこすれ。ルリは軽く歩く。"""
    heel = lowpass(speed(m.pick(m.knocks, rng), rng.uniform(1.2, 1.4)), 3200)
    heel = heel[: seconds(0.1)] * decay(len(heel[: seconds(0.1)]), 0.015)  # 硬い地面なので響きは短く
    toe = lowpass(speed(m.pick(m.knocks, rng), rng.uniform(1.6, 1.9)), 4200)[: seconds(0.05)]
    toe *= decay(len(toe), 0.012)
    grit = bandpass(random_slice(m.rain, 0.09, rng), 2500, 9000) * decay(seconds(0.09), 0.02)
    step = mix(0.24, (heel, 0.0, 1.0), (toe, rng.uniform(0.045, 0.07), 0.35), (grit, rng.uniform(0.0, 0.012), 0.3))
    return fade(highpass(step, 90))


def step_wet(m, rng):
    """濡れた路面・水たまり：やわらかいかかと＋小さな水はね。"""
    heel = lowpass(speed(m.pick(m.knocks, rng), rng.uniform(1.15, 1.3)), 2500)[: seconds(0.1)]
    heel *= decay(len(heel), 0.02)
    splash = speed(m.plop, rng.uniform(1.4, 2.0))
    water = bandpass(random_slice(m.river, 0.16, rng), 1200, 7000) * decay(seconds(0.16), 0.045)
    step = mix(0.28, (heel, 0.0, 0.8), (splash, rng.uniform(0.0, 0.01), 0.35), (water, 0.005, 0.5))
    return fade(highpass(step, 90))


def step_wood(m, rng):
    """木の床（夜の学校）：少し響くかかと＋つま先。"""
    heel = lowpass(speed(m.pick(m.knocks, rng), rng.uniform(0.95, 1.1)), 5000)[: seconds(0.14)]
    heel *= decay(len(heel), 0.04)
    toe = lowpass(speed(m.pick(m.knocks, rng), rng.uniform(1.3, 1.5)), 5000)[: seconds(0.06)]
    toe *= decay(len(toe), 0.015)
    step = mix(0.26, (heel, 0.0, 1.0), (toe, rng.uniform(0.05, 0.075), 0.3))
    return fade(highpass(step, 70))


# ---------------------------------------------------------------- ランタン

def clink(m, rng, ratio, length=0.4, tau=0.08):
    sound = lowpass(speed(m.pick(m.clangs, rng), ratio), 8000)[: seconds(length)]
    return sound * decay(len(sound), tau)


def lantern_hang(m, rng):
    """フックに掛ける：留め金の「カチ」→ 小さな金具の音 → 揺れて止まる軽い音。"""
    latch = speed(m.pick(m.ticks, rng), rng.uniform(0.85, 0.95))
    sound = mix(0.7, (latch, 0.0, 0.7), (clink(m, rng, rng.uniform(1.4, 1.6)), 0.05, 0.45),
                (clink(m, rng, rng.uniform(1.8, 2.1), tau=0.05), rng.uniform(0.17, 0.22), 0.18))
    return fade(highpass(sound, 150))


def lantern_take(m, rng):
    """フックから外す：金具の音 → 持ち手がこすれる音 → 「カチ」。"""
    scrape = bandpass(random_slice(m.rain, 0.12, rng), 1500, 6000) * np.hanning(seconds(0.12))
    sound = mix(0.55, (clink(m, rng, rng.uniform(1.5, 1.7)), 0.0, 0.4), (scrape, 0.04, 0.25),
                (speed(m.pick(m.ticks, rng), 1.0), 0.13, 0.55))
    return fade(highpass(sound, 150))


# ---------------------------------------------------------------- 街灯

def mains_hum(length, rng, flicker=False):
    """古い街灯のうなり（100 Hz とその倍音）と、ときどきの「ジジッ」。"""
    t = np.arange(seconds(length)) / RATE
    hum = sum((1.0 / k ** 1.3) * np.sin(2 * math.pi * 100 * k * t + rng.uniform(0, 6.28)) for k in range(1, 14))
    buzz_gate = (np.sin(2 * math.pi * 100 * t) > 0.92).astype(float)
    buzz = bandpass(rng.standard_normal(len(t)), 2000, 5000) * lowpass(buzz_gate, 3000)
    sound = lowpass(hum, 2500) * 0.6 + buzz * 0.25
    if flicker:
        gate = np.ones(len(t))
        for a, b in [(0.05, 0.11), (0.16, 0.2)]:
            gate[seconds(a):seconds(b)] = 0.15
        sound *= lowpass(gate, 200)
    return sound


def light_on(m, rng):
    click = speed(m.pick(m.ticks, rng), 0.75)
    hum = mains_hum(0.9, rng, flicker=True) * np.minimum(1, np.arange(seconds(0.9)) / seconds(0.2))
    hum[-seconds(0.45):] *= np.linspace(1, 0, seconds(0.45)) ** 2
    return fade(mix(1.0, (click, 0.0, 0.9), (hum, 0.03, 0.07)))


def light_off(m, rng):
    click = speed(m.pick(m.ticks, rng), 0.7)
    hum = mains_hum(0.25, rng) * np.linspace(1, 0, seconds(0.25)) ** 2
    return fade(mix(0.4, (hum, 0.0, 0.12), (click, 0.0, 0.9)))


# ---------------------------------------------------------------- 影

def shadow_presence(m, rng, length=4.0):
    """影が近くにいる気配（くり返し再生用）。逆さに流した水の音を細くして、息のようにゆらす。"""
    xfade = seconds(0.5)
    n = seconds(length)
    material = bandpass(random_slice(m.river, length + 0.5, rng)[::-1], 300, 1800)
    t = np.arange(len(material)) / RATE
    breath = 0.6 + 0.4 * np.sin(2 * math.pi * t / length * 3) ** 2  # ループの長さで 3 回、息をする
    material *= breath
    loop = material[xfade:xfade + n].copy()
    w = np.linspace(0, 1, xfade)
    loop[-xfade:] = loop[-xfade:] * np.cos(w * math.pi / 2) + material[:xfade] * np.sin(w * math.pi / 2)
    return loop


def shadow_escape(m, rng):
    """影がすっと逃げる：滝の音を細くして、高い音から低い音へ流しながら左右に横切る。"""
    n = seconds(0.75)
    raw = random_slice(m.waterfall, 0.75, rng)
    t = np.linspace(0, 1, n)
    hi, mid, lo = bandpass(raw, 2500, 7000), bandpass(raw, 900, 2500), bandpass(raw, 250, 900)
    body = hi * np.clip(1 - t * 2, 0, 1) + mid * np.sin(math.pi * t) + lo * np.clip(t * 2 - 0.5, 0, 1)
    env = np.minimum(1, t / 0.08) * (1 - t) ** 1.5
    body = fade(body * env)
    direction = rng.choice([-1.0, 1.0])
    pos = direction * (t * 1.4 - 0.7)
    return np.stack([body * np.cos((pos + 1) * math.pi / 4), body * np.sin((pos + 1) * math.pi / 4)], axis=1)


def shadow_capture(m, rng):
    """影を捕まえた：逆再生の金属の響きが吸い込まれるように近づき、やわらかい「どん」で止まる。"""
    tail = lowpass(speed(m.pick(m.clangs, rng), 0.55), 3000)[: seconds(0.7)]
    swell = tail[::-1] * np.linspace(0, 1, len(tail)) ** 2
    thud = lowpass(speed(m.pick(m.knocks, rng), 0.5), 700)[: seconds(0.3)] * decay(seconds(0.3), 0.08)
    ring = lowpass(speed(m.pick(m.clangs, rng), 0.55), 3000)[: seconds(0.9)] * decay(seconds(0.9), 0.3)
    air = bandpass(random_slice(m.waterfall, 0.9, rng), 2000, 6000) * decay(seconds(0.9), 0.25)
    mono = mix(1.7, (swell, 0.0, 0.6), (thud, 0.68, 1.0), (ring, 0.7, 0.18), (air, 0.7, 0.12))
    return fade(highpass(mono, 50), fade_out=0.15)


# ---------------------------------------------------------------- UI（uisfx dreamy、CC0）

UI_CUES = {
    "decide": ("select.ogg", "決定"),
    "cancel": ("cancel.ogg", "キャンセル"),
    "text_blip": ("typing.ogg", "会話の文字送り"),
    "menu_open": ("open.ogg", "メニューを開く"),
    "menu_close": ("close.ogg", "メニューを閉じる"),
    "cursor": ("focus.ogg", "カーソル移動"),
    "journal_add": ("notification.ogg", "ことば帳に言葉が増えた"),
}


def ui(name):
    return trim_tail(load(os.path.join("uisfx_dreamy", name)))


# ---------------------------------------------------------------- 一覧と書き出し

# (種類, 名前, 作り方, パターン数, ピーク dBFS, くり返し再生か, 説明)
CATALOG = [
    ("footsteps", "step_stone", step_stone, VARIATIONS, -18, False, "足音：石畳・アスファルト"),
    ("footsteps", "step_wet", step_wet, VARIATIONS, -18, False, "足音：濡れた路面・水たまり"),
    ("footsteps", "step_wood", step_wood, VARIATIONS, -18, False, "足音：木の床"),
    ("lantern", "lantern_hang", lantern_hang, 3, -12, False, "ランタンをフックに掛ける"),
    ("lantern", "lantern_take", lantern_take, 3, -12, False, "ランタンをフックから外す"),
    ("light", "light_on", light_on, 2, -12, False, "街灯をつける（カチッ＋ジジッ）"),
    ("light", "light_off", light_off, 2, -12, False, "街灯を消す"),
    ("shadow", "shadow_presence", shadow_presence, 1, -24, True, "影の気配（近くにいる間くり返す）"),
    ("shadow", "shadow_escape", shadow_escape, 3, -10, False, "影がすっと逃げる"),
    ("shadow", "shadow_capture", shadow_capture, 1, -8, False, "影を捕まえた"),
]
UI_LEVELS = {"text_blip": -20, "cursor": -16}


def main():
    os.makedirs(PREVIEW, exist_ok=True)
    m = Materials()
    manifest = {"groups": []}
    preview = []

    with tempfile.TemporaryDirectory() as tmp:
        def export(group, name, sound):
            path = os.path.join(OUT, group, f"{name}.ogg")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            wav = os.path.join(tmp, "x.wav")
            write_wav(wav, sound)
            encode(wav, path)
            return f"{group}/{name}.ogg"

        for group, name, make, count, peak_db, loop, title in CATALOG:
            rng = np.random.default_rng(sum(map(ord, name)) * 7919)
            files, sounds = [], []
            for i in range(count):
                sound = peak_to(make(m, rng), peak_db)
                sounds.append(sound)
                files.append(export(group, f"{name}_{i}" if count > 1 else name, sound))
            manifest["groups"].append({"name": name, "title": title, "files": files, "loop": loop,
                                       "randomOrder": count > 1, "peakDb": peak_db})
            print(f"{name:16s} {count} パターン  {title}")
            preview.append((name, sounds, group == "footsteps"))

        ui_sounds = []
        for name, (file, title) in UI_CUES.items():
            sound = peak_to(ui(file), UI_LEVELS.get(name, -12))
            manifest["groups"].append({"name": name, "title": title, "files": [export("ui", name, sound)], "loop": False,
                                       "randomOrder": False, "peakDb": UI_LEVELS.get(name, -12)})
            ui_sounds.append(sound)
            print(f"{name:16s} 1 パターン  {title}")

        with open(os.path.join(OUT, "se_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
            f.write("\n")

        write_previews(tmp, m, preview, ui_sounds)


def write_previews(tmp, m, preview, ui_sounds):
    """試聴用：① 全部を順番に（足音は 8 歩ずつ歩く速さで） ② 雨の夜の場面の中で鳴らした例。"""
    def as_stereo(x):
        return x if x.ndim == 2 else stereo(x)

    gap = np.zeros((seconds(0.7), 2))
    pieces = []
    for name, sounds, is_step in preview:
        if is_step:
            walk = np.zeros((seconds(0.48 * 8 + 0.3), 2))
            for k in range(8):
                s = as_stereo(sounds[k % len(sounds)])
                at = seconds(0.48 * k)
                walk[at:at + len(s)] += s[: len(walk) - at]
            pieces += [walk, gap]
        else:
            for s in sounds[:2]:
                s = as_stereo(s if name != "shadow_presence" else np.tile(s, 2))
                pieces += [s, gap]
    for s in ui_sounds:
        pieces += [as_stereo(s), gap]
    write_wav(os.path.join(tmp, "all.wav"), np.concatenate(pieces))
    encode(os.path.join(tmp, "all.wav"), os.path.join(PREVIEW, "se_all.mp3"), mp3_kbps=160)

    # 雨の夜：濡れた路面を歩き、ランタンを掛け、影が逃げ、捕まえる
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(ROOT, "Assets", "006_Audio", "Ambient", "ambient_rain.ogg"),
                          "-f", "f32le", "-ac", "2", "-ar", str(RATE), "-"], check=True, capture_output=True).stdout
    rain = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)[: seconds(14)]
    scene = rain.copy()
    steps = dict((n, s) for n, s, _ in preview)

    def put(sound, at, pan=0.0):
        s = as_stereo(sound) if sound.ndim == 2 else stereo(sound, pan)
        a = seconds(at)
        scene[a:a + len(s)] += s[: len(scene) - a]

    for k in range(10):
        put(steps["step_wet"][k % VARIATIONS], 0.5 + 0.5 * k, pan=0.05 * (-1) ** k)
    put(steps["lantern_hang"][0], 5.6)
    put(np.tile(steps["shadow_presence"][0], 1), 6.3, pan=0.4)
    put(steps["shadow_escape"][0], 7.6)
    for k in range(6):
        put(steps["step_stone"][k], 8.2 + 0.32 * k)
    put(steps["shadow_capture"][0], 10.3)
    put(ui_sounds[6], 12.2)
    scene[-seconds(1.0):] *= np.linspace(1, 0, seconds(1.0))[:, None] ** 2
    write_wav(os.path.join(tmp, "scene.wav"), scene)
    encode(os.path.join(tmp, "scene.wav"), os.path.join(PREVIEW, "se_demo_rain_night.mp3"), mp3_kbps=160)


if __name__ == "__main__":
    main()
