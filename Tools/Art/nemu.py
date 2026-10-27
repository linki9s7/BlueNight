"""ネム（ランタンに住みついた、しゃべる蛾）：オオミズアオがモチーフ。v0.16 で B 案「月明かり」の描き方に仕上げた。

オオミズアオ（Actias artemis／aliena）の特徴と、この絵での表し方
- 淡い青緑の大きな羽 → ほのかに光る青緑（palette.py の glow）。膜は少し透ける（不透明度 84%）。
  学名の Actias は月の女神アルテミスにちなむ。BlueNight の「大きな満月」とつながるモチーフ。
- 前羽の前のふちに赤茶の帯、4 枚の羽それぞれに目玉模様（黄色の輪＋透けた窓）、後ろ羽の長い尾（先が黄色）。
- 真っ白でふわふわの体と頭、羽毛のような触角。頭と体は控えめに（美しさは羽の大きさと透明感）。
- **口は描かない**。オオミズアオの成虫には口がない（何も食べず、1 週間ほどで命を終える。CHARACTERS.md・物語の第 4 章）。
  表情は目と触角だけで出す。

描き方（ユーザーの決定：B 案のまま、v0.16）
- 輪郭線を引かず、明暗の差と左上の縁の光で形を見せる（chara.py）。羽の縁は光が透けたように明るい。
- 左右対称なので左半分を描いて反転し、陰影はあとから自動で付ける（光はどちらの羽でも左上から）。
"""

from chara import Canvas, Mat, Style, render
from palette import RAMPS, hex_to_rgba

STYLE = Style("none", rim=True)
WING_ALPHA = 215     # 羽の膜（glow1・glow2）の不透明度。縁の光（glow3）は透けない


def curve(p0, p1, p2, steps=30):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        q = (round(x), round(y))
        if not pts or pts[-1] != q:
            pts.append(q)
    return pts


def dots(c, pts, sym, only=None):
    for (x, y) in pts:
        if 0 <= x < c.w and 0 <= y < c.h and (only is None or c.g[y][x] in only):
            c.g[y][x] = sym


def translucent(img):
    """羽の膜を少しだけ透かす（1 ドット＝1 ドットのまま、後ろの色が混ざるだけ）。"""
    membrane = {hex_to_rgba(RAMPS["glow"][i])[:3] for i in (1, 2)}
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in membrane:
                px[x, y] = (r, g, b, WING_ALPHA)
    return img


# ================================================================ ゲーム内（22x24、4 方向 × 4 コマ）
# v0.17（ユーザーの感想：「ずっと画面を向いて飛んでいるのが不気味」「もう少し親しみやすく」）
# - ルリの向きに合わせて振り向く：正面（down）・背中（up）・横（right／left。左は図を反転してから陰影、flipX は使わない）。
# - 親しみやすく：丸くふわふわの頭、つやのある大きな 2x2 の目、ほおの赤み、くるんと巻いた触角、角の丸い羽。
#   オオミズアオらしさ（透ける青緑の大きな羽・赤茶の帯・目玉模様・外へふくらむ尾）は残す。口は描かない（物語の要）。
SPRITE_W, SPRITE_H = 22, 24
DIRECTIONS = ("down", "up", "right", "left")

# 正面・背中（左半分の形。右は反転）。羽の先は丸める（とがった三角だと怖く見える）
POSES = {
    "spread": {
        "fore": [(9, 9), (6, 5), (2, 2), (0, 3), (0, 9), (2, 13), (6, 14), (9, 13)],
        "hind": [(9, 13), (6, 14), (3, 16), (3, 19), (6, 20), (9, 18)],
        "tail": ((4, 19), (1, 21), (3, 23)),
        "spots": [(3, 7), (5, 17)],
    },
    "up": {
        "fore": [(9, 9), (7, 4), (4, 0), (2, 0), (1, 3), (3, 9), (6, 13), (9, 12)],
        "hind": [(9, 13), (7, 14), (4, 16), (4, 19), (6, 20), (9, 18)],
        "tail": ((5, 19), (2, 21), (4, 23)),
        "spots": [(4, 4), (6, 17)],
    },
    "down": {
        "fore": [(9, 10), (5, 9), (1, 10), (0, 14), (2, 16), (6, 16), (9, 14)],
        "hind": [(9, 14), (7, 16), (4, 18), (4, 20), (7, 21), (9, 19)],
        "tail": ((5, 20), (2, 22), (4, 23)),
        "spots": [(3, 13), (6, 18)],
    },
}

