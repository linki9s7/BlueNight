"""UI の部品とタイトル画面の一枚絵。

UI（Assets/005_Textures/UI/）
- 会話ウィンドウ・名前札は 9 スライス用（ふちは 4 ドット）。ふちは月色の 1 ドットの線そのものを輪郭にし、
  内側に 1 列だけの別の色（帯）を作らない。角は 2 ドット丸める。
- 頭の上のアイコン：会話（…の吹き出し）・調べる（虫めがね）・ランタン。吹き出しのしっぽは下向き。
- 送りの矢印（2 コマで上下にはねる）、選択肢のカーソル、ことば帳のアイコン。

タイトル（Assets/005_Textures/Title/、480x270）
- 仕様書 1.3・6 章：大きな満月、町の上を横切る高架のハイウェイ、街灯の下に小さく影の無い少女。
- 空は暗い色から明るい色へ段々に変える。境目だけ 2 行の網点（STYLE.md：網点は色の境目の狭い帯だけ）。
- 動くもの（車の光）とロゴは別の画像にして、Unity で動かす・フェードさせる。
"""

import random

from PIL import Image, ImageDraw

import ruri
from palette import RAMPS, hex_to_rgba

CLEAR = (0, 0, 0, 0)


def P(name):
    ramp = name.rstrip("0123456789")
    return hex_to_rgba(RAMPS[ramp][int(name[len(ramp):])])


def from_map(rows, key):
    w = len(rows[0])
    img = Image.new("RGBA", (w, len(rows)), CLEAR)
    px = img.load()
    for y, row in enumerate(rows):
        assert len(row) == w, f"row {y}: {row!r}"
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = P(key[ch])
    return img


# ================================================================ UI
UI_KEY = {"O": "moon1", "f": "night1", "d": "night0", "W": "moon3", "w": "moon1", "y": "warm5", "Y": "warm4",
          "b": "scarf1", "B": "scarf0", "k": "night2", "r": "red1"}

WINDOW = [  # 16x16、9 スライスのふち 4 ドット
    "..OOOOOOOOOOOO..",
    ".OffffffffffffO.",
    "OffffffffffffffO",
    "OffffffffffffffO",
    "OffffffffffffffO",
    "OffffffffffffffO",
    "OffffffffffffffO",
    "OffffffffffffffO",
    "OffffffffffffffO",
    "OffffffffffffffO",
    "OffffffffffffffO",
    "OffffffffffffffO",
    "OffffffffffffffO",
    "OffffffffffffffO",
    ".OffffffffffffO.",
    "..OOOOOOOOOOOO..",
]

NAME_TAB = [  # 名前札 16x12、9 スライスのふち 4 ドット（青いマフラーの色）
    "..OOOOOOOOOOOO..",
    ".ObbbbbbbbbbbbO.",
    "ObbbbbbbbbbbbbbO",
    "ObbbbbbbbbbbbbbO",
    "ObbbbbbbbbbbbbbO",
    "ObbbbbbbbbbbbbbO",
    "ObbbbbbbbbbbbbbO",
    "ObbbbbbbbbbbbbbO",
    "ObbbbbbbbbbbbbbO",
    "ObbbbbbbbbbbbbbO",
    ".ObbbbbbbbbbbbO.",
    "..OOOOOOOOOOOO..",
]

NEXT_ARROW = [  # 7x5
    "WWWWWWW",
    ".WWWWW.",
    "..WWW..",
    "...W...",
    ".......",
]

CURSOR = [  # 選択肢のカーソル：小さなランタンの火（7x7）
    "...y...",
    "..yyy..",
    ".yyYyy.",
    ".yYYYy.",
    ".yYYYy.",
    "..yyy..",
    ".......",
]

