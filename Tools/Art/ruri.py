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

# idle・walk：(脚のポーズ, 上半身を持ち上げる px)
FRAMES = {
    ("idle", "down"): [("stand", 0), ("stand", 0), ("stand", 1), ("stand", 0)],
    ("idle", "up"): [("stand", 0), ("stand", 0), ("stand", 1), ("stand", 0)],
    ("idle", "side"): [("stand", 0), ("stand", 0), ("stand", 1), ("stand", 0)],
    ("walk", "down"): [("stand", 0), ("left_up", 1), ("stand", 0), ("right_up", 1)],
    ("walk", "up"): [("stand", 0), ("right_up", 1), ("stand", 0), ("left_up", 1)],
    ("walk", "side"): [("stride", 0), ("stand", 1), ("stride_alt", 0), ("stand", 1)],
}


def compose(view, legs_pose, lift, head_dy=0, crouch=0, lean=0):
    """頭・胴・脚を 16x32 のピクセルマップに組み立てる。

    lift   > 0：上半身を持ち上げ、できた隙間は脚の一番上の行で埋める（歩き・走りの上下動）。
    head_dy> 0：頭だけ下げる（のぞきこむ）。頭が胴の上の行に重なる。
    crouch > 0：すねを crouch 行ぶん縮めて、上半身を下げる（しゃがむ）。
    lean       ：頭を横へずらす（走るときの前のめり）。
    """
    head, body, legs = VIEWS[view]
    leg_rows = legs[legs_pose]
    if crouch:
        leg_rows = leg_rows[:1] + leg_rows[1 + crouch:]
    rows = [["."] * 16 for _ in range(32)]

    def put(src, top, dx=0):
        for i, row in enumerate(src):
            y = top + i
            if not 0 <= y < 32:
                continue
            for x, ch in enumerate(row):
                if ch != "." and 0 <= x + dx < 16:
                    rows[y][x + dx] = ch

    legs_top = 32 - len(leg_rows)
    body_top = legs_top - len(body) - lift
    put(body, body_top)
    put(head, body_top - len(head) + head_dy, lean)
    for i in range(lift):
        put([leg_rows[0]], legs_top - lift + i)
    put(leg_rows, legs_top)
    return ["".join(r) for r in rows]


# ---------------------------------------------------------------- 腕の動き（コマに上から描き足す）
# 座標は 16 列の絵の中の位置。y は「胴の一番上の行」からの行数（lift・crouch に合わせて動く）。
# 新しく描いた腕のまわりには、あとで自動で輪郭をつける（add_outline）。

def body_top_of(view, legs_pose, lift, crouch):
    _, body, legs = VIEWS[view]
    return 32 - (len(legs[legs_pose]) - crouch) - len(body) - lift


def edit(rows, changes, top, width_pad):
    """changes: [(x, y, 記号)]。y は胴の一番上からの行数。"""
    grid = [list(r) for r in rows]
    for (x, y, ch) in changes:
        yy, xx = top + y, x + width_pad
        if 0 <= yy < len(grid) and 0 <= xx < len(grid[0]):
            grid[yy][xx] = ch
    return ["".join(r) for r in grid]


def add_outline(rows, symbols="WwSsBb"):
    """透明の所で、腕（コート・肌）に接する所に輪郭 O をつける。"""
    grid = [list(r) for r in rows]
    h, w = len(grid), len(grid[0])
    out = [r[:] for r in grid]
    for y in range(h):
        for x in range(w):
            if grid[y][x] != ".":
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] in symbols:
                    out[y][x] = "O"
                    break
    return ["".join(r) for r in out]


def mirror_x(changes):
    """正面・背中の絵で、右腕の変更を左腕へ写す（コートの明るさは左が明るい W、右が影 w）。"""
    swap = {"w": "W", "s": "S"}
    return [(15 - x, y, swap.get(ch, ch)) for (x, y, ch) in changes]


# 正面（下向き）：画面右の腕（col 12）。ランタンはこちらの手に持つ
ARM_FRONT = {
    "swing": [(12, 5, "s"), (12, 6, "s"), (12, 7, "O"), (11, 7, "O")],         # 手を前へ（1 ドット上がる）
    "reach": [(12, 6, "w"), (12, 7, "w"), (11, 7, "w"),                          # 体の横の手を消して
              (13, 3, "w"), (14, 3, "w"), (15, 3, "s")],                          # 腕を横へのばす
    "raise": [(12, 6, "w"), (12, 7, "w"), (11, 7, "w"),
              (13, 2, "w"), (14, 1, "w"), (15, 0, "w"), (15, -1, "w"), (15, -2, "s"), (15, -3, "s")],
}
# 横向き（右向き）：手は胴の前（col 7、7 行目）
ARM_SIDE = {
    "swing_fwd": [(7, 7, "W"), (9, 7, "S")],
    "swing_back": [(7, 7, "W"), (5, 7, "S")],
    "reach": [(7, 7, "W"), (13, 4, "W"), (14, 4, "W"), (15, 4, "S")],
    "raise": [(7, 7, "W"), (13, 3, "W"), (14, 2, "W"), (15, 1, "W"), (16, 0, "S"), (16, -1, "S")],
}