# 横向き（右向きの形。左向きは反転）。v0.17 でオオミズアオの飛ぶ動画（高速度撮影）を参考に描き直した：
# - 体は寝かせず、頭を上に斜めに立てて飛ぶ。
# - 羽ばたきは大きく深い：いちばん上で左右の羽が背中の上で合わさり（細長く立つ）、後ろへ振り下ろして体の下まで下げる。
# - 長い尾は羽より半拍遅れて揺れる（羽を上げるときは下へ垂れ、打ち下ろしたあとに後ろへはね上がる）。
# - 打ち下ろすと体がふわっと浮く（bob：-1 で 1 ドット上）。
# fore＝手前の前羽、hind＝手前の後ろ羽、tail＝尾（付け根・曲がり・先）、band＝赤茶の帯を付けるふち（front＝前、top＝上）。
# 奥の羽は手前の前羽を少し前上へずらした形（一段暗い）。
SIDE_POSES = {
    "top": {   # 羽を上げきる（背中の上で合わさり、頭より高く立つ）。尾は下へ垂れる
        "fore": [(13, 10), (14, 4), (12, 0), (8, 0), (7, 3), (10, 11)],
        "hind": [(12, 12), (9, 6), (5, 7), (6, 12), (10, 14)],
        "tail": ((7, 12), (4, 18), (6, 23)),
        "spots": [(10, 4), (7, 9)],
        "band": "front", "bob": 1,
    },
    "back": {  # 後ろ上へ振り下ろしはじめ
        "fore": [(13, 10), (9, 3), (3, 0), (1, 2), (4, 9), (11, 12)],
        "hind": [(12, 12), (7, 9), (3, 10), (4, 15), (10, 15)],
        "tail": ((5, 14), (2, 18), (3, 23)),
        "spots": [(6, 4), (6, 12)],
        "band": "top", "bob": 0,
    },
    "mid": {   # 真後ろへ大きく広がる
        "fore": [(13, 10), (8, 6), (1, 5), (0, 9), (2, 13), (11, 13)],
        "hind": [(12, 13), (7, 13), (2, 15), (3, 19), (10, 17)],
        "tail": ((3, 18), (0, 20), (1, 23)),
        "spots": [(5, 9), (6, 16)],
        "band": "top", "bob": 0,
    },
    "down": {  # 打ち下ろしきる（羽は体の下）。体は浮き、尾は後ろへはね上がる
        "fore": [(14, 9), (10, 13), (6, 19), (8, 22), (13, 20), (16, 12)],
        "hind": [(12, 13), (8, 14), (4, 17), (6, 20), (11, 17)],
        "tail": ((5, 19), (2, 18), (0, 21)),
        "spots": [(11, 18), (7, 17)],
        "band": "front", "bob": -1,
    },
    "rise": {  # 羽を上げもどす（細く立つ）。尾は遅れて下へ
        "fore": [(13, 10), (13, 5), (10, 1), (7, 2), (8, 7), (12, 12)],
        "hind": [(12, 12), (9, 9), (6, 11), (7, 15), (11, 14)],
        "tail": ((7, 14), (5, 19), (4, 23)),
        "spots": [(10, 5), (8, 12)],
        "band": "front", "bob": 0,
    },
}

FLAP = ("spread", "up", "spread", "down")  # 正面・背中の 4 コマ：広げる → 上げる → 広げる → 下げる
SIDE_FLAP = ("top", "back", "mid", "down", "rise")  # 横向きの 5 コマ（打ち下ろしをなめらかに）

SPRITE_MATS = {
    "W": Mat("glow2", "glow1", "glow3", group="WCy", d=2),    # 前羽
    "V": Mat("glow2", "glow1", "glow3", group="Vy", d=1),     # 後ろ羽と尾（前羽と別の部品：前羽の下のふちに影ができて 2 枚に見える）
    "U": Mat("glow1", "glow0", "glow2", group="Uy", d=1),     # 横向きの奥の羽（体の向こう側なので一段暗い）
    "F": Mat("fluff2", "fluff1", "fluff2", group="FEebf", d=1),  # 白いふわふわの毛
}
SPRITE_DIRECT = {"a": "warm4", "A": "brown2", "y": "warm4", "C": "brown2", "E": "night0", "e": "moon3",
                 "b": "blush0", "f": "fluff1"}