BUBBLE = [  # 頭の上の吹き出し（13x13）。中身は別に描く
    ".OOOOOOOOOOO.",
    "OWWWWWWWWWWWO",
    "OWWWWWWWWWWWO",
    "OWWWWWWWWWWWO",
    "OWWWWWWWWWWWO",
    "OWWWWWWWWWWWO",
    "OWWWWWWWWWWWO",
    "OWWWWWWWWWWWO",
    "OWWWWWWWWWWWO",
    ".OOOOWWWOOOO.",
    ".....OWO.....",
    "......O......",
    ".............",
]

ICON_TALK = ["k.k.k"]                # …
ICON_LOOK = [                         # 虫めがね
    ".kkk..",
    "k...k.",
    "k...k.",
    ".kkk..",
    "....kk",
]
ICON_LANTERN = [                      # ランタン
    ".kkk.",
    "kyyyk",
    "kyYyk",
    "kyyyk",
    ".kkk.",
]

WORDBOOK = [  # ことば帳のアイコン（12x12）：青い表紙に月のしおり
    "............",
    ".OOOOOOOOO..",
    ".ObbbbbbbOO.",
    ".ObbWWbbbOwO",
    ".ObWbbbbbOwO",
    ".ObbWWbbbOwO",
    ".ObbbbbbbOwO",
    ".ObbbbbbbOwO",
    ".OBBBBBBBOwO",
    ".OOOOOOOOOwO",
    "..OOOOOOOOOO",
    "............",
]
WORDBOOK_KEY = {"O": "night0", "b": "scarf1", "B": "scarf0", "W": "moon3", "w": "stone7"}


def bubble_icon(content, x0, y0):
    img = from_map(BUBBLE, UI_KEY)
    px = img.load()
    for y, row in enumerate(content):
        for x, ch in enumerate(row):
            if ch != ".":
                px[x0 + x, y0 + y] = P(UI_KEY[ch])
    return img


def build_ui(save):
    out = {
        "window": from_map(WINDOW, UI_KEY),
        "name_tab": from_map(NAME_TAB, UI_KEY),
        "next_0": from_map(NEXT_ARROW, UI_KEY),
        "next_1": from_map(["......."] + NEXT_ARROW[:-1], UI_KEY),
        "cursor": from_map(CURSOR, UI_KEY),
        "icon_talk": bubble_icon(ICON_TALK, 4, 4),
        "icon_look": bubble_icon(ICON_LOOK, 3, 2),
        "icon_lantern": bubble_icon(ICON_LANTERN, 4, 2),
        "wordbook": from_map(WORDBOOK, WORDBOOK_KEY),
    }
    for name, img in out.items():
        out[name] = save(img, "UI", f"ui_{name}.png")
    return out


# ================================================================ タイトル
# v0.17 で描きこみを増やした（ユーザーの感想：「全体的にチープ寄り」「街灯の柱が背景と同化」）。
# - 左は坂の町（遠くの集合住宅・手前の家・電柱と電線）、右は湾。満月は海に映る。
# - 空・月のまわりの光・街灯の光は、明るさの段を「平らな面＋境目だけ網点」で置く（STYLE.md：網点は境目の狭い帯だけ）。
# - 街灯は手前の柱を明るい石の色にし、左（月と灯の側）を一段明るくして背景から浮かせる。灯の光は円すい形に地面へ落ちる。
import math

W, H = 480, 270
SEA_Y = 178          # 海の水平線
FRONT_Y = 232        # 手前の遊歩道の上のふち
MOON = (338, 74, 40)
LAMP_X = 104
BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def deck_y(x):
    """高架の道路の床の高さ（Unity の車の光もこの線を走る。BlueNightSetup.Title と合わせる）。"""
    return 150 + x * 18 // W


def qlevel(v, x, y):
    """明るさ（小数）を段に。端数が中ほどの所だけ網点にする（平らな面＋境目の狭い帯）。"""
    i = math.floor(v)
    f = v - i
    if f < 0.3:
        return i
    if f > 0.7:
        return i + 1
    return i + (1 if (f - 0.3) / 0.4 * 16 > BAYER4[y % 4][x % 4] + 0.5 else 0)


