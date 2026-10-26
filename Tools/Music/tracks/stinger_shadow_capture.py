"""影を捕まえた瞬間の短い音楽（スティンガー）。約 3 秒＋余韻。ループしない。

ハープが下から駆け上がり、チェレスタとグロッケンが F♯m(add9) を上から降らせる。弦が静かに受け止めて、
そのまま「影の言葉」の曲へクロスフェードする想定。
"""

from blue_song import CELESTA, GLOCK, HARP, SLOW_STRINGS, Song


def compose():
    song = Song("stinger_shadow_capture", "影を捕まえた", bpm=90, intro_bars=0, loop_bars=2, loop=False,
                tail_seconds=3.5, reverb_seconds=3.2, fade_seconds=3.0, compress=False)
    harp = song.part("harp", program=HARP, gain_db=-6, pan=-0.2, wet=0.5, timing_ms=3)
    celesta = song.part("celesta", program=CELESTA, gain_db=-6, pan=0.2, wet=0.55, timing_ms=4)
    glock = song.part("glock", program=GLOCK, gain_db=-14, pan=0.3, wet=0.6, timing_ms=4)
    strings = song.part("strings", program=SLOW_STRINGS, gain_db=-9, wet=0.5, lowpass=5000, timing_ms=0)

    rise = ["F#3", "G#3", "A3", "C#4", "E4", "F#4", "G#4", "A4", "C#5", "E5", "F#5", "G#5"]
    for i, p in enumerate(rise):
        harp.note(p, i * 0.125, 1.5, 34 + i)
    celesta.seq(1.5, "C#6:1/2 A5:1/2 G#5:1/2 F#5:1/2 C#5:3", vel=46)
    glock.seq(1.5, "C#7:1/2 r:1 F#6:3", vel=30)
    strings.seq(1.0, "F#3+C#4+G#4+A4:6", vel=34)
    return song
