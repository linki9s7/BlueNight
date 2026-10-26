"""第 2 章：雨の路地裏。D マイナー、♩=66。

ハープの細かい分散和音が雨粒のように降り、チェロがルリのテーマ（A–D–E–F）を低く歌う。
後半はエレピが旋律を引き継ぎ、チェロは長い音で支える。グロッケンがときどき雨だれのように鳴る。
"""

import random

from blue_song import CELLO, EPIANO, GLOCK, HARP, WARM_PAD, Song

HARP_V = {
    "Gm9": ["G2", "D3", "A3", "Bb3", "F4"],
    "A7sus4": ["A2", "E3", "D4", "G4", "A4"],
    "A7": ["A2", "E3", "C#4", "G4", "A4"],
    "Dm9": ["D3", "A3", "E4", "F4", "C5"],
    "Bbmaj7": ["Bb2", "F3", "A3", "D4", "F4"],
    "Fmaj7/C": ["C3", "F3", "A3", "E4", "G4"],
    "Bbmaj7#11": ["Bb2", "F3", "A3", "D4", "E4"],
    "Gm7": ["G2", "D3", "F3", "Bb3", "D4"],
}
PAD = {
    "Gm9": "F3+Bb3+D4", "A7sus4": "E3+G3+D4", "A7": "E3+G3+C#4", "Dm9": "F3+A3+C4",
    "Bbmaj7": "F3+A3+D4", "Fmaj7/C": "E3+A3+C4", "Bbmaj7#11": "F3+A3+E4", "Gm7": "F3+Bb3+D4",
}
RAIN = [0, None, 2, 3, 4, None, 3, None, 1, None, 2, 3, 4, 3, None, 2]
RAIN_HALF = [0, None, 2, 3, 4, None, 3, None]

PROGRESSION = [("Dm9",), ("Bbmaj7",), ("Gm9",), ("A7sus4", "A7"), ("Dm9",), ("Fmaj7/C",), ("Bbmaj7#11",), ("Gm7", "A7")]


def compose():
    song = Song("ch2_rain_alley", "第2章 雨の路地裏", bpm=66, intro_bars=2, loop_bars=16, wow_depth_ms=0.8)
    harp = song.part("harp", program=HARP, gain_db=-5, pan=-0.2, wet=0.4, timing_ms=6)
    pad = song.part("pad", program=WARM_PAD, gain_db=-15, wet=0.35, lowpass=3000, timing_ms=0)
    keys = song.part("epiano", program=EPIANO, gain_db=-5, pan=0.2, wet=0.3, delay_ms=8)
    cello = song.part("cello", program=CELLO, gain_db=-1, pan=0.05, wet=0.35, timing_ms=10)
    drops = song.part("drops", program=GLOCK, gain_db=-16, pan=0.35, wet=0.55, timing_ms=0)

    def harmony(bar, chords, vel):
        start = song.bar(bar)
        if len(chords) == 1:
            harp.arp(start, HARP_V[chords[0]], RAIN, step=0.25, span=4, vel=vel, accent=6)
            pad.seq(start, f"{PAD[chords[0]]}:4", vel=34)
        else:
            harp.arp(start, HARP_V[chords[0]], RAIN_HALF, step=0.25, span=2, vel=vel, accent=6)
            harp.arp(start + 2, HARP_V[chords[1]], RAIN_HALF, step=0.25, span=2, vel=vel, accent=4)
            pad.seq(start, f"{PAD[chords[0]]}:2 {PAD[chords[1]]}:2", vel=34)

    harmony(1, ("Gm9",), 26)
    harmony(2, ("A7sus4", "A7"), 26)
    for i in range(16):
        harmony(3 + i, PROGRESSION[i % 8], 30 if i < 8 else 34)

    # A：チェロ
    cello.seq(song.bar(3), "r:1 A3:.5 D4:.5 E4:1 F4:1@64 F4:2 E4:1 D4:1", vel=58)
    cello.seq(song.bar(5), "D4:1.5 Bb3:.5 A3:2 D4:2 C#4:2", vel=56)
    cello.seq(song.bar(7), "r:1 A3:.5 D4:.5 E4:1 F4:1@64 A4:2@68 G4:1 F4:1", vel=58)
    cello.seq(song.bar(9), "E4:1.5 F4:.5 D4:2 Bb3:2 A3:2", vel=54)

    # B：エレピが旋律、チェロは長い音で支える
    keys.seq(song.bar(11), "r:1 A4:.5 D5:.5 E5:1 F5:1@62 A5:1.5@66 G5:.5 F5:1 D5:1", vel=56)
    keys.seq(song.bar(13), "Bb4:1 D5:1 A5:2 G5:1 D5:1 E5:1 C#5:1", vel=56)
    keys.seq(song.bar(15), "F5:1.5 E5:.5 D5:1 A4:1 C5:1 E5:1 G5:2@62", vel=56)
    keys.seq(song.bar(17), "F5:1 E5:1 D5:2 D5:2 C#5:1 E5:1", vel=54)
    cello.seq(song.bar(11), "D3:4 D3:4 G2:4 A2:4 D3:4 C3:4 Bb2:4 G2:2 A2:2", vel=48)

    # 雨だれ：D マイナーのペンタトニックから、ときどき 1 音
    rng = random.Random(23)
    scale = ["A5", "C6", "D6", "E6", "G6", "A6"]
    for i in range(18):
        if rng.random() < 0.7:
            drops.note(rng.choice(scale), song.bar(1 + i) + rng.choice([0.75, 1.5, 2.25, 3.25]), 1.0, rng.randint(22, 32))
    return song
