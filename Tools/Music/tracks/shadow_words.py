"""影の言葉。F♯ マイナー、♩=60。

捕まえた影が、持ち主の「言えなかった言葉」を話す場面。オルゴールが影のモチーフ（C♯–D–C♯、B–A）をゆっくり鳴らし、
弦と合唱のパッドが息のように満ち引きする。旋律は前に出さず、言葉（テキスト）を読む邪魔をしない。
"""

from blue_song import CELESTA, CHOIR_PAD, MUSIC_BOX, PIANO, SLOW_STRINGS, Song

PAD = {
    "F#m(add9)": "F#2+C#3+G#3+A3",
    "Dmaj7": "D2+A2+C#3+F#3",
    "Dmaj7#11": "D2+A2+C#3+G#3",
    "Bm9": "B1+F#2+C#3+D3",
    "Bm7": "B1+F#2+A2+D3",
    "C#7sus4": "C#2+G#2+B2+F#3",
    "C#7": "C#2+G#2+B2+E#3",
}
LOOP = ["F#m(add9)", "Dmaj7", "Bm9", ("C#7sus4", "C#7"), "F#m(add9)", "Dmaj7#11", "Bm7", "C#7"]


def compose():
    song = Song("shadow_words", "影の言葉", bpm=60, intro_bars=1, loop_bars=8, reverb_seconds=3.4, wow_depth_ms=1.1)
    box = song.part("music_box", program=MUSIC_BOX, gain_db=-8, pan=0.15, wet=0.55, lowpass=6500)
    strings = song.part("strings", program=SLOW_STRINGS, gain_db=-11, wet=0.5, lowpass=4500, timing_ms=0)
    choir = song.part("choir_pad", program=CHOIR_PAD, gain_db=-17, wet=0.5, lowpass=3500, timing_ms=0)
    piano = song.part("piano", program=PIANO, gain_db=-9, wet=0.5, lowpass=4000)
    celesta = song.part("celesta", program=CELESTA, gain_db=-16, pan=-0.3, wet=0.6)

    strings.seq(song.bar(1), f"{PAD['F#m(add9)']}:4", vel=26)
    piano.note("F#1", song.bar(1), 4, 34)
    for i, chord in enumerate(LOOP):
        start = song.bar(2 + i)
        if isinstance(chord, tuple):
            strings.seq(start, f"{PAD[chord[0]]}:2 {PAD[chord[1]]}:2", vel=30)
            choir.seq(start, f"{PAD[chord[0]]}:2 {PAD[chord[1]]}:2", vel=26)
            piano.note(PAD[chord[0]].split("+")[0], start, 4, 34)
        else:
            strings.seq(start, f"{PAD[chord]}:4", vel=30)
            choir.seq(start, f"{PAD[chord]}:4", vel=26)
            piano.note(PAD[chord].split("+")[0], start, 4, 34)
        piano.pedal(start)

    box.seq(song.bar(2), "C#6:1 D6:1 C#6:2 B5:2 A5:2 r:1 F#5:1 A5:1 C#6:1 F#5:2 E#5:2", vel=44)
    box.seq(song.bar(6), "C#6:1 D6:1 C#6:1 B5:1 A5:2 G#5:2 F#5:1 A5:1 D6:2 C#6:2 r:2", vel=42)
    celesta.seq(song.bar(5), "r:2 G#6:2", vel=26)
    celesta.seq(song.bar(9), "r:2 E#6:2", vel=24)
    return song
