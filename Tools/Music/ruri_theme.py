"""ルリのテーマ（30 秒スケッチ）。設計は designs/ruri_theme.md。

使い方（リポジトリのルートで）:
    python3 Tools/Music/ruri_theme.py
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from blue_music import Score, encode, finish, humanize, n, render, write_midi  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "Tools", "Music", "out")
UNITY_OUT = os.path.join(ROOT, "Assets", "006_Audio", "BGM", "ruri_theme_sketch.ogg")
NAME = "ruri_theme_sketch"

BEATS = 4

# 左手のボイシング（低い音から）
CHORDS = {
    "Dbmaj9": ["Db2", "Ab2", "Eb3", "F3", "C4"],
    "Ab/C": ["C2", "Ab2", "Eb3", "Ab3", "Bb3"],
    "Bbm9": ["Bb1", "F2", "Db3", "Ab3", "C4"],
    "Gbmaj7": ["Gb1", "Db2", "Bb2", "Db3", "F3"],
    "Bbm7": ["Bb1", "F2", "Db3", "Ab3"],
    "Ebm9": ["Eb2", "Bb2", "Db3", "F3", "Gb3"],
    "Ab7sus4": ["Ab1", "Eb2", "Db3", "Eb3", "Gb3"],
    "Gbmaj7#11": ["Gb1", "Db2", "Bb2", "F3", "Ab3"],
}

# 伴奏の形（8 分音符の位置 → ボイシングの何番目の音か）
PATTERNS = {
    "flow": [0, 1, 2, 3, 4, 3, 2, 1],      # 上って下りる分散和音
    "open": [0, 2, 3, None, 4, None, 2, None],  # 間（ま）のある形
    "half": [0, 1, 2, 3],                  # 半小節ぶん
}


def bar_start(bar):
    return (bar - 1) * BEATS


def accompany(score, bar, chord, pattern, base_vel, offset=0.0, span=BEATS):
    voicing = [n(p) for p in CHORDS[chord]]
    start = bar_start(bar) + offset
    end = start + span
    for i, idx in enumerate(PATTERNS[pattern]):
        if idx is None:
            continue
        beat = start + i * 0.5
        if beat >= end:
            break
        vel = base_vel + (10 if i == 0 else 0) - (2 if idx >= 3 else 0)
        score.add(voicing[idx], beat, end - beat, vel)


def block(score, bar, chord, base_vel, roll=0.0):
    """和音をそっと置く。roll > 0 で下から少しずつずらして鳴らす。"""
    voicing = [n(p) for p in CHORDS[chord]]
    start = bar_start(bar)
    for i, pitch in enumerate(voicing):
        score.add(pitch, start + i * roll, BEATS - i * roll, base_vel + (8 if i == 0 else 0))


def melody(score, bar, notes):
    for beat, pitch, length, vel in notes:
        score.add(pitch, bar_start(bar) + beat, length, vel, voice="melody")


def compose():
    score = Score(bpm=72)

    # ---- 伴奏
    accompany(score, 1, "Dbmaj9", "flow", 34)   # 前奏
    accompany(score, 2, "Dbmaj9", "flow", 38)
    accompany(score, 3, "Ab/C", "open", 38)
    accompany(score, 4, "Bbm9", "flow", 38)
    block(score, 5, "Gbmaj7", 34, roll=0.12)
    accompany(score, 6, "Dbmaj9", "flow", 40)
    accompany(score, 7, "Ab/C", "flow", 44)     # フレーズの山
    accompany(score, 8, "Bbm7", "half", 40, offset=0, span=2)
    accompany(score, 8, "Ebm9", "half", 38, offset=2, span=2)
    accompany(score, 9, "Ab7sus4", "open", 34)
    block(score, 10, "Gbmaj7#11", 30, roll=0.18)  # 解決しないまま終わる

    # ---- メロディ（拍, 音, 長さ, 強さ）
    melody(score, 2, [(1.0, "Ab4", 0.5, 56), (1.5, "Db5", 0.5, 60), (2.0, "Eb5", 1.0, 64), (3.0, "F5", 2.5, 68)])
    melody(score, 3, [(1.5, "Eb5", 0.5, 58), (2.0, "Db5", 1.5, 54)])
    melody(score, 4, [(0.5, "C5", 0.5, 52), (1.0, "Db5", 0.5, 56), (1.5, "Eb5", 0.5, 60), (2.0, "F5", 1.5, 66), (3.5, "Eb5", 0.5, 58)])
    melody(score, 5, [(0.0, "Db5", 2.0, 56), (2.0, "Bb4", 1.5, 48)])
    melody(score, 6, [(1.0, "Ab4", 0.5, 58), (1.5, "Db5", 0.5, 62), (2.0, "Eb5", 1.0, 66), (3.0, "F5", 1.0, 70)])
    melody(score, 7, [(0.0, "Ab5", 1.5, 78), (1.5, "Gb5", 0.5, 68), (2.0, "F5", 1.0, 64), (3.0, "Eb5", 1.0, 60)])
    melody(score, 8, [(0.0, "Db5", 1.0, 58), (1.0, "Eb5", 0.5, 56), (1.5, "F5", 0.5, 58), (2.0, "Bb4", 2.0, 52)])
    melody(score, 9, [(0.0, "Ab4", 1.0, 50), (1.0, "Db5", 3.0, 54)])
    melody(score, 10, [(0.5, "C5", 3.5, 44)])  # D♭ → C：半音下がるため息

    # ---- ペダル（和音が変わるところで踏み替え）
    score.pedal_changes = [bar_start(b) for b in range(1, 11)] + [bar_start(8) + 2]

    # ---- ルバート（拍, テンポ倍率）
    score.tempo_curve = [
        (0, 0.96), (4, 1.0),
        (17, 1.0), (19.5, 0.9), (20, 1.0),     # 1 つ目のフレーズの終わりで少し緩める
        (24, 1.02), (26, 1.0),                 # 山に向かってほんの少し前へ
        (33, 1.0), (36, 0.88), (38, 0.78), (42, 0.7),  # 終わりに向けて大きく緩める
    ]
    return score


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    score = compose()
    events, pedals, _ = humanize(score, seed=7)

    midi_path = os.path.join(OUT_DIR, f"{NAME}.mid")
    write_midi(midi_path, events, pedals)

    with tempfile.TemporaryDirectory() as tmp:
        dry = os.path.join(tmp, "dry.wav")
        wet = os.path.join(tmp, "final.wav")
        render(midi_path, dry)
        stats = finish(dry, wet)
        encode(wet, UNITY_OUT)
        encode(wet, os.path.join(OUT_DIR, f"{NAME}.mp3"))

    print(f"{stats['seconds']:.1f} s, {stats['lufs']:.1f} LUFS, peak {stats['peak_db']:.1f} dBFS")


if __name__ == "__main__":
    main()
