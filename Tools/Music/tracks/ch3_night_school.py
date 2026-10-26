"""第 3 章：夜の学校。A マイナー、3/4 拍子、♩=78。

誰もいない音楽室のオルゴール。ピアノのゆっくりしたワルツの上で、オルゴールがルリのテーマ（E–A–B–C）を鳴らす。
F の上の B（増 4 度）や B7 で、夜の校舎らしい少しの不思議さを足す。後半はチェレスタが下で寄り添う。
"""

from blue_song import CELESTA, MUSIC_BOX, PIANO, SLOW_STRINGS, Song

WALTZ = {
    "Am": ("A2", ["C4", "E4"]),
    "Am/G": ("G2", ["C4", "E4"]),
    "F": ("F2", ["A3", "C4"]),
    "E": ("E2", ["G#3", "B3"]),
    "Dm": ("D2", ["F3", "A3"]),
    "Am/C": ("C3", ["E3", "A3"]),
    "B7": ("B1", ["D#3", "A3"]),
    "E7": ("E2", ["G#3", "D4"]),
    "C/G": ("G2", ["C4", "E4"]),
    "Dm/F": ("F2", ["A3", "D4"]),
    "Am/E": ("E2", ["A3", "C4"]),
}

LOOP = ["Am", "Am/G", "F", "E", "Dm", "Am/C", "B7", "E7",
        "Am", "C/G", "F", "Dm/F", "Am/E", "E7", "Am", "E7"]


def compose():
    song = Song("ch3_night_school", "第3章 夜の学校", bpm=78, beats_per_bar=3, intro_bars=2, loop_bars=16,
                reverb_seconds=2.8)
    piano = song.part("piano", program=PIANO, gain_db=-4, pan=-0.1, wet=0.35, lowpass=5500, timing_ms=10)
    box = song.part("music_box", program=MUSIC_BOX, gain_db=-6, pan=0.15, wet=0.45, lowpass=7000, delay_ms=6)
    celesta = song.part("celesta", program=CELESTA, gain_db=-14, pan=0.3, wet=0.5)
    strings = song.part("strings", program=SLOW_STRINGS, gain_db=-17, wet=0.5, lowpass=4000, timing_ms=0)

    def waltz(bar, chord, vel):
        bass, upper = WALTZ[chord]
        start = song.bar(bar)
        piano.note(bass, start, 3, vel + 6)
        for beat in (1, 2):
            piano.chord(start + beat, upper, 0.9, vel - 4)
        piano.pedal(start)

    waltz(1, "Am", 30)
    waltz(2, "E7", 30)
    for i, chord in enumerate(LOOP):
        waltz(3 + i, chord, 32 if i < 8 else 34)

    # 前奏：オルゴールがテーマの頭だけを鳴らして止まる
    box.seq(song.bar(1), "E5:1 A5:1 B5:1 C6:2 r:1", vel=46)

    # オルゴール（控えめに。8 小節ごとに少し形を変える）
    box.seq(song.bar(3), "E5:1 A5:1 B5:1 C6:2 B5:1 A5:1.5 G5:.5 F5:1 G#5:1.5 A5:.5 B5:1", vel=50)
    box.seq(song.bar(7), "A5:1 F5:1 D5:1 E5:2 C5:1 D#5:1 F#5:1 A5:1 G#5:2 r:1", vel=48)
    box.seq(song.bar(11), "E5:1 A5:1 B5:1 C6:1 E6:1 D6:1 C6:1.5 B5:.5 A5:1 F5:1 A5:1 D6:1", vel=50)
    box.seq(song.bar(15), "C6:1 B5:1 A5:1 G#5:1 B5:1 D6:1 A5:2 E5:1 G#5:2 B5:1", vel=46)

    # チェレスタ：後半だけ、旋律の下で長い音
    celesta.seq(song.bar(11), "C5:3 C5:3 A4:3 A4:3 A4:3 G#4:3 A4:3 G#4:3", vel=30)

    # 弦：ほとんど聞こえないくらいの持続音で、空間を埋める
    strings.seq(song.bar(1), "A3+E4:3 G#3+D4:3", vel=24)
    strings.seq(song.bar(3), "A3+E4:6 F3+C4:3 E3+B3:3 D3+A3:3 C3+A3:3 B2+A3:3 B2+G#3:3 "
                             "A3+E4:3 G3+E4:3 A3+C4:3 A3+D4:3 A3+C4:3 G#3+D4:3 A3+E4:3 G#3+D4:3", vel=26)
    return song
