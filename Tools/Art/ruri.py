"""ルリ（16x32 px、4 方向）と顔グラフィック（48x48）。v0.16 のリデザイン。

ユーザーと決めたこと（Tools/Art/art_plan.md「人物のリデザイン」、仕様書 7.8）
- 描き方は B 案「月明かり」：輪郭線を引かず、明暗の差と左上の縁の光（月明かり）で形を見せる。
- 色と目は C 案から：紺の髪、大きな青い目（瞳は上が濃く下が明るい、つやは左上）、ほおの小さな赤み。
- 髪は G2 改「ぱっつんロング」：眉の高さで切りそろえた前髪（毛先のすき間から額が少しのぞく）、腰までの髪。
  胸の前へ流すのは向かって左だけ、右は肩の後ろへ。頭の左上に天使の輪。
  **頭の上の左右の小さな角（猫の耳のような寝ぐせ）はチャームポイント。消さないこと。**
- 服は F1「ルームワンピース」：淡い青のコットンのワンピース（ひざ丈・ふくらんだ短いそで・胸の下からギャザー）、
  すそに白いレース。素足に紺のサンダル。夜中に部屋着のまま出てきた 14 歳。青いマフラーはミオの手編み（夏でも巻いている）。
- 静かで大人っぽいのに、まだあどけなさが残る感じ。
- 序章（v0.19、ユーザーの決定）：目を覚ましたときは**パジャマ**（淡いピンクの上下、長そで・長ズボン、白い襟とボタン、はだし）。
  部屋のタンスでワンピースに着がえ、玄関の椅子でマフラーを巻いてから家を出る。パジャマの絵は PAJAMA_VIEWS。

描き方（chara.py）
- 記号の図を書き、陰影は自動で付ける（右下へずらすと部品の外に出る所が影、左上の縁が月明かり）。
- 左向きは記号の図を反転してから陰影を付けるので、光は左上のまま（flipX は使わない）。

記号:
  .  透明
  H  髪          k 髪の筋（暗い）   h 天使の輪（つや）
  S  肌          z 奥の脚（暗い肌）  a 光の側（画面左）の腕。1 ドット幅なので自動の陰影だと全部影になるため、明るい肌のまま
  E  目のふち（上まつげ）   e 目のつや   I 瞳   r ほおの赤み
  B  マフラー
  P  ワンピース  x ギャザーの線     l すそのレース
  F  サンダル    Z 奥の足のサンダル（暗い）
  パジャマ：Q 布   y 白い襟・ボタン・すそ   u 光の側（画面左）のそで（a と同じ理由で明るいまま）
           J 奥の脚のズボン（暗い）   j 奥の脚のすそ（暗い）
"""

from chara import Canvas, Mat, Style, mirror, render

STYLE = Style("none", rim=True)
MATS = {
    "H": Mat("hair2", "hair1", "hair3", group="Hkh", d=2),
    "S": Mat("skin2", "skin1", group="SEeIr"),
    "P": Mat("pj2", "pj1", "pj3", group="Pxl", d=2),
    "l": Mat("tee3", "tee2", group="l"),
    "B": Mat("scarf1", "scarf0", "scarf2", group="B"),
    "F": Mat("hair1", "hair0", "hair2"),
    "Q": Mat("slp2", "slp1", "slp3", group="Qy", d=2),
    "y": Mat("tee3", "tee2", group="y"),
}
DIRECT = {"E": "hair0", "e": "moon3", "I": "iris1", "r": "blush0", "x": "pj1", "k": "hair1", "h": "hair3",
          "z": "skin1", "Z": "hair0", "a": "skin2",
          "u": "slp2", "J": "slp1", "j": "tee2"}

# ---------------------------------------------------------------- 下向き（正面）：頭 15 行・胴 12 行・脚 5 行
DOWN_HEAD = [
    "................",
    "................",
    "...H..HHHH..H...",   # 左右の角＝猫の耳のような寝ぐせ
    "...HHHHHHHHHH...",
    "..HHhhHHHHHHHH..",   # 天使の輪（左上）
    "..HhHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHSHHHHSHHH..",   # ぱっつん前髪。毛先のすき間から額がのぞく
    "...HSEESSEESH...",
    "...HSeISSeISH...",
    "...HSIISSIISH...",
    "...HSrSSSSrSH...",
    "...HHSSSSSSHH...",
    "...HHHHSSHHHH...",
]

