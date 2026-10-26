"""BlueNight のドット絵を書き出す。

使い方（リポジトリのルートで）:
    python3 Tools/Art/build.py

出力:
    Assets/005_Textures/...      Unity に取り込む素材（1 コマ 1 枚の PNG）
    Tools/Art/preview/*.png      確認用の拡大プレビュー
"""

import os
import random
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))

import json  # noqa: E402

import m1_assets  # noqa: E402
import ruri  # noqa: E402
from palette import RAMPS, color, hex_to_rgba  # noqa: E402
from pixel_check import clean_corners  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEX = os.path.join(ROOT, "Assets", "005_Textures")
PREVIEW = os.path.join(ROOT, "Tools", "Art", "preview")

CLEAR = (0, 0, 0, 0)


def from_map(rows, key, width=None):
    width = width or len(rows[0])
    img = Image.new("RGBA", (width, len(rows)), CLEAR)
    px = img.load()
    for y, row in enumerate(rows):
        if len(row) != width:
            raise ValueError(f"row {y} has width {len(row)}, expected {width}: {row!r}")
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if ch not in key:
                raise ValueError(f"unknown symbol {ch!r} in row {y}")
            px[x, y] = key[ch]
    return img


CLEANED = {}  # 絵ごとに clean_corners で取ったダブりの数（report/clean_corners.json に記録）


def save(img, *path, clean=False, outline=None):
    """書き出す。clean=True なら輪郭の段差のダブりを取ってから（Tools/Art/STYLE.md）。"""
    full = os.path.join(TEX, *path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if clean:
        img, removed = clean_corners(img, outline)
        CLEANED["/".join(path)] = removed
    img.save(full)
    return img


def upscale(img, scale):
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)


# ---------------------------------------------------------------- パレット
def build_palette():
    swatch = 8
    ramps = list(RAMPS.values())
    width = max(len(r) for r in ramps)
    img = Image.new("RGBA", (width * swatch, len(ramps) * swatch), CLEAR)
    draw = ImageDraw.Draw(img)
    for y, ramp in enumerate(ramps):
        for x, h in enumerate(ramp):
            draw.rectangle([x * swatch, y * swatch, x * swatch + swatch - 1, y * swatch + swatch - 1], fill=hex_to_rgba(h))
    save(img, "Palette.png")
    return img


# ---------------------------------------------------------------- ルリ
def build_ruri():
    """4 方向（下・上・右・左）。左向きは形だけ反転し、陰影は左上からの光のまま（ruri.relight_mirror）。"""
    folder = os.path.join(TEX, "Characters", "Ruri")
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            if name.endswith(".png"):
                os.remove(os.path.join(folder, name))  # 以前の「side」などを残さない
    sheets = {}
    for anim in ("idle", "walk"):
        for direction in ("down", "up", "right", "left"):
            imgs = []
            for i, rows in enumerate(ruri.frames(anim, direction)):
                img = save(from_map(rows, ruri.KEY), "Characters", "Ruri", f"ruri_{anim}_{direction}_{i}.png", clean=True)
                imgs.append(img)
            sheets[(anim, direction)] = imgs
    return sheets


# ---------------------------------------------------------------- ネム（蛾）
NEMU_KEY = {
    "O": color("night", 2),
    "W": color("warm", 5),
    "w": color("warm", 4),
    "M": color("moon", 1),
    "B": color("brown", 2),
    "E": color("night", 0),
}

NEMU_FRAMES = [  # ゲームでは左右反転しないので、影は右の羽の下側だけ（光は左上から）
    [  # 羽を上げる
        "..O......O..",
        "...O....O...",
        ".OO..OO..OO.",
        "OWWO.BB.OWWO",
        "OWMWOBBOWMwO",
        ".OWWOEEOwwO.",
        "..OOOBBOOO..",
        "....OBBO....",
        ".....OO.....",
        "............",
    ],
    [  # 羽を広げる
        "..O......O..",
        "...O....O...",
        ".....OO.....",
        "OOO.OBBO.OOO",
        "OWWWOBBOWWWO",
        "OWMWOEEOWMwO",
        ".OWWOBBOwwO.",
        "..OOOBBOOO..",
        ".....OO.....",
        "............",
    ],
    [  # 羽を下げる
        "..O......O..",
        "...O....O...",
        ".....OO.....",
        "....OBBO....",
        ".OOOOBBOOOO.",
        "OWWWOEEOWWWO",
        "OWMWOBBOWMwO",
        ".OWWOBBOwwO.",
        "..OO.OO.OO..",
        "............",
    ],
]


def build_nemu():
    order = [0, 1, 2, 1]
    imgs = []
    for i, f in enumerate(order):
        img = save(from_map(NEMU_FRAMES[f], NEMU_KEY), "Characters", "Nemu", f"nemu_fly_{i}.png", clean=True)
        imgs.append(img)
    return imgs


