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

import m1_assets  # noqa: E402
import ruri  # noqa: E402
from palette import RAMPS, color, hex_to_rgba  # noqa: E402

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


def save(img, *path):
    full = os.path.join(TEX, *path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    img.save(full)
    return full


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
    sheets = {}
    for (anim, view), frames in ruri.FRAMES.items():
        imgs = []
        for i, (pose, lift) in enumerate(frames):
            img = from_map(ruri.compose(view, pose, lift), ruri.KEY)
            save(img, "Characters", "Ruri", f"ruri_{anim}_{view}_{i}.png")
            imgs.append(img)
        sheets[(anim, view)] = imgs
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

NEMU_FRAMES = [
    [  # 羽を上げる
        "..O......O..",
        "...O....O...",
        ".OO..OO..OO.",
        "OWWO.BB.OWWO",
        "OWMWOBBOWMWO",
        ".OWWOEEOWWO.",
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
        "OWMwOEEOwMWO",
        ".OWWOBBOWWO.",
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
        "OWMWOBBOWMWO",
        ".OWWOBBOWWO.",
        "..OO.OO.OO..",
        "............",
    ],
]


def build_nemu():
    order = [0, 1, 2, 1]
    imgs = []
    for i, f in enumerate(order):
        img = from_map(NEMU_FRAMES[f], NEMU_KEY)
        save(img, "Characters", "Nemu", f"nemu_fly_{i}.png")
        imgs.append(img)
    return imgs


# ---------------------------------------------------------------- タイル（16x16）
def noise_fill(img, base, accents, density, rng):
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            px[x, y] = base
            if rng.random() < density:
                px[x, y] = rng.choice(accents)


def tile_road(variant):
    rng = random.Random(100 + variant)
    img = Image.new("RGBA", (16, 16))
    noise_fill(img, color("stone", 2), [color("stone", 1), color("stone", 3)], 0.12, rng)
    if variant == 1:  # 小さなひび
        px = img.load()
        for x, y in [(4, 9), (5, 9), (6, 10), (7, 10), (8, 11)]:
            px[x, y] = color("stone", 0)
    return img


def tile_road_line():
    img = tile_road(0)
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 7, 13, 8], fill=color("stone", 6))
    px = img.load()
    for x in (4, 9, 12):  # かすれ
        px[x, 7] = color("stone", 4)
    return img


def tile_sidewalk(variant):
    """歩道の敷石。1 タイル = 1 枚の大きな石板にして、壁（レンガ）に見えないようにする。"""
    rng = random.Random(200 + variant)
    img = Image.new("RGBA", (16, 16))
    noise_fill(img, color("stone", 4), [color("stone", 3), color("stone", 5)], 0.06, rng)
    draw = ImageDraw.Draw(img)
    draw.line([0, 15, 15, 15], fill=color("stone", 3))
    draw.line([15, 0, 15, 15], fill=color("stone", 3))
    draw.line([0, 0, 14, 0], fill=color("stone", 5))
    draw.line([0, 0, 0, 14], fill=color("stone", 5))
    if variant == 1:  # 小さな欠け
        px = img.load()
        for x, y in [(10, 4), (11, 5), (11, 6), (12, 6)]:
            px[x, y] = color("stone", 2)
    return img


def tile_curb():
    img = Image.new("RGBA", (16, 16))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 15, 15], fill=color("stone", 2))
    draw.rectangle([0, 0, 15, 6], fill=color("stone", 5))
    draw.line([0, 0, 15, 0], fill=color("stone", 6))
    draw.rectangle([0, 7, 15, 9], fill=color("stone", 3))
    draw.line([0, 10, 15, 10], fill=color("stone", 1))
    for x in (5, 13):
        draw.line([x, 1, x, 6], fill=color("stone", 4))
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
    # 台座
    d.rectangle([5, 43, 10, 47], fill=pole, outline=outline)
    d.line([6, 44, 6, 46], fill=pole_hi)
    # 柱
    d.rectangle([7, 12, 8, 43], fill=pole)
    d.line([7, 12, 7, 43], fill=pole_hi)
    # 灯具（傘＋ガラス）
    d.polygon([(3, 6), (12, 6), (10, 3), (5, 3)], fill=pole, outline=outline)
    d.rectangle([4, 7, 11, 11], fill=color("warm", 5), outline=outline)
    d.line([5, 8, 10, 8], fill=color("warm", 6))
    d.line([6, 12, 9, 12], fill=outline)
    return img


def build_vending():
    """自販機 16x32（3/4 ビュー：上面＋正面）。"""
    img = Image.new("RGBA", (16, 32), CLEAR)
    d = ImageDraw.Draw(img)
    outline = color("night", 1)
    d.rectangle([0, 0, 15, 31], fill=color("red", 1), outline=outline)
    d.rectangle([1, 1, 14, 3], fill=color("red", 2))  # 上面
    # 商品ケース（光る）
    d.rectangle([2, 5, 13, 15], fill=color("moon", 2), outline=color("red", 0))
    for y in (8, 12):
        d.line([2, y, 13, y], fill=color("moon", 0))
    rng = random.Random(7)
    for y in (6, 9, 13):
        for x in range(3, 13, 2):
            d.point((x, y), fill=rng.choice([color("warm", 3), color("red", 2), color("green", 2), color("scarf", 1)]))
    # ボタンと取り出し口
    d.rectangle([2, 17, 13, 18], fill=color("stone", 6))
    d.rectangle([10, 20, 12, 23], fill=color("night", 2))
    d.rectangle([3, 25, 12, 28], fill=color("night", 1))
    d.line([1, 30, 14, 30], fill=color("red", 0))
    return img


def build_puddle():
    """月が映る水たまり 32x16。地面に置く（ピボットは足元）。"""
    img = Image.new("RGBA", (32, 16), CLEAR)
    d = ImageDraw.Draw(img)
    d.ellipse([0, 2, 31, 15], fill=color("night", 2))
    d.ellipse([2, 3, 29, 14], fill=color("night", 3))
    # 映り込んだ満月
    d.ellipse([17, 5, 24, 10], fill=color("moon", 2))
    d.ellipse([19, 6, 23, 9], fill=color("moon", 3))
    # 水面の揺らぎ
    for x0, y in [(5, 8), (9, 11), (14, 12), (21, 12)]:
        d.line([x0, y, x0 + 3, y], fill=color("night", 5))
    return img


def build_props():
    props = {"lamp": build_lamp(), "vending": build_vending(), "puddle_moon": build_puddle()}
    for name, img in props.items():
        save(img, "Props", f"{name}.png")
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
    scene.alpha_composite(sheets[("walk", "side")][0], (80, 20))
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
    build_previews(palette, sheets, nemu, tiles, props)
    build_m1_preview(tiles, props, m1, sheets, nemu)
    print("done")


if __name__ == "__main__":
    main()
