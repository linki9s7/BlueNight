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
    "O": "night1",   # 輪郭
    "W": "moth2",    # 羽（淡い青緑）
    "w": "moth1",    # 羽の影（自動）
    "v": "moth1",    # 羽の筋
    "L": "moth3",    # 羽のつや（前羽の帯の下）
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

WING = set("WwvLCcyMS")   # 羽の部品（影の判定で「同じ部品」とみなす）
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
            if ch == "W" and at(x + 2, y + 2) not in WING:
                out[y][x] = "w"
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
                px[x, y] = P(KEY[ch])
    return img


# ================================================================ ゲーム内（20x20、4 コマ）
# 左半分（10 列）。右端の列が体の中心。y = 目玉模様の黄、S = その暗い点、y（尾の先）
SPRITE_HALVES = {
    "spread": [  # 羽を広げる
        "...A......",
        "....A.....",
        "OO...AOOOO",
        "OCCO..OFFF",
        "OWCCOOOFEF",
        "OWWCCCOFFF",
        "OWySWWCOFF",
        "OWWWWWWWOF",
        ".OWWWWWWOF",
        "..OOWWWWOF",
        "..OWWWWWOF",
        ".OWWySWWOF",
        ".OWWWWWWOF",
        "..OWWWWWOF",
        "..OWWOOOOO",
        ".OWWO.....",
        ".OWO......",
        "OWO.......",
        "OyO.......",
        "OO........",
    ],
    "up": [  # 羽を上げる（横から見ると細くなる）
        "..OO.A....",
        "..OCO.A...",
        "..OCCOOOOO",
        "..OWCCOFFF",
        "..OWWCOFEF",
        "..OySWOFFF",
        "..OWWWWOOF",
        "...OWWWWOF",
        "...OOWWWOF",
        "...OWWWWOF",
        "...OySWWOF",
        "...OWWWWOF",
        "...OWWOOOF",
        "...OWO..OO",
        "..OWO.....",
        "..OWO.....",
        ".OWO......",
        ".OyO......",
        ".OO.......",
        "..........",
    ],
    "down": [  # 羽を下げる（尾が外へふれる）
        "...A......",
        "....A.....",
        ".....AOOOO",
        "OOOO..OFFF",
        "OCCCOOOFEF",
        "OWWCCCOFFF",
        "OWySWWWOFF",
        "OWWWWWWWOF",
        "OWWWWWWOOF",
        ".OOWWWWWOF",
        "..OWWWWWOF",
        "..OWySWWOF",
        "..OWWWWWOF",
        "...OWWWWOF",
        "...OWWOOOO",
        "..OWWO....",
        "..OWO.....",
        ".OWO......",
        ".OyO......",
        ".OO.......",
    ],
}


def sprite(name):
    return to_image(shade(mirror_half(SPRITE_HALVES[name]), fur_d=1))


def sprite_frames():
    """4 コマ：広げる → 上げる → 広げる → 下げる。"""
    return [sprite("spread"), sprite("up"), sprite("spread"), sprite("down")]


# ================================================================ 顔グラフィック（48x48）
SIZE = 48


