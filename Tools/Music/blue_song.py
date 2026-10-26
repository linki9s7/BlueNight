"""BlueNight の BGM 制作エンジン（複数パート・ループ・レイヤー対応）。

- パートごとに楽器（GM 音色）を割り当て、FluidSynth で個別に WAV 化してからミックスする
- ループ曲は「ループ部分を 2 回演奏して、2 回目を切り出す」ことで、残響の尾まで含めて継ぎ目なくつなぐ
- テープの揺れはループの長さで割り切れる周期にして、ループ点でずれないようにする
- レイヤー（影を追う場面の重ね用トラック）は、同じ長さ・同じ音量基準で別々に書き出す

楽譜の書き方（Part.seq）:
    "Db5:1 Eb5:.5 r:.5 F5:2@72 Ab4+Db5:1 C5:1/3"
    音名:長さ（拍）  r = 休符  + で和音  @ で強さ  a/b で分数（3 連符など）
"""

import json
import warnings
import math
import os
import random
import subprocess
import tempfile
import zlib
from fractions import Fraction

import numpy as np
import pretty_midi
import pyloudnorm
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

from blue_music import SAMPLE_RATE, SOUNDFONT, hiss, make_reverb_ir, n

warnings.filterwarnings("ignore", category=wavfile.WavFileWarning)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UNITY_BGM = os.path.join(ROOT, "Assets", "006_Audio", "BGM")
OUT_DIR = os.path.join(ROOT, "Tools", "Music", "out")
PREVIEW_DIR = os.path.join(OUT_DIR, "preview")
MANIFEST = os.path.join(UNITY_BGM, "music_manifest.json")

# GM 音色（0 始まり）
PIANO, EPIANO, CELESTA, GLOCK, MUSIC_BOX, VIBES = 0, 4, 8, 9, 10, 11
NYLON, UPRIGHT_BASS, PIZZ, HARP = 24, 32, 45, 46
CELLO, TREMOLO, STRINGS, SLOW_STRINGS, CHOIR = 42, 44, 48, 49, 52
WARM_PAD, CHOIR_PAD = 89, 91
STANDARD_KIT, BRUSH_KIT = 0, 40


def pitch(p):
    return p if isinstance(p, int) else n(p)


def parse_length(text):
    return float(Fraction(text)) if "/" in text else float(text)


class Part:
    def __init__(self, name, program=PIANO, drum=False, gain_db=0.0, pan=0.0, wet=0.25,
                 lowpass=None, highpass=None, timing_ms=8.0, vel_jitter=4, delay_ms=0.0, layer="main"):
        self.name = name
        self.program = program
        self.drum = drum
        self.gain_db = gain_db
        self.pan = pan
        self.wet = wet
        self.lowpass = lowpass
        self.highpass = highpass
        self.timing_ms = timing_ms
        self.vel_jitter = vel_jitter
        self.delay_ms = delay_ms
        self.layer = layer
        self.notes = []    # (pitch, beat, length, velocity)
        self.pedals = []   # 踏み替える拍

    def note(self, p, beat, length, vel):
        self.notes.append((pitch(p), float(beat), float(length), int(vel)))

    def chord(self, beat, pitches, length, vel, roll=0.0):
        for i, p in enumerate(pitches):
            self.note(p, beat + i * roll, length - i * roll, vel + (6 if i == 0 else 0))

    def seq(self, beat, text, vel=60):
        """文字列の楽譜を beat から並べる。終わりの拍を返す。"""
        for token in text.split():
            v = vel
            if "@" in token:
                token, v = token.split("@")
                v = int(v)
            head, length = token.rsplit(":", 1)
            length = parse_length(length)
            if head != "r":
                for p in head.split("+"):
                    self.note(p, beat, length * 0.98, v)
            beat += length
        return beat

    def arp(self, beat, pitches, pattern, step=0.5, span=4.0, vel=40, accent=8, hold=True):
        """分散和音。pattern はボイシングの添字（None は休み）。hold なら区間の終わりまで音を伸ばす。"""
        voicing = [pitch(p) for p in pitches]
        end = beat + span
        for i, idx in enumerate(pattern):
            b = beat + i * step
            if b >= end - 1e-6:
                break
            if idx is None:
                continue
            length = (end - b) if hold else step * 0.95
            self.note(voicing[idx], b, length, vel + (accent if i == 0 else 0))

    def pedal(self, *beats):
        self.pedals.extend(beats)


