"""ルリとネムのリデザイン案（見比べ用。ゲームの素材にはまだ使わない）。

使い方（リポジトリのルートで）:
    python3 Tools/Art/concept_chars.py
出力:
    Tools/Art/preview/concepts/*.png

「イラストレーターが変わった」くらいの違いを出すため、案ごとに変えるもの
- 頭身（頭と体の比）とシルエット
- 輪郭のつけ方：紺の線（line）／塗りの色を暗くした線（selout）／線なし（none）
- 陰影：右下のかたまりの幅、月明かりの縁取り（左上）
- 服・髪型（物語は晩夏の夜。眠れずに家を出た 14 歳。マフラーだけ季節はずれ）
- ネム：口は描かない（オオミズアオの成虫には口がない。CHARACTERS.md）

参考にしたもの（STYLE.md 1 章）
- A：UNREAL LIFE（hako 生活）の細い人物。小さな頭・長い手足・点の目。色数を絞り、余白で見せる。
- B：Hyper Light Drifter・Alto のような輪郭線のない色面。形は明暗の差と、左上の縁の光で見せる。
- C：Eastward・Sea of Stars のような描きこみ。塗りの色を暗くした輪郭（selout）、つやのある大きな目。
どの案も、光は左上から（影は右下のかたまり）。左向きは記号の図を反転してから陰影を付けるので、光の向きは変わらない。
"""

import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import RAMPS, hex_to_rgba  # noqa: E402
from pixel_check import clean_corners  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "Tools", "Art", "preview", "concepts")
CLEAR = (0, 0, 0, 0)

# 案のための色（palette.py にない色）。採用が決まったら palette.py のランプに移す。
EXTRA = {
    "tee": ["#5b6384", "#8e97b8", "#d6dcec", "#f3f5fb"],       # 白い T シャツ（夜の青を含んだ白）
    "hood": ["#3a4f6b", "#5f7a96", "#8fabc2", "#c4d8e6"],      # 灰青のパーカー
    "teal": ["#0f2430", "#1b3a4a", "#2c5a6c", "#4f8a96"],      # B 案の髪（青緑がかった黒）
    "dress": ["#4f5d86", "#7d8bb4", "#b9c3df", "#e6ebf7"],     # C 案のワンピース
    "cardi": ["#6f6a86", "#a9a3bd", "#ddd8e6", "#f4f1f7"],      # C・D 案の服（クリーム。夜の青を含む）
    "fluff": ["#9aa6bf", "#d3dbe8", "#f4f6fb"],                 # ネムの毛（白）
    "glow": ["#3f8f8a", "#7fd1c0", "#c8f5e6", "#f2fff9"],      # B 案のネム（ほのかに光る羽）
    "iris": ["#16306e", "#2d5bc0", "#6aa2ee"],                  # C 案の目（青い瞳）
    "blush": ["#d98a86"],
    # 服のリメイク（E 案）
    "marine": ["#18234c", "#283a74", "#45609c"],               # ボーダーの紺
    "denim": ["#22345c", "#33507f", "#5677a8"],                # デニムのショートパンツ
    "slate": ["#1d2b46", "#2e4466", "#466189", "#5d7ba6", "#8eaad0"],  # 夜色のワンピース
    "chambray": ["#5a7397", "#88a2c4", "#b6cbe2", "#dde8f4"],  # 淡い青のシャツ
    # 部屋着（F 案）
    "pj": ["#5d6e92", "#8c9ec1", "#bccbe4", "#e3ebf7"],        # 淡い青のコットン（ワンピース・パジャマ）
    "knit": ["#34405e", "#4f5f84", "#7486ad", "#9fb0d2"],      # 薄手のカーディガン（灰青）
}


def P(name):
    ramp = name.rstrip("0123456789")
    table = RAMPS.get(ramp) or EXTRA[ramp]
    return hex_to_rgba(table[int(name[len(ramp):])])


# ================================================================ 描き方のしくみ
class Mat:
    """記号 1 つ分の素材。base が基本の色、shade が右下の影、light は縁の光（rim のとき）、line は selout の輪郭。"""

    def __init__(self, base, shade=None, light=None, line=None, group=None, d=1):
        self.base, self.shade, self.light, self.line = base, shade, light, line
        self.group, self.d = group, d


class Style:
    def __init__(self, outline="line", outline_color="hair0", rim=False):
        self.outline, self.outline_color, self.rim = outline, outline_color, rim


def render(rows, mats, direct, style):
    """記号の図 → 画像。
    - 陰影：素材ごとに「右下へ d ずらすと同じ部品（group）の外に出る所」を影にする（光は左上）。
    - rim：左か上が外（透明）の所を縁の光にする（月明かり）。
    - 輪郭：line は外側に 1 ドットの線。selout は隣の塗りの line の色。none は付けない。
    - X は中の線（部品の境目）。"""
    h, w = len(rows), len(rows[0])
    for i, r in enumerate(rows):
        assert len(r) == w, f"row {i} width {len(r)} != {w}: {r!r}"
    at = lambda x, y: rows[y][x] if 0 <= x < w and 0 <= y < h else "."  # noqa: E731
    img = Image.new("RGBA", (w, h), CLEAR)
    px = img.load()
    for y in range(h):
        for x in range(w):
            ch = rows[y][x]
            if ch == ".":
                continue
            if ch == "X":
                px[x, y] = P(style.outline_color) if style.outline != "selout" else P(_line_near(rows, x, y, mats))
                continue
            if ch in mats:
                m = mats[ch]
                group = m.group or ch
                c = m.base
                if m.shade and at(x + m.d, y + m.d) not in group:
                    c = m.shade
                if style.rim and m.light and (at(x - 1, y) == "." or at(x, y - 1) == "."):
                    c = m.light
                px[x, y] = P(c)
            elif ch in direct:
                c = direct[ch]
                if isinstance(c, tuple):  # (色, 不透明度)：ネムの羽の透ける所
                    r, g, b, _ = P(c[0])
                    px[x, y] = (r, g, b, c[1])
                else:
                    px[x, y] = P(c)
            else:
                raise ValueError(f"unknown symbol {ch!r}")
    outline_colors = []
    if style.outline != "none":
        src = img.copy().load()
        for y in range(h):
            for x in range(w):
                if rows[y][x] != ".":
                    continue
                near = [(nx, ny) for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                        if 0 <= nx < w and 0 <= ny < h and rows[ny][nx] != "." and src[nx, ny][3] > 0]
                if not near:
                    continue
                if style.outline == "line":
                    px[x, y] = P(style.outline_color)
                else:
                    px[x, y] = P(_line_near(rows, x, y, mats))
        outline_colors = ["#%02x%02x%02x" % P(n)[:3] for n in [style.outline_color] + [m.line for m in mats.values() if m.line]]
        img, _ = clean_corners(img, outline_colors)
    return img


def _line_near(rows, x, y, mats):
    """selout：隣にある塗りの中で、いちばん多い素材の輪郭の色（下・右を優先）。"""
    h, w = len(rows), len(rows[0])
    for nx, ny in ((x, y + 1), (x + 1, y), (x - 1, y), (x, y - 1), (x + 1, y + 1), (x - 1, y + 1)):
        if 0 <= nx < w and 0 <= ny < h:
            ch = rows[ny][nx]
            if ch in mats and mats[ch].line:
                return mats[ch].line
    return "hair0"


def mirror(rows, swap=None):
    """左右反転（右向き → 左向き）。陰影は反転のあとで付くので、光は左上のまま。"""
    out = [r[::-1] for r in rows]
    if swap:
        out = ["".join(swap.get(c, c) for c in r) for r in out]
    return out


def mirror_half(rows):
    return [r + r[::-1] for r in rows]


class Canvas:
    """大きな絵（顔グラフィック・ネム）用：図形を記号で塗り重ねて、記号の図を作る。"""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = [["."] * w for _ in range(h)]

    def _mask(self):
        return Image.new("L", (self.w, self.h), 0)

    def _apply(self, m, sym, only=None):
        mp = m.load()
        for y in range(self.h):
            for x in range(self.w):
                if mp[x, y] and (only is None or self.g[y][x] in only):
                    self.g[y][x] = sym

    def ellipse(self, box, sym, only=None):
        m = self._mask()
        ImageDraw.Draw(m).ellipse(box, fill=255)
        self._apply(m, sym, only)

    def poly(self, pts, sym, only=None):
        m = self._mask()
        ImageDraw.Draw(m).polygon(pts, fill=255)
        self._apply(m, sym, only)

    def rect(self, box, sym, only=None):
        m = self._mask()
        ImageDraw.Draw(m).rectangle(box, fill=255)
        self._apply(m, sym, only)

    def line(self, pts, sym, width=1, only=None):
        m = self._mask()
        ImageDraw.Draw(m).line(pts, fill=255, width=width)
        self._apply(m, sym, only)

    def stamp(self, rows, x0, y0, transparent="."):
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch != transparent and 0 <= x0 + x < self.w and 0 <= y0 + y < self.h:
                    self.g[y0 + y][x0 + x] = "." if ch == "_" else ch

    def mirror_x(self, center2):
        """左半分を右へ写す（center2 = 中心の x の 2 倍。偶数幅なら w-1）。"""
        for y in range(self.h):
            for x in range(self.w):
                mx = center2 - x
                if 0 <= mx < self.w and x < mx:
                    self.g[y][mx] = self.g[y][x]

    def rows(self):
        return ["".join(r) for r in self.g]