class Grid:
    """記号の格子（48x48）。図形は記号で塗り、最後に KEY で色にする。"""

    def __init__(self):
        self.g = [["."] * SIZE for _ in range(SIZE)]

    def poly(self, points, ch, only=None):
        m = Image.new("L", (SIZE, SIZE), 0)
        ImageDraw.Draw(m).polygon(points, fill=255)
        self._apply(m, ch, only)

    def ellipse(self, box, ch, only=None):
        m = Image.new("L", (SIZE, SIZE), 0)
        ImageDraw.Draw(m).ellipse(box, fill=255)
        self._apply(m, ch, only)

    def _apply(self, m, ch, only):
        px = m.load()
        for y in range(SIZE):
            for x in range(SIZE):
                if px[x, y] and (only is None or self.g[y][x] in only):
                    self.g[y][x] = ch

    def dots(self, pts, ch, only=None):
        for (x, y) in pts:
            if 0 <= x < SIZE and 0 <= y < SIZE and (only is None or self.g[y][x] in only):
                self.g[y][x] = ch

    def stamp(self, rows, x0, y0):
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != ".":
                    self.g[y0 + y][x0 + x] = ch

    def mirror_left(self):
        """左半分（x < 24）を右半分へ写す。"""
        for y in range(SIZE):
            for x in range(SIZE // 2):
                self.g[y][SIZE - 1 - x] = self.g[y][x]

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
FOREWING = [(22, 15), (17, 11), (11, 7), (5, 4), (1, 3), (0, 5), (2, 9), (3, 14), (4, 19), (7, 23),
            (12, 25), (18, 25), (22, 22)]
COSTA = [(23, 13), (17, 9), (11, 5), (5, 2), (1, 2), (1, 4), (5, 5), (11, 8), (17, 12), (23, 16)]   # 赤茶の帯
COSTA_LIGHT = [(17, 11), (11, 7), (5, 4), (6, 9), (11, 12), (15, 15)]   # 帯のすぐ下のつや（帯との間に 1 列の羽の色を残さない）
HINDWING = [(22, 22), (16, 24), (10, 27), (6, 31), (6, 35), (9, 37), (13, 37), (17, 35), (21, 31), (23, 27)]
TAIL_OUTER = ((6, 33), (0, 40), (3, 47))
TAIL_INNER = ((12, 37), (5, 41), (5, 47))

EYESPOT = [   # 目玉模様（5x4）：赤茶の縁・黄色の輪・透けた窓（窓は左上）
    ".cc..",
    "cMMyc",
    "cyyyc",
    ".ccc.",
]


def eyes_for(expression):
    """目（6x6）。黒い大きな目に、左上の大きなつや＋右下の小さなつや。"""
    return {
        "normal": [   # 少しまぶたを下ろした、余裕のある目
            "......",
            "OOOOOO",
            "EeeEEE",
            "EeEEEE",
            "EEEEeE",
            ".EEEE.",
        ],
        "happy": [    # にっこり
            "......",
            "......",
            ".EEEE.",
            "E....E",
            "......",
            "......",
        ],
        "surprised": [  # まんまる
            ".EEEE.",
            "EeeEEE",
            "EeEEEE",
            "EEEEEE",
            "EEEEeE",
            ".EEEE.",
        ],
        "sleepy": [   # 眠そう（名前の「ネム」）
            "......",
            "......",
            "......",
            "OOOOOO",
            ".EEEE.",
            "......",
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
    gr.poly(HINDWING, "W")
    outer, inner = curve(*TAIL_OUTER), curve(*TAIL_INNER)
    gr.poly(outer + inner[::-1], "W")
    gr.dots([(x, y) for (x, y) in outer + inner if y >= 45], "y")        # 尾の先の黄色いふち
    gr.poly([(1, 46), (7, 46), (7, 47), (1, 47)], "y", only={"W"})
    gr.poly(FOREWING, "W")
    gr.poly(COSTA, "C", only={"W"})
    gr.poly(COSTA_LIGHT, "L", only={"W"})
    gr.dots(curve((19, 18), (12, 15), (5, 15)), "v", only={"W"})        # 羽の筋（体から外へ）
    gr.dots(curve((19, 21), (13, 21), (8, 22)), "v", only={"W"})
    gr.dots(curve((20, 28), (15, 29), (10, 31)), "v", only={"W"})
    gr.stamp(EYESPOT, 7, 13)    # 前羽の目玉模様
    gr.stamp(EYESPOT, 12, 29)   # 後ろ羽の目玉模様
    gr.mirror_left()

    # ---- 体（白いふわふわ）：胸 → おなか → 頭（毛のかたまりでふちを波形に）
    gr.ellipse([18, 18, 29, 29], "F")
    gr.ellipse([20, 26, 27, 41], "F")
    for x in range(21, 27, 2):
        gr.dots([(x, 31), (x + 1, 31)] if x % 4 == 1 else [(x, 35), (x + 1, 35)], "f")   # おなかの節（短い線）
    # 首まわりの毛の影（頭と胸を分ける）：頭を描く前に胸の上を影の色にしておく
    gr.ellipse([17, 19, 30, 25], "f", only={"F"})
    gr.ellipse([16, 7, 31, 22], "F")
    for (x, y) in [(14, 11), (14, 16), (30, 11), (30, 16)]:
        gr.ellipse([x, y, x + 3, y + 3], "F")                            # 頬の毛のふさ

    # ---- 触角（羽毛：葉の形の毛の中に軸）
    for side in (1, -1):
        stem = curve((19, 9), (16, 1), (8, 1), steps=24)
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
    gr.stamp(eyes, 17, 12)
    right = []
    for r in eyes:
        rr = list(r[::-1].replace("e", "E"))
        right.append(rr)
    for y, r in enumerate(eyes):
        for x, ch in enumerate(r):
            if ch == "e":
                right[y][x] = "e"
    gr.stamp(["".join(r) for r in right], 25, 12)
    gr.stamp(MOUTHS[expression], 22, 19)

    # ---- 陰影 → 部品の境目と外側の輪郭
    rows = shade(gr.rows())
    rows = inner_lines(rows)
    img = to_image(rows)
    return outline(img)


def inner_lines(rows):
    """毛（体・頭）と羽の境目、前羽と後ろ羽の境目に 1 ドットの輪郭（町の人と同じ描き方）。"""
    grid = [list(r) for r in rows]
    h, w = len(grid), len(grid[0])
    out = [r[:] for r in grid]
    for y in range(h):
        for x in range(w):
            if grid[y][x] not in WING:
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in FUR:
                    out[y][x] = "O"
                    break
    return ["".join(r) for r in out]


def outline(img):
    src = img.copy().load()
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if src[x, y][3]:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3]:
                    px[x, y] = P("night1")
                    break
    return img


EXPRESSIONS = ("normal", "happy", "surprised", "sleepy")


def build(save):
    out = {"sprite": [], "faces": {}}
    for i, img in enumerate(sprite_frames()):
        out["sprite"].append(save(img, "Characters", "Nemu", f"nemu_fly_{i}.png", clean=True))
    for e in EXPRESSIONS:
        out["faces"][e] = save(portrait(e), "Faces", f"face_nemu_{e}.png", clean=True)
    return out
