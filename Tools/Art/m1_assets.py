"""M1 プロトタイプ用の素材：ランタン掛け、ランタン、おばあさん、逃げた影、壁、暗がり、調べるアイコン。"""

from PIL import Image, ImageDraw

from palette import RAMPS, color, hex_to_rgba

CLEAR = (0, 0, 0, 0)

# ---------------------------------------------------------------- おばあさん（16x28）
# 光は左上から：髪・顔・カーディガン・スカートとも、影は右下にかたまりで置く。
GRANDMA_KEY = {
    "O": color("night", 1),
    "H": color("stone", 7),
    "h": color("stone", 5),
    "S": color("skin", 2),
    "s": color("skin", 1),
    "m": color("skin", 0),
    "E": color("night", 1),
    "C": color("red", 1),
    "D": color("red", 0),
    "K": color("stone", 3),
    "k": color("stone", 2),
    "F": color("brown", 1),
    "f": color("brown", 2),
    "T": color("brown", 1),  # 杖（体の右側＝影の側にあるので暗い方の色）
}

GRANDMA = [
    "................",
    "......OOO.......",
    ".....OHHHO......",
    ".....OHHhO......",
    "....OOHHHOO.....",
    "...OHHHHHHHO....",
    "...OHHHHHHhhO...",
    "...OHSSSSSShO...",
    "...OSEESSEEsO...",
    "...OSSSSSSSsO...",
    "....OSSmmSsO....",
    "....OOSSSSOO....",
    "...OCCCCCCCDO...",
    "..OCCCCCCCCDDO..",
    "..OCCCCCCCCDDO..",
    "..OCSOCCCCODsOT.",
    "...OOCCCCCDOO.T.",
    "...OKKKKKKKKO.T.",
    "...OKKKKKKKkO.T.",
    "..OKKKKKKKKkO.T.",
    "..OKKKKKKKkkO.T.",
    "..OKKKKKKKkkO.T.",
    "..OKKKKKKkkkO.T.",
    "..OKKKKKKkkkO.T.",
    "...OOOOOOOOOO.T.",
    "....OfFOOfFO..T.",
    "....OFFOOFFO..T.",
    "....OOOOOOOO..O.",
]

# 2 コマ目：ゆっくり呼吸（肩が 1 px 下がる）
GRANDMA_BREATH = GRANDMA[:12] + [
    "...OCCCCCCDDO...",
    "...OCCCCCCDDO...",
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
HOOK = [
    "................",
    "................",
    "......OOOOOOOO..",
    "......OfffffffO.",
    "......OfOOOOOOO.",
    "......OfO....M..",
    "......OfO....M..",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    "......OfO.......",
    ".....OOfOO......",
    ".....OsSSO......",
    ".....OOOOO......",
]
HOOK_KEY = {
    "O": color("night", 1),
    "f": color("brown", 2),  # 腕木の上面と柱の左側は光が当たる明るい色
    "M": color("stone", 5),
    "s": color("stone", 5),
    "S": color("stone", 3),
}


LANTERN = [  # ガラスは左上が明るい（中心から同心円状に明るくしない）
    "..OOOO..",
    ".O....O.",
    "..OOOO..",
    ".OwwwwO.",
    "OOOOOOOO",
    "OyyYYYYO",
    "OyYYYYYO",
    "OYYYYYYO",
    "OYYYYYYO",
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
        out["grandma"][i] = save(img, "Characters", "Grandma", f"grandma_idle_{i}.png", clean=True)

    base = out["grandma"][0]
    out["shadow"] = [silhouette(base, 0), silhouette(base, 1), silhouette(base, 0), silhouette(base, -1)]
    rim = [RAMPS["moon"][0], RAMPS["moon"][1]]  # 逃げた影は水色のふちが輪郭線
    for i, img in enumerate(out["shadow"]):
        out["shadow"][i] = save(img, "Characters", "Shadows", f"shadow_grandma_{i}.png", clean=True, outline=rim)

    out["hook"] = save(from_map(HOOK, HOOK_KEY), "Props", "hook.png", clean=True)
    out["lantern"] = save(from_map(LANTERN, LANTERN_KEY), "Props", "lantern.png", clean=True)
    out["prompt"] = from_map(PROMPT, PROMPT_KEY)
    save(out["prompt"], "UI", "prompt.png")

    out["wall_top"] = build_wall_top()
    save(out["wall_top"], "Tiles", "wall_top.png")
    out["dark"] = build_overlay(150, "#07070f")
    save(out["dark"], "Tiles", "overlay_dark.png")
    out["cast"] = build_overlay(185, "#0b0f26")
    save(out["cast"], "Tiles", "overlay_cast_shadow.png")
    return out