# ================================================================ 案 A「余白」
# 細い 3 頭身。小さな頭・長い脚・点の目。大きめの白い T シャツ（ワンピースのように腿まで）、はだしにサンダル。
# マフラーの端を胸の前に長く垂らす（いちばん目立つ色を 1 か所に集める）。
A_STYLE = Style("line", "hair0")
A_MATS = {
    "H": Mat("hair1", "hair0", d=2),
    "S": Mat("skin2", "skin1", group="SE"),
    "W": Mat("tee2", "tee1", group="WBcX", d=2),
    "B": Mat("scarf1", "scarf0", group="Bc"),
    "F": Mat("brown1", "brown0"),
}
A_DIRECT = {"E": "hair0", "h": "hair3", "c": "scarf2", "t": "tee3"}

A_DOWN = [
    "................",
    "................",
    "......HHHH......",
    "....HHHHHHHH....",
    "...HhhHHHHHHH...",
    "...HhHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHSSSSSSHH...",
    "...HHSESSESHH...",
    "...HHSSSSSSHH...",
    "...HHHSSSSHHH...",
    "...HH..SS..HH...",
    ".....BBBBBB.....",
    "....WcBBBBBW....",
    "...WtWBBWWWWW...",
    "...WWWBBWWWWW...",
    "...WWWBBWWWWW...",
    "...WWWBBWWWWW...",
    "...SXWBBWWWXS...",
    "...SXWBBWWWXS...",
    "...SXWBBWWWXS...",
    "...SXWWWWWWXS...",
    "....WWWWWWWW....",
    "....WWWWWWWW....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....FF..FF.....",
    "................",
]

A_UP = [
    "................",
    "................",
    "......HHHH......",
    "....HHHHHHHH....",
    "...HhhHHHHHHH...",
    "...HhHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    ".....BBBBBB.....",
    "....WcBBBBBW....",
    "...WtWWBBWWWW...",
    "...WWWWWWWWWW...",
    "...WWWWWWWWWW...",
    "...WWWWWWWWWW...",
    "...SXWWWWWWXS...",
    "...SXWWWWWWXS...",
    "...SXWWWWWWXS...",
    "...SXWWWWWWXS...",
    "....WWWWWWWW....",
    "....WWWWWWWW....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....FF..FF.....",
    "................",
]

A_RIGHT = [
    "................",
    "................",
    ".....HHHH.......",
    "...HHHHHHHH.....",
    "..HhhHHHHHHH....",
    "..HhHHHHHHHHH...",
    "..HHHHHHHHHHH...",
    "..HHHHHHHSSSS...",
    "..HHHHHHHSSES...",
    "..HHHHHHHSSSS...",
    "..HHHHHHHSSS....",
    "...HHHH.SS......",
    "...BBBBBBBB.....",
    ".BBc.WWWWW......",
    ".B..WtWWWWW.....",
    "....WWWWWWW.....",
    "....WWWWWWW.....",
    "....WWWWWWW.....",
    "....WWWWWWW.....",
    "....WWWWWWW.....",
    "....WWWWWWW.....",
    "....WWWWWWW.....",
    "....WWWWWWW.....",
    ".....WWWWWW.....",
    "......SS........",
    "......SS........",
    "......SS........",
    "......SS........",
    "......SS........",
    "......SS........",
    "......FFF.......",
    "................",
]

# 歩き（下向きの 1 コマ）：片足を前に出して少し上げる
A_DOWN_STEP = A_DOWN[:24] + [
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....SS..FF.....",
    ".....SS.........",
    ".....FF.........",
    "................",
]

A_RIGHT_STEP = A_RIGHT[:24] + [
    ".....SS.SS......",
    ".....SS.SS......",
    "....SS...SS.....",
    "....SS...SS.....",
    "...SS.....SS....",
    "...SS.....SS....",
    "..FF......FFF...",
    "................",
]


def a_portrait():
    """A 案の顔グラフィック（48x48）：細い首、切りそろえた前髪のボブ、小さな目。口はほとんど描かない。"""
    c = Canvas(48, 48)
    # 肩と T シャツ
    c.poly([(6, 47), (10, 40), (18, 37), (30, 37), (38, 40), (42, 47)], "W")
    # 首
    c.rect((20, 30, 27, 39), "S")
    # マフラー（首に巻いて、胸の左に垂らす）
    c.poly([(15, 35), (19, 32), (29, 32), (33, 35), (31, 39), (17, 39)], "B")
    c.poly([(17, 37), (22, 37), (23, 47), (16, 47)], "B")
    c.stamp(["cc", "c."], 18, 36)
    # 後ろ髪（あごの線で切りそろえたボブ）
    c.ellipse((9, 4, 39, 34), "H")
    c.rect((10, 18, 38, 33), "H")
    # 顔
    c.ellipse((13, 10, 35, 35), "S")
    # 前髪（まっすぐ切りそろえる）
    c.ellipse((11, 5, 37, 22), "H", only="S.")
    c.rect((13, 14, 35, 19), "H")
    c.rect((13, 20, 15, 31), "H")   # 横髪（顔の左右にかかる）
    c.rect((33, 20, 35, 31), "H")
    # 目（たて 3 ドット。光は左上：つやは左上）
    eye = ["Ee", "EE", "EE"]
    c.stamp(eye, 19, 23)
    c.stamp(eye, 27, 23)
    c.stamp(["m"], 24, 31)
    # 髪のつや（左上に短い線）
    c.stamp(["hhh", "h.."], 15, 9)
    rows = c.rows()
    mats = dict(A_MATS)
    mats["W"] = Mat("tee2", "tee1", group="WBc", d=3)
    mats["H"] = Mat("hair1", "hair0", d=3)
    mats["S"] = Mat("skin2", "skin1", group="SEem", d=2)
    mats["B"] = Mat("scarf1", "scarf0", group="Bc", d=2)
    direct = dict(A_DIRECT, e="moon3", m="skin0")
    return render(rows, mats, direct, A_STYLE)


# ---------------------------------------------------------------- ネム A：羽だけで見せる、点の目
NEMU_A_KEY = {
    "W": Mat("moth3", "moth2", group="WLC", d=2),
    "V": Mat("moth3", "moth2", group="VL", d=2),     # 後ろ羽（前羽と別の部品）
    "F": Mat("fluff2", "fluff1", group="FE", d=1),
}


def nemu_a_sprite():
    """ゲーム内（16x18）：三角の大きな前羽と、長い尾。体は 2 ドット、目は描かない（小さすぎるので形だけ）。"""
    half = [
        "........",
        ".....a..",
        "......a.",
        ".......F",
        "WWW....F",
        ".WWWWWWF",
        ".WWWWWWF",
        "..WWWWWF",
        "..WWWWWF",
        "...WWWWF",
        "....VVVF",
        "....VVV.",
        "....VVV.",
        ".....VV.",
        ".....V..",
        ".....V..",
        ".....y..",
        "........",
    ]
    rows = mirror_half(half)
    direct = {"a": "warm4", "y": "warm4", "C": "brown2"}
    style = Style("line", "moth0")
    return render(rows, NEMU_A_KEY, direct, style)


def nemu_a_portrait():
    """顔グラフィック（48x48）：羽を大きく、体と頭は小さく。目は黒い点 2 つ、口はない。"""
    c = Canvas(48, 48)
    cx2 = 47
    # 左半分を描いて右へ写す
    c.poly([(23, 14), (2, 6), (0, 9), (6, 22), (14, 27), (23, 25)], "W")      # 前羽
    c.poly([(23, 25), (14, 27), (10, 33), (13, 38), (19, 37), (23, 31)], "V")  # 後ろ羽
    c.line([(14, 36), (11, 41), (12, 46)], "V", width=2)                       # 尾
    c.line([(3, 7), (22, 14)], "C", width=2)                                   # 前羽の前のふちの赤茶の帯
    c.ellipse((12, 15, 16, 19), "y")                                           # 目玉模様
    c.ellipse((13, 16, 15, 18), "M")
    c.ellipse((15, 30, 18, 33), "y")
    c.stamp(["M"], 16, 31)
    c.stamp(["yy"], 11, 45)
    c.mirror_x(cx2)
    # 体（細い）と頭（小さい）
    c.rect((22, 18, 25, 36), "F")
    c.ellipse((20, 11, 27, 19), "F")
    c.line([(22, 12), (17, 4), (14, 3)], "a")
    c.line([(25, 12), (30, 4), (33, 3)], "a")
    c.stamp(["E"], 21, 15)
    c.stamp(["E"], 26, 15)
    rows = c.rows()
    mats = dict(NEMU_A_KEY)
    mats["W"] = Mat("moth3", "moth2", group="WCyM", d=3)
    mats["V"] = Mat("moth3", "moth2", group="VyM", d=3)
    direct = {"a": "warm4", "y": "warm4", "C": "brown2", "M": ("moon3", 140), "E": "night0"}
    return render(rows, mats, direct, Style("line", "moth0"))