DOWN_BODY = [
    "...H.BBBBBB.H...",
    "...HPBBBBBBPH...",
    "...PPPBBBBPPP...",
    "..PPPPPBBPPPPP..",   # ふくらんだ短いそで
    "..aHPPPPPPPP.S..",   # 腕と体のすき間に、胸の前へ流した髪（向かって左）
    "..aHPPxPPxPP.S..",
    "..a.PPxPPxPP.S..",
    "..aPPPxPPxPPPS..",
    "..PPPPxPPxPPPP..",
    "..PPPPPPPPPPPP..",
    ".PPPPPPPPPPPPPP.",
    ".llllllllllllll.",   # すその白いレース
]

DOWN_LEGS = {
    "stand": [".....SS..SS.....", ".....SS..SS.....", ".....SS..SS.....", "....FFF..FFF....", "................"],
    "left_up": [".....SS..SS.....", ".....SS..SS.....", "....FFF..SS.....", ".........FFF....", "................"],
    "right_up": [".....SS..SS.....", ".....SS..SS.....", ".....SS..FFF....", "....FFF.........", "................"],
}

# ---------------------------------------------------------------- 上向き（背中）
UP_HEAD = [
    "................",
    "................",
    "...H..HHHH..H...",
    "...HHHHHHHHHH...",
    "..HHhhHHHHHHHH..",
    "..HhHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "..HHHHHHHHHHHH..",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
    "...HHHHHHHHHH...",
]

UP_BODY = [
    "....HHHHHHHH....",   # 背中へ流れる髪は、毛先へ細くなる
    "....HHHHHHHH....",
    "...PHHHHHHHHP...",
    "..PPHHHkHHHHPP..",
    "..a.HHHkHHHH.S..",
    "..a.HHHHHHHH.S..",
    "..a.PHHHHHHP.S..",
    "..aPPPHHHHPPPS..",
    "..PPPPPPPPPPPP..",
    "..PPPPPPPPPPPP..",
    ".PPPPPPPPPPPPPP.",
    ".llllllllllllll.",
]

UP_LEGS = DOWN_LEGS

# ---------------------------------------------------------------- 横向き（右向き）
SIDE_HEAD = [
    "................",
    "................",
    "..H..HHHH..H....",
    "..HHHHHHHHHH....",
    ".HHhhHHHHHHHH...",
    ".HhHHHHHHHHHHH..",
    ".HHHHHHHHHHHHH..",
    ".HHHHHHHHHHHHH..",
    ".HHHHHHHHHHSHH..",
    "..HHHHHHHSSEES..",
    "..HHHHHHHSSeIS..",
    "..HHHHHHHSSIIS..",
    "..HHHHHHHSrSSS..",
    "..HHHHHHHHSSS...",
    "...HHHHHHSS.....",
]

SIDE_BODY = [
    "...HH.BBBBB.....",
    "...HPPBBBBP.....",
    "...HHPPPPPP.....",
    "...HPPPPPPP.....",
    "...HHPSSPPP.....",
    "....HPSSPxP.....",
    ".....PSSPxP.....",
    ".....PSSPxP.....",
    "....PPPPPPPP....",
    "...PPPPPPPPP....",
    "...PPPPPPPPPP...",
    "..lllllllllll...",
]

SIDE_LEGS = {
    "stand": ["......SS........", "......SS........", "......SS........", "......FFFF......", "................"],
    # 手前の脚（S）が前、奥の脚（z、暗い）がうしろ
    "stride": [".....zzSS.......", "....zz...SS.....", "...zz.....SS....", ".ZZZ......FFFF..", "................"],
    # 手前の脚がうしろ、奥の脚が前
    "stride_alt": [".....SSzz.......", "....SS...zz.....", "...SS.....zz....", ".FFF......ZZZZ..", "................"],
}

VIEWS = {
    "down": (DOWN_HEAD, DOWN_BODY, DOWN_LEGS),
    "up": (UP_HEAD, UP_BODY, UP_LEGS),
    "side": (SIDE_HEAD, SIDE_BODY, SIDE_LEGS),
}

