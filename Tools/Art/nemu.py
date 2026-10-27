"""ネム（ランタンに住みついた、しゃべる蛾）：オオミズアオがモチーフ。v0.16 で B 案「月明かり」の描き方に仕上げた。

オオミズアオ（Actias artemis／aliena）の特徴と、この絵での表し方
- 淡い青緑の大きな羽 → ほのかに光る青緑（palette.py の glow）。膜は少し透ける（不透明度 84%）。
  学名の Actias は月の女神アルテミスにちなむ。BlueNight の「大きな満月」とつながるモチーフ。
- 前羽の前のふちに赤茶の帯、4 枚の羽それぞれに目玉模様（黄色の輪＋透けた窓）、後ろ羽の長い尾（先が黄色）。
- 真っ白でふわふわの体と頭、羽毛のような触角。頭と体は控えめに（美しさは羽の大きさと透明感）。
- **口は描かない**。オオミズアオの成虫には口がない（何も食べず、1 週間ほどで命を終える。CHARACTERS.md・物語の第 4 章）。
  表情は目と触角だけで出す。

描き方（ユーザーの決定：B 案のまま、v0.16）
- 輪郭線を引かず、明暗の差と左上の縁の光で形を見せる（chara.py）。羽の縁は光が透けたように明るい。
- 左右対称なので左半分を描いて反転し、陰影はあとから自動で付ける（光はどちらの羽でも左上から）。
"""

from chara import Canvas, Mat, Style, render
from palette import RAMPS, hex_to_rgba

STYLE = Style("none", rim=True)
WING_ALPHA = 215     # 羽の膜（glow1・glow2）の不透明度。縁の光（glow3）は透けない


def curve(p0, p1, p2, steps=30):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        q = (round(x), round(y))
        if not pts or pts[-1] != q:
            pts.append(q)
    return pts


def dots(c, pts, sym, only=None):
    for (x, y) in pts:
        if 0 <= x < c.w and 0 <= y < c.h and (only is None or c.g[y][x] in only):
            c.g[y][x] = sym


def translucent(img):
    """羽の膜を少しだけ透かす（1 ドット＝1 ドットのまま、後ろの色が混ざるだけ）。"""
    membrane = {hex_to_rgba(RAMPS["glow"][i])[:3] for i in (1, 2)}
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in membrane:
                px[x, y] = (r, g, b, WING_ALPHA)
    return img


# ================================================================ ゲーム内（22x24、4 コマ）
# シルエットだけでオオミズアオとわかるように：大きな三角の前羽、細い体（2 ドット）、小さな頭、長く垂れる尾。
SPRITE_W, SPRITE_H = 22, 24

POSES = {
    "spread": {  # 羽を広げる：前羽は先のとがった大きな三角、後ろ羽はそれより小さく、細い尾がまっすぐ下へ
        "fore": [(9, 8), (5, 6), (0, 4), (2, 8), (4, 11), (7, 12), (9, 11)],
        "hind": [(9, 11), (7, 12), (5, 14), (5, 16), (6, 17), (8, 17), (9, 16)],
        "tail": ((6, 16), (2, 19), (4, 23)),
        "spots": [(4, 8), (7, 14)],
    },
    "up": {  # 羽を上げる（前羽の先が上を向き、横から見ると細くなる）
        "fore": [(9, 8), (6, 5), (2, 3), (4, 7), (5, 10), (7, 12), (9, 11)],
        "hind": [(9, 11), (7, 12), (6, 14), (6, 16), (7, 17), (9, 16)],
        "tail": ((7, 16), (3, 19), (5, 23)),
        "spots": [(5, 6), (7, 14)],
    },
    "down": {  # 羽を下げる（前羽の先が下を向く）
        "fore": [(9, 8), (4, 8), (0, 10), (3, 12), (6, 13), (9, 12)],
        "hind": [(9, 11), (6, 13), (4, 15), (4, 17), (6, 18), (8, 18), (9, 17)],
        "tail": ((5, 17), (1, 20), (3, 23)),
        "spots": [(4, 10), (6, 15)],
    },
}

