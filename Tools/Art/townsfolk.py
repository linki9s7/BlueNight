"""第 1 章の町の人（v0.16 のリデザイン）：佐伯ハル（おばあさん）、青柳篤（ランプ屋の主人）、のら猫のゴマ。

ルリ・ネムと同じ描き方（chara.py）：輪郭線を引かず、明暗の差と左上の縁の月明かりで形を見せる。
大きさ・コマ数・ファイル名は前と同じ（Unity はそのまま差しかわる）。人物の人生は docs/CHARACTERS.md。

- ハル（82）：白髪のおだんご、やさしい目、ほおの赤み。ばら色のカーディガン（夫の正二が「似合う」と言った色）、
  灰色の長いスカート、杖。居眠りは、店先の腰かけでひざの上に手を組む。
  v0.19（ユーザーの指摘「優しそうな人に」）：いつも口もとが笑っている。目じりの下がった目、ハの字のやわらかい眉、丸いほお。
- 青柳（78）：v0.19（ユーザーの指摘「職人肌のイケオジに」）：後ろへなでつけた銀髪、きれいに整えた白いあごひげ、太い眉、
  深い目もと、通った鼻。細いふちの丸めがね（月明かりが映る）。藍のシャツのそでをまくり、太い腕。革の前かけのポケットにドライバー。
  背すじがのびて肩幅が広い。
- ゴマ：炭色の猫（ごまのような黒）。胸と足先が白い。夜に光る目。商店街の暗がりで、灰色の歩道と見分けやすい濃さ。
"""

from chara import Canvas, Mat, Style, render

STYLE = Style("none", rim=True)

# ================================================================ ハル（おばあさん）
# 記号：J おだんご  H 髪  S 肌  a 光の側の手  E 目  r ほお  m 口  C カーディガン  K スカート
#       F 草履  T 杖  b 腰かけ
HARU_MATS = {
    "J": Mat("stone7", "stone5", "tee3", group="J"),
    "H": Mat("stone7", "stone5", "tee3", d=2),
    "S": Mat("skin2", "skin1", group="SErmq"),
    "C": Mat("rose2", "rose1", "rose3", d=2),
    "K": Mat("stone3", "stone2", "stone4", d=2),
    "F": Mat("brown1", "brown0", "brown2"),
    "b": Mat("brown2", "brown1", "brown3"),
}
HARU_DIRECT = {"a": "skin2", "E": "night1", "r": "blush0", "m": "skin0", "T": "brown1", "q": "stone5"}

HARU = [
    "................",
    "......JJJJ......",
    "......JJJJ......",
    ".....HHHHHH.....",
    "....HHHHHHHH....",
    "...HHHHHHHHHH...",
    "...HHSSSSSSHH...",
    "...HqSSSSSSqH...",   # ハの字のやわらかい眉
    "...HSESSSSESH...",
    "...HrSSSSSSrH...",   # 丸いほお
    "....SmSSSSmS....",   # いつも笑っている口もと
    ".....SSmmSS.....",
    "....CCCSSCCC....",
    "...CCCCCCCCCC...",
    "..CCCCCCCCCCCC..",
    "..CCCCCCCCCCCC..",
    "..CCCCCCCCCCCC..",
    "..aCCCCCCCCCSST.",   # 右手で杖をつく
    "...KKKKKKKKKK.T.",
    "...KKKKKKKKKK.T.",
    "...KKKKKKKKKK.T.",
    "..KKKKKKKKKKK.T.",
    "..KKKKKKKKKKK.T.",
    "..KKKKKKKKKKK.T.",
    "...KKKKKKKKK..T.",
    ".....SS..SS...T.",
    "....FFF..FFF..T.",
    "..............T.",
]
# 2 コマ目：ゆっくり呼吸（頭が 1 ドット下がる）
HARU_BREATH = ["." * 16] + HARU[:12] + HARU[13:]