class Song:
    def __init__(self, name, title, bpm, beats_per_bar=4, intro_bars=0, loop_bars=8, loop=True,
                 swing=0.5, tail_seconds=3.0, reverb_seconds=2.2, wow_depth_ms=0.7, hiss_db=-60.0,
                 target_lufs=-16.0, fade_seconds=4.0, compress=True, mid_dip_db=-2.5):
        self.name = name
        self.title = title
        self.bpm = bpm
        self.beats_per_bar = beats_per_bar
        self.intro_bars = intro_bars
        self.loop_bars = loop_bars
        self.loop = loop
        self.swing = swing  # 0.5 = まっすぐ、0.6 前後 = 軽くはねる
        self.tail_seconds = tail_seconds
        self.reverb_seconds = reverb_seconds
        self.wow_depth_ms = wow_depth_ms
        self.hiss_db = hiss_db
        self.target_lufs = target_lufs
        self.fade_seconds = fade_seconds
        self.compress = compress
        self.mid_dip_db = mid_dip_db
        self.parts = {}

    def part(self, name, **kwargs):
        p = Part(name, **kwargs)
        self.parts[name] = p
        return p

    def bar(self, number):
        """小節の頭の拍（1 小節目 = 0）。前奏も含めて通し番号で数える。"""
        return (number - 1) * self.beats_per_bar

    @property
    def intro_beats(self):
        return self.intro_bars * self.beats_per_bar

    @property
    def loop_beats(self):
        return self.loop_bars * self.beats_per_bar

    def seconds(self, beats):
        return beats * 60.0 / self.bpm

    def layers(self):
        names = []
        for p in self.parts.values():
            if p.layer not in names:
                names.append(p.layer)
        return names


# ---------------------------------------------------------------- 演奏の味付け

def swing_map(beat, ratio):
    if abs(ratio - 0.5) < 1e-6:
        return beat
    whole = math.floor(beat)
    frac = beat - whole
    if frac <= 0.5:
        return whole + frac / 0.5 * ratio
    return whole + ratio + (frac - 0.5) / 0.5 * (1.0 - ratio)


def expand_notes(song, part):
    """ループ曲はループ部分を 2 回目にも複製する（残響の尾をループ頭に含めるため）。"""
    notes = list(part.notes)
    pedals = list(part.pedals)
    if song.loop:
        lo, hi = song.intro_beats, song.intro_beats + song.loop_beats
        notes += [(p, b + song.loop_beats, l, v) for (p, b, l, v) in part.notes if lo - 1e-6 <= b < hi - 1e-6]
        pedals += [b + song.loop_beats for b in part.pedals if lo - 1e-6 <= b < hi - 1e-6]
    return notes, pedals


def humanize(song, part, notes):
    """1 音ずつの揺らぎ。ループの 2 回目に複製した音は、1 回目と同じ揺らぎにする（継ぎ目をそろえる）。"""
    events = []
    loop_end = song.intro_beats + song.loop_beats
    for (p, b, l, v) in notes:
        canonical = b - song.loop_beats if song.loop and b >= loop_end - 1e-6 else b
        rng = random.Random(zlib.crc32(f"{song.name}/{part.name}/{p}/{canonical:.4f}/{l:.4f}".encode()))
        start = song.seconds(swing_map(b, song.swing)) + rng.gauss(0.0, part.timing_ms / 2000.0) + part.delay_ms / 1000.0
        end = song.seconds(swing_map(b + l, song.swing))
        vel = max(1, min(127, v + rng.randint(-part.vel_jitter, part.vel_jitter)))
        events.append((max(0.0, start), max(start + 0.04, end), p, vel))
    return events


def write_part_midi(path, song, part, events, pedals):
    pm = pretty_midi.PrettyMIDI(initial_tempo=song.bpm)
    inst = pretty_midi.Instrument(program=part.program, is_drum=part.drum, name=part.name)
    for start, end, p, vel in events:
        inst.notes.append(pretty_midi.Note(velocity=vel, pitch=p, start=start, end=end))
    for i, b in enumerate(sorted(pedals)):
        t = song.seconds(b)
        if i > 0:
            inst.control_changes.append(pretty_midi.ControlChange(64, 0, max(0.0, t - 0.01)))
        inst.control_changes.append(pretty_midi.ControlChange(64, 100, t + 0.05))
    if pedals:
        inst.control_changes.append(pretty_midi.ControlChange(64, 0, max(e[1] for e in events) + 0.3))
    pm.instruments.append(inst)
    pm.write(path)
    return pm


