"""会話の顔グラフィック（48x48）。

作り方
- 形は「部品（うしろ髪・顔・前髪・横髪・首・マフラー・コート）」の図形を重ねて作る。
- 陰影は部品ごとに、光（左上）と反対の右下のふちに 3 ドット幅の影のかたまりを置く（shade_mask）。
  形を右下へずらした時にはみ出す所だけを影にするので、同心円状（ピローシェーディング）にはならない。
- 目・口は表情ごとのピクセルマップを置く。目のつやは左右どちらの目も左上（光の向き）。
- 最後にまわりへ 1 ドットの輪郭をつけ、clean_corners でダブりを取る（build.py の save）。
"""

from PIL import Image, ImageChops, ImageDraw

import ruri
from palette import RAMPS, hex_to_rgba

CLEAR = (0, 0, 0, 0)
SIZE = 48


def P(name):
    ramp = name.rstrip("0123456789")
    return hex_to_rgba(RAMPS[ramp][int(name[len(ramp):])])


# ---------------------------------------------------------------- 図形と陰影
def mask():
    return Image.new("L", (SIZE, SIZE), 0)


def ellipse(box):
    m = mask()
    ImageDraw.Draw(m).ellipse(box, fill=255)
    return m


def polygon(points):
    m = mask()
    ImageDraw.Draw(m).polygon(points, fill=255)
    return m


def rect(box):
    m = mask()
    ImageDraw.Draw(m).rectangle(box, fill=255)
    return m


def union(*ms):
    out = mask()
    for m in ms:
        out = ImageChops.lighter(out, m)
    return out


def minus(a, b):
    return ImageChops.subtract(a, b)


def _shift(m, dx, dy):
    out = mask()
    out.paste(m, (dx, dy))
    return out


def edge_mask(m, dx, dy):
    """m の中で、(-dx, -dy) 方向から見て「ふち」になる所＝ m をずらした形に入らない所。
    dx, dy > 0 なら右下のふち（影）、< 0 なら左上のふち（つや）。"""
    return minus(m, _shift(m, -dx, -dy))


class Portrait:
    def __init__(self):
        self.img = Image.new("RGBA", (SIZE, SIZE), CLEAR)

    def fill(self, m, color):
        self.img.paste(Image.new("RGBA", (SIZE, SIZE), P(color)), (0, 0), m)

    def part(self, m, base, shade=None, light=None, shade_d=(3, 3), light_d=(-2, -2), light_clip=None):
        """部品を塗る：基本の色＋右下の影のかたまり＋（あれば）左上のつや。"""
        self.fill(m, base)
        if shade:
            self.fill(edge_mask(m, *shade_d), shade)
        if light:
            lm = edge_mask(m, *light_d)
            if light_clip is not None:
                lm = ImageChops.multiply(lm, light_clip)
            self.fill(lm, light)

    def stamp(self, rows, key, x0, y0):
        px = self.img.load()
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != ".":
                    px[x0 + x, y0 + y] = P(key[ch])

    def outline(self, color):
        src = self.img.copy().load()
        px = self.img.load()
        for y in range(SIZE):
            for x in range(SIZE):
                if src[x, y][3]:
                    continue
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < SIZE and 0 <= ny < SIZE and src[nx, ny][3]:
                        px[x, y] = P(color)
                        break


# ================================================================ ルリ
# v0.16 のリデザインで ruri.py に移した（輪郭線なし・月明かりの縁取り・大きな青い目・眉）。