def ramp_color(ramp, level):
    table = RAMPS[ramp]
    return hex_to_rgba(table[max(0, min(len(table) - 1, level))])


REVERSE = {hex_to_rgba(h)[:3]: (name, i) for name, table in RAMPS.items() for i, h in enumerate(table)}


def brighten(px, x, y, amount):
    """その点の色を、同じ系統で amount 段（小数は網点）明るくする。光の当たる所に使う。"""
    if amount <= 0 or not (0 <= x < W and 0 <= y < H):
        return
    c = px[x, y]
    found = REVERSE.get(c[:3])
    if not found:
        return
    name, i = found
    step = qlevel(amount, x, y)
    if step:
        px[x, y] = ramp_color(name, i + step)


def moon_glow(x, y):
    cx, cy, r = MOON
    d = math.hypot(x - cx, y - cy)
    return 0.0 if d <= r else 1.8 * max(0.0, 1 - (d - r) / 36) ** 1.6


def sky(img):
    """空：上の暗い紺から水平線へ少しずつ明るく。月のまわりは光でふんわり明るい。"""
    px = img.load()
    for y in range(SEA_Y + 1):
        base = 0.2 + 3.0 * (y / SEA_Y) ** 1.7
        for x in range(W):
            px[x, y] = ramp_color("night", min(5, qlevel(base + moon_glow(x, y), x, y)))


def stars(img, rng):
    px = img.load()
    dark = {P("night0")[:3], P("night1")[:3]}
    for _ in range(170):
        x, y = rng.randrange(W), rng.randrange(0, 150)
        if px[x, y][:3] not in dark:
            continue
        k = rng.random()
        px[x, y] = P("moon1") if k < 0.35 else P("night6") if k < 0.8 else P("night7") if k < 0.95 else P("warm5")
    for x, y in [(52, 24), (148, 16), (232, 40), (448, 22), (264, 108), (14, 130)]:   # 明るい星（十字）
        if px[x, y][:3] in dark or (x, y) == (264, 108):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                px[x + dx, y + dy] = P("moon1")
            px[x, y] = P("moon3")


def moon(img):
    """大きな満月：明るい丸＋右下の影のかたまり＋左寄りの海（模様）。光の輪は sky() の月明かり。"""
    cx, cy, r = MOON
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=P("night6"))  # ふちのにじみ（1 段）
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=P("moon3"))
    m1 = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m1).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    m2 = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m2).ellipse([cx - r - 5, cy - r - 5, cx + r - 5, cy + r - 5], fill=255)
    shade = Image.new("L", (W, H), 0)
    sp, ap, bp = shade.load(), m1.load(), m2.load()
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if ap[x, y] and not bp[x, y]:
                sp[x, y] = 255
    img.paste(Image.new("RGBA", (W, H), P("moon2")), (0, 0), shade)
    sea = [
        (cx - 24, cy - 20, 12, 7), (cx - 16, cy - 15, 10, 9), (cx - 9, cy - 9, 8, 6),
        (cx - 20, cy + 2, 7, 5), (cx - 14, cy + 6, 11, 6), (cx + 2, cy - 26, 6, 4),
        (cx + 10, cy + 12, 9, 5), (cx + 16, cy - 4, 5, 4),
    ]
    for (x, y, w, h) in sea:
        d.ellipse([x, y, x + w, y + h], fill=P("moon2"))
    d.ellipse([cx - 13, cy - 12, cx - 9, cy - 9], fill=P("moon1"))  # いちばん濃い所は 1 か所だけ
    for (x, y) in [(cx + 20, cy - 18), (cx - 4, cy + 24), (cx + 26, cy + 6)]:  # 小さなクレーター（2x2、左上が明るい）
        d.point((x + 1, y + 1), fill=P("moon2"))
        d.point((x, y + 1), fill=P("moon2"))


