"""第 5 章：夜明けの丘。E♭ メジャー、♩=76。

これまで「言いかけて止まっていた」ルリのテーマ（B♭–E♭–F–G）が、ここではじめて先へ続き、
ループの終わりで主和音へ解決する。後半の A♭m6（借用和音）で、別れの切なさを一瞬だけのぞかせる。
"""

from blue_song import CHOIR, GLOCK, PIANO, STRINGS, Song

V = {
    "Ebmaj9": ["Eb2", "Bb2", "D3", "F3", "G3"],
    "Bb/D": ["D2", "Bb2", "D3", "F3", "Bb3"],
    "Cm9": ["C2", "G2", "Bb2", "D3", "Eb3"],
    "Abmaj7": ["Ab1", "Eb2", "G2", "C3", "Eb3"],
    "Eb/G": ["G1", "Eb2", "G2", "Bb2", "Eb3"],
    "Fm9": ["F1", "C2", "Ab2", "Eb3", "G3"],
    "Bb7sus4": ["Bb1", "F2", "Ab2", "Eb3", "F3"],
    "Bb7": ["Bb1", "F2", "Ab2", "D3", "F3"],
    "Abmaj9": ["Ab1", "Eb2", "G2", "Bb2", "C3"],
    "Bb6": ["Bb1", "F2", "G2", "D3", "F3"],
    "Gm7": ["G1", "D2", "F2", "Bb2", "D3"],
    "Abm6": ["Ab1", "Eb2", "F2", "Cb3", "Eb3"],
    "Eb/Bb": ["Bb1", "G2", "Bb2", "Eb3", "G3"],
}
UPPER = {
    "Ebmaj9": "Bb3+D4+G4", "Bb/D": "Bb3+D4+F4", "Cm9": "Bb3+Eb4+G4", "Abmaj7": "C4+Eb4+G4",
    "Eb/G": "Bb3+Eb4+G4", "Fm9": "Ab3+C4+Eb4", "Bb7sus4": "Ab3+Eb4+F4", "Abmaj9": "C4+Eb4+G4",
    "Bb6": "D4+F4+G4", "Gm7": "Bb3+D4+F4", "Cm7": "Bb3+Eb4+G4", "Abm6": "Cb4+Eb4+F4",
    "Eb/Bb": "Bb3+Eb4+G4", "Bb7": "Ab3+D4+F4",
}
FLOW = [0, 1, 2, 3, 4, 3, 2, 1]
OPEN = [0, 2, 3, None, 4, None, 2, None]

LOOP = ["Ebmaj9", "Bb/D", "Cm9", "Abmaj7", "Eb/G", "Abmaj7", "Fm9", ("Bb7sus4", "Bb7"),
        "Abmaj9", "Bb6", "Gm7", "Cm9", "Fm9", "Abm6", "Eb/Bb", "Bb7"]


def compose():
    song = Song("ch5_dawn_hill", "第5章 夜明けの丘", bpm=76, intro_bars=2, loop_bars=16, reverb_seconds=2.6)
    lh = song.part("piano_lh", program=PIANO, gain_db=-3, pan=-0.1, wet=0.3, lowpass=6000)
    rh = song.part("piano_rh", program=PIANO, gain_db=-5, pan=0.1, wet=0.32, delay_ms=12, lowpass=6500)
    strings = song.part("strings", program=STRINGS, gain_db=-12, wet=0.45, lowpass=5500, timing_ms=0)
    choir = song.part("choir", program=CHOIR, gain_db=-18, wet=0.55, lowpass=4000, timing_ms=0)
    glock = song.part("glock", program=GLOCK, gain_db=-17, pan=0.3, wet=0.55)

    def harmony(bar, chord, vel, pattern=FLOW):
        start = song.bar(bar)
        if isinstance(chord, tuple):
            lh.arp(start, V[chord[0]], pattern[:4], span=2, vel=vel)
            lh.arp(start + 2, V[chord[1]], pattern[:4], span=2, vel=vel - 2)
            lh.pedal(start, start + 2)
            rh.pedal(start, start + 2)
        else:
            lh.arp(start, V[chord], pattern, span=4, vel=vel)
            lh.pedal(start)
            rh.pedal(start)

    harmony(1, "Abmaj9", 30, OPEN)
    harmony(2, ("Bb7sus4", "Bb7"), 30, OPEN)
    for i, chord in enumerate(LOOP):
        harmony(3 + i, chord, 34 if i < 8 else 36)

    # 旋律（ピアノ右手、控えめ）
    rh.seq(song.bar(3), "r:1 Bb4:.5 Eb5:.5 F5:1 G5:1 G5:1.5 F5:.5 D5:2", vel=52)
    rh.seq(song.bar(5), "Eb5:1 F5:.5 G5:.5 Bb5:2 Ab5:1.5 G5:.5 Eb5:2", vel=52)
    rh.seq(song.bar(7), "r:1 Bb4:.5 Eb5:.5 F5:1 G5:1 C6:1.5 Bb5:.5 Ab5:1 G5:1", vel=54)
    rh.seq(song.bar(9), "F5:1.5 G5:.5 Ab5:1 C6:1 Bb5:2 Ab5:1 D5:1", vel=52)
    rh.seq(song.bar(11), "Eb5:1 G5:1 C6:1.5 Bb5:.5 Bb5:2 G5:1 F5:1", vel=54)
    rh.seq(song.bar(13), "F5:1.5 D5:.5 Bb4:2 Eb5:1 D5:1 G5:2", vel=52)
    rh.seq(song.bar(15), "Ab5:1.5 G5:.5 F5:1 C5:1 Cb5:2 Bb4:1 Ab4:1", vel=50)
    rh.seq(song.bar(17), "G4:1 Bb4:1 Eb5:1 F5:1 F5:1 Ab5:1 D5:1.5 Eb5:.5", vel=50)  # 最後に主音へ

    # 弦と合唱：後半で少しずつ明るく
    strings.seq(song.bar(1), f"{UPPER['Abmaj9']}:4 {UPPER['Bb7sus4']}:4", vel=24)
    for i, chord in enumerate(LOOP):
        name = chord[0] if isinstance(chord, tuple) else chord
        strings.seq(song.bar(3 + i), f"{UPPER[name]}:4", vel=26 if i < 8 else 34)
    choir.seq(song.bar(11), "Eb4+G4:4 D4+F4:4 D4+F4:4 Eb4+G4:4 C4+Eb4:4 Cb4+Eb4:4 Eb4+G4:4 D4+F4:4", vel=30)

    # グロッケン：夜明けの光のように、区切りでひと粒ずつ
    for bar, note in [(3, "G6"), (7, "G6"), (11, "C7"), (15, "Ab6"), (17, "Eb7")]:
        glock.note(note, song.bar(bar), 2, 30)
    return song