# ---------------------------------------------------------------- パジャマ（序章、着がえるまで）：胴 10 行・脚 7 行
# 上着は胸の下まで、ズボンは足首まで。白い襟とボタン、すそに白い線。はだし。腕の位置はワンピースと同じ（腕の動きを使い回す）。
PJ_DOWN_BODY = [
    "...H...SS...H...",
    "...HQQySSyQQH...",   # 白い襟
    "...QQQQyyQQQQ...",
    "..QQQQQQQQQQQQ..",
    "..uHQQQQyQQQ.Q..",   # 長そで。胸の前へ流した髪（向かって左）。ボタン
    "..uHQQQQQQQQ.Q..",
    "..u.QQQQyQQQ.Q..",
    "..aQQQQQQQQQQS..",   # そで口から手
    "....QQQQQQQQ....",   # ズボン
    "....QQQQQQQQ....",
]
PJ_DOWN_LEGS = {
    "stand": ["....QQQ..QQQ....", "....QQQ..QQQ....", "....QQQ..QQQ....", "....yyy..yyy....",
              ".....SS..SS.....", "....SSS..SSS....", "................"],
    "left_up": ["....QQQ..QQQ....", "....QQQ..QQQ....", "....yyy..QQQ....", ".....SS..yyy....",
                "....SSS..SS.....", ".........SSS....", "................"],
    "right_up": ["....QQQ..QQQ....", "....QQQ..QQQ....", "....QQQ..yyy....", "....yyy..SS.....",
                 ".....SS..SSS....", "....SSS.........", "................"],
}
PJ_UP_BODY = [
    "....HHHHHHHH....",
    "....HHHHHHHH....",
    "...QHHHHHHHHQ...",
    "..QQHHHkHHHHQQ..",
    "..u.HHHkHHHH.Q..",
    "..u.HHHHHHHH.Q..",
    "..u.QHHHHHHQ.Q..",
    "..aQQQHHHHQQQS..",
    "....QQQQQQQQ....",
    "....QQQQQQQQ....",
]
PJ_SIDE_BODY = [
    "...HH....SS.....",
    "...HQQQQySy.....",   # 白い襟
    "...HHQQQQQQ.....",
    "...HQQQQQQQ.....",
    "...HHQuuQQQ.....",   # 体の前の腕（長そで）
    "....HQuuQyQ.....",
    ".....QuuQQQ.....",
    ".....QSSQyQ.....",   # 手
    ".....QQQQQ......",
    ".....QQQQQ......",
]
PJ_SIDE_LEGS = {
    "stand": [".....QQQ........", ".....QQQ........", ".....QQQ........", ".....yyy........",
              "......SS........", "......SSSS......", "................"],
    # 手前の脚（Q）が前、奥の脚（J、暗い）がうしろ
    "stride": [".....JJQQ.......", "....JJ..QQ......", "...JJ....QQ.....", "..jj.....yy.....",
               "..zz......SS....", ".zzz......SSSS..", "................"],
    "stride_alt": [".....QQJJ.......", "....QQ..JJ......", "...QQ....JJ.....", "..yy.....jj.....",
                   "..SS......zz....", ".SSS......zzzz..", "................"],
}
PAJAMA_VIEWS = {
    "down": (DOWN_HEAD, PJ_DOWN_BODY, PJ_DOWN_LEGS),
    "up": (UP_HEAD, PJ_UP_BODY, PJ_DOWN_LEGS),
    "side": (SIDE_HEAD, PJ_SIDE_BODY, PJ_SIDE_LEGS),
}
OUTFITS = {"dress": VIEWS, "pajama": PAJAMA_VIEWS}

# idle・walk：(脚のポーズ, 上半身を持ち上げる px)
FRAMES = {
    ("idle", "down"): [("stand", 0), ("stand", 0), ("stand", 1), ("stand", 0)],
    ("idle", "up"): [("stand", 0), ("stand", 0), ("stand", 1), ("stand", 0)],
    ("idle", "side"): [("stand", 0), ("stand", 0), ("stand", 1), ("stand", 0)],
    ("walk", "down"): [("stand", 0), ("left_up", 1), ("stand", 0), ("right_up", 1)],
    ("walk", "up"): [("stand", 0), ("right_up", 1), ("stand", 0), ("left_up", 1)],
    ("walk", "side"): [("stride", 0), ("stand", 1), ("stride_alt", 0), ("stand", 1)],
}


