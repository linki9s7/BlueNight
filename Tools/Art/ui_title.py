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
W, H = 480, 270
HORIZON = 196  # 町の屋根の並ぶ高さ


def sky(img):
    """空：上から night0 → night1 → night2 → night3。境目だけ 2 行の網点。"""
    d = ImageDraw.Draw(img)
    bands = [("night0", 0), ("night1", 46), ("night2", 104), ("night3", 160)]
    for i, (c, y0) in enumerate(bands):
        y1 = bands[i + 1][1] - 1 if i + 1 < len(bands) else H - 1
        d.rectangle([0, y0, W - 1, y1], fill=P(c))
    px = img.load()
    for i in range(1, len(bands)):
        upper, y = bands[i - 1][0], bands[i][1]
        for x in range(W):
            if x % 2 == 0:
                px[x, y] = P(upper)        # 境目の 1 行目は 2 ドットに 1 つ上の色
            if x % 4 == 1:
                px[x, y + 1] = P(upper)    # 2 行目は 4 ドットに 1 つ


def stars(img, rng):
    px = img.load()
    for _ in range(90):
        x, y = rng.randrange(W), rng.randrange(0, 140)
        if px[x, y][:3] in (P("night0")[:3], P("night1")[:3]):
            px[x, y] = P("moon1") if rng.random() < 0.6 else P("night5")
    # 明るい星（十字）をいくつか
    for x, y in [(52, 30), (148, 18), (402, 128), (232, 52), (448, 22)]:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            px[x + dx, y + dy] = P("moon2") if (dx, dy) != (0, 0) else P("moon3")


def moon(img, cx, cy, r):
    """大きな満月：明るい丸＋右下の欠けたような影のかたまり＋左寄りの海（模様）。まわりに 1 段だけの淡い光。"""
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r - 9, cy - r - 9, cx + r + 9, cy + r + 9], fill=P("night3"))  # 光の輪（1 段）
    d.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=P("night4"))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=P("moon3"))
    # 右下の影：月の形を左上へずらした形からはみ出す所
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
    # 海（月の模様）：形のちがう平らなかたまりを左寄りに。顔に見えないよう、横に並べず斜めにつなげる
    sea = [
        (cx - 24, cy - 20, 12, 7), (cx - 16, cy - 15, 10, 9), (cx - 9, cy - 9, 8, 6),
        (cx - 20, cy + 2, 7, 5), (cx - 14, cy + 6, 11, 6), (cx + 2, cy - 26, 6, 4),
    ]
    for (x, y, w, h) in sea:
        d.ellipse([x, y, x + w, y + h], fill=P("moon2"))
    d.ellipse([cx - 13, cy - 12, cx - 9, cy - 9], fill=P("moon1"))  # いちばん濃い所は 1 か所だけ