# ---------------------------------------------------------------- タイル（16x16）
# 平らな塗り＋小さな模様。ランダムな点々（ノイズ）で質感を出さない。模様は 2〜3 ドットのかたまりにして、
# 光の当たる左上を明るく、右下を暗くする。

def flat(c):
    return Image.new("RGBA", (16, 16), c)


def pebble(px, x, y, base_ramp_index):
    """2x2 の小石：左上が明るく、右下が暗い。"""
    px[x, y] = color("stone", base_ramp_index + 1)
    px[x + 1, y] = color("stone", base_ramp_index)
    px[x, y + 1] = color("stone", base_ramp_index)
    px[x + 1, y + 1] = color("stone", base_ramp_index - 1)


def tile_road(variant):
    img = flat(color("stone", 2))
    px = img.load()
    for x, y in ([(3, 4), (11, 11)] if variant == 0 else [(12, 3)]):
        pebble(px, x, y, 2)
    if variant == 1:  # 小さなひび（つながった線）
        for x, y in [(3, 8), (4, 8), (5, 9), (6, 9), (7, 10), (8, 10), (8, 11)]:
            px[x, y] = color("stone", 1)
    return img


def tile_road_line():
    img = flat(color("stone", 2))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 7, 13, 8], fill=color("stone", 6))
    px = img.load()
    for x, y in [(9, 8), (10, 8)]:  # すり減った所（かたまり）
        px[x, y] = color("stone", 4)
    pebble(px, 4, 12, 2)
    return img


def tile_sidewalk(variant):
    """歩道の敷石。1 タイル = 1 枚の石板。左上の辺が明るく、右下の目地が暗い。"""
    img = flat(color("stone", 4))
    d = ImageDraw.Draw(img)
    d.line([0, 0, 14, 0], fill=color("stone", 5))
    d.line([0, 0, 0, 14], fill=color("stone", 5))
    d.line([0, 15, 15, 15], fill=color("stone", 3))
    d.line([15, 0, 15, 15], fill=color("stone", 3))
    px = img.load()
    if variant == 1:  # 角の小さな欠け
        for x, y in [(11, 11), (12, 11), (12, 12)]:
            px[x, y] = color("stone", 3)
        px[11, 12] = color("stone", 2)
    else:
        pebble(px, 5, 6, 3)
    return img


def tile_curb():
    img = flat(color("stone", 2))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 15, 6], fill=color("stone", 5))   # 上の面（光が当たる）
    d.line([0, 0, 15, 0], fill=color("stone", 6))
    d.rectangle([0, 7, 15, 9], fill=color("stone", 3))   # 正面
    for x in (5, 13):                                      # 継ぎ目
        d.line([x, 1, x, 6], fill=color("stone", 4))
    pebble(img.load(), 9, 12, 2)
    return img


def build_tiles():
    tiles = {
        "road_0": tile_road(0),
        "road_1": tile_road(1),
        "road_line": tile_road_line(),
        "sidewalk_0": tile_sidewalk(0),
        "sidewalk_1": tile_sidewalk(1),
        "curb": tile_curb(),
    }
    for name, img in tiles.items():
        save(img, "Tiles", f"{name}.png")
    return tiles


# ---------------------------------------------------------------- 小物
def build_lamp():
    """街灯 16x48。足元がピボット。"""
    img = Image.new("RGBA", (16, 48), CLEAR)
    d = ImageDraw.Draw(img)
    pole, pole_hi, outline = color("night", 3), color("night", 5), color("night", 1)
    # 台座（左上につや）
    d.rectangle([5, 43, 10, 47], fill=pole, outline=outline)
    d.line([6, 44, 6, 45], fill=pole_hi)
    # 柱（左の列が明るい）
    d.rectangle([7, 12, 8, 42], fill=pole)
    d.line([7, 12, 7, 42], fill=pole_hi)
    # 灯具（傘＋ガラス）。つやは 1 列の線ではなく、左上の 2x2 のかたまり
    d.polygon([(3, 6), (12, 6), (10, 3), (5, 3)], fill=pole, outline=outline)
    d.rectangle([5, 4, 6, 5], fill=pole_hi)
    d.rectangle([4, 7, 11, 11], fill=color("warm", 5), outline=outline)
    d.rectangle([5, 8, 6, 9], fill=color("warm", 6))
    d.line([6, 12, 9, 12], fill=outline)
    return img