# 居眠り（16x22）：店先の腰かけで、目を閉じて、ひざの上で手を組む
HARU_DOZE = [
    "................",
    "......JJJJ......",
    "......JJJJ......",
    ".....HHHHHH.....",
    "....HHHHHHHH....",
    "...HHHHHHHHHH...",
    "...HHSSSSSSHH...",
    "...HqSSSSSSqH...",
    "...HSEESSEESH...",   # 目を閉じる
    "...HrSSSSSSrH...",
    "....SmSSSSmS....",   # 眠っていても口もとは笑っている
    ".....SSmmSS.....",
    "....CCCSSCCC....",
    "...CCCCCCCCCC...",
    "..CCaaCCCCSSCC..",   # ひざの上で手を組む
    "..KKKKKKKKKKKK..",
    ".KKKKKKKKKKKKKK.",
    ".KKKKKKKKKKKKKK.",
    "..bbbbbbbbbbbb..",
    "..b.FF....FF.b..",
    "..b..........b..",
    "..b..........b..",
]
HARU_NOD = ["." * 16] + HARU_DOZE[:12] + HARU_DOZE[13:]
# 起きて店先の腰かけに座っている（台本 9.4「店先の明かりの中に、椅子に座っている」）：居眠りの図の目を開ける
HARU_SIT = [r if i != 8 else "...HSESSSSESH..." for i, r in enumerate(HARU_DOZE)]
HARU_SIT_BREATH = ["." * 16] + HARU_SIT[:12] + HARU_SIT[13:]


def haru_frames():
    return [render(r, HARU_MATS, HARU_DIRECT, STYLE) for r in (HARU, HARU_BREATH)]


def haru_doze_frames():
    return [render(r, HARU_MATS, HARU_DIRECT, STYLE) for r in (HARU_DOZE, HARU_NOD)]


def haru_sit_frames():
    return [render(r, HARU_MATS, HARU_DIRECT, STYLE) for r in (HARU_SIT, HARU_SIT_BREATH)]


# ================================================================ 青柳（ランプ屋の主人）
# 記号：S 肌  H 銀髪  h 髪のつや  b 太い眉  E 目  L 丸めがね（月明かりの照り返し）  B あごひげ  W 口ひげ  m 口
#       C 藍のシャツ（そでをまくる）  A 革の前かけ  y ポケットのドライバー  P ズボン  F 靴  a 光の側の腕
AOYAGI_MATS = {
    "S": Mat("skin2", "skin1", group="SEbLm"),
    "H": Mat("stone6", "stone4", "stone7", group="Hh", d=1),
    "B": Mat("stone7", "stone5", "tee3", group="BW", d=1),
    "C": Mat("night5", "night4", "stone5", group="C", d=1),
    "A": Mat("brown2", "brown1", "brown3", group="Ay", d=2),
    "P": Mat("stone3", "stone2", "stone4"),
    "F": Mat("brown1", "brown0", "brown2"),
}
AOYAGI_DIRECT = {"h": "tee3", "b": "stone5", "E": "night1", "L": "moon1", "W": "stone7", "m": "skin0", "y": "warm4", "a": "skin2"}

AOYAGI = [
    "................",
    ".....HHHHHH.....",   # 後ろへなでつけた銀髪
    "....HhhHHHHH....",
    "...HHHHHHHHHH...",
    "...HSSSSSSSSH...",
    "...HbbbSSbbbH...",   # 太い眉
    "...HLESSSSLEH...",   # 丸めがね（左上が光る）と、深い目もと
    "....SSSSSSSS....",
    "....BSWWWWSB....",   # 口ひげと、整えたあごひげ
    "....BBSmmSBB....",
    ".....BBBBBB.....",
    "......SSSS......",
    "...CCCCSSCCCC...",   # 肩幅が広い。藍のシャツ
    "..CCCCAAAACCCC..",
    "..CCCAAAAAACCC..",
    "..CCAAAAAAAACC..",
    "..CCAAAAAyAACC..",   # 前かけのポケットにドライバー
    "..aSAAAAAAyASS..",   # まくったそでから、太い腕
    "..aSAAAAAAAASS..",
    "..a.AAAAAAAA.S..",
    "....AAAAAAAA....",
    "....AAAAAAAA....",
    "....PPPPPPPP....",
    "....PPPPPPPP....",
    "....PPP..PPP....",
    "....PPP..PPP....",
    "....PPP..PPP....",
    "...FFFF..FFFF...",
    "................",
]
# 2 コマ目：ゆっくりうなずく（頭が 1 ドット下がる）
AOYAGI_NOD = ["." * 16] + AOYAGI[:10] + AOYAGI[11:]


def aoyagi_frames():
    return [render(r, AOYAGI_MATS, AOYAGI_DIRECT, STYLE) for r in (AOYAGI, AOYAGI_NOD)]


# ================================================================ ゴマ（のら猫、16x12、横向きに座る）
GOMA_MATS = {
    "C": Mat("stone2", "stone1", "stone5"),
    "W": Mat("stone7", "stone5", "tee3"),
}
GOMA_DIRECT = {"E": "warm4", "n": "red2"}