def far_town(img, rng):
    """遠くの町並み（シルエット）。屋根の高さを変え、ところどころ窓の明かり。"""
    d = ImageDraw.Draw(img)
    x = 0
    while x < W:
        w = rng.choice([14, 18, 22, 26, 30])
        h = rng.choice([10, 14, 18, 24, 30])
        top = HORIZON - h
        d.rectangle([x, top, x + w - 1, H - 1], fill=P("night1"))
        if rng.random() < 0.4:  # 三角屋根
            d.polygon([(x, top), (x + w // 2, top - 6), (x + w - 1, top)], fill=P("night1"))
        for _ in range(rng.choice([0, 1, 1, 2])):
            wx = x + rng.randrange(3, max(4, w - 4))
            wy = top + rng.randrange(4, max(5, h - 2))
            d.rectangle([wx, wy, wx + 1, wy], fill=P("warm4") if rng.random() < 0.7 else P("warm3"))
        x += w


def highway(img):
    """町の上を横切る高架のハイウェイ（左から右へゆるく下る）。"""
    d = ImageDraw.Draw(img)
    def deck_y(x):
        return 150 + x * 18 // W
    # 橋脚
    for x in range(30, W, 76):
        y = deck_y(x)
        d.rectangle([x, y + 8, x + 5, HORIZON + 6], fill=P("night2"))
        d.rectangle([x, y + 8, x + 1, HORIZON + 6], fill=P("night3"))  # 左（光の側）が少し明るい 2 列
    # 道路の床：上のふち（防音壁）＋側面
    for x in range(W):
        y = deck_y(x)
        d.line([x, y - 3, x, y - 1], fill=P("stone2"))   # 防音壁
        d.line([x, y, x, y + 7], fill=P("night2"))       # 床の側面
        d.point((x, y - 4), fill=P("night1"))            # 輪郭
        d.point((x, y + 8), fill=P("night1"))
    # 街灯の列（オレンジの点、2x1）
    for x in range(12, W, 40):
        y = deck_y(x)
        d.rectangle([x, y - 9, x, y - 4], fill=P("night1"))
        d.rectangle([x, y - 10, x + 2, y - 10], fill=P("warm4"))
    return deck_y


def ground_and_lamp(img, lamp_x):
    """手前の歩道と街灯、街灯の下の明るいかたまり。"""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 232, W - 1, H - 1], fill=P("night2"))
    d.rectangle([0, 232, W - 1, 233], fill=P("stone1"))  # 縁石
    # 街灯の光のたまり（楕円を 2 段。ふちは段差のまま）
    d.ellipse([lamp_x - 46, 238, lamp_x + 50, 266], fill=P("stone2"))
    d.ellipse([lamp_x - 26, 243, lamp_x + 30, 262], fill=P("stone3"))
    # 街灯（柱・腕・灯具）
    d.rectangle([lamp_x, 168, lamp_x + 2, 254], fill=P("night1"))
    d.rectangle([lamp_x, 166, lamp_x + 14, 168], fill=P("night1"))
    d.rectangle([lamp_x + 10, 169, lamp_x + 17, 171], fill=P("night1"))
    d.rectangle([lamp_x + 11, 172, lamp_x + 16, 173], fill=P("warm5"))
    d.rectangle([lamp_x + 11, 172, lamp_x + 12, 172], fill=P("warm6"))


LOGO_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"  # DejaVu（Bitstream Vera 系の自由なライセンス、docs/CREDITS.md）


def logo():
    """ロゴ「BlueNight」：DejaVu Serif Bold を 30 px でアンチエイリアス無しに描く（拡大しないので 1 ドット＝1 ドット）。
    上は月の明るい色、下は少し青く（光は上から）。まわりに 1 ドットの紺の輪郭、右下に 1 ドットの影。"""
    from PIL import ImageFont

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
    moon(bg, 338, 74, 40)
    far_town(bg, rng)
    deck_y = highway(bg)
    lamp_x = 104
    ground_and_lamp(bg, lamp_x)
    # 街灯の下で月を見上げるルリ（背中・影は無い）
    girl = Image.new("RGBA", (16, 32), CLEAR)
    gp = girl.load()
    for y, row in enumerate(ruri.frames("idle", "up")[0]):
        for x, ch in enumerate(row):
            if ch != ".":
                gp[x, y] = ruri.KEY[ch]
    bg.alpha_composite(girl, (lamp_x + 16, 254 - 32))
    out = {"bg": save(bg, "Title", "title_bg.png")}
    out["logo"] = save(logo(), "Title", "title_logo.png", clean=True, outline=[RAMPS["night"][0]])
    key = {"W": "moon3", "w": "moon1", "r": "red0", "R": "red2"}
    out["car_head"] = save(from_map(CAR_HEAD, key), "Title", "title_car_head.png")
    out["car_tail"] = save(from_map(CAR_TAIL, key), "Title", "title_car_tail.png")
    out["deck_y"] = deck_y
    return out
