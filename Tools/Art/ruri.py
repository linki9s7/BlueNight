"""ルリ（16x32 px、4 方向）のピクセルマップ。

頭・胴体・脚をパーツに分けて書き、コマごとに組み合わせる。

描き方のルール（Tools/Art/STYLE.md）
- 光はどの向きの絵でも画面の左上から。影は右下に「かたまり」で置き、輪郭に沿った内側 1 列の影は作らない。
- 左向きは右向きの形を反転して作るが、陰影は反転しない（relight_mirror）。ゲーム側でも flipX は使わない。
- 少ない色数、くっきりした 1 ドットの輪郭、平らな塗り＋小さな模様。

記号:
  .  透明
  O  輪郭（紺）
  H  髪   h 髪・明   k 髪・ハイライト
  S  肌   s 肌・影   m 口
  E  目
  B  マフラー   b マフラー・影   c マフラー・明
  W  コート     w コート・影     v コートのしわ
  K  スカート
  T  靴下       t 靴下・影
  F  靴         f 靴・明
"""

from palette import color

KEY = {
    "O": color("hair", 0),
    "H": color("hair", 1),
    "h": color("hair", 2),
    "k": color("hair", 3),
    "S": color("skin", 2),
    "s": color("skin", 1),
    "m": color("skin", 0),
    "E": color("hair", 0),
    "B": color("scarf", 1),
    "b": color("scarf", 0),
    "c": color("scarf", 2),
    "W": color("coat", 2),
    "w": color("coat", 1),
    "v": color("coat", 0),
    "K": color("night", 3),
    "T": color("stone", 7),
    "t": color("stone", 5),
    "F": color("brown", 1),
    "f": color("brown", 2),
}

# 同じ素材の色のまとまり（左向きを作るときの陰影の付け直しに使う）。先頭が基本の色。
# （コートのしわ v・口 m・目 E は陰影ではなく形なので、ここには入れない）
MATERIALS = ["Hhk", "Ss", "Bbc", "Ww", "Tt", "Ff"]

# ---------------------------------------------------------------- 下向き（正面）
DOWN_HEAD = [
    "................",
    ".....OOOOOO.....",
    "...OOHHHHHHOO...",
    "..OHkhhHHHHHHO..",
    "..OHhhHHHHHHHO..",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHSHHSSHHHO.",
    ".OHHSSSSSSSSHHO.",
    ".OHHSESSSSESHHO.",
    ".OHHSESSSSESHHO.",
    ".OHHSSSSSSssHHO.",
    "..OHHSSSmSsHHO..",
]

DOWN_BODY = [
    "....OBBBBBBO....",
    "...OBBBBBBbbO...",
    "..OWOBBBBbbOwO..",
    "..OWWOBBbbOwwO..",
    "..OWWWWBBWWwwO..",
    "..OWWWWBBWWwwO..",
    "..OSWWWBbwwwsO..",
    "..OSOWWBbwwOsO..",
    "...OKKKKKKKKO...",
    "...OKKKKKKKKO...",
    "..OKKKKKKKKKKO..",
    "...OOOOOOOOOO...",
]

DOWN_LEGS = {
    "stand": [
        ".....OSOOsO.....",
        ".....OTOOtO.....",
        ".....OTOOtO.....",
        ".....OTOOtO.....",
        "....OfFOOFFO....",
        "....OOOOOOOO....",
    ],
    "left_up": [
        ".....OSOOsO.....",
        ".....OTOOtO.....",
        ".....OTOOtO.....",
        "....OfFOOtO.....",
        "....OOOOOFFO....",
        "........OOOO....",
    ],
    "right_up": [
        ".....OSOOsO.....",
        ".....OTOOtO.....",
        ".....OTOOtO.....",
        ".....OTOOFFO....",
        "....OfFOOOOO....",
        "....OOOO........",
    ],
}

# ---------------------------------------------------------------- 上向き（背中）
UP_HEAD = [
    "................",
    ".....OOOOOO.....",
    "...OOHHHHHHOO...",
    "..OHkhhHHHHHHO..",
    "..OHhhHHHHHHHO..",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    "..OHHHOHHOHHHO..",
]

UP_BODY = [
    "....OBBBBBBO....",
    "...OBBBBBBbbO...",
    "..OWOBBBBbbOwO..",
    "..OWWOBBbbOwwO..",
    "..OWWWWBBWWwwO..",
    "..OWWWWBBWWwwO..",
    "..OSWWWBbwwwsO..",
    "..OSOWWBbwwOsO..",
    "...OKKKKKKKKO...",
    "...OKKKKKKKKO...",
    "..OKKKKKKKKKKO..",
    "...OOOOOOOOOO...",
]

UP_LEGS = DOWN_LEGS