def compose(view, legs_pose, lift, head_dy=0, crouch=0, lean=0, outfit="dress"):
    """頭・胴・脚を 16x32 の記号の図に組み立てる。

    lift   > 0：上半身を持ち上げ、できた隙間は脚の一番上の行で埋める（歩き・走りの上下動）。
    head_dy> 0：頭だけ下げる（のぞきこむ）。頭が胴の上の行に重なる。
    crouch > 0：すねを crouch 行ぶん縮めて、上半身を下げる（しゃがむ）。
    lean       ：頭を横へずらす（走るときの前のめり）。
    outfit     ："dress"（ワンピース）か "pajama"（序章のパジャマ）。
    """
    head, body, legs = OUTFITS[outfit][view]
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

def body_top_of(view, legs_pose, lift, crouch, outfit="dress"):
    _, body, legs = OUTFITS[outfit][view]
    return 32 - (len(legs[legs_pose]) - crouch) - len(body) - lift


def edit(rows, changes, top, width_pad):
    """changes: [(x, y, 記号)]。y は胴の一番上からの行数。"""
    grid = [list(r) for r in rows]
    for (x, y, ch) in changes:
        yy, xx = top + y, x + width_pad
        if 0 <= yy < len(grid) and 0 <= xx < len(grid[0]):
            grid[yy][xx] = ch
    return ["".join(r) for r in grid]


def mirror_x(changes):
    """正面・背中の絵で、画面右の腕の変更を画面左の腕へ写す（画面左の腕は光の側なので明るい肌 a）。"""
    return [(15 - x, y, "a" if ch == "S" else ch) for (x, y, ch) in changes]


_FRONT_CLEAR = [(13, y, ".") for y in range(4, 8)]   # 体の横に下ろした腕（画面右）を消す
# 正面（下向き）：画面右の腕。ランタンはこちらの手に持つ
ARM_FRONT = {
    "swing": [(13, 7, ".")],                                                      # 手を前へ（腕が短く見える）
    "reach": _FRONT_CLEAR + [(14, 3, "S"), (15, 3, "S"), (16, 3, "S")],           # 腕を横へのばす
    "raise": _FRONT_CLEAR + [(14, 2, "S"), (15, 1, "S"), (15, 0, "S"), (16, -1, "S"), (16, -2, "S")],
}
_SIDE_CLEAR = [(x, y, "P") for x in (6, 7) for y in range(4, 8)]   # 体の前に下ろした腕を消す（下はワンピース）
# 横向き（右向き）：腕は胴の前（6〜7 列）
ARM_SIDE = {
    "swing_fwd": _SIDE_CLEAR + [(7, 4, "S"), (8, 5, "S"), (9, 6, "S"), (10, 6, "S")],
    "swing_back": _SIDE_CLEAR + [(6, 4, "S"), (5, 5, "S"), (4, 6, "S"), (3, 6, "S")],
    "reach": _SIDE_CLEAR + [(8, 3, "S"), (9, 3, "S"), (10, 3, "S"), (11, 3, "S"), (12, 3, "S")],
    "raise": _SIDE_CLEAR + [(9, 2, "S"), (10, 1, "S"), (11, 0, "S"), (11, -1, "S"), (12, -2, "S"), (12, -3, "S")],
}


def arm(view, name):
    """向きと動きの名前から、腕の変更（16 列の座標）を返す。背中向きはランタンを持つ左手（画面左）。"""
    if view == "side":
        return ARM_SIDE[name]
    if view == "up":
        return mirror_x(ARM_FRONT[name])
    return ARM_FRONT[name]


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


def in_sleeves(changes):
    """パジャマの腕：ワンピースの絵の上の変更（腕は肌、消した所はワンピース）を、長そで＋手に置きかえる。
    肌の点のうち最後の 1 つが手（ARM_FRONT・ARM_SIDE はどれも肩から手の順に並べてある）。"""
    skin = [i for i, (_, _, ch) in enumerate(changes) if ch in "Sa"]
    hand = skin[-1] if skin else None
    out = []
    for i, (x, y, ch) in enumerate(changes):
        if ch == "P":
            ch = "Q"
        elif ch in "Sa" and i != hand:
            ch = "u" if ch == "a" else "Q"
        out.append((x, y, ch))
    return out


