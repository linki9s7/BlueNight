"""BlueNight 作曲用の共通ライブラリ。

楽譜（拍単位）→ 演奏の味付け（揺らぎ・ルバート・ペダル）→ MIDI → 音源で WAV 化 → 仕上げ、を行う。
"""

import math
import os
import random
import subprocess
from dataclasses import dataclass, field

import numpy as np
import pretty_midi
import pyloudnorm
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SOUNDFONT = "/usr/share/sounds/sf3/MuseScore_General_Full.sf3"
SAMPLE_RATE = 48000

NOTE_NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def n(name):
    """'Db4' や 'F#3' を MIDI ノート番号に変換する。"""
    letter, rest = name[0], name[1:]
    shift = 0
    while rest and rest[0] in "b#":
        shift += -1 if rest[0] == "b" else 1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + NOTE_NAMES[letter] + shift


@dataclass
class Note:
    pitch: int
    beat: float      # 開始位置（拍）
    length: float    # 長さ（拍）
    velocity: int
    voice: str = "accomp"  # "melody" / "accomp"


@dataclass
class Score:
    bpm: float
    beats_per_bar: int = 4
    notes: list = field(default_factory=list)
    pedal_changes: list = field(default_factory=list)  # 踏み替える拍
    # (拍, テンポ倍率) のリスト。ルバート用。線形補間する。
    tempo_curve: list = field(default_factory=lambda: [(0.0, 1.0)])

    def add(self, pitch, beat, length, velocity, voice="accomp"):
        self.notes.append(Note(pitch if isinstance(pitch, int) else n(pitch), beat, length, velocity, voice))


class Clock:
    """拍 → 秒。テンポ倍率の曲線を積分して、ルバートを表現する。"""

    def __init__(self, score, resolution=0.01):
        last = max((nt.beat + nt.length for nt in score.notes), default=0.0) + 8.0
        beats = np.arange(0.0, last + resolution, resolution)
        pts = sorted(score.tempo_curve)
        scale = np.interp(beats, [p[0] for p in pts], [p[1] for p in pts])
        sec_per_beat = 60.0 / (score.bpm * scale)
        self._beats = beats
        self._seconds = np.concatenate([[0.0], np.cumsum(sec_per_beat[:-1] * resolution)])

    def __call__(self, beat):
        return float(np.interp(beat, self._beats, self._seconds))


def humanize(score, seed=1, timing_ms=10.0, melody_delay_ms=14.0, velocity_jitter=4):
    """1 音ずつ、タイミングと強さをわずかに揺らす。"""
    rng = random.Random(seed)
    clock = Clock(score)
    events = []
    for nt in score.notes:
        start = clock(nt.beat) + rng.gauss(0.0, timing_ms / 1000.0 / 2.0)
        if nt.voice == "melody":
            start += melody_delay_ms / 1000.0
        end = clock(nt.beat + nt.length) - 0.02
        vel = int(max(1, min(127, nt.velocity + rng.randint(-velocity_jitter, velocity_jitter))))
        events.append((max(0.0, start), max(start + 0.05, end), nt.pitch, vel))
    pedals = [clock(b) for b in score.pedal_changes]
    return events, pedals, clock


def write_midi(path, events, pedals, program=0):
    pm = pretty_midi.PrettyMIDI(initial_tempo=120)
    inst = pretty_midi.Instrument(program=program, name="Piano")
    for start, end, pitch, vel in events:
        inst.notes.append(pretty_midi.Note(velocity=vel, pitch=pitch, start=start, end=end))
    # レガートペダル：踏み替える瞬間に一度上げ、少し遅れて踏み直す
    for i, t in enumerate(pedals):
        if i > 0:
            inst.control_changes.append(pretty_midi.ControlChange(64, 0, max(0.0, t - 0.01)))
        inst.control_changes.append(pretty_midi.ControlChange(64, 100, t + 0.06))
    end_time = max(e[1] for e in events) + 0.2
    inst.control_changes.append(pretty_midi.ControlChange(64, 0, end_time))
    pm.instruments.append(inst)
    pm.write(path)