EYE = ["eE", "EE"]   # 2x2 の目。つやは左上（向きを変えても左上のまま）


def band(c, xs):
    """前羽の前のふちの赤茶の帯（各列のいちばん上の前羽）。"""
    for x in xs:
        ys = [y for y in range(c.h) if c.g[y][x] == "W"]
        if ys:
            dots(c, [(x, ys[0])], "C")


def wings_front(c, pose):
    c.poly(pose["hind"], "V")
    dots(c, curve(*pose["tail"], steps=12), "V")   # 尾は外へふくらませてから内へ（まっすぐだと脚に見える）
    c.poly(pose["fore"], "W")
    band(c, range(10))
    for (x, y) in pose["spots"]:
        dots(c, [(x, y)], "y", only="WV")         # 目玉模様（黄色の 1 ドット）
    c.mirror_x(SPRITE_W - 1)


def sprite_front(pose_name, back=False):
    """正面（down）と背中（up）。背中は目とほおが無く、頭の後ろの毛のふさを描く。"""
    c = Canvas(SPRITE_W, SPRITE_H)
    wings_front(c, POSES[pose_name])
    c.ellipse((9, 12, 12, 17), "F")                # おなか（細く短く。白が大きすぎると羽が目立たない）
    dots(c, [(10, 14), (11, 14), (10, 16), (11, 16)], "f")   # おなかの節
    c.ellipse((8, 9, 13, 12), "F")                 # 首まわりのふわふわ
    c.ellipse((7, 3, 14, 9), "F")                  # 丸い頭（大きめ＝親しみやすさ）
    for side in (0, 1):                            # くるんと巻いた触角（先は外へ）
        stem = [(8, 3), (7, 2), (6, 1), (5, 1), (4, 2)]
        if side:
            stem = [(SPRITE_W - 1 - x, y) for (x, y) in stem]
        dots(c, stem[:-1], "a")
        dots(c, stem[-1:], "A")
    if not back:   # 背中は目とほおを描かない（頭は丸い毛のかたまりだけ）
        c.stamp(EYE, 8, 5)
        c.stamp(EYE, 12, 5)
        dots(c, [(7, 8), (14, 8)], "b")            # ほおの赤み（口は描かない）
    return translucent(render(c.rows(), SPRITE_MATS, SPRITE_DIRECT, STYLE))


def front_band(c, rows):
    """横向きで羽が立っているときの帯：羽の先の側の行だけ、いちばん前（右）の前羽（付け根まで引くと線が重い）。"""
    for y in rows:
        xs = [x for x in range(c.w) if c.g[y][x] == "W"]
        if xs:
            dots(c, [(xs[-1], y)], "C")


def ribbon(c, pts, sym):
    """尾：付け根から 6 割は 2 ドット幅（1 ドットだと全部が縁の光の白になって棒に見える）、先は 1 ドット。"""
    line = curve(*pts, steps=16)
    for i, (x, y) in enumerate(line):
        dots(c, [(x, y)], sym)
        if i < len(line) * 0.6:
            dots(c, [(x + 1, y)], sym)