# ---------------------------------------------------------------- 横向き（右向き）
SIDE_HEAD = [
    "................",
    ".....OOOOOO.....",
    "...OOHHHHHHOO...",
    "..OHkhhHHHHHHO..",
    "..OHhhHHHHHHHO..",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHSHHSHO.",
    ".OHHHHHHSSSSSSO.",
    ".OHHHHHHSSSESSO.",
    ".OHHHHHHSSSESSO.",
    ".OHHHHHHSSSSmSO.",
    "..OHHHHHHSssO...",
]

SIDE_BODY = [
    ".....OBBBBBO....",
    "..OOOBcBBBBbO...",
    ".OBBBOWWWWBbO...",
    "..OOOWWWWWWwO...",
    "...OWWWvWWwwO...",
    "...OWWWvWwwwO...",
    "...OWWWvWwwwO...",
    "...OWWWSWwwwO...",
    "...OKKKKKKKO....",
    "...OKKKKKKKKO...",
    "..OKKKKKKKKKO...",
    "...OOOOOOOOO....",
]

SIDE_LEGS = {
    "stand": [
        "......OSSO......",
        "......OTTO......",
        "......OTTO......",
        "......OTTO......",
        "......OfFFO.....",
        "......OOOOO.....",
    ],
    "stride": [
        ".....OSSSO......",
        "....OtsOOTTO....",
        "...OttO..OTTO...",
        "...OttO...OTTO..",
        "..OFFFO...OfFFO.",
        "..OOOOO...OOOOO.",
    ],
    "stride_alt": [
        ".....OSSSO......",
        "....OTSOOttO....",
        "...OTTO..OttO...",
        "...OTTO...OttO..",
        "..OfFFO...OFFFO.",
        "..OOOOO...OOOOO.",
    ],
}

VIEWS = {
    "down": (DOWN_HEAD, DOWN_BODY, DOWN_LEGS),
    "up": (UP_HEAD, UP_BODY, UP_LEGS),
    "side": (SIDE_HEAD, SIDE_BODY, SIDE_LEGS),
}

# (脚のポーズ, 上半身を持ち上げる px)
FRAMES = {
    ("idle", "down"): [("stand", 0), ("stand", 0), ("stand", 1), ("stand", 0)],
    ("idle", "up"): [("stand", 0), ("stand", 0), ("stand", 1), ("stand", 0)],
    ("idle", "side"): [("stand", 0), ("stand", 0), ("stand", 1), ("stand", 0)],
    ("walk", "down"): [("stand", 0), ("left_up", 1), ("stand", 0), ("right_up", 1)],
    ("walk", "up"): [("stand", 0), ("right_up", 1), ("stand", 0), ("left_up", 1)],
    ("walk", "side"): [("stride", 0), ("stand", 1), ("stride_alt", 0), ("stand", 1)],
}


def compose(view, legs_pose, lift):
    """頭・胴・脚を 16x32 のピクセルマップに組み立てる。

    lift > 0 のときは上半身を持ち上げ、できた隙間は脚の一番上の行で埋める（歩きの上下動）。
    """
    head, body, legs = VIEWS[view]
    leg_rows = legs[legs_pose]
    upper = head + body  # 26 行
    rows = ["." * 16] * 32
    top = 0 - lift
    for i, row in enumerate(upper):
        y = top + i
        if 0 <= y < 32:
            rows[y] = row
    for i in range(lift):
        rows[26 - lift + i] = leg_rows[0]
    for i, row in enumerate(leg_rows):
        rows[26 + i] = row
    return rows


def material_of(symbol):
    for group in MATERIALS:
        if symbol in group:
            return group
    return None


def relight_mirror(rows):
    """
    左右反転した絵を作る。ただし陰影は反転しない（光は常に画面の左上から）。
    形は反転し、素材の色（髪・肌・コートなど）は「反転前の同じ位置が同じ素材ならその陰影の色」を使い、
    違う素材なら基本の色にする（光の当たる側に来た影は消える）。目・口・輪郭などはそのまま反転する。
    """
    mirrored = [row[::-1] for row in rows]
    out = []
    for y, row in enumerate(mirrored):
        line = []
        for x, symbol in enumerate(row):
            group = material_of(symbol)
            if group is None:
                line.append(symbol)
                continue
            original = rows[y][x]
            line.append(original if original in group else group[0])
        out.append("".join(line))
    return out


def frames(anim, direction):
    """direction は down / up / right / left。"""
    view = "side" if direction in ("left", "right") else direction
    result = [compose(view, pose, lift) for pose, lift in FRAMES[(anim, view)]]
    if direction == "left":
        result = [relight_mirror(rows) for rows in result]
    return result


def all_parts():
    parts = {}
    for view, (head, body, legs) in VIEWS.items():
        parts[f"{view}_head"] = head
        parts[f"{view}_body"] = body
        for name, rows in legs.items():
            parts[f"{view}_legs_{name}"] = rows
    return parts