def render(midi_path, wav_path, gain=0.6):
    """FluidSynth で WAV に書き出す（内蔵のリバーブ・コーラスは切って、仕上げで自前の残響をかける）。"""
    subprocess.run([
        "fluidsynth", "-ni", "-q",
        "-g", str(gain),
        "-r", str(SAMPLE_RATE),
        "-R", "0", "-C", "0",
        "-F", wav_path,
        SOUNDFONT, midi_path,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------- 仕上げ

def _load(path):
    rate, data = wavfile.read(path)
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    if data.ndim == 1:
        data = np.stack([data, data], axis=1)
    return rate, data.astype(np.float64)


def make_reverb_ir(rate, seconds=2.2, predelay_ms=18.0, seed=3):
    """広めの部屋の残響（指数減衰するノイズを左右で別々に作る）。"""
    rng = np.random.default_rng(seed)
    length = int(rate * seconds * 1.4)
    t = np.arange(length) / rate
    decay = np.exp(-6.9 * t / seconds)  # 60 dB 減衰 = seconds
    ir = rng.standard_normal((length, 2)) * decay[:, None]
    # 残響の高域は早く減衰させる（夜の部屋の柔らかさ）
    sos = butter(2, 4500, "low", fs=rate, output="sos")
    ir = sosfilt(sos, ir, axis=0)
    pre = np.zeros((int(rate * predelay_ms / 1000.0), 2))
    ir = np.concatenate([pre, ir])
    return ir / np.sqrt(np.sum(ir ** 2, axis=0, keepdims=True))


def tape_wow(audio, rate, depth_ms=0.9, rate_hz=0.45, flutter_ms=0.08, flutter_hz=6.5):
    """テープのわずかな揺れ（可変ディレイで音程をほんの少し揺らす）。"""
    t = np.arange(len(audio)) / rate
    delay = (depth_ms * (1 + np.sin(2 * math.pi * rate_hz * t)) + flutter_ms * np.sin(2 * math.pi * flutter_hz * t)) / 1000.0
    src = t - delay
    out = np.empty_like(audio)
    for ch in range(audio.shape[1]):
        out[:, ch] = np.interp(src, t, audio[:, ch], left=0.0)
    return out


def hiss(length, rate, level_db=-58.0, seed=5):
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal((length, 2))
    sos = butter(1, [300, 9000], "band", fs=rate, output="sos")
    noise = sosfilt(sos, noise, axis=0)
    noise /= np.max(np.abs(noise)) + 1e-9
    return noise * (10 ** (level_db / 20.0))


def finish(dry_wav, out_wav, wet=0.28, target_lufs=-16.0, peak_db=-1.0, tail_seconds=2.5, fade_seconds=2.0):
    rate, dry = _load(dry_wav)
    dry = np.concatenate([dry, np.zeros((int(rate * tail_seconds), 2))])

    # 高音を少しだけ丸める
    sos = butter(1, 9000, "low", fs=rate, output="sos")
    dry = sosfilt(sos, dry, axis=0)

    ir = make_reverb_ir(rate)
    wet_sig = np.stack([fftconvolve(dry[:, ch], ir[:, ch])[: len(dry)] for ch in range(2)], axis=1)
    mix = dry * (1.0 - wet) + wet_sig * wet

    mix = tape_wow(mix, rate)
    mix += hiss(len(mix), rate)

    # 終わりはやさしくフェードアウト
    fade = int(rate * fade_seconds)
    mix[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None] ** 2

    meter = pyloudnorm.Meter(rate)
    loudness = meter.integrated_loudness(mix)
    mix = pyloudnorm.normalize.loudness(mix, loudness, target_lufs)
    peak = np.max(np.abs(mix))
    limit = 10 ** (peak_db / 20.0)
    if peak > limit:
        mix *= limit / peak

    wavfile.write(out_wav, rate, (mix * 32767).astype(np.int16))
    return {
        "lufs": meter.integrated_loudness(mix),
        "peak_db": 20 * math.log10(np.max(np.abs(mix)) + 1e-12),
        "seconds": len(mix) / rate,
    }


def encode(wav_path, out_path):
    """拡張子に応じて OGG（Unity 用）や MP3（試聴用）に変換する。"""
    codec = ["-c:a", "libvorbis", "-q:a", "6"] if out_path.endswith(".ogg") else ["-c:a", "libmp3lame", "-b:a", "192k"]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path, *codec, out_path], check=True)