def sprite_side(pose_name, left=False):
    """横向き（体を斜めに立てて飛ぶ）。右向きの図を作り、左向きは図を反転してから陰影を付ける（光は左上のまま）。
    目とほおは反転のあとで置く（つやを左上に保つ）。"""
    pose = SIDE_POSES[pose_name]
    bob = pose["bob"]

    def m(pts):
        return [(x, y + bob) for (x, y) in pts]

    c = Canvas(SPRITE_W, SPRITE_H)
    c.poly([(x + 2, y - 1) for (x, y) in m(pose["fore"])], "U")   # 奥の羽（手前の羽の少し前上、一段暗い）
    c.poly(m(pose["hind"]), "V")
    ribbon(c, m(pose["tail"]), "V")                                # 長い尾（外へふくらんでから戻る）
    c.poly(m([(12, 13), (14, 14), (12, 17), (11, 17)]), "F")       # おなか（斜め下へ、小さく）
    dots(c, m([(12, 15)]), "f")                                    # おなかの節
    c.ellipse((12, 9 + bob, 15, 13 + bob), "F")                    # 胸のふわふわ
    c.poly(m(pose["fore"]), "W")                                   # 手前の前羽は体の上に重なる
    if pose["band"] == "front":
        tip_up = min(y for (_, y) in m(pose["fore"])) < 5
        front_band(c, range(0, 5 + bob) if tip_up else range(14 + bob, SPRITE_H))
    else:
        band(c, range(SPRITE_W))
    for (x, y) in m(pose["spots"]):
        dots(c, [(x, y)], "y", only="WV")
    c.ellipse((13, 5 + bob, 18, 10 + bob), "F")                    # 丸い頭（上の前）
    dots(c, m([(16, 5), (17, 3), (18, 2), (19, 2)]), "a")          # 触角（前へのびて、先は下へ巻く）
    dots(c, m([(20, 3)]), "A")
    dots(c, m([(14, 4), (14, 3), (13, 2)]), "a")                   # 奥の触角
    dots(c, m([(12, 2)]), "A")
    rows = c.rows()
    eye_x, eye_y = 15, 6 + bob
    cheek = (15, 8 + bob)
    if left:
        rows = [r[::-1] for r in rows]
        eye_x = SPRITE_W - 1 - (eye_x + 1)
        cheek = (SPRITE_W - 1 - cheek[0], cheek[1])
    c2 = Canvas(SPRITE_W, SPRITE_H)
    c2.g = [list(r) for r in rows]
    c2.stamp(EYE, eye_x, eye_y)
    dots(c2, [cheek], "b")
    return translucent(render(c2.rows(), SPRITE_MATS, SPRITE_DIRECT, STYLE))


def sprite_frames():
    """{向き: [4 コマ]}。"""
    return {
        "down": [sprite_front(p) for p in FLAP],
        "up": [sprite_front(p, back=True) for p in FLAP],
        "right": [sprite_side(p) for p in SIDE_FLAP],
        "left": [sprite_side(p, left=True) for p in SIDE_FLAP],
    }


# ================================================================ 顔グラフィック（48x48）
# 左側の図形（右側は反転して作る）。実物の標本の、羽を広げた形に合わせる
FOREWING = [(23, 12), (15, 10), (8, 8), (2, 6), (0, 7), (1, 11), (3, 16), (6, 21), (10, 26), (14, 28),
            (19, 26), (23, 21)]
COSTA = [(23, 11), (15, 9), (8, 7), (2, 5), (0, 6), (1, 8), (8, 10), (15, 12), (23, 14)]   # 赤茶の帯
HINDWING = [(23, 20), (15, 23), (9, 27), (6, 32), (7, 36), (11, 38), (17, 37), (21, 33), (23, 28)]
TAIL = [(13, 37), (9, 41), (9, 44), (12, 47)]   # 後ろ羽から外へふくらんで、内へ戻る細い尾（2 ドット幅）

EYESPOT = [   # 目玉模様（5x4）：赤茶の縁・黄色の輪・透けた窓（窓は左上）
    ".cc..",
    "cMMyc",
    "cyyyc",
    ".ccc.",
]

EXPRESSIONS = ("normal", "happy", "surprised", "sleepy")

# 目（左右とも同じ形。つやは左上）。口は描かない
EYES = {
    "normal": [".EE.", "EeEE", "EEEE", ".EE."],
    "happy": ["....", ".EE.", "E..E", "...."],          # にっこり（目を細める）
    "surprised": [".EE.", "EeEE", "EEEE", "EEEE", ".EE."],
    "sleepy": ["....", "....", "EEEE", ".EE."],          # 眠そう（名前の「ネム」）
}
# 触角の軸（頭の左の付け根 → 先）。表情で角度を変える（右は反転）
ANTENNA = {
    "normal": ((20, 9), (17, 2), (10, 2)),
    "happy": ((20, 9), (17, 1), (11, 0)),
    "surprised": ((20, 9), (19, 1), (15, 0)),             # ぴんと立つ
    "sleepy": ((20, 9), (16, 3), (10, 4)),                # 少したれる
}