def render_midi(midi_path, wav_path):
    subprocess.run([
        "fluidsynth", "-ni", "-q", "-g", "0.5", "-r", str(SAMPLE_RATE), "-R", "0", "-C", "0",
        "-o", "audio.file.format=float", "-F", wav_path, SOUNDFONT, midi_path,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    rate, data = wavfile.read(wav_path)
    data = data.astype(np.float64)
    if data.ndim == 1:
        data = np.stack([data, data], axis=1)
    return data


def process_part(audio, part):
    if part.highpass:
        audio = sosfilt(butter(2, part.highpass, "high", fs=SAMPLE_RATE, output="sos"), audio, axis=0)
    if part.lowpass:
        audio = sosfilt(butter(2, part.lowpass, "low", fs=SAMPLE_RATE, output="sos"), audio, axis=0)
    gain = 10 ** (part.gain_db / 20.0)
    left = min(1.0, 1.0 - part.pan)
    right = min(1.0, 1.0 + part.pan)
    return audio * gain * np.array([left, right])


def pad_to(a, length):
    if len(a) >= length:
        return a[:length]
    return np.concatenate([a, np.zeros((length - len(a), 2))])


def periodic_wow(audio, period_seconds, depth_ms):
    """ループの長さで割り切れる周期のテープの揺れ。"""
    if depth_ms <= 0:
        return audio
    t = np.arange(len(audio)) / SAMPLE_RATE
    k1 = max(1, round(period_seconds * 0.4))
    k2 = max(1, round(period_seconds * 6.0))
    delay = (depth_ms * (1 + np.sin(2 * math.pi * k1 / period_seconds * t))
             + depth_ms * 0.08 * np.sin(2 * math.pi * k2 / period_seconds * t)) / 1000.0
    out = np.empty_like(audio)
    for ch in range(2):
        out[:, ch] = np.interp(t - delay, t, audio[:, ch], left=0.0)
    return out


def mix_layer(song, parts, tmp, compress_layer=True):
    rendered = []
    for part in parts:
        notes, pedals = expand_notes(song, part)
        if not notes:
            continue
        events = humanize(song, part, notes)
        midi = os.path.join(tmp, f"{part.name}.mid")
        write_part_midi(midi, song, part, events, pedals)
        wav = os.path.join(tmp, f"{part.name}.wav")
        rendered.append((part, process_part(render_midi(midi, wav), part)))

    total_beats = song.intro_beats + song.loop_beats * (2 if song.loop else 1)
    length = int(SAMPLE_RATE * (song.seconds(total_beats) + song.tail_seconds + song.reverb_seconds))
    dry = np.zeros((length, 2))
    send = np.zeros((length, 2))
    for part, audio in rendered:
        audio = pad_to(audio, length)
        dry += audio
        send += audio * part.wet

    ir = make_reverb_ir(SAMPLE_RATE, seconds=song.reverb_seconds)
    wet = np.stack([fftconvolve(send[:, ch], ir[:, ch])[:length] for ch in range(2)], axis=1)
    mix = master_eq(dry + wet, song.mid_dip_db)
    # 圧縮もテープの揺れも、切り出す前の通しの音にかける（ループ点で状態がつながる）
    if song.compress and compress_layer:
        mix = gentle_compressor(mix)
    loop_seconds = song.seconds(song.loop_beats)
    return periodic_wow(mix, loop_seconds if song.loop else 2.5, song.wow_depth_ms)


# ---------------------------------------------------------------- 聴き心地を整える（マスター）

def peaking_sos(f0, gain_db, q):
    """ピーキング EQ（RBJ の式）。"""
    a = 10 ** (gain_db / 40.0)
    w0 = 2 * math.pi * f0 / SAMPLE_RATE
    alpha = math.sin(w0) / (2 * q)
    b = [1 + alpha * a, -2 * math.cos(w0), 1 - alpha * a]
    den = [1 + alpha / a, -2 * math.cos(w0), 1 - alpha / a]
    return np.array([[b[0] / den[0], b[1] / den[0], b[2] / den[0], 1.0, den[1] / den[0], den[2] / den[0]]])


def master_eq(mix, mid_dip_db):
    """
    - 40 Hz 以下の重低音を落とす（お腹に響くトゲを取る）
    - 500 Hz〜2 kHz（話し声の帯域）を少し下げて、BGM を一歩後ろへ
    - 8 kHz より上をなだらかに丸める（耳に刺さる高音を取る）
    """
    mix = sosfilt(butter(2, 40, "high", fs=SAMPLE_RATE, output="sos"), mix, axis=0)
    if mid_dip_db:
        mix = sosfilt(peaking_sos(1000, mid_dip_db, 0.6), mix, axis=0)
    return sosfilt(butter(1, 8000, "low", fs=SAMPLE_RATE, output="sos"), mix, axis=0)


def gentle_compressor(mix, ratio=2.2, attack=0.03, release=0.35, block_seconds=0.01, headroom_db=4.0):
    """
    音量の差を縮めるゆるいコンプレッサー（急に大きく・小さくならないように）。
    しきい値は曲そのものの大きめの部分の音量から決める。
    """
    block = int(SAMPLE_RATE * block_seconds)
    blocks = len(mix) // block
    if blocks < 2:
        return mix
    mono = mix[: blocks * block].mean(axis=1).reshape(blocks, block)
    level_db = 10 * np.log10(np.mean(mono ** 2, axis=1) + 1e-12)
    active = level_db[level_db > level_db.max() - 40]
    threshold = np.percentile(active, 80) - headroom_db

    target = np.minimum(0.0, (threshold - level_db) * (1.0 - 1.0 / ratio))
    a_coef = math.exp(-block_seconds / attack)
    r_coef = math.exp(-block_seconds / release)
    gain = np.empty(blocks)
    g = 0.0
    for i, t in enumerate(target):
        coef = a_coef if t < g else r_coef
        g = coef * g + (1 - coef) * t
        gain[i] = g
    centers = (np.arange(blocks) + 0.5) * block
    curve = np.interp(np.arange(len(mix)), centers, gain)
    return mix * (10 ** (curve / 20.0))[:, None]


def cut(song, mix):
    """ループ曲：前奏＋2 回目のループ部分。ループしない曲：全体＋フェードアウト。"""
    if not song.loop:
        end = int(SAMPLE_RATE * (song.seconds(song.intro_beats + song.loop_beats) + song.tail_seconds))
        whole = mix[:end].copy()
        fade = int(SAMPLE_RATE * min(song.fade_seconds, song.tail_seconds))
        whole[-fade:] *= (np.linspace(1.0, 0.0, fade) ** 2)[:, None]
        return None, whole
    i = int(round(SAMPLE_RATE * song.seconds(song.intro_beats)))
    l = int(round(SAMPLE_RATE * song.seconds(song.loop_beats)))
    body = mix[i + l: i + 2 * l].copy()
    # ループ本体の頭の直前に鳴っている音（= 1 回目のループの終わり）
    before_body = mix[i + l - LOOP_XFADE: i + l]
    # 終わりの 50 ms を「頭の直前の音」へなめらかに移す → 最後のサンプルから頭へ途切れなくつながる
    body[-LOOP_XFADE:] = equal_power_blend(body[-LOOP_XFADE:], before_body)
    intro = None
    if i > 0:
        intro = mix[:i].copy()
        if i >= LOOP_XFADE:
            intro[-LOOP_XFADE:] = equal_power_blend(intro[-LOOP_XFADE:], before_body)
    return intro, body


LOOP_XFADE = int(SAMPLE_RATE * 0.05)


def equal_power_blend(a, b):
    """a から b へ、音量が落ち込まないカーブで移る。"""
    t = np.linspace(0.0, 1.0, len(a))[:, None]
    return a * np.cos(t * math.pi / 2) + b * np.sin(t * math.pi / 2)


def write_wav(path, audio):
    wavfile.write(path, SAMPLE_RATE, (np.clip(audio, -1, 1) * 32767).astype(np.int16))


def encode(wav, out, mp3_kbps=None):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    codec = ["-c:a", "libvorbis", "-q:a", "6"] if out.endswith(".ogg") else ["-c:a", "libmp3lame", "-b:a", f"{mp3_kbps or 160}k"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, *codec, out], check=True)


def write_reference_midi(song):
    """全パートをまとめた MIDI（別の音源や DAW で鳴らし直すための楽譜）。"""
    pm = pretty_midi.PrettyMIDI(initial_tempo=song.bpm)
    for part in song.parts.values():
        notes = part.notes
        inst = pretty_midi.Instrument(program=part.program, is_drum=part.drum, name=f"{part.layer}:{part.name}")
        for start, end, p, vel in humanize(song, part, notes):
            inst.notes.append(pretty_midi.Note(velocity=vel, pitch=p, start=start, end=end))
        pm.instruments.append(inst)
    os.makedirs(OUT_DIR, exist_ok=True)
    pm.write(os.path.join(OUT_DIR, f"{song.name}.mid"))


def build(song):
    """曲を書き出し、マニフェスト用の情報を返す。"""
    os.makedirs(UNITY_BGM, exist_ok=True)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    write_reference_midi(song)
    meter = pyloudnorm.Meter(SAMPLE_RATE)

    with tempfile.TemporaryDirectory() as tmp:
        layers = {}
        for layer in song.layers():
            parts = [p for p in song.parts.values() if p.layer == layer]
            intro, body = cut(song, mix_layer(song, parts, tmp, compress_layer=len(song.layers()) == 1))
            layers[layer] = [intro, body]

        # 全レイヤーを重ねた音量を基準にして、すべてのレイヤーに同じ音量調整をかける
        full_body = sum(v[1] for v in layers.values())
        gain = 10 ** ((song.target_lufs - meter.integrated_loudness(full_body)) / 20.0)
        full_intro = sum(v[0] for v in layers.values()) if song.loop and song.intro_bars else None
        peak = max(np.max(np.abs(full_body)), np.max(np.abs(full_intro)) if full_intro is not None else 0.0) * gain
        limit = 10 ** (-1.0 / 20.0)
        if peak > limit:
            gain *= limit / peak

        files = {}
        for layer, (intro, body) in layers.items():
            suffix = "" if len(layers) == 1 else f"_{layer}"
            for kind, audio in (("intro", intro), ("loop" if song.loop else "full", body)):
                if audio is None:
                    continue
                audio = audio * gain
                if layer == song.layers()[0]:
                    audio = audio + hiss(len(audio), SAMPLE_RATE, level_db=song.hiss_db, seed=zlib.crc32(f"{song.name}/{kind}".encode()))
                wav = os.path.join(tmp, f"{song.name}{suffix}_{kind}.wav")
                write_wav(wav, audio)
                name = f"{song.name}{suffix}_{kind}.ogg"
                encode(wav, os.path.join(UNITY_BGM, name))
                files.setdefault(layer, {})[kind] = name
                layers[layer][0 if kind == "intro" else 1] = audio

        # 試聴用：前奏＋ループ 2 回（レイヤー曲は 1 回目が土台だけ、2 回目に全部を重ねる）
        intro_all = sum(v[0] for v in layers.values()) if song.loop and song.intro_bars else None
        if song.loop:
            first = layers[song.layers()[0]][1]
            second = sum(v[1] for v in layers.values())
            pieces = ([intro_all] if intro_all is not None else []) + [first, second]
            preview = np.concatenate(pieces)
            fade = int(SAMPLE_RATE * song.fade_seconds)
            preview[-fade:] *= (np.linspace(1.0, 0.0, fade) ** 2)[:, None]
        else:
            preview = sum(v[1] for v in layers.values())
        wav = os.path.join(tmp, "preview.wav")
        write_wav(wav, preview)
        encode(wav, os.path.join(PREVIEW_DIR, f"{song.name}.mp3"), mp3_kbps=128)

    intro_seconds = song.seconds(song.intro_beats) if song.loop else 0.0
    loop_seconds = song.seconds(song.loop_beats) if song.loop else 0.0
    info = {
        "name": song.name,
        "title": song.title,
        "bpm": song.bpm,
        "beatsPerBar": song.beats_per_bar,
        "loop": song.loop,
        "introSeconds": round(intro_seconds, 6),
        "loopSeconds": round(loop_seconds, 6),
        "sampleRate": SAMPLE_RATE,
        "layers": [{"name": layer, **files[layer]} for layer in song.layers()],
        "loudnessLufs": round(meter.integrated_loudness(sum(v[1] for v in layers.values())), 1),
    }
    update_manifest(info)
    return info


def update_manifest(info):
    data = {"tracks": []}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            data = json.load(f)
    data["tracks"] = [t for t in data["tracks"] if t["name"] != info["name"]] + [info]
    data["tracks"].sort(key=lambda t: t["name"])
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
