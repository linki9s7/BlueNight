"""ルリ（16x32 px、4 方向）のピクセルマップ。

頭・胴体・脚をパーツに分けて書き、コマごとに組み合わせる。
横向きは右向きだけを描き、左向きはゲーム側で反転する。

記号:
  .  透明
  O  輪郭（紺）
  H  髪   h 髪・明   k 髪・ハイライト
  S  肌   s 肌・影   m 口・頬
  E  目
  B  マフラー   b マフラー・影   c マフラー・明
  W  コート     w コート・影     v コート・暗
  K  スカート
  T  靴下       t 靴下・影
  F  靴
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
}

# ---------------------------------------------------------------- 下向き（正面）
DOWN_HEAD = [
    "................",
    ".....OOOOOO.....",
    "...OOHHHHHHOO...",
    "..OHhhhHHHHHHO..",
    "..OHkkhHHHHHHO..",
    ".OHHhhHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHSHHHSSHHHO.",
    ".OHHSSSSSSSSHHO.",
    ".OHSESSSSSSESHO.",
    ".OHSESSSSSSESHO.",
    ".OHHmSSSSSSmHHO.",
    "..OHHSSSmSSHHO..",
]

DOWN_BODY = [
    "....ObBBBBbO....",
    "...ObBBcBBBbO...",
    "..OWObBBBBbOWO..",
    "..OWWObBBbOWwO..",
    "..OWWWBbWWWWwO..",
    "..OWWWBbWWWWwO..",
    "..OSWWWbWWWWSO..",
    "..OsOWWWWWWOsO..",
    "...OKKKKKKKKO...",
    "...OKKKKKKKKO...",
    "..OKKKKKKKKKKO..",
    "...OOOOOOOOOO...",
]

DOWN_LEGS = {
    "stand": [
        ".....OSOOSO.....",
        ".....OTOOTO.....",
        ".....OTOOTO.....",
        ".....OTOOTO.....",
        "....OFFOOFFO....",
        "....OOOOOOOO....",
    ],
    "left_up": [
        ".....OSOOSO.....",
        ".....OTOOTO.....",
        ".....OTOOTO.....",
        "....OFFOOTO.....",
        "....OOOOOFFO....",
        "........OOOO....",
    ],
    "right_up": [
        ".....OSOOSO.....",
        ".....OTOOTO.....",
        ".....OTOOTO.....",
        ".....OTOOFFO....",
        "....OFFOOOOO....",
        "....OOOO........",
    ],
}

# ---------------------------------------------------------------- 上向き（背中）
UP_HEAD = [
    "................",
    ".....OOOOOO.....",
    "...OOHHHHHHOO...",
    "..OHHHHHHhhHHO..",
    "..OHHHHHhkkhHO..",
    ".OHHHHHHHhhHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHhHHHHhHHHO.",
    ".OHHhHHHHHHhHHO.",
    "..OHHHHHHHHHHO..",
]

UP_BODY = [
    "....ObBBBBbO....",
    "...OBBBBBBBBO...",
    "..OWObBBBBbOWO..",
    "..OWWOBBBBOWwO..",
    "..OWWWWBbWWWwO..",
    "..OWWWWBbWWWwO..",
    "..OSWWWcbWWWSO..",
    "..OsOWWWWWWOsO..",
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
    "..OHHHHhhhHHHO..",
    "..OHHHHhkkhHHO..",
    ".OHHHHHHhhHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHHHHHHO.",
    ".OHHHHHHHSHHSHO.",
    ".OHHHHHHSSSSSSO.",
    ".OHHHHHHSSSESSO.",
    ".OHHHHHHSSSESSO.",
    ".OHHHHHHsSSSmSO.",
    "..OHHHHHHSSSO...",
]

SIDE_BODY = [
    ".....ObBBBBO....",
    "....ObBBcBBBO...",
    "..bbOWWWWBbO....",
    ".bbOWWWWWWwO....",
    "...OWWWvWWwO....",
    "...OWWWvWWwO....",
    "...OWWWvWWwO....",
    "...OWWWSWWwO....",
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
        "......OTtO......",
        "......OFFFO.....",
        "......OOOOO.....",
    ],
    "stride": [
        ".....OSSSO......",
        "....OtSOOTTO....",
        "...OttO..OTTO...",
        "...OttO...OTTO..",
        "..OFFFO...OFFFO.",
        "..OOOOO...OOOOO.",
    ],
    "stride_alt": [
        ".....OSSSO......",
        "....OTSOOttO....",
        "...OTTO..OttO...",
        "...OTTO...OttO..",
        "..OFFFO...OFFFO.",
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


def all_parts():
    parts = {}
    for view, (head, body, legs) in VIEWS.items():
        parts[f"{view}_head"] = head
        parts[f"{view}_body"] = body
        for name, rows in legs.items():
            parts[f"{view}_legs_{name}"] = rows
    return parts