# ================================================================ 案 B「月明かり」（輪郭線なし）
# 2.5 頭身。輪郭線を引かず、明暗の差と左上の縁の光（月明かり）で形を見せる。
# 大きめのパーカー（そでが手までかかる）、短パン、スニーカー。肩までの髪で、前髪を斜めに流して片目に少しかける。
B_STYLE = Style("none", "hood0", rim=True)
B_MATS = {
    "H": Mat("teal1", "teal0", "teal3", d=2),
    "S": Mat("skin2", "skin1", group="SEm"),
    "W": Mat("hood1", "hood0", "hood3", group="Wxw", d=2),
    "B": Mat("scarf1", "scarf0", "scarf2", group="B"),
    "K": Mat("night3", "night2", "night5"),
    "T": Mat("stone7", "stone5", group="T"),
    "F": Mat("stone6", "stone4", "stone7"),
}
B_DIRECT = {"E": "night0", "x": "hood0", "w": "hood0", "m": "skin0"}

B_DOWN = [
    "................",
    "................",
    "......HHHH......",
    "....HHHHHHHH....",
    "...HHHHHHHHHH...",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHSSHH..",
    "..HHHHHHSSSSHH..",
    "..HHHHSESSESHH..",
    "..HHHHSSSSSSHH..",
    "..HHHSSSSSSSHH..",
    "..HHHHSSSSHHHH..",
    "..HHHBBBBBBHHH..",
    "..HHWBBBBBBWHH..",
    "..WWWWBBBBWWWW..",
    "..WWxWWBBWWxWW..",
    "..WWxWWWWWWxWW..",
    "..WWxWWWWWWxWW..",
    "..WWxWWWWWWxWW..",
    "..WWxxxxxxxxWW..",
    "..wwWWWWWWWWww..",
    "...WWWWWWWWWW...",
    "....KKKKKKKK....",
    "....KKK..KKK....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....TT..TT.....",
    ".....TT..TT.....",
    "....FFF..FFF....",
    "....FFF..FFF....",
    "................",
]

B_UP = [
    "................",
    "................",
    "......HHHH......",
    "....HHHHHHHH....",
    "...HHHHHHHHHH...",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHBBBBBBHHH..",
    "..HHWWWWWWWWHH..",
    "..WWWwwwwwwWWW..",
    "..WWxWwwwwWxWW..",
    "..WWxWWWWWWxWW..",
    "..WWxWWWWWWxWW..",
    "..WWxWWWWWWxWW..",
    "..WWxWWWWWWxWW..",
    "..wwWWWWWWWWww..",
    "...WWWWWWWWWW...",
    "....KKKKKKKK....",
    "....KKK..KKK....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....TT..TT.....",
    ".....TT..TT.....",
    "....FFF..FFF....",
    "....FFF..FFF....",
    "................",
]

B_RIGHT = [
    "................",
    "................",
    ".....HHHH.......",
    "...HHHHHHHH.....",
    "..HHHHHHHHHH....",
    ".HHHHHHHHHHHH...",
    ".HHHHHHHHHHHHH..",
    ".HHHHHHHHHHHHH..",
    ".HHHHHHHHSSSS...",
    ".HHHHHHHSSSES...",
    ".HHHHHHHSSSSS...",
    ".HHHHHHHHSSS....",
    "..HHHHHHHSS.....",
    "..HHHHBBBBB.....",
    "...WWWBBBBWW....",
    "...WWWWWWWWW....",
    "...WWWWxWWWW....",
    "...WWWWxWWWW....",
    "...WWWWxWWWW....",
    "...WWWWxWWWW....",
    "...WWWWxWWWW....",
    "...WWWWwwwWW....",
    "...WWWWWWWWW....",
    "....KKKKKK......",
    ".....KKKK.......",
    "......SS........",
    "......SS........",
    "......TT........",
    "......TT........",
    "......FFFF......",
    "......FFFF......",
    "................",
]

B_DOWN_STEP = B_DOWN[:23] + [
    "....KKKKKKKK....",
    "....KKK..KKK....",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....TT..TT.....",
    ".....TT..FFF....",
    "....FFF..FFF....",
    "....FFF.........",
    "................",
]

B_RIGHT_STEP = B_RIGHT[:23] + [
    "....KKKKKK......",
    "....KKKKKK......",
    "....SS...SS.....",
    "...SS....SS.....",
    "...TT.....TT....",
    "..TT......TT....",
    ".FFF......FFFF..",
    ".FF.......FFFF..",
    "................",
]


def b_portrait():
    """B 案の顔グラフィック：パーカーのフード、斜めに流した前髪、細めの目。輪郭線なし、左上の縁に月明かり。"""
    c = Canvas(48, 48)
    c.poly([(3, 47), (7, 40), (15, 35), (33, 35), (41, 40), (45, 47)], "W")
    c.ellipse((11, 31, 37, 43), "W")                 # 首のまわりにたまったフード
    c.ellipse((15, 34, 33, 41), "w")
    c.rect((20, 29, 27, 37), "S")
    c.poly([(15, 33), (19, 30), (29, 30), (33, 33), (30, 37), (18, 37)], "B")
    c.poly([(26, 35), (31, 35), (32, 47), (26, 47)], "B")
    c.ellipse((8, 4, 40, 34), "H")
    c.poly([(9, 18), (39, 18), (40, 39), (35, 36), (31, 40), (29, 32), (19, 32), (17, 40), (13, 36), (8, 39)], "H")
    c.ellipse((14, 11, 34, 35), "S")
    # 前髪：右上から左下へ流す（向かって左の目に少しかかる）
    c.poly([(10, 7), (38, 7), (36, 17), (31, 14), (26, 17), (21, 20), (18, 25), (15, 30), (12, 24)], "H", only="S.H")
    c.stamp(["EEEE", "eIIE"], 27, 24)                # 目（細め）：つやは左上
    c.stamp(["EE", "IE"], 20, 24)                    # 向かって左の目は前髪の下からのぞく
    c.stamp(["mm"], 23, 31)
    rows = c.rows()
    mats = dict(B_MATS)
    mats["H"] = Mat("teal1", "teal0", "teal3", d=3)
    mats["W"] = Mat("hood1", "hood0", "hood3", group="W", d=3)
    mats["w"] = Mat("hood0", None, None)
    mats["S"] = Mat("skin2", "skin1", group="SEIem", d=2)
    mats["B"] = Mat("scarf1", "scarf0", "scarf2", d=2)
    direct = dict(B_DIRECT, I="teal2", e="moon3")
    direct.pop("w")
    return render(rows, mats, direct, B_STYLE)


def nemu_b_sprite():
    """ゲーム内（20x18）：輪郭なしで、羽がほのかに光る。丸くふわふわの体、ゆるく曲がる長い尾。"""
    c = Canvas(20, 18)
    c.poly([(9, 6), (5, 2), (0, 1), (0, 5), (2, 9), (9, 10)], "W")
    c.poly([(9, 10), (5, 11), (3, 13), (5, 14), (9, 13)], "V")
    c.line([(4, 14), (2, 16)], "V")
    c.stamp(["y"], 4, 5)
    c.line([(1, 1), (8, 5)], "C")
    c.mirror_x(19)
    c.ellipse((8, 4, 11, 12), "F")
    c.stamp(["a....a", ".a..a."], 7, 1)
    c.stamp(["EE"], 9, 5)
    mats = {
        "W": Mat("glow2", "glow1", "glow3", group="WyC", d=2),
        "V": Mat("glow2", "glow1", "glow3", group="Vy", d=1),
        "F": Mat("fluff2", "fluff1", "fluff2", group="FE"),
    }
    return render(c.rows(), mats, {"a": "warm4", "y": "warm4", "C": "brown2", "E": "night0"}, Style("none", rim=True))


def nemu_b_portrait():
    """顔グラフィック：羽のふちを明るく（光が透ける）、体は丸い毛のかたまり。目は大きな黒い楕円 2 つ。口はない。"""
    c = Canvas(48, 48)
    c.poly([(23, 17), (12, 6), (2, 5), (0, 10), (3, 20), (11, 27), (23, 27)], "W")
    c.poly([(23, 27), (13, 28), (9, 34), (12, 39), (19, 38), (23, 33)], "V")
    c.line([(13, 38), (9, 42), (10, 45), (13, 47)], "V", width=2)
    c.line([(3, 6), (21, 16)], "C", width=2)
    c.ellipse((11, 15, 16, 20), "y")
    c.ellipse((12, 16, 15, 19), "M")
    c.ellipse((14, 31, 18, 35), "y")
    c.stamp(["MM"], 15, 32)
    c.mirror_x(47)
    c.ellipse((19, 16, 28, 28), "F")                 # 胸のふわふわ
    c.ellipse((21, 26, 26, 37), "F")                 # 腹
    c.ellipse((18, 8, 29, 18), "F")                  # 頭
    c.line([(21, 9), (16, 3), (12, 2)], "a", width=2)
    c.line([(26, 9), (31, 3), (35, 2)], "a", width=2)
    c.stamp(["EEE", "eEE", "EEE"], 19, 11)
    c.stamp(["EEE", "eEE", "EEE"], 26, 11)
    mats = {
        "W": Mat("glow2", "glow1", "glow3", group="WCyM", d=3),
        "V": Mat("glow2", "glow1", "glow3", group="VyM", d=3),
        "F": Mat("fluff2", "fluff1", "fluff2", group="FEe", d=2),
    }
    direct = {"a": "warm4", "y": "warm4", "C": "brown2", "M": ("glow3", 140), "E": "night0", "e": "fluff1"}
    return render(c.rows(), mats, direct, Style("none", rim=True))