def action_frame(view, spec, width, outfit="dress"):
    pad = (width - 16) // 2
    rows = compose(view, spec["pose"], spec["lift"], spec["head_dy"], spec["crouch"], spec["lean"], outfit)
    rows = ["." * pad + r + "." * pad for r in rows]
    top = body_top_of(view, spec["pose"], spec["lift"], spec["crouch"], outfit)
    dress = (lambda c: c) if outfit == "dress" else in_sleeves
    if spec["arm"]:
        rows = edit(rows, dress(arm(view, spec["arm"])), top, pad)
    if spec["arm2"] and view != "side":
        other = mirror_x(ARM_FRONT[spec["arm2"]]) if view == "down" else ARM_FRONT[spec["arm2"]]
        rows = edit(rows, dress(other), top, pad)
    return rows


def frames(anim, direction, outfit="dress"):
    """記号の図のコマの一覧。direction は down / up / right / left。左向きは右向きの図を反転したもの。"""
    view = "side" if direction in ("left", "right") else direction
    if (anim, view) in FRAMES:
        result = [compose(view, pose, lift, outfit=outfit) for pose, lift in FRAMES[(anim, view)]]
    else:
        width = 24 if anim in WIDE else 16
        result = [action_frame(view, spec, width, outfit) for spec in ACTIONS[(anim, view)]]
    if direction == "left":
        result = [mirror(rows) for rows in result]
    return result


def without_scarf(rows):
    """マフラーを巻く前（序章、玄関の椅子で手に取るまで）の図：マフラー（B）を、首は肌、胸はワンピースに置きかえる。
    マフラーのいちばん上の行は首：その行のマフラーの真ん中 2 ドットだけ肌にして、ほかは透明（首は細い）。"""
    rows = [list(r) for r in rows]
    top = next((y for y, r in enumerate(rows) if "B" in r), None)
    if top is None:
        return ["".join(r) for r in rows]
    for y, r in enumerate(rows):
        xs = [x for x, ch in enumerate(r) if ch == "B"]
        if not xs:
            continue
        if y == top:
            mid = (xs[0] + xs[-1]) // 2
            for x in xs:
                r[x] = "S" if x in (mid, mid + 1) else "."
        else:
            for x in xs:
                r[x] = "P"
    return ["".join(r) for r in rows]


NO_SCARF_ANIMS = ("idle", "walk", "run", "inspect")   # 序章（部屋の中）で使う動きだけ。パジャマの絵も同じ動きだけ描く


def to_image(rows):
    """記号の図 → 画像（陰影と月明かりの縁取りはここで付く）。"""
    return render(rows, MATS, DIRECT, STYLE)


def all_parts():
    parts = {}
    for view, (head, body, legs) in VIEWS.items():
        parts[f"{view}_head"] = head
        parts[f"{view}_body"] = body
        for name, rows in legs.items():
            parts[f"{view}_legs_{name}"] = rows
    return parts


# ================================================================ 顔グラフィック（48x48）
# 形は B 案（フードは無し）、髪は G2 改、服は F1。眉は前髪のすぐ下に見える（ぱっつん前髪が眉の高さ）。
EXPRESSIONS = ("normal", "gentle", "smile", "sad", "surprised")