GOMA = [
    ".C...C..........",
    ".CC.CC..........",
    ".CCCCC..........",
    ".CECEC..........",   # 目の位置（2, 3）と（4, 3）は猫の影の光る目と同じ
    ".CCnCC......C...",
    "..WCC.......C...",
    "..WWCCCCC...C...",
    ".WWWCCCCCC..C...",
    ".WWCCCCCCCC.C...",
    ".WWCCCCCCCCCC...",
    ".WCCCCCCCCCCC...",
    ".WW.WW.CC.CC....",
]
GOMA_BLINK = GOMA[:3] + [".CCCCC.........."] + GOMA[4:]
GOMA_TAIL = GOMA[:4] + [
    ".CCnCC.....C....",
    "..WCC......C....",
    "..WWCCCCC..C....",
    ".WWWCCCCCC.C....",
    ".WWCCCCCCCCC....",
] + GOMA[9:]


def goma_frames():
    """4 コマ：座る／まばたき／しっぽを振る／座る。"""
    return [render(r, GOMA_MATS, GOMA_DIRECT, STYLE) for r in (GOMA, GOMA_BLINK, GOMA_TAIL, GOMA)]


# ================================================================ 顔グラフィック（48x48）
SHOULDERS = [(3, 47), (7, 40), (15, 37), (33, 37), (41, 40), (45, 47)]

HARU_FACE_MATS = {
    "J": Mat("stone7", "stone5", "tee3", group="J", d=2),
    "H": Mat("stone7", "stone5", "tee3", d=2),
    "S": Mat("skin2", "skin1", group="SEeBLmnrq", d=2),
    "C": Mat("rose2", "rose1", "rose3", d=3),
    "w": Mat("tee3", "tee2", group="w", d=2),
}
HARU_FACE_DIRECT = {"E": "night1", "B": "brown1", "e": "moon3", "L": "moon1", "m": "skin0", "n": "skin1", "r": "blush0", "q": "stone5"}
HARU_EYES = {   # (左, 右)。やさしい目：目じりが下がり、黒目がちで、上のまぶたは丸い
    # v0.19（ユーザーの指摘）：前の目は、つやを左右の目で反対に置いていたので黒目が内へ寄って見えた（斜視）。
    # 形は前のまま、黒目を真ん中に、つやはどちらも左上（光の向き）。まわりを茶色（B）でぼかす（AA）
    "normal": ([".BEB.", "BeEEB", ".BEB.", "n...."], [".BEB.", "BeEEB", ".BEB.", "....n"]),
    "smile": (["......", ".EEEE.", "E....E", "......"], ["......", ".EEEE.", "E....E", "......"]),     # 目を細めて笑う
    "teary": (["......", ".EEEE.", "E....E", "....L."], ["......", ".EEEE.", "E....E", ".L...."]),   # 笑いながら涙
}
HARU_BROWS = {   # ハの字（目じり側が下がる）のやわらかい眉
    "normal": (["..qq", "qq.."], ["qq..", "..qq"]),
    "smile": (["..qq", "qq.."], ["qq..", "..qq"]),
    "teary": (["...qq", "qqq.."], ["qq...", "..qqq"]),
}
HARU_MOUTHS = {"normal": ["m....m", ".mmmm."], "smile": ["m....m", ".mmmm.", "..nn.."], "teary": ["m....m", ".mmmm."]}