SPRITE_MATS = {
    "W": Mat("glow2", "glow1", "glow3", group="WCy", d=2),    # 前羽
    "V": Mat("glow2", "glow1", "glow3", group="Vy", d=1),     # 後ろ羽と尾（前羽と別の部品：前羽の下のふちに影ができて 2 枚に見える）
    "F": Mat("fluff2", "fluff1", "fluff2", group="FE"),       # 白い毛
}
SPRITE_DIRECT = {"a": "warm4", "y": "warm4", "C": "brown2", "E": "night0"}


def sprite(name):
    pose = POSES[name]
    c = Canvas(SPRITE_W, SPRITE_H)
    c.poly(pose["hind"], "V")
    tail = curve(*pose["tail"], steps=12)
    dots(c, tail, "V")
    # 尾は外へふくらませる（まっすぐ下へ垂らすと足に見える）。小さな絵では先の黄色も足に見えるので付けない
    c.poly(pose["fore"], "W")
    for x in range(10):                                           # 前羽の前のふちの赤茶の帯（各列のいちばん上）
        ys = [y for y in range(SPRITE_H) if c.g[y][x] == "W"]
        if ys:
            dots(c, [(x, ys[0])], "C")
    for (x, y) in pose["spots"]:
        dots(c, [(x, y)], "y", only="WV")                         # 目玉模様（黄色の 1 ドット）
    c.mirror_x(SPRITE_W - 1)
    # 体：小さな頭（横に黒い目）、短い胸、細いおなか
    c.rect((9, 5, 12, 7), "F")
    dots(c, [(9, 6), (12, 6)], "E")
    c.rect((9, 8, 12, 9), "F")
    c.rect((10, 10, 11, 16), "F")
    dots(c, [(8, 4), (7, 3), (6, 2)], "a")                        # 触角
    dots(c, [(13, 4), (14, 3), (15, 2)], "a")
    return translucent(render(c.rows(), SPRITE_MATS, SPRITE_DIRECT, STYLE))


def sprite_frames():
    """4 コマ：広げる → 上げる → 広げる → 下げる。"""
    return [sprite("spread"), sprite("up"), sprite("spread"), sprite("down")]


# ================================================================ 顔グラフィック（48x48）
# 左側の図形（右側は反転して作る）。実物の標本の、羽を広げた形に合わせる
FOREWING = [(23, 12), (15, 10), (8, 8), (2, 6), (0, 7), (1, 11), (3, 16), (6, 21), (10, 26), (14, 28),
            (19, 26), (23, 21)]
COSTA = [(23, 11), (15, 9), (8, 7), (2, 5), (0, 6), (1, 8), (8, 10), (15, 12), (23, 14)]   # 赤茶の帯
HINDWING = [(23, 20), (15, 23), (9, 27), (6, 32), (7, 36), (11, 38), (17, 37), (21, 33), (23, 28)]
TAIL = [(13, 37), (9, 41), (9, 44), (12, 47)]   # 後ろ羽から外へふくらんで、内へ戻る細い尾（2 ドット幅）

EYESPOT = [   # 目玉模様（5x4）：赤茶の縁・黄色の輪・透けた窓（窓は左上）
    ".cc..",
    "cMMyc",
    "cyyyc",
    ".ccc.",
]

EXPRESSIONS = ("normal", "happy", "surprised", "sleepy")

# 目（左右とも同じ形。つやは左上）。口は描かない
EYES = {
    "normal": [".EE.", "EeEE", "EEEE", ".EE."],
    "happy": ["....", ".EE.", "E..E", "...."],          # にっこり（目を細める）
    "surprised": [".EE.", "EeEE", "EEEE", "EEEE", ".EE."],
    "sleepy": ["....", "....", "EEEE", ".EE."],          # 眠そう（名前の「ネム」）
}
# 触角の軸（頭の左の付け根 → 先）。表情で角度を変える（右は反転）
ANTENNA = {
    "normal": ((20, 9), (17, 2), (10, 2)),
    "happy": ((20, 9), (17, 1), (11, 0)),
    "surprised": ((20, 9), (19, 1), (15, 0)),             # ぴんと立つ
    "sleepy": ((20, 9), (16, 3), (10, 4)),                # 少したれる
}