def arm(view, name):
    """向きと動きの名前から、腕の変更（16 列の座標）を返す。背中向きはランタンを持つ左手（画面左）。"""
    if view == "side":
        return ARM_SIDE[name]
    if view == "up":
        return mirror_x(ARM_FRONT[name])
    return ARM_FRONT[name]


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


# 動きのコマ：dict(pose=脚のポーズ, lift, head_dy, crouch, lean, arm=腕の動き, arm2=もう一方の腕)
def F(pose="stand", lift=0, head_dy=0, crouch=0, lean=0, arm=None, arm2=None):
    return dict(pose=pose, lift=lift, head_dy=head_dy, crouch=crouch, lean=lean, arm=arm, arm2=arm2)


ACTIONS = {
    # 小走り 6 コマ：大きな上下動、腕を振る。横向きは頭が 1 ドット前へ（前のめり）
    ("run", "down"): [F("left_up", 2, arm="swing"), F("left_up", 1, arm="swing"), F("stand", 0),
                      F("right_up", 2, arm2="swing"), F("right_up", 1, arm2="swing"), F("stand", 0)],
    ("run", "up"): [F("right_up", 2, arm="swing"), F("right_up", 1, arm="swing"), F("stand", 0),
                    F("left_up", 2, arm2="swing"), F("left_up", 1, arm2="swing"), F("stand", 0)],
    ("run", "side"): [F("stride", 1, lean=1, arm="swing_fwd"), F("stride", 2, lean=1, arm="swing_fwd"), F("stand", 1, lean=1),
                      F("stride_alt", 1, lean=1, arm="swing_back"), F("stride_alt", 2, lean=1, arm="swing_back"),
                      F("stand", 1, lean=1)],
    # 調べる 3 コマ：のぞきこむ（頭を下げ、少しかがむ）
    ("inspect", "down"): [F(), F(head_dy=1), F(head_dy=1, crouch=1)],
    ("inspect", "up"): [F(), F(head_dy=1), F(head_dy=1, crouch=1)],
    ("inspect", "side"): [F(), F(head_dy=1, lean=1), F(head_dy=1, crouch=1, lean=1, arm="reach")],
    # ランタンを掛ける 5 コマ：腕を横へ → 上へ（背のびして 1 ドット上がる）→ 横へもどす
    ("hang", "down"): [F(), F(arm="reach"), F(arm="raise"), F(lift=1, arm="raise"), F(arm="reach")],
    ("hang", "up"): [F(), F(arm="reach"), F(arm="raise"), F(lift=1, arm="raise"), F(arm="reach")],
    ("hang", "side"): [F(), F(arm="reach"), F(arm="raise"), F(lift=1, arm="raise"), F(arm="reach")],
    # ランタンを置く 5 コマ：しゃがんで、手を下へのばす
    ("place", "down"): [F(), F(crouch=2, head_dy=1), F(crouch=2, head_dy=1, arm="reach"),
                        F(crouch=2, head_dy=1, arm="reach"), F(crouch=1)],
    ("place", "up"): [F(), F(crouch=2, head_dy=1), F(crouch=2, head_dy=1, arm="reach"),
                      F(crouch=2, head_dy=1, arm="reach"), F(crouch=1)],
    ("place", "side"): [F(), F(crouch=2, head_dy=1, lean=1), F(crouch=2, head_dy=1, lean=1, arm="reach"),
                        F(crouch=2, head_dy=1, lean=1, arm="reach"), F(crouch=1)],
}

ANIMS = ("idle", "walk", "run", "inspect", "hang", "place")
# 腕を体の外へのばす動きは、絵の幅を 24 にする（左右 4 ドットずつ広げる。足元の中心は同じ）
WIDE = {"hang", "place", "inspect"}


def action_frame(view, spec, width):
    pad = (width - 16) // 2
    rows = compose(view, spec["pose"], spec["lift"], spec["head_dy"], spec["crouch"], spec["lean"])
    rows = ["." * pad + r + "." * pad for r in rows]
    top = body_top_of(view, spec["pose"], spec["lift"], spec["crouch"])
    changed = False
    if spec["arm"]:
        rows = edit(rows, arm(view, spec["arm"]), top, pad)
        changed = True
    if spec["arm2"] and view != "side":
        other = mirror_x(ARM_FRONT[spec["arm2"]]) if view == "down" else ARM_FRONT[spec["arm2"]]
        rows = edit(rows, other, top, pad)
        changed = True
    return add_outline(rows) if changed else rows


def frames(anim, direction):
    """direction は down / up / right / left。"""
    view = "side" if direction in ("left", "right") else direction
    if (anim, view) in FRAMES:
        result = [compose(view, pose, lift) for pose, lift in FRAMES[(anim, view)]]
    else:
        width = 24 if anim in WIDE else 16
        result = [action_frame(view, spec, width) for spec in ACTIONS[(anim, view)]]
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
