"""第 1 章の残りの素材：おばあさんの影の動き、影の演出、おばあさんの居眠り、足元の影、環境の動き。

描き方は Tools/Art/STYLE.md のとおり。
- 逃げた影は「真っ黒＋水色のふち」（m1_assets.silhouette）。形は持ち主の絵から作る。
  影には陰影が無い（左右対称の光り方）ので、左向きは右向きの反転でよい。
- 影の動きはドットを拡大・縮小せず、行を足す／抜く・位置をずらすだけで伸び縮みを表す（ミクセルを作らない）。
- 足元の影は、同じドットの格子の上に半透明で重ねる（色を暗くするだけ）。
"""

import math
import random

from PIL import Image, ImageDraw

import townsfolk
from m1_assets import silhouette
from palette import RAMPS, hex_to_rgba

CLEAR = (0, 0, 0, 0)


def P(name, a=255):
    ramp = name.rstrip("0123456789")
    r, g, b, _ = hex_to_rgba(RAMPS[ramp][int(name[len(ramp):])])
    return (r, g, b, a)


def mask_from_rows(rows):
    """'#' の所を黒く塗った画像（影の形の元）。"""
    img = Image.new("RGBA", (len(rows[0]), len(rows)), CLEAR)
    px = img.load()
    for y, row in enumerate(rows):
        assert len(row) == len(rows[0]), f"row {y}: {row!r}"
        for x, ch in enumerate(row):
            if ch == "#":
                px[x, y] = (0, 0, 0, 255)
    return img


# ================================================================ おばあさんの影
# 横向き（右向き）の形：背中を丸め、頭を前へ出し、杖を前につく
GRANDMA_SIDE = [
    "................",
    ".......###......",
    "......#####.....",
    "......#####.....",
    ".....#######....",
    "....#########...",
    "....##########..",
    "....##########..",
    "....##########..",
    "....#########...",
    ".....#######....",
    ".....######.....",
    "...########.....",
    "..##########....",
    "..###########...",
    "..############..",
    "...#########.#..",
    "...########..#..",
    "...#########.#..",
    "..##########.#..",
    "..##########.#..",
    "..##########.#..",
    "..##########.#..",
    "..##########.#..",
    "...########..#..",
    "....###..###.#..",
    "....###..###.#..",
    "....###..###.#..",
]

PAD_TOP = 6  # のび・跳ねる分の余白（全部のコマを同じ大きさにそろえ、足元の位置を変えない）


def shadow_canvas(sil, dy=0):
    """silhouette の結果を、上に余白のある同じ大きさの絵に置く（dy > 0 で上へ）。"""
    w, h = sil.size
    out = Image.new("RGBA", (w, h + PAD_TOP), CLEAR)
    out.alpha_composite(sil, (0, PAD_TOP - dy))
    return out


def stretch_rows(img, at, n):
    """at 行目を n 回くり返して背をのばす（行を足すだけで、ドットの大きさは変わらない）。"""
    w, h = img.size
    out = Image.new("RGBA", (w, h + n), CLEAR)
    out.paste(img.crop((0, 0, w, at)), (0, 0))
    for i in range(n + 1):
        out.paste(img.crop((0, at, w, at + 1)), (0, at + i))
    out.paste(img.crop((0, at + 1, w, h)), (0, at + n + 1))
    return out


def squash_rows(img, at, n):
    """at 行目から n 行を抜いて背を縮める。"""
    w, h = img.size
    out = Image.new("RGBA", (w, h - n), CLEAR)
    out.paste(img.crop((0, 0, w, at)), (0, 0))
    out.paste(img.crop((0, at + n, w, h)), (0, at))
    return out