CLOUDS = [  # 細くたなびく雲（楕円の組）。下の雲は月の下のほうにかかる
    [(300, 104, 50, 4), (350, 101, 40, 4), (395, 106, 34, 3), (262, 108, 22, 2)],
    [(40, 106, 44, 3), (92, 103, 32, 3), (130, 108, 20, 2)],
    [(420, 140, 46, 3), (470, 137, 24, 3), (200, 132, 26, 2), (232, 134, 16, 2)],
]


def clouds(img):
    """雲：月にかかる所は明るい灰青、月から遠い所は空より少し明るい紺。上のふちに月明かり、下は一段暗く。"""
    px = img.load()
    cx, cy, r = MOON
    for cloud in CLOUDS:
        m = Image.new("L", (W, H), 0)
        dm = ImageDraw.Draw(m)
        for (x, y, rx, ry) in cloud:
            dm.ellipse([x - rx, y - ry, x + rx, y + ry], fill=255)
        mp = m.load()
        for y in range(1, SEA_Y):
            for x in range(W):
                if not mp[x, y]:
                    continue
                on_moon = math.hypot(x - cx, y - cy) <= r + 2
                near = moon_glow(x, y) > 0.6 or on_moon
                if not mp[x, y - 1]:
                    c = "moon1" if on_moon else "night6" if near else "night4"
                elif y + 1 < H and not mp[x, y + 1]:
                    c = "night4" if near else "night2"
                else:
                    c = "night5" if near else "night3"
                px[x, y] = P(c)


def far_shore(img, rng):
    """水平線の向こうの低い山並みと、右の岬の灯台（第 4 章の舞台を遠くに見せる）。"""
    px = img.load()
    for x in range(W):
        h = 4 + 3 * math.sin(x / 37.0) + 2 * math.sin(x / 13.0 + 1.3)
        if x > 420:
            h += (x - 420) * 0.22            # 岬が少し高くなる
        top = int(SEA_Y - h)
        for y in range(top, SEA_Y + 1):
            px[x, y] = P("night2") if y == top else P("night1")
    lx = 462
    top = int(SEA_Y - (4 + 3 * math.sin(lx / 37.0) + 2 * math.sin(lx / 13.0 + 1.3) + (lx - 420) * 0.22))
    d = ImageDraw.Draw(img)
    d.rectangle([lx, top - 9, lx + 2, top], fill=P("stone3"))
    d.line([lx, top - 9, lx, top], fill=P("stone5"))
    d.rectangle([lx - 1, top - 11, lx + 3, top - 10], fill=P("night2"))
    d.point((lx + 1, top - 12), fill=P("warm6"))   # 灯台の灯
    d.point((lx, top - 12), fill=P("warm3"))
    d.point((lx + 2, top - 12), fill=P("warm3"))
    for _ in range(4):   # 岸の小さな明かり
        x = rng.randrange(300, 450)
        y = int(SEA_Y - (4 + 3 * math.sin(x / 37.0) + 2 * math.sin(x / 13.0 + 1.3))) + 2
        px[x, y] = P("warm3")


def sea(img, rng):
    """湾：遠くは明るく、手前ほど暗い。月の光の道（横線のかけら）と、さざ波。"""
    px = img.load()
    cx = MOON[0]
    for y in range(SEA_Y + 1, FRONT_Y):
        t = (y - SEA_Y) / (FRONT_Y - SEA_Y)
        base = 2.6 - 1.6 * t
        for x in range(W):
            px[x, y] = ramp_color("night", qlevel(base, x, y))
    # さざ波：短い横線（3〜7 ドット）。手前ほど長く、間をあける
    for y in range(SEA_Y + 3, FRONT_Y, 3):
        t = (y - SEA_Y) / (FRONT_Y - SEA_Y)
        for _ in range(int(10 + 14 * t)):
            x = rng.randrange(W)
            length = rng.randint(3, 4 + int(5 * t))
            c = px[x, y]
            found = REVERSE.get(c[:3])
            if found:
                for k in range(length):
                    if x + k < W:
                        px[x + k, y] = ramp_color("night", found[1] + 1)
    # 月の光の道：真下に、幅はあまり変えず（三角にすると木に見える）。1 行おきに横線のかけら、中ほどほど明るい
    for y in range(SEA_Y + 2, FRONT_Y, 2):
        t = (y - SEA_Y) / (FRONT_Y - SEA_Y)
        width = 14 + int(12 * t) + rng.randint(-3, 3)
        for _ in range(4 + int(4 * t)):
            off = int(rng.triangular(-width, width, 0))
            length = rng.randint(2, 5 + int(5 * t))
            x = cx + off - length // 2
            near = abs(off) < width * 0.35
            c = P("moon2") if near and t < 0.35 else P("moon1") if near else P("night6")
            for k in range(length):
                if 0 <= x + k < W:
                    px[x + k, y] = c