# ================================================================ 案 C「描きこみ」（selout・大きな目）
# 2 頭身。大きな頭と、つやのある青い目。輪郭は塗りの色を暗くした線（selout）で、紺の線より柔らかい。
# 夏のワンピースに薄いカーディガン。長い髪を一本の三つ編みにして、右肩（向かって左）から前へ垂らす。
C_STYLE = Style("selout", "hair0")
C_MATS = {
    "H": Mat("hair2", "hair1", line="hair0", group="Hh", d=2),
    "S": Mat("skin2", "skin1", line="skin0", group="SEeIrm"),
    "C": Mat("cardi2", "cardi1", line="cardi0", group="CX", d=2),
    "D": Mat("dress1", "dress0", line="hair0", group="D", d=2),
    "B": Mat("scarf1", "scarf0", line="hair0", group="Bc"),
    "T": Mat("stone7", "stone5", line="stone3"),
    "F": Mat("brown2", "brown1", line="brown0"),
}
C_DIRECT = {"E": "hair0", "e": "moon3", "I": "iris1", "r": "blush0", "m": "skin0", "h": "hair3", "c": "scarf2"}

C_DOWN = [
    "....................",
    ".......HHHHHH.......",
    ".....HHHHHHHHHH.....",
    "....HHhhHHHHHHHH....",
    "...HHhhHHHHHHHHHH...",
    "...HHhHHHHHHHHHHH...",
    "...HHHHHHHHHHHHHH...",
    "...HHHHSHHHHSHHHH...",
    "...HHHSSSHHSSSHHH...",
    "...HHSSSSSSSSSSHH...",
    "...HHSSEESSEESSHH...",
    "...HHSSeISSeISSHH...",
    "...HHSSIISSIISSHH...",
    "...HHSrSSSSSSrSHH...",
    "...HHHSSSSmSSSHHH...",
    "....HHHSSSSSSHHH....",
    "...HH.BBBBBBBB......",
    "...HHCCBBBBBBCC.....",
    "...HHCCDBBBBDCC.....",
    "...HHCCDDBBDDCC.....",
    "...ccCCDDBBDDCC.....",
    "...HHCCDDDDDDCC.....",
    "....HCCDDDDDDCC.....",
    ".....SSDDDDDDSS.....",
    ".....DDDDDDDDDD.....",
    "....DDDDDDDDDDDD....",
    ".......SS..SS.......",
    ".......SS..SS.......",
    ".......SS..SS.......",
    ".......TT..TT.......",
    "......FFF..FFF......",
    "....................",
]

C_UP = [
    "....................",
    ".......HHHHHH.......",
    ".....HHHHHHHHHH.....",
    "....HHhhHHHHHHHH....",
    "...HHhhHHHHHHHHHH...",
    "...HHhHHHHHHHHHHH...",
    "...HHHHHHHHHHHHHH...",
    "...HHHHHHHHHHHHHH...",
    "...HHHHHHHHHHHHHH...",
    "...HHHHHHHHHHHHHH...",
    "...HHHHHHHHHHHHHH...",
    "...HHHHHHHHHHHHHH...",
    "...HHHHHHHHHHHHHH...",
    "...HHHHHHHHHHHHHH...",
    "...HHHHHHHHHHHHHH...",
    "....HHHHHHHHHHHH....",
    "......BBBBBBBB.HH...",
    ".....CCCCCCCCCCHH...",
    ".....CCCCCCCCCCHH...",
    ".....CCCCCCCCCCHH...",
    ".....CCCCCCCCCCcc...",
    ".....CCCCCCCCCCHH...",
    ".....CCCCCCCCCCH....",
    ".....SSCCCCCCSS.....",
    ".....DDDDDDDDDD.....",
    "....DDDDDDDDDDDD....",
    ".......SS..SS.......",
    ".......SS..SS.......",
    ".......SS..SS.......",
    ".......TT..TT.......",
    "......FFF..FFF......",
    "....................",
]

C_RIGHT = [
    "....................",
    "......HHHHHH........",
    "....HHHHHHHHHH......",
    "...HHhhHHHHHHHH.....",
    "..HHhhHHHHHHHHHH....",
    "..HHhHHHHHHHHHHHH...",
    "..HHHHHHHHHHHHHHH...",
    "..HHHHHHHHHHHHSHH...",
    "..HHHHHHHHHHSSSSH...",
    "..HHHHHHHHHSSSSSS...",
    "..HHHHHHHHHSSSEES...",
    "..HHHHHHHHHSSSeIS...",
    "..HHHHHHHHHSSSIIS...",
    "..HHHHHHHHHSSrSSS...",
    "..HHHHHHHHHHSSSm....",
    "...HHHHHHHHHSSS.....",
    "...HHHHHBBBBBB......",
    "....HHCCCCBBBCC.....",
    "....HHCCCCDDDCC.....",
    "....HHCCCCDDDCC.....",
    "....ccCCXCDDDCC.....",
    "....HHCCXCDDDCC.....",
    ".....HCCXCDDDCC.....",
    "......CCSSDDDCC.....",
    "......DDDDDDDDD.....",
    ".....DDDDDDDDDDD....",
    ".........SS.........",
    ".........SS.........",
    ".........SS.........",
    ".........TT.........",
    ".........FFFF.......",
    "....................",
]

C_DOWN_STEP = C_DOWN[:26] + [
    ".......SS..SS.......",
    ".......SS..SS.......",
    ".......SS..TT.......",
    ".......TT.FFF.......",
    "......FFF...........",
    "....................",
]

C_RIGHT_STEP = C_RIGHT[:26] + [
    "........SS.SS.......",
    ".......SS...SS......",
    "......SS.....SS.....",
    "......TT.....TT.....",
    ".....FFF.....FFFF...",
    "....................",
]


def c_portrait():
    """C 案の顔グラフィック：大きな目（青い瞳・左上のつや）、前髪の毛先、三つ編み、紺のカーディガン。"""
    c = Canvas(48, 48)
    c.ellipse((7, 3, 41, 37), "H")
    c.rect((8, 18, 40, 40), "H")                     # 背中へ流れる長い髪
    c.poly([(3, 47), (7, 41), (15, 37), (33, 37), (41, 41), (45, 47)], "C")
    c.poly([(18, 37), (30, 37), (24, 47)], "D")
    c.rect((20, 31, 27, 39), "S")
    c.poly([(14, 35), (18, 31), (30, 31), (34, 35), (31, 39), (17, 39)], "B")
    c.poly([(21, 37), (26, 37), (25, 46), (20, 46)], "B")
    c.ellipse((13, 10, 35, 36), "S")
    c.ellipse((9, 4, 39, 22), "H", only="S.")
    # 前髪の毛先（顔へ下りる三角）
    for pts in ([(13, 18), (19, 18), (15, 26)], [(18, 18), (25, 18), (21, 24)], [(23, 18), (30, 18), (27, 25)],
                [(29, 18), (35, 18), (33, 27)]):
        c.poly(pts, "H")
    # 三つ編み（向かって左の肩から前へ）：ひと房ごとに記号を変えて、房ごとに影がつくようにする
    c.rect((0, 29, 15, 47), ".", only="H")            # 三つ編みのうしろの髪を消して、編み目を浮かせる
    c.stamp([                                         # 編み目が左右に交互に重なる
        ".HHHH...",
        "HHHHHH..",
        "HHHHJJJ.",
        ".HJJJJJ.",
        "..JJJJJJ",
        ".HHJJJJ.",
        "HHHHHJ..",
        "HHHHHH..",
        ".HHJJJ..",
        "..JJJJJ.",
        ".HHJJJ..",
        ".HHHH...",
        ".cccc...",                                   # 髪をまとめるリボン（マフラーと同じ青）
        "..HHH...",
        "..HHHH..",
        "...HH...",
    ], 12, 31)
    eye = [
        ".EEEE.",
        "EEeiiE",
        "EeeiIE",
        "EiIIIE",
        ".iIoI.",
    ]
    c.stamp(eye, 16, 22)
    c.stamp(eye, 26, 22)
    c.stamp(["rr"], 15, 29)
    c.stamp(["rr"], 31, 29)
    c.stamp(["mm"], 23, 32)
    c.stamp(["hhh", "hh."], 14, 8)
    mats = dict(C_MATS)
    mats["H"] = Mat("hair2", "hair1", line="hair0", group="Hh", d=3)
    mats["J"] = Mat("hair2", "hair1", line="hair0", group="J", d=2)
    mats["S"] = Mat("skin2", "skin1", line="skin0", group="SEeiIor", d=2)
    mats["C"] = Mat("cardi2", "cardi1", line="cardi0", d=3)
    mats["D"] = Mat("dress1", "dress0", line="hair0", d=2)
    mats["B"] = Mat("scarf1", "scarf0", line="hair0", group="Bc", d=2)
    direct = dict(C_DIRECT, i="iris0", I="iris1", o="iris2")
    return render(c.rows(), mats, direct, C_STYLE)