FACE_MATS = {
    "W": Mat("glow2", "glow1", "glow3", group="WCLcyMv", d=3),
    "V": Mat("glow2", "glow1", "glow3", group="VcyMv", d=3),
    "F": Mat("fluff2", "fluff1", "fluff2", group="FEef", d=2),
}
FACE_DIRECT = {"a": "warm4", "A": "brown2", "y": "warm4", "c": "brown1", "C": "brown2", "L": "glow3",
               "M": ("moon3", 120), "E": "night0", "e": "moon3", "f": "fluff1", "v": "glow1"}


def portrait(expression):
    c = Canvas(48, 48)
    # ---- 左半分：後ろ羽と尾 → 前羽 → 帯 → 羽の筋 → 目玉模様
    c.poly(HINDWING, "V")
    c.line(TAIL, "V", width=2)
    c.poly([(9, 45), (13, 45), (13, 47), (9, 47)], "y", only="V")     # 尾の先の黄色
    c.poly(FOREWING, "W")
    c.poly(COSTA, "C", only="W")
    dots(c, curve((21, 15), (12, 13), (4, 10)), "v", only="W")      # 羽の筋（体から外へ）
    dots(c, curve((21, 19), (14, 20), (7, 21)), "v", only="W")
    dots(c, curve((21, 26), (15, 29), (10, 34)), "v", only="V")
    c.stamp(EYESPOT, 9, 14)
    c.stamp(EYESPOT, 11, 30)
    c.mirror_x(47)
    # ---- 体（白いふわふわ）：胸 → おなか → 首まわりの影 → 頭と頬の毛
    c.ellipse((19, 16, 28, 26), "F")
    c.ellipse((21, 24, 26, 38), "F")
    for (x, y) in [(22, 29), (23, 33)]:
        dots(c, [(x, y), (x + 1, y)], "f")                          # おなかの節
    c.ellipse((18, 17, 29, 22), "f", only="F")
    c.ellipse((17, 7, 30, 20), "F")
    for (x, y) in [(15, 11), (15, 15), (29, 11), (29, 15)]:
        c.ellipse((x, y, x + 3, y + 3), "F")
    # ---- 触角（羽毛：葉の形の毛の中に軸）
    for side in (1, -1):
        stem = curve(*ANTENNA[expression], steps=20)
        blade = []
        n = len(stem)
        for i, (x, y) in enumerate(stem):
            if i % 2:
                continue
            width = 2 if 0.2 < i / n < 0.75 else 1
            blade += [(x - k, y - k) for k in range(1, width + 1)] + [(x + k - 1, y + k) for k in range(1, width + 1)]
        if side == -1:
            stem = [(47 - x, y) for (x, y) in stem]
            blade = [(47 - x, y) for (x, y) in blade]
        dots(c, blade, "A", only=".")
        dots(c, stem, "a")
    # ---- 目（口はない）
    eyes = EYES[expression]
    c.stamp(eyes, 18, 11)
    c.stamp(eyes, 26, 11)
    return translucent(render(c.rows(), FACE_MATS, FACE_DIRECT, STYLE))


def build(save):
    """輪郭線が無いので clean_corners はかけない。"""
    out = {"sprite": [], "faces": {}}
    for i, img in enumerate(sprite_frames()):
        out["sprite"].append(save(img, "Characters", "Nemu", f"nemu_fly_{i}.png"))
    for e in EXPRESSIONS:
        out["faces"][e] = save(portrait(e), "Faces", f"face_nemu_{e}.png")
    return out