TOWN_EDGE = 300   # 町（左）と湾（右）の境。手前ほど左へ


def far_town(img, rng):
    """遠くの町：集合住宅とビルのシルエット。屋上のふちに月明かり、窓は格子に並べて一部だけ灯す。"""
    d = ImageDraw.Draw(img)
    px = img.load()
    x = -4
    while x < TOWN_EDGE:
        w = rng.choice([16, 20, 24, 30, 36])
        h = rng.choice([14, 20, 26, 32, 40])
        if x + w > TOWN_EDGE:
            h = min(h, 14)
        top = SEA_Y + 14 - h
        d.rectangle([x, top, x + w - 1, 214], fill=P("night1"))
        d.line([x, top, x + w - 1, top], fill=P("night3"))           # 屋上のふち（月明かり）
        if h >= 26 and rng.random() < 0.5:                           # 屋上の給水塔
            d.rectangle([x + 3, top - 4, x + 6, top - 1], fill=P("night1"))
            d.line([x + 3, top - 4, x + 6, top - 4], fill=P("night3"))
        for wy in range(top + 3, SEA_Y + 12, 4):                       # 窓の格子
            for wx in range(x + 2, x + w - 2, 4):
                if rng.random() < 0.22:
                    px[wx, wy] = P("warm4") if rng.random() < 0.7 else P("warm3")
                    if wx + 1 < x + w - 2 and rng.random() < 0.5:
                        px[wx + 1, wy] = P("warm3")
        x += w + rng.choice([0, 0, 2])


HOUSES = [  # 手前の家（左端 x、幅、壁の高さ、屋根の高さ）。足元は FRONT_Y - 6
    (-6, 34, 16, 10), (30, 28, 20, 9), (60, 40, 14, 12), (102, 30, 22, 9), (134, 36, 16, 11),
    (172, 26, 18, 8), (200, 38, 14, 11), (240, 30, 12, 8), (272, 20, 8, 6),
]


