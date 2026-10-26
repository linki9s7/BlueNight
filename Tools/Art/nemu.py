"""ネム（ランタンに住みついた、しゃべる蛾）：オオミズアオがモチーフ（v0.13、一から作り直し）。

オオミズアオ（Actias artemis／aliena）の特徴と、この絵での表し方
- 淡い青緑の羽 → 月明かりの色の「ミント」ランプ（palette.py の moth）。青い夜の中で月のようにほの白く光る。
  学名の Actias は月の女神アルテミスにちなむ。BlueNight の「大きな満月」とつながるモチーフ。
- 前羽の前のふち（肩から羽の先まで）に赤茶の帯 → brown2 の 2 ドット幅の帯。肩の上で左右がつながる。
- 4 枚の羽それぞれに小さな目玉模様（黄色の輪＋暗い縁＋透けた窓） → 小さなピクセルマップ。
- 後ろ羽の長い尾（先が黄色っぽい） → 外へふくらんでから下へ流れる尾。根元は羽と同じ幅にして「羽の続き」に見せる
  （細い線 2 本にすると脚に見える）。
- 真っ白でふわふわの体と頭、羽毛のような触角 → クリーム色の毛のかたまり、葉の形の触角。

この世界のドット絵の記法（Tools/Art/STYLE.md、ruri.py と同じやり方）
- ピクセルマップ（記号の文字の図）で描く。輪郭は 1 ドットの紺（night1、町の人と同じ）。
- 左右対称の生き物なので左半分を書いて反転し、陰影はあとから自動で置く（shade）：
  「右下へ 2 ドットずらすと同じ部品の外に出る所」だけを影の色にする。光はどちらの羽でも左上から（反転しない）。
- 平らな塗り＋小さな模様（帯・目玉模様・羽の筋）。網点・中間色のぼかしは使わない。
"""

from PIL import Image, ImageDraw

from palette import RAMPS, hex_to_rgba

CLEAR = (0, 0, 0, 0)


def P(name):
    ramp = name.rstrip("0123456789")
    return hex_to_rgba(RAMPS[ramp][int(name[len(ramp):])])


KEY = {
    "O": "night1",   # 輪郭（体・頭・触角）
    "o": "moth0",    # 羽の輪郭：紺より軽い暗い青緑にして、羽を重く見せない（透明感）
    "W": "moth3",    # 羽（淡い青緑）
    "w": "moth2",    # 羽の影（自動）
    "H": "moth3",    # 後ろ羽（色は前羽と同じ。前羽との境目に輪郭を入れるため記号を分ける）
    "h": "moth2",    # 後ろ羽の影（自動）
    "v": "moth2",    # 羽の筋
    "L": "moth4",    # 羽のつや（前羽の帯の下）
    "C": "brown2",   # 前羽の前のふちの赤茶の帯
    "c": "brown1",   # 目玉模様の縁
    "y": "warm4",    # 目玉模様の黄色・尾の先
    "M": "moon3",    # 目玉模様の透けた窓
    "S": "brown1",   # 目玉模様（ゲーム内の小さな絵）の暗い点
    "F": "warm6",    # ふわふわの毛（体・頭）
    "f": "stone7",   # 毛の影（自動）
    "A": "warm4",    # 触角の軸
    "a": "brown2",   # 触角の毛
    "E": "night0",   # 目（黒）
    "e": "moon3",    # 目のつや
    "m": "brown1",   # 口
}

WING = set("WwHhvLCcyMS")   # 羽の部品

# 羽の膜は少しだけ透ける（後ろの夜や灯りがかすかに見える）。目玉模様の窓はもっと透ける。
# 1 ドット＝1 ドットのまま、色の重なり方だけが変わる（ドットの大きさは混ざらない）
ALPHA = {"W": 215, "w": 215, "H": 215, "h": 215, "L": 215, "v": 235, "M": 120}
FORE = set("WwLCvcyMS")     # 前羽（影の判定で「同じ部品」とみなす）
HIND = set("HhvcyMS")       # 後ろ羽と尾
FUR = set("FfEem")


