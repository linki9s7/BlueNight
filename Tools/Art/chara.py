"""人物の描き方のしくみ（ルリ・ネム・顔グラフィック・リデザイン案で共通）。

記号の図（1 文字 = 1 ドット）を、素材（Mat）ごとの色に置きかえて画像にする。
- 陰影は自動：素材ごとに「右下へ d ずらすと同じ部品（group）の外に出る所」を影の色にする（光はどの向きでも左上から）。
- 輪郭（Style.outline）：line＝外側に 1 ドットの線／selout＝隣の塗りを暗くした線／none＝線なし。
- 月明かりの縁取り（Style.rim）：左か上が外（透明）の所を、その素材の明るい色にする。
  ルリ・ネムは輪郭線なし＋縁取り（ユーザーの決定、仕様書 7.8・Tools/Art/STYLE.md 3 章）。
- 左向きの絵は、記号の図を反転してから陰影を付ける（mirror）。光の向きは変わらない。
"""

from PIL import Image, ImageDraw

from palette import RAMPS, hex_to_rgba
from pixel_check import clean_corners

CLEAR = (0, 0, 0, 0)


EXTRA = {}  # 検討中の色（concept_chars.py が足す）。採用した色は palette.py の RAMPS に入れる


def P(name):
    ramp = name.rstrip("0123456789")
    table = RAMPS.get(ramp) or EXTRA[ramp]
    return hex_to_rgba(table[int(name[len(ramp):])])


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