def nemu_c_sprite():
    """ゲーム内（20x20）：大きな頭に、つやのある目。白い毛の襟、羽の筋と目玉模様。"""
    c = Canvas(20, 20)
    c.poly([(9, 8), (5, 4), (0, 3), (0, 7), (3, 11), (9, 11)], "W")
    c.poly([(9, 11), (5, 12), (4, 15), (6, 16), (9, 14)], "V")
    c.line([(5, 15), (4, 18), (5, 19)], "V")
    c.line([(1, 3), (8, 7)], "C")
    c.stamp(["y"], 4, 7)
    c.stamp(["y"], 6, 13)
    c.line([(3, 9), (8, 10)], "v")
    c.mirror_x(19)
    c.ellipse((6, 6, 13, 13), "F")
    c.ellipse((7, 11, 12, 16), "F")
    c.stamp(["a......a", ".a....a.", "..a..a.."], 6, 1)
    c.stamp(["EE..EE", "eE..eE"], 7, 7)
    mats = {
        "W": Mat("moth3", "moth2", line="moth0", group="WCyv", d=2),
        "V": Mat("moth3", "moth2", line="moth0", group="Vy", d=1),
        "F": Mat("fluff2", "fluff1", line="fluff0", group="FEe"),
    }
    direct = {"a": "warm4", "y": "warm4", "C": "brown2", "E": "night0", "e": "moon3", "v": "moth2"}
    return render(c.rows(), mats, direct, Style("selout", "moth0"))


def nemu_c_portrait():
    """顔グラフィック：ふわふわの大きな頭、つやのある大きな黒い目、くし形の触角。羽には筋と目玉模様。口はない。"""
    c = Canvas(48, 48)
    c.poly([(23, 18), (12, 8), (1, 6), (0, 12), (4, 22), (12, 28), (23, 28)], "W")
    c.poly([(23, 28), (13, 29), (9, 35), (12, 40), (19, 39), (23, 34)], "V")
    c.line([(13, 39), (10, 43), (12, 47)], "V", width=2)
    c.line([(2, 7), (21, 17)], "C", width=2)
    c.line([(6, 20), (20, 24)], "v")
    c.line([(10, 12), (19, 22)], "v")
    c.ellipse((10, 16, 16, 22), "y")
    c.ellipse((11, 17, 15, 21), "c")
    c.ellipse((12, 18, 14, 20), "M")
    c.ellipse((14, 32, 19, 37), "y")
    c.stamp(["MM"], 16, 34)
    c.mirror_x(47)
    c.ellipse((16, 20, 31, 33), "F")                 # 毛の襟
    c.ellipse((20, 30, 27, 42), "F")
    c.ellipse((14, 7, 33, 24), "F")                  # 大きな頭
    # くし形の触角（羽毛のよう）
    c.line([(19, 8), (14, 2), (10, 1)], "a", width=2)
    c.line([(28, 8), (33, 2), (37, 1)], "a", width=2)
    c.stamp(["A.A.A"], 11, 3)
    c.stamp(["A.A.A"], 32, 3)
    eye = [".EEE.", "EeeEE", "EeEEE", "EEEEE", ".EEo."]
    c.stamp(eye, 17, 13)
    c.stamp(eye, 26, 13)
    mats = {
        "W": Mat("moth3", "moth2", line="moth0", group="WCycMv", d=3),
        "V": Mat("moth3", "moth2", line="moth0", group="VyM", d=3),
        "F": Mat("fluff2", "fluff1", line="fluff0", group="FEeo", d=2),
    }
    direct = {"a": "warm4", "A": "brown2", "y": "warm4", "c": "brown1", "C": "brown2", "M": ("moon3", 140),
              "E": "night0", "e": "moon3", "o": "night3", "v": "moth2"}
    return render(c.rows(), mats, direct, Style("selout", "moth0"))


# ================================================================ 案 D「月明かり＋青い目」（B をもとに、C の色と目）
# ユーザーの指定：B が中心。C の色合い（紺の髪・クリームの服・淡い青・ほおの赤み）と大きな青い目を入れる。
# 静かで大人っぽいのに、まだあどけなさが残る感じ。ネムは B のまま。
# - 輪郭線なし、左上の縁に月明かり（B）。髪は紺（C）で、縁の光は明るい紺。
# - 目は大きく、瞳は上が濃く下が明るい青、つやは左上（C）。まぶたの線は平らにして、見開かない（静かさ）。
# - 頭を B より 1〜2 ドット大きく、ほおに小さな赤み（あどけなさ）。前髪は斜めに流すが、目は隠さない（先が少し触れる程度）。
# - 服：クリーム色の大きめのパーカー（そでが手にかかる）、淡い青のスカート、白い靴下、茶色の靴。
D_STYLE = Style("none", "cardi1", rim=True)
D_MATS = {
    "H": Mat("hair2", "hair1", "hair3", d=2),
    "S": Mat("skin2", "skin1", group="SEeiIor"),
    "W": Mat("cardi2", "cardi1", "cardi3", group="Wxw", d=2),
    "B": Mat("scarf1", "scarf0", "scarf2", group="B"),
    "K": Mat("dress1", "dress0", "dress2", d=1),
    "T": Mat("stone7", "stone5", group="T"),
    "F": Mat("brown2", "brown1"),
}
D_DIRECT = {"E": "hair0", "e": "moon3", "i": "iris0", "I": "iris1", "o": "iris2", "r": "blush0",
            "x": "cardi1", "w": "cardi1", "m": "skin0"}

D_DOWN = [
    "................",
    "................",
    "...H..HHHH..H...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHSHH..",
    "..HHHHHHHSSSHH..",
    "..HHHEESSEESHH..",
    "..HHSeISSeISHH..",
    "..HHSIISSIISHH..",
    "..HHSrSSSSrSHH..",
    "..HHHSSSSSSHHH..",
    "..HHHHHSSHHHHH..",
    "..HHHBBBBBBHHH..",
    "..HHWBBBBBBWHH..",
    "..WWWWBBBBWWWW..",
    "..WWxWWBBWWxWW..",
    "..WWxWWWWWWxWW..",
    "..WWxWWWWWWxWW..",
    "..WWxxxxxxxxWW..",
    "..wwWWWWWWWWww..",
    "...WWWWWWWWWW...",
    "....KKKKKKKK....",
    "...KKKKKKKKKK...",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....TT..TT.....",
    ".....TT..TT.....",
    "....FFF..FFF....",
    "................",
]

D_UP = [
    "................",
    "................",
    "...H..HHHH..H...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHBBBBBBHHH..",
    "..HHWWWWWWWWHH..",
    "..WWWwwwwwwWWW..",
    "..WWxWwwwwWxWW..",
    "..WWxWWWWWWxWW..",
    "..WWxWWWWWWxWW..",
    "..WWxWWWWWWxWW..",
    "..wwWWWWWWWWww..",
    "...WWWWWWWWWW...",
    "....KKKKKKKK....",
    "...KKKKKKKKKK...",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....TT..TT.....",
    ".....TT..TT.....",
    "....FFF..FFF....",
    "................",
]

D_RIGHT = [
    "................",
    "................",
    "..H..HHHH..H....",
    "..HHHHHHHHHH....",
    "..HHHHHHHHHH....",
    ".HHHHHHHHHHHH...",
    ".HHHHHHHHHHHHH..",
    ".HHHHHHHHHHHHH..",
    ".HHHHHHHHHSSSS..",
    ".HHHHHHHHSSEES..",
    ".HHHHHHHHSSeIS..",
    ".HHHHHHHHSSIIS..",
    ".HHHHHHHHSrSSS..",
    ".HHHHHHHHHSSS...",
    "..HHHHHHHSS.....",
    "..HHHHBBBBB.....",
    "...WWWBBBBWW....",
    "...WWWWWWWWW....",
    "...WWWWxWWWW....",
    "...WWWWxWWWW....",
    "...WWWWxWWWW....",
    "...WWWWxWWWW....",
    "...WWWWwwwWW....",
    "...WWWWWWWWW....",
    "....KKKKKK......",
    "...KKKKKKKK.....",
    "......SS........",
    "......SS........",
    "......TT........",
    "......TT........",
    "......FFFF......",
    "................",
]

D_DOWN_STEP = D_DOWN[:24] + [
    "....KKKKKKKK....",
    "...KKKKKKKKKK...",
    ".....SS..SS.....",
    ".....SS..SS.....",
    ".....TT..TT.....",
    ".....TT..FFF....",
    "....FFF.........",
    "................",
]

D_RIGHT_STEP = D_RIGHT[:24] + [
    "....KKKKKK......",
    "...KKKKKKKK.....",
    "....SS...SS.....",
    "...SS....SS.....",
    "...TT.....TT....",
    "..TT......TT....",
    ".FFF......FFFF..",
    "................",
]

# 顔グラフィックの目（6x6）。どちらの目も、つやは左上。表情ごとに目と口を入れかえる。
# 左右で形が変わる表情（かなしい）は (向かって左, 向かって右) の組で書く（目じりが外側）。
D_EYES = {
    "normal": [".EEEE.", "EeeiiE", "EeiiIE", ".iIIo.", ".iIoI.", "..II.."],
    "smile": ["......", ".EEEE.", "EeeiiE", "EeiIIE", ".iIoI.", "......"],    # 下まぶたが少し上がる（静かなほほえみ）
    "sad": (["......", "..EEEE", "EEeii.", ".eiII.", ".iIoI.", "..II.."],      # 目じりが下がる伏し目
            ["......", "EEEE..", ".eeiEE", ".eiII.", ".iIoI.", "..II.."]),
    "surprised": [".EEEE.", "EeeiiE", "EeiIIE", "EiIIoE", ".IIoI.", "..II.."],  # 少し見開く
}
D_MOUTHS = {"normal": ["mm"], "smile": ["n..n", ".mm."], "sad": [".m."], "surprised": ["mm", "mm"]}