def mirror_half(rows):
    """左半分の行から左右対称の行を作る（陰影はまだ付いていない）。"""
    return [row + row[::-1] for row in rows]


def shade(rows, fur_d=2):
    """右下へ 2 ドットずらすと同じ部品の外に出る所を影にする（光は左上から）。
    小さなゲーム内の絵では、細い体が全部影にならないよう毛は 1 ドットで判定する（fur_d=1）。"""
    grid = [list(r) for r in rows]
    h, w = len(grid), len(grid[0])

    def at(x, y):
        return grid[y][x] if 0 <= x < w and 0 <= y < h else "."

    out = [row[:] for row in grid]
    for y in range(h):
        for x in range(w):
            ch = grid[y][x]
            if ch == "W" and at(x + 2, y + 2) not in FORE:
                out[y][x] = "w"
            elif ch == "H" and at(x + 2, y + 2) not in HIND:
                out[y][x] = "h"
            elif ch == "F" and at(x + fur_d, y + fur_d) not in FUR:
                out[y][x] = "f"
    return ["".join(r) for r in out]


def to_image(rows):
    w = len(rows[0])
    img = Image.new("RGBA", (w, len(rows)), CLEAR)
    px = img.load()
    for y, row in enumerate(rows):
        assert len(row) == w, f"row {y}: {row!r} ({len(row)} != {w})"
        for x, ch in enumerate(row):
            if ch != ".":
                r, g, b, _ = P(KEY[ch])
                px[x, y] = (r, g, b, ALPHA.get(ch, 255))
    return img


def soften_wing_outline(rows):
    """羽だけに接する輪郭（O）を、羽の輪郭の色（o）にする。体・頭・触角に接する所は紺のまま。"""
    grid = [list(r) for r in rows]
    h, w = len(grid), len(grid[0])
    out = [r[:] for r in grid]
    for y in range(h):
        for x in range(w):
            if grid[y][x] != "O":
                continue
            near = [grid[ny][nx] for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                    if 0 <= nx < w and 0 <= ny < h]
            if any(c in WING for c in near) and not any(c in FUR or c in "Aa" for c in near):
                out[y][x] = "o"
    return ["".join(r) for r in out]


# ================================================================ ゲーム内（22x24、4 コマ）
# シルエットだけでオオミズアオとわかるように：大きな三角の前羽、細い体（2 ドット）、小さな頭、長く垂れる尾。
# 図形（左側の座標）を記号の格子に塗って反転し、顔グラフィックと同じ手順で境目・陰影・輪郭をつける。
SPRITE_W, SPRITE_H = 22, 24

POSES = {
    "spread": {  # 羽を広げる：前羽は先のとがった大きな三角、後ろ羽はそれより小さく、細い尾がまっすぐ下へ
        "fore": [(9, 8), (5, 6), (0, 4), (2, 8), (4, 11), (7, 12), (9, 11)],
        "hind": [(9, 11), (7, 12), (5, 14), (5, 16), (6, 17), (8, 17), (9, 16)],
        "tail": ((7, 16), (5, 19), (6, 22)),
        "spots": [(4, 8), (7, 14)],
    },
    "up": {  # 羽を上げる（前羽の先が上を向き、横から見ると細くなる）
        "fore": [(9, 8), (6, 5), (2, 3), (4, 7), (5, 10), (7, 12), (9, 11)],
        "hind": [(9, 11), (7, 12), (6, 14), (6, 16), (7, 17), (9, 16)],
        "tail": ((8, 16), (6, 19), (7, 22)),
        "spots": [(5, 6), (7, 14)],
    },
    "down": {  # 羽を下げる（前羽の先が下を向く）
        "fore": [(9, 8), (4, 8), (0, 10), (3, 12), (6, 13), (9, 12)],
        "hind": [(9, 11), (6, 13), (4, 15), (4, 17), (6, 18), (8, 18), (9, 17)],
        "tail": ((6, 17), (4, 20), (5, 23)),
        "spots": [(4, 10), (6, 15)],
    },
}