FACE_MATS = {
    "W": Mat("glow2", "glow1", "glow3", group="WCLcyMv", d=3),
    "V": Mat("glow2", "glow1", "glow3", group="VcyMv", d=3),
    "F": Mat("fluff2", "fluff1", "fluff2", group="FEef", d=2),
}
FACE_DIRECT = {"a": "warm4", "A": "brown2", "y": "warm4", "c": "brown1", "C": "brown2", "L": "glow3",
               "M": ("moon3", 120), "E": "night0", "e": "moon3", "f": "fluff1", "v": "glow1"}


def portrait(expression):
    c = Canvas(48, 48)
    # ---- 左半分：後ろ羽と尾 → 前羽 → 帯 → 羽の筋 → 目玉模様
    c.poly(HINDWING, "V")
    c.line(TAIL, "V", width=2)
    c.poly([(9, 45), (13, 45), (13, 47), (9, 47)], "y", only="V")     # 尾の先の黄色
    c.poly(FOREWING, "W")
    c.poly(COSTA, "C", only="W")
    dots(c, curve((21, 15), (12, 13), (4, 10)), "v", only="W")      # 羽の筋（体から外へ）
    dots(c, curve((21, 19), (14, 20), (7, 21)), "v", only="W")
    dots(c, curve((21, 26), (15, 29), (10, 34)), "v", only="V")
    c.stamp(EYESPOT, 9, 14)
    c.stamp(EYESPOT, 11, 30)
    c.mirror_x(47)
    # ---- 体（白いふわふわ）：胸 → おなか → 首まわりの影 → 頭と頬の毛
    c.ellipse((19, 16, 28, 26), "F")
    c.ellipse((21, 24, 26, 38), "F")
    for (x, y) in [(22, 29), (23, 33)]:
        dots(c, [(x, y), (x + 1, y)], "f")                          # おなかの節
    c.ellipse((18, 17, 29, 22), "f", only="F")
    c.ellipse((17, 7, 30, 20), "F")
    for (x, y) in [(15, 11), (15, 15), (29, 11), (29, 15)]:
        c.ellipse((x, y, x + 3, y + 3), "F")
    # ---- 触角（羽毛：葉の形の毛の中に軸）
    for side in (1, -1):
        stem = curve(*ANTENNA[expression], steps=20)
        blade = []
        n = len(stem)
        for i, (x, y) in enumerate(stem):
            if i % 2:
                continue
            width = 2 if 0.2 < i / n < 0.75 else 1
            blade += [(x - k, y - k) for k in range(1, width + 1)] + [(x + k - 1, y + k) for k in range(1, width + 1)]
        if side == -1:
            stem = [(47 - x, y) for (x, y) in stem]
            blade = [(47 - x, y) for (x, y) in blade]
        dots(c, blade, "A", only=".")
        dots(c, stem, "a")
    # ---- 目（口はない）
    eyes = EYES[expression]
    c.stamp(eyes, 18, 11)
    c.stamp(eyes, 26, 11)
    return translucent(render(c.rows(), FACE_MATS, FACE_DIRECT, STYLE))


def build(save):
    """輪郭線が無いので clean_corners はかけない。"""
    import os
    out = {"sprite": {}, "faces": {}}
    folder = None
    for direction, imgs in sprite_frames().items():
        out["sprite"][direction] = []
        for i, img in enumerate(imgs):
            saved = save(img, "Characters", "Nemu", f"nemu_fly_{direction}_{i}.png")
            out["sprite"][direction].append(saved)
            folder = folder or os.path.dirname(os.path.join(os.path.dirname(__file__), "..", "..", "Assets", "005_Textures",
                                                            "Characters", "Nemu", "x"))
    for i in range(4):  # 向きの無い以前のコマ（nemu_fly_0〜3）を残さない
        for ext in (".png", ".png.meta"):
            old = os.path.join(folder, f"nemu_fly_{i}{ext}")
            if os.path.exists(old):
                os.remove(old)
    for e in EXPRESSIONS:
        out["faces"][e] = save(portrait(e), "Faces", f"face_nemu_{e}.png")
    return out