# 自販機 16x32（3/4 ビュー：上面＋正面）。光は左上から：上面が明るく、右の 2 列が影。
# 枠を 1 ドットずつ何重にも重ねる（帯になる）のではなく、部品は輪郭線で区切り、すき間は 2 ドット以上あける。
VENDING = [
    "OOOOOOOOOOOOOOOO",
    "OccccccccccccccO",
    "OccccccccccccccO",
    "ORRRRRRRRRRRRddO",
    "ORRRRRRRRRRRRddO",
    "ORROOOOOOOOOOddO",
    "ORROggggggggOddO",
    "ORROggggggggOddO",
    "ORROYYgPPgmmOddO",
    "ORROnnnnnnnnOddO",
    "ORROggggggggOddO",
    "ORROggggggggOddO",
    "ORROPPgyygYYOddO",
    "ORROnnnnnnnnOddO",
    "ORROnnnnnnnnOddO",
    "ORROOOOOOOOOOddO",
    "ORRRRRRRRRRRRddO",
    "ORRRRRRRRRRRRddO",
    "ORRSSSSSSRRRRddO",
    "ORRSSSSSSRRRRddO",
    "ORRRRRRRRRRRRddO",
    "ORRRRRRRRRkkRddO",
    "ORRRRRRRRRkkRddO",
    "ORRRRRRRRRRRRddO",
    "ORRRRRRRRRRRRddO",
    "ORRKKKKKKKKRRddO",
    "ORRKKKKKKKKRRddO",
    "ORRKKKKKKKKRRddO",
    "ORRRRRRRRRRRRddO",
    "ORRRRRRRRRRRRddO",
    "ORRRRRRRRRRRRddO",
    "OOOOOOOOOOOOOOOO",
]
VENDING_KEY = {
    "O": color("night", 1),
    "c": color("red", 2),
    "R": color("red", 1),
    "d": color("red", 0),
    "g": color("moon", 2),
    "n": color("moon", 0),
    "Y": color("warm", 3),
    "y": color("warm", 5),
    "P": color("red", 2),
    "m": color("moon", 0),
    "S": color("stone", 6),
    "k": color("night", 0),
    "K": color("night", 1),
}


def build_vending():
    return from_map(VENDING, VENDING_KEY)


def build_puddle():
    """月が映る水たまり 32x16。地面に置く（ピボットは足元）。"""
    img = Image.new("RGBA", (32, 16), CLEAR)
    d = ImageDraw.Draw(img)
    d.ellipse([0, 2, 31, 15], fill=color("night", 2))
    d.ellipse([2, 3, 29, 14], fill=color("night", 3))
    # 映り込んだ満月（左上寄り）。同心円に明るくせず、平らな丸＋左上の小さなつや
    d.ellipse([7, 4, 14, 9], fill=color("moon", 2))
    for xy in [(9, 4), (10, 4), (8, 5), (9, 5)]:
        d.point(xy, fill=color("moon", 3))
    # 水面の揺らぎ（ふちから離して置く）
    for x0, y in [(4, 8), (9, 11), (16, 10), (21, 9)]:
        d.line([x0, y, x0 + 3, y], fill=color("night", 5))
    return img


def build_props():
    props = {"lamp": build_lamp(), "vending": build_vending(), "puddle_moon": build_puddle()}
    for name in props:
        props[name] = save(props[name], "Props", f"{name}.png", clean=True)
    return props


# ---------------------------------------------------------------- プレビュー
def build_previews(palette, sheets, nemu, tiles, props):
    os.makedirs(PREVIEW, exist_ok=True)
    upscale(palette, 6).save(os.path.join(PREVIEW, "palette.png"))

    # ルリ全コマ一覧（行 = アニメ×向き、列 = コマ）
    scale = 8
    rows = list(sheets.items())
    cols = max(len(v) for _, v in rows)
    pad = 4
    w = cols * (16 + pad) + pad
    h = len(rows) * (32 + pad) + pad
    sheet = Image.new("RGBA", (w, h), hex_to_rgba(RAMPS["night"][2]))
    for r, (_, imgs) in enumerate(rows):
        for c, img in enumerate(imgs):
            sheet.alpha_composite(img, (pad + c * (16 + pad), pad + r * (32 + pad)))
    upscale(sheet, scale).save(os.path.join(PREVIEW, "ruri_frames.png"))

    # 夜の地面に並べた全体の見え方
    scene = Image.new("RGBA", (160, 90), CLEAR)
    names = ["sidewalk_0", "sidewalk_1"]
    for ty in range(6):
        for tx in range(10):
            if ty == 3:
                tile = tiles["curb"]
            elif ty > 3:
                tile = tiles["road_line"] if ty == 5 and tx % 2 == 0 else tiles["road_0" if (tx + ty) % 3 else "road_1"]
            else:
                tile = tiles[names[(tx * 7 + ty * 3) % 2]]
            scene.alpha_composite(tile, (tx * 16, ty * 16))
    scene.alpha_composite(props["puddle_moon"], (96, 30))
    scene.alpha_composite(props["lamp"], (20, 2))
    scene.alpha_composite(props["vending"], (126, 16))
    scene.alpha_composite(sheets[("idle", "down")][0], (60, 18))
    scene.alpha_composite(sheets[("walk", "right")][0], (80, 20))
    scene.alpha_composite(sheets[("walk", "left")][0], (100, 20))
    scene.alpha_composite(sheets[("idle", "up")][0], (40, 22))
    scene.alpha_composite(nemu[1], (52, 10))
    # 月明かりの青で暗く沈め、街灯の周りだけ明るくした簡易プレビュー
    tint = Image.new("RGBA", scene.size, (40, 55, 120, 120))
    lit = Image.alpha_composite(scene, tint)
    upscale(lit, 6).save(os.path.join(PREVIEW, "scene_mock.png"))


