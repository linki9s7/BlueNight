"""第 4 章：灯台と港。G マイナー、6/8 拍子（付点 4 分音符 = 50、波のうねりの速さ）。

ピアノのうねる分散和音の上で、チェロがルリのテーマ（D–G–A–B♭）を低く歌う。
後半は弦が満ち潮のように少しずつ厚くなり、ハープが灯台の光のように時々きらめく。
（ここでは 1 拍 = 8 分音符、1 小節 = 6 拍として書く）
"""

from blue_song import CELLO, HARP, PIANO, STRINGS, Song

V = {
    "Gm": ["G2", "D3", "G3", "Bb3", "D4"],
    "Ebmaj7": ["Eb2", "Bb2", "D3", "G3", "Bb3"],
    "Bb": ["Bb1", "F2", "Bb2", "D3", "F3"],
    "F/A": ["A1", "F2", "C3", "F3", "A3"],
    "Eb": ["Eb2", "Bb2", "Eb3", "G3", "Bb3"],
    "Cm7": ["C2", "G2", "Bb2", "Eb3", "G3"],
    "D7sus4": ["D2", "A2", "C3", "G3", "A3"],
    "D7": ["D2", "A2", "C3", "F#3", "A3"],
    "Bb/D": ["D2", "Bb2", "D3", "F3", "Bb3"],
    "Cm": ["C2", "G2", "C3", "Eb3", "G3"],
    "Gm/Bb": ["Bb1", "G2", "Bb2", "D3", "G3"],
    "F": ["F1", "C2", "F2", "A2", "C3"],
}
WAVE = [0, 2, 3, 4, 3, 2]
HALF_WAVE = [0, 2, 3]

LOOP = ["Gm", "Ebmaj7", "Bb", "F/A", "Gm", "Eb", "Cm7", ("D7sus4", "D7"),
        "Eb", "Bb/D", "Cm", "Gm/Bb", "Eb", "F", "Gm", "D7"]


def compose():
    song = Song("ch4_lighthouse_harbor", "第4章 灯台と港", bpm=150, beats_per_bar=6, intro_bars=2, loop_bars=16,
                reverb_seconds=3.0, wow_depth_ms=1.0)
    piano = song.part("piano", program=PIANO, gain_db=-4, pan=-0.1, wet=0.35, lowpass=5500, timing_ms=10)
    cello = song.part("cello", program=CELLO, gain_db=-4, pan=0.05, wet=0.38, lowpass=5000, timing_ms=12)
    strings = song.part("strings", program=STRINGS, gain_db=-14, wet=0.45, lowpass=5000, timing_ms=0)
    harp = song.part("harp", program=HARP, gain_db=-15, pan=0.35, wet=0.55)

    def wave(bar, chord, vel):
        start = song.bar(bar)
        if isinstance(chord, tuple):
            piano.arp(start, V[chord[0]], HALF_WAVE, step=1, span=3, vel=vel)
            piano.arp(start + 3, V[chord[1]], HALF_WAVE, step=1, span=3, vel=vel - 2)
        else:
            piano.arp(start, V[chord], WAVE, step=1, span=6, vel=vel)
        piano.pedal(start)

    wave(1, "Gm", 30)
    wave(2, "D7", 30)
    for i, chord in enumerate(LOOP):
        wave(3 + i, chord, 32 if i < 8 else 36)

    # チェロ（A は控えめに、B で少し高く）
    cello.seq(song.bar(3), "D3:2 G3:1 A3:2 Bb3:1 Bb3:4 A3:1 G3:1 F3:4 Bb3:2 A3:6", vel=50)
    cello.seq(song.bar(7), "D3:2 G3:1 A3:2 Bb3:1 C4:3 Bb3:2 G3:1 Eb4:4 D4:1 C4:1 G3:3 F#3:3", vel=50)
    cello.seq(song.bar(11), "G3:2 Bb3:1 Eb4:3 D4:4 F4:2 Eb4:3 D4:2 C4:1 D4:6", vel=52)
    cello.seq(song.bar(15), "Bb3:2 C4:1 D4:2 Eb4:1 F4:4 Eb4:1 C4:1 D4:3 Bb3:2 A3:1 A3:3 F#3:3", vel=50)

    # 弦：前半はごく薄く、後半は満ち潮のように
    strings.seq(song.bar(3), "G3+Bb3+D4:6 G3+Bb3+Eb4:6 F3+Bb3+D4:6 F3+A3+C4:6 "
                             "G3+Bb3+D4:6 G3+Bb3+Eb4:6 G3+Bb3+Eb4:6 F#3+A3+C4:6", vel=24)
    strings.seq(song.bar(11), "G3+Bb3+Eb4:6 F3+Bb3+D4:6 G3+C4+Eb4:6 G3+Bb3+D4:6 "
                              "G3+Bb3+Eb4:6 A3+C4+F4:6 G3+Bb3+D4:6 F#3+A3+C4:6", vel=32)

    # ハープ：灯台の光のように、ときどき高い音
    for bar, notes in [(4, "Bb5+D6"), (8, "G5+Bb5"), (11, "Eb6+G6"), (13, "Eb6+G6"), (15, "D6+G6"), (17, "Bb5+D6")]:
        harp.seq(song.bar(bar) + 3, f"{notes}:3", vel=34)
    return song
