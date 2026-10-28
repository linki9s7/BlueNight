"""第 1 章の町の人（v0.16 のリデザイン）：佐伯ハル（おばあさん）、青柳篤（ランプ屋の主人）、のら猫のゴマ。

ルリ・ネムと同じ描き方（chara.py）：輪郭線を引かず、明暗の差と左上の縁の月明かりで形を見せる。
大きさ・コマ数・ファイル名は前と同じ（Unity はそのまま差しかわる）。人物の人生は docs/CHARACTERS.md。

- ハル（82）：白髪のおだんご、やさしい目、ほおの赤み。ばら色のカーディガン（夫の正二が「似合う」と言った色）、
  灰色の長いスカート、杖。居眠りは、店先の腰かけでひざの上に手を組む。
- 青柳（78）：はげ頭に白い横髪、丸めがね（月明かりが映る）、白い口ひげ、白いシャツに革の前かけ。
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
    "S": Mat("skin2", "skin1", group="SErm"),
    "C": Mat("rose2", "rose1", "rose3", d=2),
    "K": Mat("stone3", "stone2", "stone4", d=2),
    "F": Mat("brown1", "brown0", "brown2"),
    "b": Mat("brown2", "brown1", "brown3"),
}
HARU_DIRECT = {"a": "skin2", "E": "night1", "r": "blush0", "m": "skin0", "T": "brown1"}

HARU = [
    "................",
    "......JJJJ......",
    "......JJJJ......",
    ".....HHHHHH.....",
    "....HHHHHHHH....",
    "...HHHHHHHHHH...",
    "...HHSSSSSSHH...",
    "...HSSSSSSSSH...",
    "...HSESSSSESH...",
    "...HrSSSSSSrH...",
    "....SSSmmSSS....",
    ".....SSSSSS.....",
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
    "...HSSSSSSSSH...",
    "...HSEESSEESH...",   # 目を閉じる
    "...HrSSSSSSrH...",
    "....SSSmmSSS....",
    ".....SSSSSS.....",
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
# 記号：S 肌  g はげ頭のつや  H 白い横髪  L めがね（月明かりの照り返し）  W 口ひげ  C シャツ  A 革の前かけ
#       P ズボン  F 靴  a 光の側の手
AOYAGI_MATS = {
    "S": Mat("skin2", "skin1", group="SgLW"),
    "H": Mat("stone7", "stone5", "tee3", d=1),
    "W": Mat("stone7", "stone5", group="W"),
    "C": Mat("coat2", "coat1", "tee3", group="C", d=1),
    "A": Mat("brown2", "brown1", "brown3", d=2),
    "P": Mat("stone3", "stone2", "stone4"),
    "F": Mat("night3", "night2", "night5"),
}
AOYAGI_DIRECT = {"g": "tee3", "L": "moon1", "a": "skin2"}

AOYAGI = [
    "................",
    "................",
    ".....SSSSSS.....",
    "....SggSSSSS....",
    "...HSSSSSSSSH...",
    "...HSSSSSSSSH...",
    "...HLLSSSSLLH...",
    "...HSSSSSSSSH...",
    "...HSWWWWWWSH...",
    "....SSSSSSSS....",
    ".....SSSSSS.....",
    "....CCCSSCCC....",
    "...CCCAAAACCC...",
    "..CCCAAAAAACCC..",
    "..CCAAAAAAAACC..",
    "..CCAAAAAAAACC..",
    "..aCAAAAAAAACS..",
    "..a.AAAAAAAA.S..",
    "....AAAAAAAA....",
    "....AAAAAAAA....",
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
    "S": Mat("skin2", "skin1", group="SEeLmnrq", d=2),
    "C": Mat("rose2", "rose1", "rose3", d=3),
    "w": Mat("tee3", "tee2", group="w", d=2),
}
HARU_FACE_DIRECT = {"E": "night1", "e": "moon3", "L": "moon1", "m": "skin0", "n": "skin1", "r": "blush0", "q": "stone5"}
HARU_EYES = {   # (左, 右)。やさしい目：まぶたが少し下りている
    "normal": (["EEEE", ".EeE", "..E."], ["EEEE", ".EeE", "..E."]),
    "smile": (["....", ".EE.", "E..E"], ["....", ".EE.", "E..E"]),      # 目を細めて笑う
    "teary": (["....", ".EE.", "E..E", "...L"], ["....", ".EE.", "E..E", "L..."]),   # 笑いながら涙
}
HARU_BROWS = {
    "normal": (["qqq."], [".qqq"]),
    "smile": ([".qq.", "q..q"], [".qq.", "q..q"]),
    "teary": (["..qq", "qq.."], ["qq..", "..qq"]),     # 眉間が上がる
}
HARU_MOUTHS = {"normal": [".mm."], "smile": ["m..m", ".mm."], "teary": ["m..m", ".mm."]}


def haru_portrait(expression):
    c = Canvas(48, 48)
    c.poly(SHOULDERS, "C")                                   # ばら色のカーディガン
    c.poly([(18, 37), (30, 37), (27, 43), (21, 43)], "w")    # ブラウスの白い襟
    c.rect((20, 30, 27, 38), "S")
    c.ellipse((10, 5, 37, 31), "H")                          # 白髪
    c.ellipse((18, 0, 29, 10), "J")                          # おだんご（別の部品として重ねる）
    c.ellipse((13, 11, 34, 37), "S")
    c.poly([(12, 17), (16, 10), (24, 8), (32, 10), (35, 17), (30, 13), (24, 12), (17, 13)], "H")   # 生え際
    c.poly([(12, 15), (15, 15), (15, 25), (12, 22)], "H")    # こめかみの髪
    c.poly([(32, 15), (35, 15), (35, 22), (32, 25)], "H")
    left_brow, right_brow = HARU_BROWS[expression]
    c.stamp(left_brow, 17, 18)
    c.stamp(right_brow, 27, 18)
    left, right = HARU_EYES[expression]
    c.stamp(left, 17, 21)
    c.stamp(right, 27, 21)
    c.stamp(["..n", ".nn"], 22, 25)                          # 鼻
    c.stamp(["rr"], 15, 27)
    c.stamp(["rr"], 31, 27)
    c.stamp(["n"], 16, 30)                                   # 笑いじわ
    c.stamp(["n"], 31, 30)
    mouth = HARU_MOUTHS[expression]
    c.stamp(mouth, 24 - len(mouth[0]) // 2, 30)
    return render(c.rows(), HARU_FACE_MATS, HARU_FACE_DIRECT, STYLE)


AOYAGI_FACE_MATS = {
    "S": Mat("skin2", "skin1", group="SgGLqEmn", d=3),
    "H": Mat("stone7", "stone5", "tee3", d=2),
    "W": Mat("stone7", "stone5", "tee3", group="W", d=2),
    "A": Mat("brown2", "brown1", "brown3", d=3),
    "C": Mat("coat2", "coat1", "tee3", group="C", d=2),
}
AOYAGI_FACE_DIRECT = {"g": "tee3", "G": "night1", "L": "moon2", "q": "skin2", "E": "night1", "m": "skin0", "n": "skin1",
                      "B": "stone7"}
GLASSES = {   # 丸めがね（G ふち・L 月明かりの照り返し・q レンズ越しの肌・E 目）
    "normal": [
        ".GGGGGG...GGGGGG.",
        "GLLqqqqGGGLLqqqqG",
        "GLqqEqqG.GLqqEqqG",
        "GqqqEqqG.GqqqEqqG",
        ".GGGGGG...GGGGGG.",
    ],
    "smile": [
        ".GGGGGG...GGGGGG.",
        "GLLqqqqGGGLLqqqqG",
        "GLqEEEqG.GLqEEEqG",
        "GqEqqqEG.GqEqqqEG",
        ".GGGGGG...GGGGGG.",
    ],
}


def aoyagi_portrait(expression):
    c = Canvas(48, 48)
    c.poly(SHOULDERS, "A")                                   # 革の前かけ
    c.poly([(16, 37), (31, 37), (28, 44), (19, 44)], "C")    # シャツの襟
    c.rect((19, 30, 28, 38), "S")
    c.ellipse((11, 5, 36, 36), "S")                          # はげ頭
    c.poly([(14, 10), (19, 7), (21, 8), (16, 12)], "g")      # 頭のつや（左上）
    c.poly([(10, 14), (14, 13), (15, 26), (12, 28), (9, 22)], "H")    # 白い横髪
    c.poly([(37, 14), (33, 13), (32, 26), (35, 28), (38, 22)], "H")
    c.stamp(["BBBB......BBBB"], 16, 15)                      # 白い眉
    c.stamp(GLASSES[expression], 15, 17)
    c.stamp(["..nn..", ".nnnn."], 21, 23)                    # 鼻
    c.stamp(["..WWWWWWWWW..", ".WWWWWWWWWWW.", "WWW.......WWW"], 17, 26)   # 口ひげ
    c.stamp(["mmm"] if expression == "normal" else ["m.m", ".m."], 22, 29)
    return render(c.rows(), AOYAGI_FACE_MATS, AOYAGI_FACE_DIRECT, STYLE)