def read_m1_map():
    """C# 側の M1Map.Rows（Assets/002_Scripts/Logic/GridMap.cs）を読み取る。マップの定義は 1 か所だけにする。"""
    import re
    src = open(os.path.join(ROOT, "Assets", "002_Scripts", "Logic", "GridMap.cs"), encoding="utf-8").read()
    block = src[src.index("public static readonly string[] Rows"):]
    block = block[: block.index("};")]
    return re.findall(r'"([^"]+)"', block)


def build_m1_preview(tiles, props, m1, sheets, nemu):
    rows = read_m1_map()
    h, w = len(rows), len(rows[0])
    img = Image.new("RGBA", (w * 16, h * 16), CLEAR)
    alley = set(",HS")
    for ty, row in enumerate(rows):
        for tx, ch in enumerate(row):
            pos = (tx * 16, ty * 16)
            if ch == "#":
                img.alpha_composite(m1["wall_top"], pos)
            elif ch in alley:
                img.alpha_composite(tiles["road_1" if (tx * 3 + ty) % 7 == 0 else "road_0"], pos)
            else:
                img.alpha_composite(tiles["sidewalk_1" if (tx * 5 + ty * 3) % 6 == 0 else "sidewalk_0"], pos)
    # 暗い路地（入口以外）を暗がりで覆う：ゲームでは光の計算で決まる。ここでは目安。
    for ty, row in enumerate(rows):
        for tx, ch in enumerate(row):
            if ch in alley and not (ty == h - 1 - 5):
                img.alpha_composite(m1["dark"], (tx * 16, ty * 16))

    def place(sprite, tx, ty, dx=0, dy=0):
        x = tx * 16 + 8 - sprite.width // 2 + dx
        y = ty * 16 + 16 - sprite.height + dy
        img.alpha_composite(sprite, (x, y))

    for ty, row in enumerate(rows):
        for tx, ch in enumerate(row):
            if ch == "L":
                place(props["lamp"], tx, ty)
            elif ch in "Hh":
                place(m1["hook"], tx, ty)
            elif ch == "V":
                place(props["vending"], tx, ty)
            elif ch == "G":
                place(m1["grandma"][0], tx, ty)
            elif ch == "S":
                place(m1["shadow"][0], tx, ty)
            elif ch == "P":
                place(sheets[("idle", "up")][0], tx, ty)
                place(m1["lantern"], tx, ty, dx=-6, dy=-8)
                place(nemu[1], tx, ty, dx=-12, dy=-24)
    tint = Image.new("RGBA", img.size, (40, 55, 120, 110))
    upscale(Image.alpha_composite(img, tint), 3).save(os.path.join(PREVIEW, "m1_map.png"))

    chars = Image.new("RGBA", (120, 40), hex_to_rgba(RAMPS["night"][2]))
    for i, frame in enumerate(m1["grandma"] + m1["shadow"][:2]):
        chars.alpha_composite(frame, (4 + i * 20, 6))
    chars.alpha_composite(m1["hook"], (86, 10))
    chars.alpha_composite(m1["lantern"], (104, 14))
    chars.alpha_composite(m1["prompt"], (104, 4))
    upscale(chars, 8).save(os.path.join(PREVIEW, "m1_characters.png"))


def main():
    palette = build_palette()
    sheets = build_ruri()
    nemu = build_nemu()
    tiles = build_tiles()
    props = build_props()
    m1 = m1_assets.build(save)
    os.makedirs(os.path.join(ROOT, "Tools", "Art", "report"), exist_ok=True)
    with open(os.path.join(ROOT, "Tools", "Art", "report", "clean_corners.json"), "w", encoding="utf-8") as f:
        json.dump(dict(sorted(CLEANED.items())), f, ensure_ascii=False, indent=1)
    build_previews(palette, sheets, nemu, tiles, props)
    build_m1_preview(tiles, props, m1, sheets, nemu)
    print("done")


if __name__ == "__main__":
    main()