def sprite(name):
    pose = POSES[name]
    gr = Grid(SPRITE_W, SPRITE_H)
    gr.poly(pose["hind"], "H")
    tail = curve(*pose["tail"], steps=12)
    gr.dots(tail, "H")                                                    # 細い尾（1 ドット＋輪郭）
    tip = max(tail, key=lambda p: p[1])
    gr.dots([tip, (tip[0], tip[1] - 1)], "y")                             # 尾の先の黄色
    gr.poly(pose["fore"], "W")
    # 前羽の前のふちの赤茶の帯：各列のいちばん上の羽の 1 ドット（小さな絵では細い線のほうが実物らしい）
    for x in range(10):
        ys = [y for y in range(SPRITE_H) if gr.g[y][x] == "W"]
        if ys:
            gr.dots([(x, ys[0])], "C", only={"W"})
    for (x, y) in pose["spots"]:
        gr.dots([(x, y)], "y", only={"W", "H"})                            # 目玉模様（黄色の 1 ドット）
    gr.mirror_left()
    # 体：小さな頭（横に黒い目）、短い胸、細いおなか（2 ドット：左が白、右が影で細く見える）
    gr.poly([(9, 5), (12, 5), (12, 7), (9, 7)], "F")
    gr.dots([(9, 6), (12, 6)], "E")
    gr.poly([(9, 8), (12, 8), (12, 9), (9, 9)], "F")
    gr.poly([(10, 10), (11, 10), (11, 16), (10, 16)], "F")
    gr.dots([(8, 4), (7, 3), (6, 2)], "A")                                 # 触角
    gr.dots([(13, 4), (14, 3), (15, 2)], "A")
    rows = fore_hind_line(gr.rows())
    rows = shade(rows, fur_d=1)
    rows = inner_lines(rows)
    rows = outline_rows(rows)
    return to_image(rows)


def sprite_frames():
    """4 コマ：広げる → 上げる → 広げる → 下げる。"""
    return [sprite("spread"), sprite("up"), sprite("spread"), sprite("down")]


# ================================================================ 顔グラフィック（48x48）
SIZE = 48


