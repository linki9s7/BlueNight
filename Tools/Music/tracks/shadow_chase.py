"""影を追う。E マイナー、♩=100。3 つの重ね用トラック（レイヤー）で、曲を切り替えずに緊張感だけを足し引きする。

- base   ：低いピアノの刻みとピチカート。影が近くにいるとき
- drums  ：シェイカーとリムの軽い打楽器（強いキックは使わない）。追いかけ始めたら重ねる
- strings：トレモロの弦と、チェレスタの「影のモチーフ」（B–C–B、A–G：半音で沈むため息）。追いつめたら重ねる
"""

from blue_song import CELESTA, PIANO, PIZZ, STANDARD_KIT, TREMOLO, WARM_PAD, Song

LOW = {
    "Em": ["E2", "B2", "E3", "G3"],
    "Cmaj7": ["C2", "G2", "B2", "E3"],
    "Am7": ["A1", "E2", "G2", "C3"],
    "B7sus4": ["B1", "F#2", "A2", "E3"],
    "B7": ["B1", "F#2", "A2", "D#3"],
    "D/F#": ["F#1", "D2", "A2", "D3"],
    "G": ["G1", "D2", "G2", "B2"],
    "A": ["A1", "E2", "A2", "C#3"],
}
TREM = {
    "Em": "E3+G3+B3", "Cmaj7": "E3+G3+B3", "Am7": "E3+G3+C4", "B7sus4": "E3+F#3+B3",
    "B7": "D#3+F#3+A3", "D/F#": "D3+F#3+A3", "G": "D3+G3+B3", "A": "C#3+E3+A3",
}
PIZZ_V = {
    "Em": ["G3", "B3"], "Cmaj7": ["E3", "B3"], "Am7": ["E3", "C4"], "B7sus4": ["E3", "A3"],
    "B7": ["D#3", "A3"], "D/F#": ["D3", "A3"], "G": ["D3", "B3"], "A": ["C#3", "A3"],
}
OSTINATO = [0, 1, 2, 1, 3, 1, 2, 1]
LOOP = ["Em", "Em", "Cmaj7", "Cmaj7", "Am7", "Am7", "B7sus4", "B7",
        "Em", "D/F#", "G", "A", "Cmaj7", "Am7", "B7sus4", "B7"]


def compose():
    song = Song("shadow_chase", "影を追う", bpm=100, intro_bars=0, loop_bars=16, reverb_seconds=1.8,
                wow_depth_ms=0.4, mid_dip_db=-2.0)
    piano = song.part("piano", program=PIANO, gain_db=-4, wet=0.2, lowpass=5000, layer="base")
    pizz = song.part("pizz", program=PIZZ, gain_db=-8, pan=0.25, wet=0.25, layer="base")
    pad = song.part("pad", program=WARM_PAD, gain_db=-18, wet=0.3, lowpass=2500, timing_ms=0, layer="base")
    kit = song.part("kit", program=STANDARD_KIT, drum=True, gain_db=-13, wet=0.15, lowpass=7000, vel_jitter=5, layer="drums")
    trem = song.part("tremolo", program=TREMOLO, gain_db=-14, wet=0.35, lowpass=5000, timing_ms=0, layer="strings")
    celesta = song.part("celesta", program=CELESTA, gain_db=-12, pan=-0.25, wet=0.45, layer="strings")

    for i, chord in enumerate(LOOP):
        start = song.bar(1 + i)
        piano.arp(start, LOW[chord], OSTINATO, step=0.5, span=4, vel=44, accent=8, hold=False)
        for beat in (1.5, 3.5):
            pizz.chord(start + beat, PIZZ_V[chord], 0.4, 38)
        pad.seq(start, f"{TREM[chord]}:4", vel=30)

        # 打楽器：キックはごく弱く、リムとシェイカーで進む
        kit.note(36, start, 0.5, 30)
        kit.note(36, start + 2.5, 0.5, 22)
        for beat in (1, 3):
            kit.note(37, start + beat, 0.5, 34)
        for k in range(16):
            kit.note(70, start + k * 0.25, 0.25, 22 if k % 2 == 0 else 14)
        if i in (7, 15):
            kit.note(45, start + 3, 0.5, 30)
            kit.note(43, start + 3.5, 0.5, 30)

        trem.seq(start, f"{TREM[chord]}:4", vel=34 if i < 8 else 40)

    # 影のモチーフ（2 小節）を、8 小節ごとに場所を変えて置く
    for bar in (1, 5, 9, 13):
        celesta.seq(song.bar(bar), "B5:1 C6:1 B5:2 A5:2 G5:2", vel=38)
    return song