def hoodie_torso(c):
    c.poly([(3, 47), (7, 40), (15, 35), (33, 35), (41, 40), (45, 47)], "W")
    c.ellipse((11, 31, 37, 43), "W")                 # 首のまわりにたまったフード
    c.ellipse((15, 34, 33, 41), "w")


def d_portrait(expr="normal", torso=hoodie_torso, outfit_mats=None, outfit_direct=None):
    """D 案の顔グラフィック：B の形（フード・斜めの前髪・輪郭線なし・月明かり）に、C の色と大きな青い目。
    torso で首から下（服）を差しかえる（E 案）。"""
    c = Canvas(48, 48)
    torso(c)
    c.rect((20, 29, 27, 37), "S")
    c.poly([(15, 33), (19, 30), (29, 30), (33, 33), (30, 37), (18, 37)], "B")
    c.poly([(26, 35), (31, 35), (32, 47), (26, 47)], "B")
    c.ellipse((8, 3, 40, 34), "H")
    c.poly([(9, 18), (39, 18), (40, 39), (35, 36), (31, 40), (29, 32), (19, 32), (17, 40), (13, 36), (8, 39)], "H")
    c.ellipse((13, 10, 35, 36), "S")                 # B より少し丸く大きい顔（あどけなさ）
    # 前髪：右上から左下へ流す。先が向かって左の目に少し触れる
    # 上の辺は頭の丸より左右に少し広い。はみ出した所が左右の小さな角＝猫の耳のような寝ぐせ（チャームポイント。消さないこと）
    c.poly([(10, 6), (38, 6), (36, 16), (31, 14), (26, 17), (21, 20), (17, 22), (14, 28), (12, 22)], "H", only="S.H")
    c.stamp(["hh.", "h.."], 14, 9)                   # 髪のつや（左上）
    eyes = D_EYES[expr]
    left, right = eyes if isinstance(eyes, tuple) else (eyes, eyes)
    c.stamp(left, 16, 22)
    c.stamp(right, 26, 22)
    c.stamp(["rr"], 15, 29)
    c.stamp(["rr"], 31, 29)
    mouth = D_MOUTHS[expr]
    c.stamp(mouth, 24 - len(mouth[0]) // 2, 32)
    mats = dict(D_MATS)
    mats["H"] = Mat("hair2", "hair1", "hair3", group="Hh", d=3)
    mats["W"] = Mat("cardi2", "cardi1", "cardi3", group="W", d=3)
    mats["w"] = Mat("cardi1", None, None)
    mats["S"] = Mat("skin2", "skin1", group="SEeiIormn", d=2)
    mats["B"] = Mat("scarf1", "scarf0", "scarf2", d=2)
    direct = dict(D_DIRECT, h="hair3", n="skin1")
    direct.pop("w")
    mats.update(outfit_mats or {})
    direct.update(outfit_direct or {})
    return render(c.rows(), mats, direct, D_STYLE)


# ================================================================ 案 E：D の服をリメイク（3 種）
# ユーザー：「服がダサい。世界線と年齢層に合わせて魅力的な服に」。頭（髪・目・マフラー）は D のまま、首から下を描き直す。
# 世界線：晩夏の港町、夜中の 3 時に眠れずに家を出た 14 歳。部屋着ではなく、自分で選んで着た「好きな服」。
# - E1「マリン」：紺と白のボーダーのボートネック T、デニムのショートパンツ、白いスニーカー。港町の子らしく、軽やか。
# - E2「夜のワンピース」：夜色（灰青）のワンピースに白い丸襟、ふくらんだ短いそで。後ろ腰に白いリボン。白い靴下にストラップの靴。
# - E3「シャツ」：淡い青の大きめのシャツを前を開けて羽織り、白い T シャツ。そでをまくる。紺のショートパンツ、スニーカー。
E_LEGS_SHORTS = {
    "down": [".....SS..SS.....", ".....SS..SS.....", ".....SS..SS.....", ".....SS..SS.....",
             ".....TT..TT.....", "....FFF..FFF....", "................"],
    "down_step": [".....SS..SS.....", ".....SS..SS.....", ".....SS..SS.....", ".....SS..TT.....",
                  ".....TT..FFF....", "....FFF.........", "................"],
    "right": ["......SS........", "......SS........", "......SS........", "......SS........",
              "......TT........", "......FFFF......", "................"],
    "right_step": [".....SS.SS......", "....SS...SS.....", "....SS...SS.....", "...SS.....SS....",
                   "...TT.....TT....", ".FFF......FFFF..", "................"],
}
E_LEGS_LONG = {   # ワンピース・長めのシャツ（脚が見える所が 6 行）
    "down": [".....SS..SS.....", ".....SS..SS.....", ".....TT..TT.....", ".....TT..TT.....",
             "....FFF..FFF....", "................"],
    "down_step": [".....SS..SS.....", ".....SS..SS.....", ".....TT..TT.....", ".....TT..FFF....",
                  "....FFF.........", "................"],
    "right": ["......SS........", "......SS........", "......TT........", "......TT........",
              "......FFFF......", "................"],
    "right_step": [".....SS.SS......", "....SS...SS.....", "...TT.....TT....", "..TT.......TT...",
                   ".FFF.......FFF..", "................"],
}

E_OUTFITS = {
    "e1": dict(
        name="マリン",
        mats={
            "W": Mat("tee2", "tee1", "tee3", group="WN", d=2),
            "N": Mat("marine1", "marine0", "marine2", group="WN", d=2),
            "D": Mat("denim1", "denim0", "denim2"),
            "T": Mat("tee3", "tee2", group="T"),
            "F": Mat("stone7", "stone5", "tee3"),
        },
        legs=E_LEGS_SHORTS,
        down=[
            "..HHHBBBBBBHHH..",
            "..HHWBBBBBBWHH..",
            "..NNNNBBBBNNNN..",
            "..WWWWWBBWWWWW..",
            "..SNNNNNNNNNNS..",
            "..SWWWWWWWWWWS..",
            "..SNNNNNNNNNNS..",
            "..SWWWWWWWWWWS..",
            "...DDDDDDDDDD...",
            "...DDDD..DDDD...",
        ],
        up=[
            "..HHHBBBBBBHHH..",
            "..HHWWWWWWWWHH..",
            "..NNNNNNNNNNNN..",
            "..WWWWWWWWWWWW..",
            "..SNNNNNNNNNNS..",
            "..SWWWWWWWWWWS..",
            "..SNNNNNNNNNNS..",
            "..SWWWWWWWWWWS..",
            "...DDDDDDDDDD...",
            "...DDDD..DDDD...",
        ],
        right=[
            "..HHHHBBBBB.....",
            "...HWWBBBBW.....",
            "....NNNNNNN.....",
            "....WWWWWWW.....",
            "....NNNSSNN.....",
            "....WWWSSWW.....",
            "....NNNSSNN.....",
            "....WWWSSWW.....",
            "....DDDDDDD.....",
            ".....DDDDD......",
        ],
    ),
    "e2": dict(
        name="夜のワンピース",
        mats={
            "P": Mat("slate3", "slate2", "slate4", group="Pcx", d=2),
            "c": Mat("tee3", "tee2", group="c"),
            "T": Mat("tee3", "tee2", group="T"),
            "F": Mat("brown1", "brown0", "brown2"),
        },
        direct={"x": "slate2"},
        legs=E_LEGS_LONG,
        down=[
            "..HHHBBBBBBHHH..",
            "..HHcBBBBBBcHH..",
            "...PccBBBBccP...",
            "..PPPPPBBPPPPP..",
            "..S.PPPPPPPP.S..",
            "..S.xxxxxxxx.S..",
            "..S.PPPPPPPP.S..",
            "..SPPPPPPPPPPS..",
            "..PPPPPPPPPPPP..",
            ".PPPPPPPPPPPPPP.",
            ".PPPPPPPPPPPPPP.",
        ],
        up=[
            "..HHHBBBBBBHHH..",
            "..HHccccccccHH..",
            "...PccccccccP...",
            "..PPPPPPPPPPPP..",
            "..S.PPPPPPPP.S..",
            "..S.xxxccxxx.S..",
            "..S.PPPccPPP.S..",
            "..SPPPPPPPPPPS..",
            "..PPPPPPPPPPPP..",
            ".PPPPPPPPPPPPPP.",
            ".PPPPPPPPPPPPPP.",
        ],
        right=[
            "..HHHHBBBBB.....",
            "...HPPBBBBc.....",
            ".....PPPPPP.....",
            "....PPPPPPP.....",
            ".....PSSPPP.....",
            ".....xSSxxx.....",
            ".....PSSPPP.....",
            ".....PSSPPP.....",
            "....PPPPPPPP....",
            "...PPPPPPPPPP...",
            "..PPPPPPPPPPPP..",
        ],
    ),
    "e3": dict(
        name="シャツ",
        mats={
            "C": Mat("chambray1", "chambray0", "chambray2", group="Cct", d=2),
            "t": Mat("tee3", "tee2", group="tB"),
            "K": Mat("night3", "night2", "night5"),
            "T": Mat("tee3", "tee2", group="T"),
            "F": Mat("stone7", "stone5", "tee3"),
        },
        direct={"c": "chambray2"},
        legs=E_LEGS_LONG,
        down=[
            "..HHHBBBBBBHHH..",
            "..HHCBBBBBBCHH..",
            "..CCCCBBBBCCCC..",
            "..CCCCBBBBCCCC..",
            "..CCCCCttCCCCC..",
            "..ccCCCttCCCcc..",
            "..SCCCCttCCCCS..",
            "..SCCCCttCCCCS..",
            "..SCCCCttCCCCS..",
            "...CCKKKKKKCC...",
            "....KKK..KKK....",
        ],
        up=[
            "..HHHBBBBBBHHH..",
            "..HHCCCCCCCCHH..",
            "..CCCCCCCCCCCC..",
            "..CCCCCCCCCCCC..",
            "..CCCCCCCCCCCC..",
            "..ccCCCCCCCCcc..",
            "..SCCCCCCCCCCS..",
            "..SCCCCCCCCCCS..",
            "..SCCCCCCCCCCS..",
            "...CCCCCCCCCC...",
            "....KKK..KKK....",
        ],
        right=[
            "..HHHHBBBBB.....",
            "...HCCBBBBC.....",
            "....CCCCCCt.....",
            "....CCCCCCt.....",
            "....CCcccCt.....",
            "....CCCSSCt.....",
            "....CCCSSCt.....",
            "....CCCSSCC.....",
            "....CCCCCCC.....",
            "....CCCCCCC.....",
            ".....KKKKK......",
        ],
    ),
}


def e_frames(key):
    """D の頭（0〜14 行）＋服（15 行〜）＋脚。7 コマ（下・下歩き・上・右・右歩き・左・左歩き）。"""
    o = E_OUTFITS[key]
    legs = o["legs"]
    down = D_DOWN[:15] + o["down"] + legs["down"]
    down_step = D_DOWN[:15] + o["down"] + legs["down_step"]
    up = D_UP[:15] + o["up"] + legs["down"]
    right = D_RIGHT[:15] + o["right"] + legs["right"]
    right_step = D_RIGHT[:15] + o["right"] + legs["right_step"]
    mats = dict(D_MATS)
    mats.update(o["mats"])
    direct = dict(D_DIRECT)
    direct.update(o.get("direct", {}))
    return sprites(down, down_step, up, right, right_step, mats, direct, D_STYLE)


SHOULDERS = [(4, 47), (8, 40), (16, 36), (32, 36), (40, 40), (44, 47)]


def marine_torso(c):
    c.poly(SHOULDERS, "N")
    for y in range(36, 48):
        if (y // 2) % 2 == 0:                         # 2 ドット幅のボーダー
            c.rect((0, y, 47, y), "W", only="N")
    c.ellipse((15, 33, 33, 40), "W")                  # ボートネックの白いふち


def dress_torso(c):
    c.poly(SHOULDERS, "P")
    c.ellipse((13, 33, 24, 42), "c")                  # 白い丸襟（左右 2 枚）
    c.ellipse((24, 33, 35, 42), "c")


def shirt_torso(c):
    c.poly(SHOULDERS, "C")
    c.poly([(21, 36), (27, 36), (26, 47), (22, 47)], "t")   # 前を開けたシャツの下の白い T シャツ
    c.poly([(14, 35), (21, 35), (19, 42)], "c")              # 襟
    c.poly([(27, 35), (34, 35), (29, 42)], "c")


E_TORSOS = {"e1": marine_torso, "e2": dress_torso, "e3": shirt_torso}


def e_portrait(key, expr="normal"):
    o = E_OUTFITS[key]
    mats = {k: Mat(m.base, m.shade, m.light, m.line, m.group, 3 if k in "WNPC" else m.d) for k, m in o["mats"].items()}
    if key == "e2":
        mats["c"] = Mat("tee3", "tee2", "tee3", group="c", d=2)
    if key == "e3":
        mats["c"] = Mat("chambray2", "chambray1", "chambray3", group="c", d=2)
        mats["t"] = Mat("tee3", "tee2", group="t", d=2)
    return d_portrait(expr, E_TORSOS[key], mats, o.get("direct"))


# ================================================================ 案 F：おしゃれな部屋着（3 種）
# ユーザー：「E2・E3 の方向がいい。でも、夜中におしゃれな部屋着で出てきたくらいがいい」。
# 眠れずに、部屋着のまま上だけ整えて出てきた 14 歳。足元はどれも素足にサンダル（家からそのまま出てきた感じ）。
# - F1「ルームワンピース」：淡い青のコットンのワンピース（ひざ丈・ふくらんだ短いそで・胸の下からギャザー）、すそに白いレース。
# - F2「パイピングのパジャマ」：淡い青の開襟シャツとショートパンツ。襟・前立て・そで口・すそに紺のパイピング、白いボタン。
# - F3「T シャツとロングカーディガン」：白い大きめの T シャツ、紺のショートパンツに、ひざまでの薄手のカーディガン（そでが少し長い）。
F_LEGS = {   # 27〜31 行（素足にサンダル）
    "down": [".....SS..SS.....", ".....SS..SS.....", ".....SS..SS.....", "....FFF..FFF....", "................"],
    "down_step": [".....SS..SS.....", ".....SS..SS.....", ".....SS..FFF....", "....FFF.........", "................"],
    "right": ["......SS........", "......SS........", "......SS........", "......FFFF......", "................"],
    "right_step": [".....SS.SS......", "....SS...SS.....", "...SS.....SS....", ".FFF......FFF...", "................"],
}
SANDAL = Mat("night4", "night3", "night5")

F_OUTFITS = {
    "f1": dict(
        name="ルームワンピース",
        mats={
            "P": Mat("pj2", "pj1", "pj3", group="Pxl", d=2),
            "l": Mat("tee3", "tee2", group="l"),
            "F": SANDAL,
        },
        direct={"x": "pj1"},
        down=[
            "..HHHBBBBBBHHH..",
            "..HHPBBBBBBPHH..",
            "...PPPBBBBPPP...",
            "..PPPPPBBPPPPP..",
            "..S.PPPPPPPP.S..",
            "..S.PPxPPxPP.S..",
            "..S.PPxPPxPP.S..",
            "..SPPPxPPxPPPS..",
            "..PPPPxPPxPPPP..",
            "..PPPPPPPPPPPP..",
            ".PPPPPPPPPPPPPP.",
            ".llllllllllllll.",
        ],
        up=[
            "..HHHBBBBBBHHH..",
            "..HHPPPPPPPPHH..",
            "...PPPPPPPPPP...",
            "..PPPPPPPPPPPP..",
            "..S.PPPPPPPP.S..",
            "..S.PPPPPPPP.S..",
            "..S.PPPPPPPP.S..",
            "..SPPPPPPPPPPS..",
            "..PPPPPPPPPPPP..",
            "..PPPPPPPPPPPP..",
            ".PPPPPPPPPPPPPP.",
            ".llllllllllllll.",
        ],
        right=[
            "..HHHHBBBBB.....",
            "...HPPBBBBP.....",
            ".....PPPPPP.....",
            "....PPPPPPP.....",
            ".....PSSPPP.....",
            ".....PSSPxP.....",
            ".....PSSPxP.....",
            ".....PSSPxP.....",
            "....PPPPPPPP....",
            "...PPPPPPPPP....",
            "...PPPPPPPPPP...",
            "..lllllllllll...",
        ],
    ),
    "f2": dict(
        name="パイピングのパジャマ",
        mats={
            "J": Mat("pj2", "pj1", "pj3", group="Jpb", d=2),
            "p": Mat("marine1", "marine0", "marine2", group="pJb"),
            "F": SANDAL,
        },
        direct={"b": "tee3"},
        down=[
            "..HHHBBBBBBHHH..",
            "..HHpBBBBBBpHH..",
            "..JJJpBBBBpJJJ..",
            "..JJJJpBBpJJJJ..",
            "..ppJJJpJJJJpp..",
            "..SJJJJpbJJJJS..",
            "..SJJJJpJJJJJS..",
            "..SJJJJpbJJJJS..",
            "...JJJJpJJJJJ...",
            "...pppppppppp...",
            "...JJJJ..JJJJ...",
            "...pppp..pppp...",
        ],
        up=[
            "..HHHBBBBBBHHH..",
            "..HHppppppppHH..",
            "..JJJJJJJJJJJJ..",
            "..JJJJJJJJJJJJ..",
            "..ppJJJJJJJJpp..",
            "..SJJJJJJJJJJS..",
            "..SJJJJJJJJJJS..",
            "..SJJJJJJJJJJS..",
            "...JJJJJJJJJJ...",
            "...pppppppppp...",
            "...JJJJ..JJJJ...",
            "...pppp..pppp...",
        ],
        right=[
            "..HHHHBBBBB.....",
            "...HJJBBBBp.....",
            "....JJJJJJp.....",
            "....JJJJJJp.....",
            "....JJpppJp.....",
            "....JJJSSJb.....",
            "....JJJSSJp.....",
            "....JJJSSJb.....",
            "....JJJJJJJ.....",
            "....ppppppp.....",
            ".....JJJJJ......",
            ".....ppppp......",
        ],
    ),
    "f3": dict(
        name="T シャツとロングカーディガン",
        mats={
            "G": Mat("knit2", "knit1", "knit3", group="Gg", d=2),
            "g": Mat("knit1", "knit0", "knit2", group="Gg"),
            "W": Mat("tee3", "tee2", group="WK", d=2),
            "K": Mat("night3", "night2", "night5"),
            "F": SANDAL,
        },
        down=[
            "..HHHBBBBBBHHH..",
            "..HHGBBBBBBGHH..",
            "..GGGWBBBBWGGG..",
            "..GGGWWBBWWGGG..",
            "..GGGWWWWWWGGG..",
            "..GGGWWWWWWGGG..",
            "..GGGWWWWWWGGG..",
            "..ggGWWWWWWGgg..",
            "..SGGWWWWWWGGS..",
            "...GGKKKKKKGG...",
            "...GGSS..SSGG...",
            "...ggSS..SSgg...",
        ],
        up=[
            "..HHHBBBBBBHHH..",
            "..HHGGGGGGGGHH..",
            "..GGGGGGGGGGGG..",
            "..GGGGGGGGGGGG..",
            "..GGGGGGGGGGGG..",
            "..GGGGGGGGGGGG..",
            "..GGGGGGGGGGGG..",
            "..ggGGGGGGGGgg..",
            "..SGGGGGGGGGGS..",
            "...GGGGGGGGGG...",
            "...GGGGGGGGGG...",
            "...gggggggggg...",
        ],
        right=[
            "..HHHHBBBBB.....",
            "...HGGBBBBW.....",
            "....GGGGGGW.....",
            "....GGGGGGW.....",
            "....GGGGGGW.....",
            "....GGGGGGW.....",
            "....GGGGGGW.....",
            "....GGgggGW.....",
            "....GGGSSGW.....",
            "....GGGGGGK.....",
            "....GGSSGG......",
            "....ggSSgg......",
        ],
    ),
}


def f_frames(key):
    o = F_OUTFITS[key]
    legs = F_LEGS
    down = D_DOWN[:15] + o["down"] + legs["down"]
    down_step = D_DOWN[:15] + o["down"] + legs["down_step"]
    up = D_UP[:15] + o["up"] + legs["down"]
    right = D_RIGHT[:15] + o["right"] + legs["right"]
    right_step = D_RIGHT[:15] + o["right"] + legs["right_step"]
    mats = dict(D_MATS)
    mats.update(o["mats"])
    direct = dict(D_DIRECT)
    direct.update(o.get("direct", {}))
    return sprites(down, down_step, up, right, right_step, mats, direct, D_STYLE)


def roomdress_torso(c):
    c.poly(SHOULDERS, "P")
    c.ellipse((14, 33, 34, 41), "l")                  # 首まわりの白いレース
    c.ellipse((16, 33, 32, 39), "P")
    c.rect((6, 42, 42, 42), "l", only="P")            # 胸の下の切りかえ（ここからギャザー）にもレース


def pajama_torso(c):
    c.poly(SHOULDERS, "J")
    c.poly([(8, 39), (21, 36), (17, 47)], "p")        # 開襟（ふちが紺のパイピング）
    c.poly([(27, 36), (40, 39), (31, 47)], "p")
    c.poly([(10, 40), (19, 38), (17, 45)], "J")
    c.poly([(29, 38), (38, 40), (31, 45)], "J")
    c.line([(24, 40), (24, 47)], "p")                 # 前立て
    c.stamp(["b"], 25, 42)                            # 白いボタン
    c.stamp(["b"], 25, 46)


def cardigan_torso(c):
    c.poly(SHOULDERS, "G")
    c.poly([(18, 36), (30, 36), (29, 47), (19, 47)], "W")   # 白い T シャツ（カーディガンの前があいている）


F_TORSOS = {"f1": roomdress_torso, "f2": pajama_torso, "f3": cardigan_torso}


def f_portrait(key, expr="normal"):
    o = F_OUTFITS[key]
    mats = {k: Mat(m.base, m.shade, m.light, m.line, m.group, 3 if k in "PJGW" else m.d) for k, m in o["mats"].items()}
    if key == "f1":
        mats["l"] = Mat("tee3", "tee2", "tee3", group="l", d=2)
    return d_portrait(expr, F_TORSOS[key], mats, o.get("direct"))


# ================================================================ 商店街に置いた見え方
def street_views(concepts):
    """第 1 章の商店街（今の建物・小物はそのまま）に、案ごとのルリとネムを置いて、同じ場所を切り出して並べる。"""
    import build  # 商店街の絵を借りる（Assets へは書き出さない）

    build.save = lambda img, *path, clean=False, outline=None: (clean_corners(img, outline)[0] if clean else img)
    tiles, props = build.build_tiles(), build.build_props()
    import ch1_assets
    import m1_assets
    ch1 = ch1_assets.build(build.save)
    m1 = m1_assets.build(build.save)
    views = []
    for key, c in concepts:
        scene, gy = build.ch1_street_scene(tiles, props, ch1)

        def put(img, x, foot):
            scene.alpha_composite(img, (x - img.width // 2, foot - img.height))

        ruri = c["ruri"]()
        put(ruri[3], 262, gy + 40)        # 右向き（街灯の下）
        put(m1["lantern"], 270, gy + 30)
        put(c["nemu"](), 252, gy + 6)
        put(ruri[0], 340, gy + 24)        # 正面（おばあさんの店の前）
        put(ruri[6], 190, gy + 30)        # 左向きで歩く
        lit = build.light_ch1_street(scene, gy)
        views.append(lit.crop((150, 40, 400, 180)))
    return views


# ================================================================ 書き出し
def sprites(down, down_step, up, right, right_step, mats, direct, st):
    """下・下（歩き）・上・右・右（歩き）・左・左（歩き）。"""
    frames = (down, down_step, up, right, right_step, mirror(right), mirror(right_step))
    return [render(r, mats, direct, st) for r in frames]


CONCEPTS = {
    "a": dict(ruri=lambda: sprites(A_DOWN, A_DOWN_STEP, A_UP, A_RIGHT, A_RIGHT_STEP, A_MATS, A_DIRECT, A_STYLE),
              nemu=nemu_a_sprite, face=a_portrait, nemu_face=nemu_a_portrait),
    "b": dict(ruri=lambda: sprites(B_DOWN, B_DOWN_STEP, B_UP, B_RIGHT, B_RIGHT_STEP, B_MATS, B_DIRECT, B_STYLE),
              nemu=nemu_b_sprite, face=b_portrait, nemu_face=nemu_b_portrait),
    "c": dict(ruri=lambda: sprites(C_DOWN, C_DOWN_STEP, C_UP, C_RIGHT, C_RIGHT_STEP, C_MATS, C_DIRECT, C_STYLE),
              nemu=nemu_c_sprite, face=c_portrait, nemu_face=nemu_c_portrait),
    "d": dict(ruri=lambda: sprites(D_DOWN, D_DOWN_STEP, D_UP, D_RIGHT, D_RIGHT_STEP, D_MATS, D_DIRECT, D_STYLE),
              nemu=nemu_b_sprite, face=d_portrait, nemu_face=nemu_b_portrait),
}
for _k in F_OUTFITS:
    CONCEPTS[_k] = dict(ruri=(lambda k=_k: f_frames(k)), nemu=nemu_b_sprite,
                        face=(lambda k=_k: f_portrait(k)), nemu_face=nemu_b_portrait)
for _k in E_OUTFITS:
    CONCEPTS[_k] = dict(ruri=(lambda k=_k: e_frames(k)), nemu=nemu_b_sprite,
                        face=(lambda k=_k: e_portrait(k)), nemu_face=nemu_b_portrait)


def upscale(img, s):
    return img.resize((img.width * s, img.height * s), Image.NEAREST)


def sheet(images, bg, pad=6):
    w = sum(i.width for i in images) + pad * (len(images) + 1)
    h = max(i.height for i in images) + pad * 2
    out = Image.new("RGBA", (w, h), bg)
    x = pad
    for i in images:
        out.alpha_composite(i, (x, h - pad - i.height))
        x += i.width + pad
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    bg = hex_to_rgba(RAMPS["night"][2])
    for key, c in CONCEPTS.items():
        upscale(sheet(c["ruri"]() + [c["nemu"]()], bg), 6).save(os.path.join(OUT, f"{key}_sprites.png"))
        upscale(sheet([c["face"](), c["nemu_face"]()], bg), 5).save(os.path.join(OUT, f"{key}_faces.png"))
    for (key, _), view in zip(CONCEPTS.items(), street_views(list(CONCEPTS.items()))):
        upscale(view, 3).save(os.path.join(OUT, f"{key}_street.png"))
    # 案ごとの 1 枚（上：商店街に置いた見え方、中：ゲーム内の絵、下：顔グラフィック）
    for key in CONCEPTS:
        parts = [Image.open(os.path.join(OUT, f"{key}_{n}.png")) for n in ("street", "sprites", "faces")]
        w = max(p.width for p in parts)
        board = Image.new("RGBA", (w, sum(p.height for p in parts)), bg)
        y = 0
        for p in parts:
            board.alpha_composite(p.convert("RGBA"), ((w - p.width) // 2, y))
            y += p.height
        board.save(os.path.join(OUT, f"concept_{key}.png"))
    # D 案の表情（普通・ほほえみ・かなしい・おどろき）
    upscale(sheet([d_portrait(e) for e in D_EYES], bg), 5).save(os.path.join(OUT, "d_expressions.png"))
    # E 案（服のリメイク）：3 種の顔グラフィックを並べる
    upscale(sheet([e_portrait(k) for k in E_OUTFITS], bg), 5).save(os.path.join(OUT, "e_faces_compare.png"))
    upscale(sheet([f_portrait(k) for k in F_OUTFITS], bg), 5).save(os.path.join(OUT, "f_faces_compare.png"))
    print("done")


if __name__ == "__main__":
    main()
