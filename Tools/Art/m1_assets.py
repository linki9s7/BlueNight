"""M1 プロトタイプ用の素材：ランタン掛け、ランタン、おばあさん、逃げた影、壁、暗がり、調べるアイコン。"""

from PIL import Image, ImageDraw

from palette import color, hex_to_rgba

CLEAR = (0, 0, 0, 0)

# ---------------------------------------------------------------- おばあさん（16x28）
GRANDMA_KEY = {
    "O": color("night", 1),
    "H": color("stone", 7),
    "h": color("stone", 5),
    "S": color("skin", 2),
    "s": color("skin", 1),
    "m": color("skin", 0),
    "E": color("night", 1),
    "C": color("red", 0),
    "c": color("red", 1),
    "K": color("stone", 3),
    "k": color("stone", 2),
    "F": color("brown", 1),
    "T": color("brown", 2),
}

GRANDMA = [
    "................",
    "......OOO.......",
    ".....OHHHO......",
    ".....OHhHO......",
    "....OOHHHOO.....",
    "...OHHHHHHHO....",
    "...OHhHHHHhHO...",
    "...OHSSSSSSHO...",
    "...OSEESSEESO...",
    "...OSSSSSSSSO...",
    "....OsSmmSsO....",
    "....OOSSSSOO....",
    "...OCCcCCcCCO...",
    "..OCCCcCCcCCCO..",
    "..OCCCCCCCCCCO..",
    "..OCSOCCCCCOSCO.",
    "..OCSOCCCCCOSTO.",
    "...OOCCCCCCOOTO.",
    "...OKKKKKKKKOT..",
    "...OKKKKKKKKOT..",
    "..OKKKKkKKKKOT..",
    "..OKKKKkKKKKOT..",
    "..OKKKKkKKKKOT..",
    "..OKKKKKKKKKOT..",
    "...OOOOOOOOOOT..",
    "....OFFOOFFO.T..",
    "....OFFOOFFO.T..",
    "....OOOOOOOO.O..",
]

# 2 コマ目：ゆっくり呼吸（肩が 1 px 下がる）
GRANDMA_BREATH = GRANDMA[:12] + [
    "...OCCcCCcCCO...",
    "...OCCcCCcCCO...",
] + GRANDMA[14:]


def from_map(rows, key):
    img = Image.new("RGBA", (len(rows[0]), len(rows)), CLEAR)
    px = img.load()
    for y, row in enumerate(rows):
        assert len(row) == len(rows[0]), f"row {y}: {row!r}"
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = key[ch]
    return img


def silhouette(img, wobble=0):
    """持ち主の形をした「逃げた影」。真っ黒の体に、水色にかすかに光るふち。"""
    w, h = img.size
    out = Image.new("RGBA", (w + 2, h + 2), CLEAR)
    src = img.load()
    filled = set()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] > 0:
                # 下半分を左右にゆらして、影らしい不安定さを出す
                dx = wobble if y > h // 2 and (y // 3) % 2 == 0 else 0
                filled.add((x + 1 + dx, y + 1))
    px = out.load()
    body = color("night", 0)
    rim = color("moon", 0)
    rim_soft = color("moon", 1)
    for (x, y) in filled:
        px[x, y] = body
    for y in range(h + 2):
        for x in range(w + 2):
            if (x, y) in filled:
                continue
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if any(n in filled for n in neighbors):
                px[x, y] = rim if y < (h + 2) // 2 else rim_soft
    return out


# ---------------------------------------------------------------- 小物
def build_hook():
    """ランタン掛け 16x24。木の柱と腕木。足元がピボット。"""
    img = Image.new("RGBA", (16, 24), CLEAR)
    d = ImageDraw.Draw(img)
    outline, wood, wood_hi = color("night", 1), color("brown", 1), color("brown", 2)
    d.rectangle([6, 3, 8, 23], fill=wood, outline=outline)
    d.line([7, 4, 7, 22], fill=wood_hi)
    d.rectangle([8, 3, 13, 5], fill=wood, outline=outline)
    d.line([13, 6, 13, 7], fill=color("stone", 5))  # 金具
    d.rectangle([5, 21, 9, 23], fill=color("stone", 3), outline=outline)
    return img


LANTERN = [
    "..OOOO..",
    ".O....O.",
    "..OOOO..",
    ".OwwwwO.",
    "OOOOOOOO",
    "OwYYYYwO",
    "OwYyyYwO",
    "OwYyyYwO",
    "OwYYYYwO",
    "OOOOOOOO",
    ".OwwwwO.",
    "..OOOO..",
]
LANTERN_KEY = {
    "O": color("night", 1),
    "w": color("night", 4),
    "Y": color("warm", 5),
    "y": color("warm", 6),
}

PROMPT = [
    ".OOOOO.",
    "OWWWWWO",
    ".OWWWO.",
    "..OWO..",
    "...O...",
]
PROMPT_KEY = {"O": color("night", 1), "W": color("moon", 3)}


def build_wall_top():
    """壁・建物の上面 16x16。"""
    img = Image.new("RGBA", (16, 16), color("night", 3))
    d = ImageDraw.Draw(img)
    for y in (3, 7, 11, 15):
        d.line([0, y, 15, y], fill=color("night", 2))
    for i, y in enumerate((0, 4, 8, 12)):
        off = 0 if i % 2 == 0 else 8
        d.line([(off + 3) % 16, y, (off + 3) % 16, y + 2], fill=color("night", 2))
        d.line([(off + 11) % 16, y, (off + 11) % 16, y + 2], fill=color("night", 2))
    d.line([0, 0, 15, 0], fill=color("night", 4))
    return img


def build_overlay(alpha, rgb_hex):
    r, g, b, _ = hex_to_rgba(rgb_hex)
    return Image.new("RGBA", (16, 16), (r, g, b, alpha))


def build(save):
    """save(img, *path) で書き出す。プレビュー用に画像の辞書を返す。"""
    out = {}
    out["grandma"] = [from_map(GRANDMA, GRANDMA_KEY), from_map(GRANDMA_BREATH, GRANDMA_KEY)]
    for i, img in enumerate(out["grandma"]):
        save(img, "Characters", "Grandma", f"grandma_idle_{i}.png")

    base = out["grandma"][0]
    out["shadow"] = [silhouette(base, 0), silhouette(base, 1), silhouette(base, 0), silhouette(base, -1)]
    for i, img in enumerate(out["shadow"]):
        save(img, "Characters", "Shadows", f"shadow_grandma_{i}.png")

    out["hook"] = build_hook()
    save(out["hook"], "Props", "hook.png")
    out["lantern"] = from_map(LANTERN, LANTERN_KEY)
    save(out["lantern"], "Props", "lantern.png")
    out["prompt"] = from_map(PROMPT, PROMPT_KEY)
    save(out["prompt"], "UI", "prompt.png")

    out["wall_top"] = build_wall_top()
    save(out["wall_top"], "Tiles", "wall_top.png")
    out["dark"] = build_overlay(150, "#07070f")
    save(out["dark"], "Tiles", "overlay_dark.png")
    out["cast"] = build_overlay(185, "#0b0f26")
    save(out["cast"], "Tiles", "overlay_cast_shadow.png")
    return out
