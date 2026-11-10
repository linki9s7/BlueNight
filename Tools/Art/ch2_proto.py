"""第 2 章の試作で、ランタンと見間違えないための小物：門灯（点いている・消えている）とランタン立て。

参考：日本の住宅の門柱の上に載っている四角い門灯（乳白色のガラスの箱）。灯りは白っぽい（ランタンの橙と分ける）。
ランタン立て：ハルの夫が作った「木と鉄の小さな台」（台本 9.8）。木の丸い台座と、ランタンを吊るす鉄のフック。
光はどの絵も左上から（STYLE.md 5）。輪郭は 1 ドットの紺。
"""
from build import from_map
from palette import color

# 門灯：上が四角いガラスの箱（10 幅）、下がコンクリートの門柱（8 幅）。足元がピボット。16 x 26
GATE_LAMP = [
    "................",
    "...OOOOOOOOOO...",
    "..OrrrrrrrrRRO..",
    "...OOOOOOOOOO...",
    "...OGGgggggkO...",
    "...OGgggggggO...",
    "...OggggggggO...",
    "...OgggggggkO...",
    "...OkkkkkkkkO...",
    "...OOOOOOOOOO...",
    "....OOOOOOOO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "....OppppPPO....",
    "...OOOOOOOOOO...",
    "...OssssssSSO...",
]


def gate_lamp(on):
    key = {
        "O": color("night", 1),
        "r": color("stone", 3), "R": color("stone", 2),        # 箱の屋根（金属）。左が明るい
        "p": color("stone", 5), "P": color("stone", 4),        # 門柱（コンクリート）。左の面が明るい
        "s": color("stone", 4), "S": color("stone", 3),        # 足元の台
    }
    if on:   # 白っぽい灯り（ランタンの橙と見分ける）。つやは左上の小さなかたまり
        key.update({"G": color("moon", 3), "g": color("moon", 2), "k": color("moon", 1)})
    else:    # 消えている：くもったガラス
        key.update({"G": color("stone", 6), "g": color("stone", 5), "k": color("stone", 4)})
    return from_map(GATE_LAMP, key)


# ランタン立て：ハルの夫の手作り。重い木の丸い台座（切り株）から、曲げた鉄の細い棒が立ち、
# 先の腕のフックにランタンを吊るす（実物のランタンスタンドはほぼ吊るす形。木の丸い台座の鉄のスタンドを参考に）。
# 高さはルリの腰くらい。ランタン（8 幅）はフックの先（x = 13）に吊るす：Lantern の吊るす位置 = 足元から (5, 9) ドット。16 x 24
LANTERN_STAND = [
    "................",
    ".....OOOOOOOOO..",
    ".....OiiiiiiiiO.",
    ".....OiOOOOOOiO.",
    ".....OiO....OiO.",
    ".....OiO....OOO.",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    ".....OiO........",
    "...OOOOOOOOOO...",
    "..OwwwwwwwwwoO..",
    "..OddddddddDDO..",
    "..OddddddddDDO..",
    "...OOOOOOOOOO...",
]
LANTERN_STAND_KEY = {
    "O": color("night", 1),
    "i": color("stone", 4),                               # 鉄の棒
    "w": color("brown", 2), "o": color("brown", 1),       # 切り株の上の面（左が明るい）
    "d": color("brown", 1), "D": color("brown", 0),       # 切り株の横（樹皮）
}


def build(save):
    out = {
        "gate_lamp_on": save(gate_lamp(True), "Props", "gate_lamp_on.png", clean=True),
        "gate_lamp_off": save(gate_lamp(False), "Props", "gate_lamp_off.png", clean=True),
        "lantern_stand": save(from_map(LANTERN_STAND, LANTERN_STAND_KEY), "Props", "lantern_stand.png", clean=True),
    }
    return out