class Grid:
    """記号の格子（顔グラフィックは 48x48、ゲーム内は小さい格子）。図形は記号で塗り、最後に KEY で色にする。"""

    def __init__(self, w=None, h=None):
        self.w, self.h = w or SIZE, h or SIZE
        self.g = [["."] * self.w for _ in range(self.h)]

    def poly(self, points, ch, only=None):
        m = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(m).polygon(points, fill=255)
        self._apply(m, ch, only)

    def ellipse(self, box, ch, only=None):
        m = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(m).ellipse(box, fill=255)
        self._apply(m, ch, only)

    def _apply(self, m, ch, only):
        px = m.load()
        for y in range(self.h):
            for x in range(self.w):
                if px[x, y] and (only is None or self.g[y][x] in only):
                    self.g[y][x] = ch

    def dots(self, pts, ch, only=None):
        for (x, y) in pts:
            if 0 <= x < self.w and 0 <= y < self.h and (only is None or self.g[y][x] in only):
                self.g[y][x] = ch

    def stamp(self, rows, x0, y0):
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != ".":
                    self.g[y0 + y][x0 + x] = ch

    def mirror_left(self):
        """左半分を右半分へ写す。"""
        for y in range(self.h):
            for x in range(self.w // 2):
                self.g[y][self.w - 1 - x] = self.g[y][x]

    def rows(self):
        return ["".join(r) for r in self.g]

    def set_rows(self, rows):
        self.g = [list(r) for r in rows]


def mirror(pts):
    return [(SIZE - 1 - x, y) for (x, y) in pts]


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


# 左側の図形（右側は反転して作る）
# 実物のオオミズアオ（標本の、羽を広げた形）に合わせる
# 前羽：前のふち（赤茶の帯）は体からほぼ真横にのび、先はとがる。外のふちは先から内側へななめに下がる三角形
FOREWING = [(23, 12), (15, 10), (8, 8), (2, 6), (0, 7), (1, 11), (3, 16), (6, 21), (10, 26), (14, 28),
            (19, 26), (23, 21)]
COSTA = [(23, 11), (15, 9), (8, 7), (2, 5), (0, 6), (1, 8), (8, 10), (15, 12), (23, 14)]   # 赤茶の帯
COSTA_LIGHT = [(16, 11), (8, 9), (2, 7), (3, 11), (9, 12), (15, 14)]   # 帯のすぐ下のつや（帯との間に 1 列の羽の色を残さない）
# 後ろ羽：前羽の下にのぞく、丸みのある大きな三角形。下のふちから長い尾がほぼまっすぐ下へ
HINDWING = [(23, 20), (15, 23), (9, 27), (6, 32), (7, 37), (11, 40), (17, 39), (21, 34), (23, 28)]
TAIL_OUTER = ((11, 38), (8, 43), (10, 48))
TAIL_INNER = ((16, 39), (12, 43), (12, 48))

EYESPOT = [   # 目玉模様（5x4）：赤茶の縁・黄色の輪・透けた窓（窓は左上）
    ".cc..",
    "cMMyc",
    "cyyyc",
    ".ccc.",
]


def eyes_for(expression):
    """目（5x5）。黒い目に、左上の大きなつや＋右下の小さなつや。"""
    return {
        "normal": [   # 少しまぶたを下ろした、余裕のある目
            "OOOOO",
            "EeeEE",
            "EeEEE",
            "EEEeE",
            ".EEE.",
        ],
        "happy": [    # にっこり
            ".....",
            ".EEE.",
            "E...E",
            ".....",
            ".....",
        ],
        "surprised": [  # まんまる
            ".EEE.",
            "EeeEE",
            "EeEEE",
            "EEEeE",
            ".EEE.",
        ],
        "sleepy": [   # 眠そう（名前の「ネム」）
            ".....",
            ".....",
            "OOOOO",
            ".EEE.",
            ".....",
        ],
    }[expression]


MOUTHS = {
    "normal": ["m..m", ".mm."],      # ちいさく笑う
    "happy": ["mmmm", ".mm."],       # 口をあけて笑う
    "surprised": [".mm.", ".mm."],   # 「お」の口
    "sleepy": ["....", ".mm."],
}


def portrait(expression):
    gr = Grid()
    # ---- 左半分：後ろ羽と尾 → 前羽 → 帯 → 目玉模様 → 羽の筋
    gr.poly(HINDWING, "H")
    outer, inner = curve(*TAIL_OUTER), curve(*TAIL_INNER)
    gr.poly(outer + inner[::-1], "H")
    gr.dots([(x, y) for (x, y) in outer + inner if y >= 45], "y")        # 尾の先の黄色いふち
    gr.poly([(6, 46), (14, 46), (14, 47), (6, 47)], "y", only={"H"})
    gr.poly(FOREWING, "W")
    gr.poly(COSTA, "C", only={"W"})
    gr.poly(COSTA_LIGHT, "L", only={"W"})
    gr.dots(curve((21, 15), (12, 13), (4, 10)), "v", only={"W"})        # 羽の筋（体から外へ）
    gr.dots(curve((21, 19), (14, 20), (7, 21)), "v", only={"W"})
    gr.dots(curve((21, 26), (15, 29), (10, 34)), "v", only={"H"})
    gr.stamp(EYESPOT, 9, 14)    # 前羽の目玉模様（羽のまん中より少し前のふち寄り）
    gr.stamp(EYESPOT, 11, 30)   # 後ろ羽の目玉模様
    gr.mirror_left()

    # ---- 体（白いふわふわ）：胸 → おなか → 頭（毛のかたまりでふちを波形に）
    # 頭と体は羽より控えめに（オオミズアオの美しさは羽の大きさ）
    gr.ellipse([19, 16, 28, 25], "F")
    gr.ellipse([21, 22, 26, 37], "F")
    for (x, y) in [(22, 28), (24, 32)]:
        gr.dots([(x, y), (x + 1, y)], "f")                               # おなかの節（短い線）
    # 首まわりの毛の影（頭と胸を分ける）：頭を描く前に胸の上を影の色にしておく
    gr.ellipse([18, 17, 29, 22], "f", only={"F"})
    gr.ellipse([17, 8, 30, 20], "F")
    for (x, y) in [(15, 11), (15, 15), (29, 11), (29, 15)]:
        gr.ellipse([x, y, x + 3, y + 3], "F")                            # 頬の毛のふさ

    # ---- 触角（羽毛：葉の形の毛の中に軸）
    for side in (1, -1):
        stem = curve((20, 9), (17, 2), (10, 2), steps=20)
        blade = []
        n = len(stem)
        for i, (x, y) in enumerate(stem):
            if i % 2:
                continue  # 毛は 1 本おき（羽毛のすじ）
            width = 2 if 0.2 < i / n < 0.75 else 1
            blade += [(x - k, y - k) for k in range(1, width + 1)] + [(x + k - 1, y + k) for k in range(1, width + 1)]
        if side == -1:
            stem, blade = mirror(stem), mirror(blade)
        gr.dots(blade, "a", only={"."})
        gr.dots(stem, "A")

    # ---- 目と口（右目は形を反転、つやは左上のまま）
    eyes = eyes_for(expression)
    gr.stamp(eyes, 18, 11)
    right = []
    for r in eyes:
        rr = list(r[::-1].replace("e", "E"))
        right.append(rr)
    for y, r in enumerate(eyes):
        for x, ch in enumerate(r):
            if ch == "e":
                right[y][x] = "e"
    gr.stamp(["".join(r) for r in right], 25, 11)
    gr.stamp(MOUTHS[expression], 22, 16)

    # ---- 前羽と後ろ羽の境目 → 陰影 → 毛と羽の境目 → 外側の輪郭
    rows = fore_hind_line(gr.rows())
    rows = shade(rows)
    rows = inner_lines(rows)
    rows = outline_rows(rows)
    return to_image(rows)


def fore_hind_line(rows):
    """後ろ羽のうち、前羽に接する所を 1 ドットの輪郭にする（2 枚の羽が重なって見えるように）。"""
    grid = [list(r) for r in rows]
    h, w = len(grid), len(grid[0])
    out = [r[:] for r in grid]
    for y in range(h):
        for x in range(w):
            if grid[y][x] != "H":
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in "WLC":
                    out[y][x] = "o"
                    break
    return ["".join(r) for r in out]


def outline_rows(rows):
    """外側の輪郭：羽だけに接する所は羽の輪郭の色（o）、体・頭・触角に接する所は紺（O）。"""
    grid = [list(r) for r in rows]
    h, w = len(grid), len(grid[0])
    out = [r[:] for r in grid]
    for y in range(h):
        for x in range(w):
            if grid[y][x] != ".":
                continue
            near = [grid[ny][nx] for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                    if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] not in ".oO"]
            if not near:
                continue
            out[y][x] = "o" if all(c in WING for c in near) else "O"
    return ["".join(r) for r in out]


def inner_lines(rows):
    """毛（体・頭）と羽の境目に 1 ドットの輪郭（羽の側に、羽の輪郭の色で）。"""
    grid = [list(r) for r in rows]
    h, w = len(grid), len(grid[0])
    out = [r[:] for r in grid]
    for y in range(h):
        for x in range(w):
            if grid[y][x] not in WING:
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in FUR:
                    out[y][x] = "o"
                    break
    return ["".join(r) for r in out]


EXPRESSIONS = ("normal", "happy", "surprised", "sleepy")


def build(save):
    out = {"sprite": [], "faces": {}}
    for i, img in enumerate(sprite_frames()):
        out["sprite"].append(save(img, "Characters", "Nemu", f"nemu_fly_{i}.png", clean=True))
    for e in EXPRESSIONS:
        out["faces"][e] = save(portrait(e), "Faces", f"face_nemu_{e}.png", clean=True)
    return out