def bottom_align(img, size):
    out = Image.new("RGBA", size, CLEAR)
    out.alpha_composite(img, ((size[0] - img.width) // 2, size[1] - img.height))
    return out


def brighten_rim(img):
    """ふちの水色を 1 段明るくする（捕まって、ふっと光る）。"""
    out = img.copy()
    px = out.load()
    up = {P("moon0")[:3]: P("moon2"), P("moon1")[:3]: P("moon3")}
    for y in range(out.height):
        for x in range(out.width):
            c = px[x, y]
            if c[3] and c[:3] in up:
                px[x, y] = up[c[:3]]
    return out


def shadow_set(base):
    """1 つの向きの「移動 6 コマ」と、驚く 3 コマ・捕まる 6 コマ。"""
    w, h = base.size
    size = (w + 2, h + 2 + PAD_TOP)
    move = []
    for wob, bob in zip([0, 1, 1, 0, -1, -1], [0, 1, 1, 0, 1, 1]):
        move.append(shadow_canvas(silhouette(base, wob), bob))
    third = h // 3
    surprised = [
        shadow_canvas(silhouette(base, 0)),
        bottom_align(silhouette(stretch_rows(base, third, 3), 0), size),       # びくっと背がのびる
        shadow_canvas(silhouette(base, 0), 4),                                 # 跳び上がる
    ]
    caught = [
        bottom_align(silhouette(squash_rows(base, third, 3), 1), size),        # じたばた：縮む
        bottom_align(silhouette(stretch_rows(base, third, 2), -1), size),      # のびる
        bottom_align(silhouette(squash_rows(base, third, 2), 1), size),
        bottom_align(brighten_rim(silhouette(base, 0)), size),                 # ふっと光って、おとなしくなる
        bottom_align(brighten_rim(silhouette(base, 0)), size),
        shadow_canvas(silhouette(base, 0)),
    ]
    return move, surprised, caught


def grandma_shadow(save):
    front = townsfolk.haru_frames()[0]
    side = mask_from_rows(GRANDMA_SIDE)
    rim = [RAMPS["moon"][0], RAMPS["moon"][1], RAMPS["moon"][2], RAMPS["moon"][3]]
    out = {}
    for direction, base in (("down", front), ("up", front), ("right", side),
                            ("left", side.transpose(Image.FLIP_LEFT_RIGHT))):
        move, surprised, caught = shadow_set(base)
        out[direction] = [save(img, "Characters", "Shadows", f"shadow_grandma_move_{direction}_{i}.png",
                               clean=True, outline=rim) for i, img in enumerate(move)]
        if direction == "down":
            out["surprised"] = [save(img, "Characters", "Shadows", f"shadow_grandma_surprised_{i}.png",
                                     clean=True, outline=rim) for i, img in enumerate(surprised)]
            out["caught"] = [save(img, "Characters", "Shadows", f"shadow_grandma_caught_{i}.png",
                                  clean=True, outline=rim) for i, img in enumerate(caught)]
    return out


# ================================================================ おばあさんの居眠り（影が戻って眠りにつく）
def grandma_doze(save):
    """2 コマ：ふつう／こくりと頭が 1 ドット下がる（絵は townsfolk.py）。"""
    return [save(img, "Characters", "Grandma", f"grandma_doze_{i}.png") for i, img in enumerate(townsfolk.haru_doze_frames())]


# ================================================================ 足元の影（影がある人の足もと）
def foot_shadow(save):
    """影がある人だけ足元に置く、横長の楕円（半透明の紺）。ルリとネムには付けない（影が無い）。"""
    img = Image.new("RGBA", (14, 5), CLEAR)
    ImageDraw.Draw(img).ellipse([0, 0, 13, 4], fill=P("night0", 120))
    return save(img, "Effects", "foot_shadow.png")


# ================================================================ 演出
def ring(img, cx, cy, r, color, dotted=False):
    """1 ドットの輪（dotted なら 1 つおき）。"""
    px = img.load()
    seen = set()
    steps = max(8, int(2 * math.pi * r * 2))
    for i in range(steps):
        a = 2 * math.pi * i / steps
        p = (round(cx + r * math.cos(a)), round(cy + r * math.sin(a)))
        if p in seen:
            continue
        seen.add(p)
        if dotted and len(seen) % 2:
            continue
        if 0 <= p[0] < img.width and 0 <= p[1] < img.height:
            px[p] = color


def fx_capture(save):
    """影を捕まえた瞬間：光の点 → 広がる輪と 8 方向の光の筋 → 消えていく（32x32、6 コマ）。"""
    frames = []
    for f in range(6):
        img = Image.new("RGBA", (32, 32), CLEAR)
        d = ImageDraw.Draw(img)
        c = 15.5
        if f == 0:
            d.rectangle([14, 14, 17, 17], fill=P("moon3"))
            d.rectangle([15, 13, 16, 18], fill=P("moon3"))
            d.rectangle([13, 15, 18, 16], fill=P("moon3"))
        else:
            r = [0, 4, 7, 10, 12, 14][f]
            col = [None, "moon3", "moon2", "moon1", "moon0", "moon0"][f]
            ring(img, c, c, r, P(col), dotted=f >= 4)
            if f <= 3:  # 光の筋（輪の外側に短い線）
                for k in range(8):
                    a = math.pi / 4 * k
                    for t in range(2):
                        p = (round(c + (r + 2 + t) * math.cos(a)), round(c + (r + 2 + t) * math.sin(a)))
                        if 0 <= p[0] < 32 and 0 <= p[1] < 32:
                            img.putpixel(p, P("moon3" if f == 1 else "moon2"))
        frames.append(save(img, "Effects", f"fx_capture_{f}.png"))
    return frames


def fx_return(save):
    """影が持ち主に戻るとき：足元から光のつぶが立ちのぼる（16x32、6 コマ）。"""
    rng = random.Random(5)
    motes = [(rng.randrange(2, 14), rng.randrange(20, 31), rng.choice(["moon3", "moon2", "warm5"])) for _ in range(9)]
    frames = []
    for f in range(6):
        img = Image.new("RGBA", (16, 32), CLEAR)
        px = img.load()
        for i, (x, y0, col) in enumerate(motes):
            y = y0 - f * 4 - (i % 3)
            if not 0 <= y < 32:
                continue
            colour = col if f < 3 else ("moon1" if col != "warm5" else "warm4")
            px[x, y] = P(colour)
            if f < 2 and y + 1 < 32:
                px[x, y + 1] = P("moon1")  # 動き始めは尾を引く
        frames.append(save(img, "Effects", f"fx_return_{f}.png"))
    return frames


def fx_sparkle(save):
    """小さなきらめき（拾えるもの・落とし影の目印、8x8、4 コマ）。"""
    shapes = [
        ["...", ".W.", "..."],
        [".w.", "wWw", ".w."],
        ["..w..", "..W..", "wWWWw", "..W..", "..w.."],
        [".w.", "wWw", ".w."],
    ]
    frames = []
    for f, rows in enumerate(shapes):
        img = Image.new("RGBA", (8, 8), CLEAR)
        o = (8 - len(rows)) // 2
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != ".":
                    img.putpixel((o + x, o + y), P("moon3" if ch == "W" else "moon1"))
        frames.append(save(img, "Effects", f"fx_sparkle_{f}.png"))
    return frames


# ================================================================ 環境の動き
def ripple(save):
    """水たまりの波紋（16x8、4 コマ）。1 ドットの楕円の輪が広がり、広がるほど暗くなって消える。"""
    frames = []
    for f, (box, col) in enumerate([([6, 3, 9, 4], "moon2"), ([4, 2, 11, 5], "night5"),
                                    ([2, 1, 13, 6], "night5"), ([0, 0, 15, 7], "night4")]):
        img = Image.new("RGBA", (16, 8), CLEAR)
        ImageDraw.Draw(img).ellipse(box, outline=P(col))
        if f == 3:  # 最後は輪のところどころを消して、とけるように
            px = img.load()
            for x in range(0, 16, 3):
                for y in range(8):
                    px[x, y] = CLEAR
        frames.append(save(img, "Effects", f"fx_ripple_{f}.png"))
    return frames


def moths(save):
    """街灯に集まる小さな蛾の群れ（24x24、4 コマ）。5 匹が明かりのまわりを回る。羽は 1 コマごとに開閉。"""
    frames = []
    for f in range(4):
        img = Image.new("RGBA", (24, 24), CLEAR)
        px = img.load()
        for k in range(5):
            a = 2 * math.pi * (k / 5 + f / 16) + (k % 2) * 0.6
            r = 6 + (k * 3) % 5
            x = round(11.5 + r * math.cos(a))
            y = round(11.5 + r * 0.7 * math.sin(a))
            open_ = (f + k) % 2 == 0
            dots = [(x - 1, y), (x + 1, y), (x, y)] if open_ else [(x, y), (x, y - 1)]
            for (dx, dy) in dots:
                if 0 <= dx < 24 and 0 <= dy < 24:
                    px[dx, dy] = P("stone7" if (dx, dy) != (x, y) else "warm5")
        frames.append(save(img, "Effects", f"fx_moths_{f}.png"))
    return frames


def build(save):
    out = {"grandma_shadow": grandma_shadow(save), "grandma_doze": grandma_doze(save),
           "foot_shadow": foot_shadow(save), "fx_capture": fx_capture(save), "fx_return": fx_return(save),
           "fx_sparkle": fx_sparkle(save), "fx_ripple": ripple(save), "fx_moths": moths(save)}
    return out
