"""タイトル／ルリのテーマ。D♭ メジャー、♩=72。

A：スケッチの旋律（言いかけて、やめる）。最後は A♭sus4 のまま解決しない。
B：相対調寄りに広がり、弦が加わる。最後の A♭sus4 からループ頭の D♭ に戻ったところで、はじめて落ち着く。
"""

from blue_song import CELESTA, PIANO, SLOW_STRINGS, Song

V = {
    "Dbmaj9": ["Db2", "Ab2", "Eb3", "F3", "C4"],
    "Ab/C": ["C2", "Ab2", "Eb3", "Ab3", "Bb3"],
    "Bbm9": ["Bb1", "F2", "Db3", "Ab3", "C4"],
    "Gbmaj7": ["Gb1", "Db2", "Bb2", "Db3", "F3"],
    "Gbmaj9": ["Gb1", "Db2", "Bb2", "F3", "Ab3"],
    "Bbm7": ["Bb1", "F2", "Db3", "Ab3"],
    "Ebm9": ["Eb2", "Bb2", "Db3", "F3", "Gb3"],
    "Ab7sus4": ["Ab1", "Eb2", "Db3", "Eb3", "Gb3"],
    "Fm7": ["F1", "C2", "Ab2", "Eb3", "G3"],
    "Ab7": ["Ab1", "Eb2", "C3", "Gb3", "Bb3"],
    "Fm/Ab": ["Ab1", "Eb2", "F2", "C3", "Ab3"],
}
FLOW = [0, 1, 2, 3, 4, 3, 2, 1]
OPEN = [0, 2, 3, None, 4, None, 2, None]
HALF = [0, 1, 2, 3]

STRINGS_UPPER = {
    "Dbmaj9": "Ab3+C4+F4", "Ab/C": "Ab3+C4+Eb4", "Bbm9": "Db4+F4+Ab4", "Gbmaj7": "Bb3+Db4+F4",
    "Gbmaj9": "Bb3+Db4+F4", "Fm7": "Ab3+C4+Eb4", "Ebm9": "Gb3+Bb3+Db4", "Ab7": "Gb3+C4+Eb4",
    "Fm/Ab": "Ab3+C4+F4", "Ab7sus4": "Gb3+Db4+Eb4",
}


def compose():
    song = Song("title_ruri_theme", "タイトル／ルリのテーマ", bpm=72, intro_bars=2, loop_bars=16)
    lh = song.part("piano_lh", program=PIANO, gain_db=-2, pan=-0.1, wet=0.3)
    rh = song.part("piano_rh", program=PIANO, gain_db=0, pan=0.1, wet=0.3, delay_ms=12)
    strings = song.part("strings", program=SLOW_STRINGS, gain_db=-9, wet=0.45, lowpass=6000, timing_ms=4)
    celesta = song.part("celesta", program=CELESTA, gain_db=-12, pan=0.3, wet=0.5)

    plan = [
        # 前奏
        (1, "Gbmaj9", OPEN, 30), (2, "Ab7sus4", OPEN, 30),
        # A
        (3, "Dbmaj9", FLOW, 36), (4, "Ab/C", OPEN, 36), (5, "Bbm9", FLOW, 36), (6, "Gbmaj7", OPEN, 32),
        (7, "Dbmaj9", FLOW, 38), (8, "Ab/C", FLOW, 42), (9, ("Bbm7", "Ebm9"), HALF, 38), (10, "Ab7sus4", OPEN, 34),
        # B
        (11, "Gbmaj9", FLOW, 40), (12, "Fm7", FLOW, 40), (13, "Ebm9", FLOW, 42), (14, "Ab7", FLOW, 44),
        (15, "Bbm9", FLOW, 42), (16, "Fm/Ab", OPEN, 40), (17, "Gbmaj7", FLOW, 38), (18, "Ab7sus4", OPEN, 34),
    ]
    for bar, chord, pattern, vel in plan:
        start = song.bar(bar)
        if isinstance(chord, tuple):
            lh.arp(start, V[chord[0]], pattern, span=2, vel=vel)
            lh.arp(start + 2, V[chord[1]], pattern, span=2, vel=vel - 2)
            lh.pedal(start, start + 2)
            rh.pedal(start, start + 2)
        else:
            lh.arp(start, V[chord], pattern, span=4, vel=vel)
            lh.pedal(start)
            rh.pedal(start)

    # 旋律
    rh.seq(song.bar(3), "r:1 Ab4:.5 Db5:.5 Eb5:1 F5:2.5@68 Eb5:.5 Db5:1.5 r:.5", vel=60)
    rh.seq(song.bar(5), "r:.5 C5:.5 Db5:.5 Eb5:.5 F5:1.5@66 Eb5:.5 Db5:2 Bb4:1.5 r:.5", vel=56)
    rh.seq(song.bar(7), "r:1 Ab4:.5 Db5:.5 Eb5:1 F5:1@70 Ab5:1.5@78 Gb5:.5 F5:1 Eb5:1", vel=62)
    rh.seq(song.bar(9), "Db5:1 Eb5:.5 F5:.5 Bb4:2 Ab4:1 Db5:3", vel=54)
    rh.seq(song.bar(11), "r:1 Db5:.5 Gb5:.5 Ab5:1 Bb5:1@72 Ab5:2.5 F5:.5 Eb5:1", vel=64)
    rh.seq(song.bar(13), "Gb5:1.5 F5:.5 Eb5:1 Db5:1 C5:2 Eb5:1 Gb5:1@70", vel=60)
    rh.seq(song.bar(15), "F5:1.5 Db5:.5 C5:1 Db5:1 Ab5:2@74 Gb5:1 F5:1", vel=62)
    rh.seq(song.bar(17), "F5:1.5 Eb5:.5 Db5:1 Bb4:1 Db5:1 Eb5:.5 Db5:.5 Ab4:2", vel=54)

    # 弦：A の後半からそっと入り、B で支える
    for bar, chord, vel in [(1, "Gbmaj9", 22), (2, "Ab7sus4", 22),
                            (7, "Dbmaj9", 26), (8, "Ab/C", 28), (9, "Bbm9", 28), (10, "Ab7sus4", 26),
                            (11, "Gbmaj9", 34), (12, "Fm7", 34), (13, "Ebm9", 36), (14, "Ab7", 40),
                            (15, "Bbm9", 38), (16, "Fm/Ab", 36), (17, "Gbmaj7", 34), (18, "Ab7sus4", 30)]:
        strings.seq(song.bar(bar), f"{STRINGS_UPPER[chord]}:4", vel=vel)

    # チェレスタ：B の頭と、ループに戻る直前だけ旋律をなぞる
    celesta.seq(song.bar(11), "r:1 Db6:.5 Gb6:.5 Ab6:1 Bb6:1", vel=34)
    celesta.seq(song.bar(18), "r:2 Ab5:2", vel=30)
    return song
