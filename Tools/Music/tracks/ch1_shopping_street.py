"""第 1 章：バス停と商店街。F メジャー、♩=80、軽くはねるリズム（スウィング）。

夜の散歩。エレピの和音、ウッドベース、ブラシのドラム。
A はヴィブラフォン、A' はピアノが、ルリのテーマ（C–F–G–A：ソ・ド・レ・ミ）を歩く速さで歌う。
"""

from blue_song import BRUSH_KIT, EPIANO, PIANO, UPRIGHT_BASS, VIBES, Song, pitch

# エレピのボイシングと、ベースの根音・5 度
CHORDS = {
    "Fmaj7": (["A3", "C4", "E4", "G4"], "F2", "C3"),
    "Em7": (["G3", "B3", "D4"], "E2", "B2"),
    "A7": (["G3", "C#4", "E4"], "A2", "E2"),
    "Dm9": (["F3", "A3", "C4", "E4"], "D2", "A2"),
    "Cm7": (["Bb3", "Eb4", "G4"], "C2", "G2"),
    "F7": (["A3", "Eb4", "G4"], "F2", "C2"),
    "Bbmaj7": (["A3", "D4", "F4"], "Bb1", "F2"),
    "Am7": (["G3", "C4", "E4"], "A1", "E2"),
    "Gm7": (["F3", "Bb3", "D4"], "G1", "D2"),
    "C7sus4": (["Bb3", "F4", "G4"], "C2", "G2"),
    "C7": (["Bb3", "E4", "G4"], "C2", "G2"),
}

PROGRESSION = [("Fmaj7",), ("Em7", "A7"), ("Dm9",), ("Cm7", "F7"), ("Bbmaj7",), ("Am7",), ("Gm7",), ("C7sus4", "C7")]


def compose():
    song = Song("ch1_shopping_street", "第1章 バス停と商店街", bpm=80, intro_bars=1, loop_bars=16, swing=0.62)
    keys = song.part("epiano", program=EPIANO, gain_db=-3, pan=-0.15, wet=0.22, timing_ms=10)
    bass = song.part("bass", program=UPRIGHT_BASS, gain_db=-1, wet=0.06, lowpass=3500, timing_ms=6)
    drums = song.part("drums", program=BRUSH_KIT, drum=True, gain_db=-7, wet=0.12, timing_ms=6, vel_jitter=6)
    vibes = song.part("vibes", program=VIBES, gain_db=-3, pan=0.2, wet=0.3, delay_ms=8)
    piano = song.part("piano", program=PIANO, gain_db=-2, pan=0.15, wet=0.25, delay_ms=10)

    # 前奏：エレピだけ
    keys.chord(song.bar(1), CHORDS["Fmaj7"][0], 3.5, 34, roll=0.06)
    bass.note("F2", song.bar(1) + 2, 2, 46)

    bars = [song.bar(2 + i) for i in range(16)]
    for i, start in enumerate(bars):
        chords = PROGRESSION[i % 8]
        next_root = pitch(CHORDS[PROGRESSION[(i + 1) % 8][0]][1])
        second_half = i >= 8
        vel = 40 if second_half else 36

        if len(chords) == 1:
            voicing, root, fifth = CHORDS[chords[0]]
            keys.chord(start, voicing, 1.4, vel)
            keys.chord(start + 1.5, voicing, 2.3, vel - 6)
            bass.note(root, start, 1.5, 54)
            bass.note(fifth, start + 2, 1.0, 46)
        else:
            (v1, r1, _), (v2, r2, _) = CHORDS[chords[0]], CHORDS[chords[1]]
            keys.chord(start, v1, 1.8, vel)
            keys.chord(start + 2, v2, 1.8, vel - 4)
            bass.note(r1, start, 1.5, 54)
            bass.note(r2, start + 2, 1.0, 50)
        # 次の小節の根音へ半音上から近づく
        bass.note(next_root + 1, start + 3.5, 0.5, 40)

        # ブラシ：キックは控えめ、2・4 拍目にブラシ、ライドで刻む
        drums.note(36, start, 0.5, 38)
        drums.note(36, start + 2.5, 0.5, 26)
        for b in (1, 3):
            drums.note(38, start + b, 0.5, 30)
            drums.note(44, start + b, 0.5, 22)
        for b in (0, 1, 1.5, 2, 3, 3.5):
            drums.note(51, start + b, 0.5, 26 if b in (0, 2) else 20)
        if i in (7, 15):
            drums.note(40, start + 3, 1.0, 30)  # ブラシのスウィッシュで次へ

    # A：ヴィブラフォン
    vibes.seq(bars[0], "r:1 C5:.5 F5:.5 G5:1 A5:1@66 G5:1.5 E5:.5 r:1 C#5:1", vel=58)
    vibes.seq(bars[2], "D5:1 E5:.5 F5:.5 A5:2 G5:1 Eb5:1 r:.5 F5:.5 A5:1", vel=58)
    vibes.seq(bars[4], "Bb5:1.5 A5:.5 F5:1 D5:1 E5:2 C5:1 G4:1", vel=56)
    vibes.seq(bars[6], "F5:1.5 D5:.5 Bb4:1 C5:1 F5:2 E5:1 r:1", vel=54)

    # A'：ピアノがはずむように歌い直す
    piano.seq(bars[8], "r:.5 C5:.5 F5:.5 G5:.5 A5:1.5@68 C6:.5 B5:1 G5:1 A5:.5 G5:.5 E5:1", vel=60)
    piano.seq(bars[10], "F5:1.5 E5:.5 D5:1 A4:1 Bb4:1 G4:1 A4:1.5 C5:.5", vel=58)
    piano.seq(bars[12], "D5:2 F5:1 A5:1@64 G5:1.5 E5:.5 C5:2", vel=58)
    piano.seq(bars[14], "Bb4:1 D5:1 F5:1 E5:1 F5:1.5 G5:.5 E5:2", vel=56)
    return song