# 目（6x6）。左右で形が違う目は (向かって左, 向かって右)。つやはどちらの目も左上。
EYES = {
    "normal": [".EEEE.", "EeeiiE", "EeiiIE", ".iIIo.", ".iIoI.", "..II.."],
    "gentle": ["......", ".EEEE.", "EeeiiE", "EeiIIE", ".iIoI.", "..II.."],          # まぶたを少し下ろした、おだやかな目
    "smile": ["......", ".EEEE.", "EeeiiE", "EiIIoE", ".nnnn.", "......"],           # 下まぶたが上がる
    "sad": (["......", "..EEEE", "EEeii.", ".eiII.", ".iIoI.", "..II.."],            # 目じりが下がる伏し目
            ["......", "EEEE..", ".eeiEE", ".eiII.", ".iIoI.", "..II.."]),
    "surprised": [".EEEE.", "EeeiiE", "EeiIIE", "EiIIoE", ".IIoI.", "..II.."],
}
# 眉（5x2）：(向かって左, 向かって右, 上の行の y)
BROWS = {
    "normal": ([".qqqq", "q...."], ["qqqq.", "....q"], 20),
    "gentle": ([".qqq.", "q...q"], [".qqq.", "q...q"], 20),
    "smile": ([".qqq.", "q...q"], [".qqq.", "q...q"], 20),
    "sad": (["...qq", "qqq.."], ["qq...", "..qqq"], 20),                             # 内側（眉間）が上がる
    "surprised": ([".qqq.", "q...q"], [".qqq.", "q...q"], 19),                       # 少し上がる（前髪にかかる）
}
MOUTHS = {
    "normal": ["mm"],
    "gentle": ["n..n", ".mm."],
    "smile": ["m..m", ".mm."],
    "sad": [".mm.", "n..n"],
    "surprised": ["mm", "mm"],
}
FACE_MATS = {
    "H": Mat("hair2", "hair1", "hair3", group="Hhk", d=3),
    "S": Mat("skin2", "skin1", group="SEeiIormnq", d=2),
    "P": Mat("pj2", "pj1", "pj3", group="Pxl", d=3),
    "l": Mat("tee3", "tee2", "tee3", group="l", d=2),
    "B": Mat("scarf1", "scarf0", "scarf2", d=2),
}
FACE_DIRECT = {"E": "hair0", "e": "moon3", "i": "iris0", "I": "iris1", "o": "iris2", "r": "blush0",
               "m": "skin0", "n": "skin1", "q": "hair1", "k": "hair1", "h": "hair3", "x": "pj1"}
SHOULDERS = [(4, 47), (8, 40), (16, 36), (32, 36), (40, 40), (44, 47)]


def portrait(expression="normal"):
    c = Canvas(48, 48)
    # 服（F1）：肩とふくらんだそで、首まわりと胸の下の白いレース
    c.poly(SHOULDERS, "P")
    c.ellipse((14, 33, 34, 41), "l")
    c.ellipse((16, 33, 32, 39), "P")
    c.rect((6, 42, 42, 42), "l", only="P")
    # 首とマフラー（端は向かって右に垂らす）
    c.rect((20, 29, 27, 37), "S")
    c.poly([(15, 33), (19, 30), (29, 30), (33, 33), (30, 37), (18, 37)], "B")
    c.poly([(26, 35), (31, 35), (32, 47), (26, 47)], "B")
    # 髪（G2 改）
    c.ellipse((10, 3, 38, 33), "H")
    c.poly([(10, 18), (16, 18), (16, 38), (14, 47), (10, 47), (11, 36)], "H")     # 向かって左：胸の前へ細くなる房
    c.poly([(32, 18), (38, 18), (39, 33), (37, 39), (33, 35)], "H")               # 向かって右：肩の後ろへ
    c.line([(13, 24), (13, 38), (12, 45)], "k", only="H")                         # 房の中の暗い筋
    c.ellipse((13, 10, 35, 36), "S")
    c.rect((12, 6, 36, 19), "H", only="S.H")                                      # ぱっつん前髪（眉の高さ）
    for x, y0 in ((19, 17), (27, 18)):                                           # 毛先のすき間から額がのぞく
        c.line([(x, y0), (x, 19)], "S", only="H")
    c.poly([(11, 5), (37, 5), (37, 8), (11, 8)], "H", only=".")                   # 猫の耳のような寝ぐせ（消さないこと）
    c.rect((13, 20, 14, 33), "H")                                                 # 顔の横の髪
    c.rect((34, 20, 35, 31), "H")
    c.line([(13, 13), (17, 10), (23, 9)], "h", only="H")                          # 天使の輪
    # 顔
    left_brow, right_brow, by = BROWS[expression]
    c.stamp(left_brow, 16, by)
    c.stamp(right_brow, 27, by)
    eyes = EYES[expression]
    left, right = eyes if isinstance(eyes, tuple) else (eyes, eyes)
    c.stamp(left, 16, 23)
    c.stamp(right, 26, 23)
    c.stamp(["rr"], 15, 30)
    c.stamp(["rr"], 31, 30)
    mouth = MOUTHS[expression]
    c.stamp(mouth, 24 - len(mouth[0]) // 2, 32)
    return render(c.rows(), FACE_MATS, FACE_DIRECT, STYLE)