# ================================================================ ランプ屋の主人
def keeper_portrait(expression):
    pt = Portrait()
    coat = polygon([(3, 47), (6, 40), (14, 37), (33, 37), (41, 40), (44, 47)])
    pt.part(coat, "brown2", shade="brown1", shade_d=(4, 3))  # 革の前かけ
    pt.fill(polygon([(16, 37), (31, 37), (28, 44), (19, 44)]), "coat2")  # シャツのえり
    pt.fill(edge_mask(polygon([(16, 37), (31, 37), (28, 44), (19, 44)]), 2, 2), "coat1")
    neck = rect([19, 30, 28, 38])
    pt.fill(neck, "skin1")
    head = union(ellipse([11, 5, 36, 36]))
    pt.part(head, "skin2", shade="skin1", shade_d=(3, 3))
    pt.fill(polygon([(14, 10), (19, 7), (21, 8), (16, 12)]), "skin2")  # はげ頭のつや（左上）
    # 白い横髪
    for pts in ([(10, 14), (14, 13), (15, 26), (12, 28), (9, 22)], [(37, 14), (33, 13), (32, 26), (35, 28), (38, 22)]):
        pt.part(polygon(pts), "stone7", shade="stone5", shade_d=(2, 2))
    # まゆ（白）・めがね・口ひげ
    glasses = [
        ".OOOOOO...OOOOOO.",
        "OLLqqqqOOOLLqqqqO",
        "OLqqEqqO.OLqqEqqO",
        "OqqqEqqO.OqqqEqqO",
        ".OOOOOO...OOOOOO.",
    ] if expression == "normal" else [
        ".OOOOOO...OOOOOO.",
        "OLLqqqqOOOLLqqqqO",
        "OLqEEEqO.OLqEEEqO",
        "OqqqqqqO.OqqqqqqO",
        ".OOOOOO...OOOOOO.",
    ]
    pt.stamp(["WWWW......WWWW"], {"W": "stone7"}, 16, 15)  # まゆ
    pt.stamp(glasses, {"O": "night1", "L": "moon2", "q": "skin2", "E": "night1"}, 15, 17)
    pt.stamp(["..ss..", ".ssss."], {"s": "skin1"}, 21, 23)  # 鼻
    mustache = [
        "..WWWWWWWWW..",
        ".WWWWWWWWWww.",
        "WWWw.....wwwW",
    ]
    pt.stamp(mustache, {"W": "stone7", "w": "stone5"}, 17, 26)
    pt.stamp(["mmm"] if expression == "normal" else ["m.m", ".m."], {"m": "skin0"}, 22, 29)
    pt.outline("night1")
    return pt.img


# ================================================================ おばあさん
def grandma_portrait(expression):
    pt = Portrait()
    coat = polygon([(3, 47), (6, 40), (14, 37), (33, 37), (41, 40), (44, 47)])
    pt.part(coat, "red1", shade="red0", shade_d=(4, 3))  # カーディガン
    neck = rect([19, 30, 28, 38])
    pt.fill(neck, "skin1")
    # 髪（白髪のおだんご）
    hair = ellipse([10, 5, 37, 30])
    pt.part(hair, "stone7", shade="stone5", shade_d=(3, 3))
    # おだんご：髪の上に別の丸として重ね、右下の影で髪と分ける
    bun = ellipse([18, 0, 28, 9])
    pt.part(bun, "stone7", shade="stone5", shade_d=(2, 3))
    pt.fill(minus(ellipse([18, 1, 28, 10]), ellipse([18, 0, 28, 9])), "stone5")
    face = union(ellipse([13, 11, 34, 36]))
    pt.part(face, "skin2", shade="skin1", shade_d=(3, 3))
    # 前髪の生え際（顔の上を髪でおおう）
    fringe = polygon([(12, 16), (16, 10), (24, 8), (32, 10), (35, 16), (30, 13), (24, 12), (17, 13)])
    pt.part(fringe, "stone7", shade="stone5", shade_d=(2, 2))
    eyes = {
        "normal": ["OOOO.....OOOO", ".OO.......OO."],
        "smile": [".OO.......OO.", "O..O.....O..O"],
        "teary": [".OO.......OO.", "O..O.....O..O", "...L.......L."],
    }[expression]
    pt.stamp(eyes, {"O": "night1", "L": "moon1"}, 17, 21)
    pt.stamp(["..s", ".ss"], {"s": "skin1"}, 23, 24)  # 鼻
    mouth = {"normal": ["mmmm"], "smile": ["m..m", ".mm."], "teary": ["m..m", ".mm."]}[expression]
    pt.stamp(mouth, {"m": "skin0"}, 22, 29)
    pt.stamp(["s"], {"s": "skin1"}, 16, 27)  # しわ
    pt.stamp(["s"], {"s": "skin1"}, 31, 27)
    pt.outline("night1")
    return pt.img


def build(save):
    out = {}
    for e in ruri.EXPRESSIONS:
        out[f"ruri_{e}"] = save(ruri.portrait(e), "Faces", f"face_ruri_{e}.png")
    for e in ("normal", "smile"):
        out[f"keeper_{e}"] = save(keeper_portrait(e), "Faces", f"face_keeper_{e}.png", clean=True)
    for e in ("normal", "smile", "teary"):
        out[f"grandma_{e}"] = save(grandma_portrait(e), "Faces", f"face_grandma_{e}.png", clean=True)
    return out