def near_town(img, rng):
    """手前の家々：切妻の屋根（上のふちに月明かり、左の面が明るい）、灯った窓（2x2、左上につや）。"""
    d = ImageDraw.Draw(img)
    foot = FRONT_Y - 6
    for (x, w, wall, roof) in HOUSES:
        wall_top = foot - wall
        d.rectangle([x, wall_top, x + w - 1, foot], fill=P("night2"))
        peak = (x + w // 2, wall_top - roof)
        d.polygon([(x - 2, wall_top), peak, (x + w + 1, wall_top)], fill=P("stone1"))
        d.polygon([(x - 2, wall_top), peak, (x + w // 2, wall_top)], fill=P("stone2"))  # 左の面（月の側）
        d.line([(x - 2, wall_top), peak], fill=P("stone4"))                              # 屋根のふちの光
        d.line([peak, (x + w + 1, wall_top)], fill=P("stone3"))
        d.line([x - 2, wall_top + 1, x + w + 1, wall_top + 1], fill=P("night1"))         # 軒の影
        for k in range(max(1, w // 12)):
            wx = x + 4 + k * 12
            wy = wall_top + 4
            if wx + 3 >= x + w:
                break
            if rng.random() < 0.6:
                d.rectangle([wx, wy, wx + 3, wy + 3], fill=P("warm4"))
                d.rectangle([wx, wy, wx + 1, wy + 1], fill=P("warm5"))
                d.line([wx + 2, wy, wx + 2, wy + 3], fill=P("warm3"))                     # 窓の桟
            else:
                d.rectangle([wx, wy, wx + 3, wy + 3], fill=P("night1"))


def highway(img):
    """高架のハイウェイ：防音壁（上のふちに月明かり）・床の側面（継ぎ目）・橋桁の影・橋脚（海では水に映る）・ナトリウム灯。"""
    d = ImageDraw.Draw(img)
    px = img.load()
    for x in range(20, W, 64):   # 橋脚
        y = deck_y(x)
        bottom = 214 if x < TOWN_EDGE else FRONT_Y - 1
        d.rectangle([x, y + 8, x + 5, bottom], fill=P("stone1"))
        d.rectangle([x, y + 8, x + 1, bottom], fill=P("stone2"))      # 左の 2 列が明るい
        d.rectangle([x - 2, y + 8, x + 7, y + 9], fill=P("stone1"))   # 橋脚の頭
        if x >= TOWN_EDGE:                                             # 水に映った橋脚（横線のかけら）
            for ry in range(SEA_Y + 20, FRONT_Y, 2):
                if (ry // 2 + x) % 3:
                    d.line([x, ry, x + 4, ry], fill=P("night1"))
    for x in range(W):
        y = deck_y(x)
        px[x, y - 4] = P("night1")                                  # 輪郭
        px[x, y - 3] = P("stone3")                                  # 防音壁の上のふち（月明かり）
        for k in (-2, -1):
            px[x, y + k] = P("stone2")
        for k in range(0, 6):
            px[x, y + k] = P("stone1")
        px[x, y + 6] = P("night1")                                  # 橋桁の影
        px[x, y + 7] = P("night1")
        if x % 12 == 0:
            for k in range(0, 6):
                px[x, y + k] = P("night2")                          # 床の継ぎ目
    for x in range(12, W, 40):   # ナトリウム灯（柱・灯・ふちのにじみ）
        y = deck_y(x)
        d.line([x, y - 9, x, y - 4], fill=P("night1"))
        d.line([x, y - 10, x + 2, y - 10], fill=P("warm5"))
        d.point((x + 3, y - 10), fill=P("warm3"))
        d.point((x + 1, y - 11), fill=P("warm3"))


def wires(img):
    """電柱と電線（日本の町らしさ）。電線はたるませる。"""
    d = ImageDraw.Draw(img)
    poles = [(18, 112), (238, 124)]
    for (x, top) in poles:
        d.rectangle([x, top, x + 2, FRONT_Y], fill=P("night0"))
        d.line([x, top, x, FRONT_Y], fill=P("night2"))                # 左のふちに月明かり
        d.rectangle([x - 6, top + 6, x + 8, top + 7], fill=P("night0"))
        d.point((x - 5, top + 5), fill=P("stone3"))                   # 碍子
        d.point((x + 7, top + 5), fill=P("stone3"))
    (x0, t0), (x1, t1) = poles
    for (a, b, sag) in [(x0 - 5, x1 - 5, 9), (x0 + 7, x1 + 7, 11)]:
        ya, yb = t0 + 5, t1 + 5
        for x in range(a, b + 1):
            t = (x - a) / (b - a)
            y = ya + (yb - ya) * t + sag * 4 * t * (1 - t)
            d.point((x, round(y)), fill=P("night0"))
    for (a, sag) in [(x0 - 5, 6), (x0 + 7, 7)]:                    # 左の画面外へのびる線
        for x in range(0, a + 1):
            t = x / max(1, a)
            y = t0 + 5 + sag * 4 * t * (1 - t) * 0.5 + (1 - t) * 4
            d.point((x, round(y)), fill=P("night0"))


def promenade(img):
    """手前の海ぞいの遊歩道と手すり。"""
    d = ImageDraw.Draw(img)
    d.rectangle([0, FRONT_Y - 6, W - 1, FRONT_Y - 1], fill=P("night1"))         # 岸壁の下
    d.rectangle([0, FRONT_Y, W - 1, H - 1], fill=P("stone1"))
    d.line([0, FRONT_Y, W - 1, FRONT_Y], fill=P("stone3"))                       # 岸壁の上のふち
    for x in range(-8, W, 28):                                                    # 敷石の目地（少し斜め）
        d.line([x + 4, FRONT_Y + 1, x, H - 1], fill=P("night2"))
    d.line([0, 250, W - 1, 250], fill=P("night2"))
    # 手すり（横の棒 2 本＋支柱）
    for y, c in ((FRONT_Y - 12, "stone3"), (FRONT_Y - 7, "stone2")):
        d.line([0, y, W - 1, y], fill=P(c))
    for x in range(6, W, 16):
        d.line([x, FRONT_Y - 13, x, FRONT_Y - 1], fill=P("stone2"))
        d.point((x, FRONT_Y - 13), fill=P("stone4"))


def street_lamp(img):
    """手前の街灯：明るい石の色の柱（左が明るい）、腕の先の灯具、円すい形に落ちる光と地面の明るいかたまり、灯に集まる蛾。"""
    px = img.load()
    hx, hy = LAMP_X + 13, 152       # 灯のガラスの中心
    ground = 256
    # 光：灯から地面へ円すい形に広がる（同じ系統で 1 段明るく。ふちは網点）
    for y in range(hy + 3, H):
        spread = (y - hy) * 0.62
        for x in range(int(hx - spread) - 2, int(hx + spread) + 3):
            if not 0 <= x < W:
                continue
            k = 1 - abs(x - hx) / max(1.0, spread)
            fall = max(0.0, 1 - (y - hy) / 150)
            brighten(px, x, y, max(0.0, min(1.0, k * 2.2)) * 0.95 * (0.5 + 0.5 * fall))
    # 地面の明るいかたまり（楕円 2 段、ふちは網点）
    for y in range(ground - 14, H):
        for x in range(hx - 70, hx + 70):
            if not 0 <= x < W:
                continue
            e = ((x - hx) / 62.0) ** 2 + ((y - ground) / 11.0) ** 2
            if e < 1:
                brighten(px, x, y, 1.0 + 1.3 * (1 - e))
    d = ImageDraw.Draw(img)
    # 柱（3 列：左が明るい）と台座
    top = hy - 6
    d.rectangle([LAMP_X, top, LAMP_X + 2, ground], fill=P("stone3"))
    d.line([LAMP_X, top, LAMP_X, ground], fill=P("stone5"))
    d.line([LAMP_X + 2, top, LAMP_X + 2, ground], fill=P("stone2"))
    d.rectangle([LAMP_X - 2, ground - 5, LAMP_X + 4, ground], fill=P("stone2"))
    d.line([LAMP_X - 2, ground - 5, LAMP_X - 2, ground], fill=P("stone4"))
    d.line([LAMP_X - 2, ground - 5, LAMP_X + 4, ground - 5], fill=P("stone4"))
    # 腕（ゆるく曲がる）と灯具（傘＋ガラス）
    for x, y in [(LAMP_X + 1, top - 1), (LAMP_X + 2, top - 2)] + [(LAMP_X + k, top - 3) for k in range(3, 12)]:
        d.point((x, y), fill=P("stone3"))
    for k in range(4, 11):
        d.point((LAMP_X + k, top - 4), fill=P("stone5"))
    d.polygon([(hx - 5, hy - 3), (hx - 3, hy - 6), (hx + 3, hy - 6), (hx + 5, hy - 3)], fill=P("stone2"))
    d.line([hx - 3, hy - 6, hx + 3, hy - 6], fill=P("stone4"))
    d.rectangle([hx - 3, hy - 2, hx + 3, hy + 2], fill=P("warm5"))
    d.rectangle([hx - 3, hy - 2, hx - 2, hy - 1], fill=P("warm6"))
    d.line([hx - 3, hy + 3, hx + 3, hy + 3], fill=P("warm3"))
    for (x, y) in [(hx - 9, hy - 4), (hx + 8, hy + 1), (hx - 6, hy + 7), (hx + 11, hy - 6)]:   # 灯に集まる蛾
        d.point((x, y), fill=P("warm6"))


LOGO_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"  # DejaVu（Bitstream Vera 系の自由なライセンス、docs/CREDITS.md）


def logo():
    """ロゴ「BlueNight」：DejaVu Serif Bold を 30 px でアンチエイリアス無しに描く（拡大しないので 1 ドット＝1 ドット）。
    上は月の明るい色、下は少し青く（光は上から）。まわりに 1 ドットの紺の輪郭、右下に 1 ドットの影。
    フォントが無い環境（Windows など）では、書き出し済みのロゴをそのまま使う。"""
    import os

    from PIL import ImageFont

    if not os.path.exists(LOGO_FONT):
        done = os.path.join(os.path.dirname(__file__), "..", "..", "Assets", "005_Textures", "Title", "title_logo.png")
        return Image.open(done).convert("RGBA")
    font = ImageFont.truetype(LOGO_FONT, 30)
    m = Image.new("L", (190, 40), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = "1"
    d.text((3, 1), "BlueNight", font=font, fill=255)
    m = m.crop(m.getbbox())
    w, h = m.size
    img = Image.new("RGBA", (w + 3, h + 3), CLEAR)
    px, mp = img.load(), m.load()
    dots = [(x + 1, y + 1) for y in range(h) for x in range(w) if mp[x, y]]
    dot_set = set(dots)
    for (x, y) in dots:  # 影（右下）
        if (x + 1, y + 1) not in dot_set:
            px[x + 1, y + 1] = P("night0")
    for (x, y) in dots:  # 輪郭
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if (nx, ny) not in dot_set:
                px[nx, ny] = P("night0")
    top, bottom = min(y for _, y in dots), max(y for _, y in dots)
    split = top + (bottom - top) * 5 // 9
    for (x, y) in dots:
        px[x, y] = P("moon3") if y < split else P("moon2")
    return img


CAR_HEAD = ["WWw"]   # 車の光（右から左へ流れる前照灯）
CAR_TAIL = ["rRR"]   # 左から右へ流れる尾灯


def build_title(save):
    rng = random.Random(11)
    bg = Image.new("RGBA", (W, H), CLEAR)
    sky(bg)
    stars(bg, rng)
    moon(bg)
    clouds(bg)
    far_shore(bg, rng)
    sea(bg, rng)
    far_town(bg, rng)
    highway(bg)
    near_town(bg, rng)
    wires(bg)
    promenade(bg)
    street_lamp(bg)
    # 街灯の下で月を見上げるルリ（背中・影は無い）
    girl = ruri.to_image(ruri.frames("idle", "up")[0])
    bg.alpha_composite(girl, (LAMP_X + 16, 256 - 32))
    # 紺の面どうしの継ぎ目（高架の灯の柱・海の網点）にできる段差のダブりを取る
    out = {"bg": save(bg, "Title", "title_bg.png", clean=True)}
    out["logo"] = save(logo(), "Title", "title_logo.png", clean=True, outline=[RAMPS["night"][0]])
    key = {"W": "moon3", "w": "moon1", "r": "red0", "R": "red2"}
    out["car_head"] = save(from_map(CAR_HEAD, key), "Title", "title_car_head.png")
    out["car_tail"] = save(from_map(CAR_TAIL, key), "Title", "title_car_tail.png")
    out["deck_y"] = deck_y
    return out