def haru_portrait(expression):
    c = Canvas(48, 48)
    c.poly(SHOULDERS, "C")                                   # ばら色のカーディガン
    c.poly([(18, 37), (30, 37), (27, 43), (21, 43)], "w")    # ブラウスの白い襟
    c.rect((20, 30, 27, 38), "S")
    c.ellipse((10, 5, 37, 31), "H")                          # 白髪
    c.ellipse((18, 0, 29, 10), "J")                          # おだんご（別の部品として重ねる）
    c.ellipse((12, 11, 35, 38), "S")                         # 丸い顔
    c.poly([(12, 17), (16, 10), (24, 8), (32, 10), (35, 17), (30, 13), (24, 12), (17, 13)], "H")   # 生え際
    c.poly([(12, 15), (15, 15), (15, 25), (12, 22)], "H")    # こめかみの髪
    c.poly([(32, 15), (35, 15), (35, 22), (32, 25)], "H")
    left_brow, right_brow = HARU_BROWS[expression]
    c.stamp(left_brow, 17, 18)
    c.stamp(right_brow, 27, 18)
    left, right = HARU_EYES[expression]
    c.stamp(left, 16, 21)
    c.stamp(right, 27, 21)
    c.stamp(["..n", ".nn"], 22, 25)                          # 鼻
    c.stamp(["rrr", ".rr"], 14, 27)                          # 丸いほお
    c.stamp(["rrr", "rr."], 31, 27)
    c.stamp(["n."], 17, 31)                                  # 笑いじわ
    c.stamp([".n"], 29, 31)
    mouth = HARU_MOUTHS[expression]
    c.stamp(mouth, 24 - len(mouth[0]) // 2, 30)
    return render(c.rows(), HARU_FACE_MATS, HARU_FACE_DIRECT, STYLE)


AOYAGI_FACE_MATS = {
    "S": Mat("skin2", "skin1", group="SGLqEemnb", d=3),
    "H": Mat("stone6", "stone4", "stone7", group="Hh", d=2),
    "B": Mat("stone7", "stone5", "tee3", group="BW", d=2),
    "A": Mat("brown2", "brown1", "brown3", group="A", d=3),
    "C": Mat("night5", "night4", "stone5", group="C", d=2),
}
AOYAGI_FACE_DIRECT = {"G": "night1", "L": "moon2", "q": "skin2", "E": "night1", "e": "moon3", "m": "skin0", "n": "skin1",
                      "b": "stone5", "h": "tee3", "W": "stone7"}
GLASSES = {   # 細いふちの小さな丸めがね（G ふち・L 月明かりの照り返し・q レンズ越しの肌・E 目、e 目のつや）。目は細く鋭い
    "normal": [
        ".GGGG.....GGGG.",
        "GLqqqG...GLqqqG",
        "GEEEeGGGGGEEEeG",
        ".GGGG.....GGGG.",
    ],
    "smile": [
        ".GGGG.....GGGG.",
        "GLqqqG...GLqqqG",
        "GqEEqGGGGGqEEqG",
        ".GGGG.....GGGG.",
    ],
}


def aoyagi_portrait(expression):
    c = Canvas(48, 48)
    c.poly(SHOULDERS, "C")                                   # 肩幅の広い、藍のシャツ
    c.poly([(13, 40), (19, 39), (22, 47), (14, 47)], "A")    # 革の前かけのつり紐
    c.poly([(35, 40), (29, 39), (26, 47), (34, 47)], "A")
    c.rect((19, 31, 28, 40), "S")                            # 太い首
    c.poly([(19, 38), (24, 44), (29, 38)], "S")              # 開いた襟もと
    c.ellipse((11, 1, 37, 24), "H")                          # 後ろへなでつけた銀髪（上にボリューム）
    c.poly([(13, 13), (35, 13), (36, 26), (33, 34), (27, 39), (21, 39), (15, 34), (12, 26)], "S")   # 面長で角ばったあご
    c.poly([(13, 14), (15, 9), (20, 10), (24, 8), (28, 10), (33, 9), (35, 14), (30, 12), (24, 11), (18, 12)], "H")   # 生え際（こめかみが少し上がる）
    c.rect((12, 13, 13, 22), "H")                            # もみあげ
    c.rect((35, 13, 36, 22), "H")
    for pts in ([(15, 7), (20, 4), (27, 3)], [(14, 10), (19, 7), (24, 6)], [(28, 5), (33, 7)]):   # なでつけた髪の筋
        c.line(pts, "h", only="H")
    c.stamp(["bbbbbb", "..bbbb"], 14, 16)                    # 太い眉（眉間へ向けて少し下がる）
    c.stamp(["bbbbbb", "bbbb.."], 28, 16)
    c.stamp(GLASSES[expression], 16, 19)
    c.stamp(["n", "n", "n", "n", "nn"], 24, 22)              # 通った鼻
    c.stamp(["n", "n"], 14, 21)                              # 目じりのしわ
    c.stamp(["n", "n"], 33, 21)
    c.stamp(["n", "n", "n"], 16, 26)                         # こけたほお
    c.stamp(["n", "n", "n"], 31, 26)
    # 短く整えた白いあごひげ（口のまわりとあごだけ）と口ひげ
    c.poly([(18, 30), (22, 31), (26, 31), (30, 30), (31, 34), (28, 38), (24, 39), (20, 38), (17, 34)], "B")
    c.stamp(["WWWWWWWWW", "W.......W"], 20, 29)
    c.stamp(["mmm"] if expression == "normal" else ["m...m", ".mmm."], 23 if expression == "normal" else 22, 32)
    return render(c.rows(), AOYAGI_FACE_MATS, AOYAGI_FACE_DIRECT, STYLE)
