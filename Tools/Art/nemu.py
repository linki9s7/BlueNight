"""ネム（ランタンに住みついた、しゃべる蛾）のゲーム内スプライトと顔グラフィック。

デザイン（v0.12、ユーザーの依頼：オリジナリティがあって妖艶で有機的に）
- 月明かりの鱗粉のような青みの銀色の羽（世界の色に合わせる。紫は不採用）。
  後ろ羽は「オナガミズアオ」や「コメットモス」のように長い尾になって、ひらひらと後を引く。
- 前羽には金色の目玉模様（ランタンの火の色）。羽の筋（翅脈）は体から外へ曲線で流れる。
- 首にはクリーム色のふわふわの毛（襟巻きのよう）。頭はビロードのような暗い色。
- 触角は羽毛のような櫛形（蛾らしさ）。
- 目は暗い大きな複眼で、ランタンの光を受けると金色に光る（実際の蛾の「目の照り返し」）。
  顔グラフィックでは半分まぶたを下ろした、あやしく笑う目。
- 光は左上から。影は各部品の右下にかたまりで置く（STYLE.md）。
"""

import math

from PIL import Image, ImageDraw

from palette import RAMPS, hex_to_rgba
from portrait import Portrait, edge_mask, ellipse, minus, polygon, union

CLEAR = (0, 0, 0, 0)


def P(name):
    ramp = name.rstrip("0123456789")
    return hex_to_rgba(RAMPS[ramp][int(name[len(ramp):])])


SPOT = "warm4"  # 目玉模様の色

# ================================================================ ゲーム内（20x18、4 コマ）
SPRITE_KEY = {
    "O": "moth0",
    "W": "moth3",   # 羽
    "w": "moth2",   # 羽の影（右下のかたまり：自動）
    "Y": "warm4",   # 目玉模様・触角
    "T": "moth4",   # 尾
    "c": "moth1",   # 頭（ビロード）
    "E": "warm5",   # 光る目
    "F": "warm5",   # 首のふわふわ
    "B": "moth4",   # 胴
    "b": "moth3",   # 胴の節
}

SPRITE_FRAMES = {
    "up": [  # 羽を上げる
        "OWO..............OWO",
        "OWWO.Y........Y.OWWO",
        ".OWWO.Y.OOOO.Y.OWWO.",
        ".OWYWO.OEccEO.OWYWO.",
        "..OYOWOOccccOOWOYO..",
        "..OWYWWOOccOOWWYWO..",
        "...OWWWOFFFFOWWWO...",
        "...OWWWOFFFFOWWWO...",
        "..OWWWWOOBBOOWWWWO..",
        "..OWWWWOBbbBOWWWWO..",
        "...OWWWWOBBOWWWWO...",
        "...OWWYWOBbOWYWWO...",
        "....OWWWOBBOWWWO....",
        "....OWTOOOOOOTWO....",
        "....OTTO....OTTO....",
        "...OTO........OTO...",
        "...OTO........OTO...",
        "....O..........O....",
    ],
    "spread": [  # 羽を広げる
        "..Y..............Y..",
        "...Y............Y...",
        "OO..Y..OOOOOO..Y..OO",
        "OWOO.Y.OEccEO.Y.OOWO",
        "OWWWOOYOccccOYOOWWWO",
        "OWYYWWOOOccOOOWWYYWO",
        "OWYOYWWOFFFFOWWYOYWO",
        "OWWYYWWOFFFFOWWYYWWO",
        ".OWWWWWOOBBOOWWWWWO.",
        "..OOWWWOBbbBOWWWOO..",
        "...OWWWWOBBOWWWWO...",
        "...OWWYWOBbOWYWWO...",
        "....OWWWOBBOWWWO....",
        "....OWTOOOOOOTWO....",
        "...OTTO......OTTO...",
        "...OTO........OTO...",
        "..OTO..........OTO..",
        "..OO............OO..",
    ],
    "down": [  # 羽を下げる（尾が外へふれる）
        "...Y............Y...",
        "....Y..........Y....",
        ".....Y..OOOO..Y.....",
        "......YOEccEOY......",
        ".OOOOOOOccccOOOOOOO.",
        "OWWWWWWWOccOWWWWWWWO",
        "OWYYWWWOFFFFOWWWYYWO",
        "OWYOYWWOFFFFOWWYOYWO",
        "OWWYYWWOOBBOOWWYYWWO",
        ".OWWWWWOBbbBOWWWWWO.",
        "..OOWWWOBBBBOWWWOO..",
        "...OWWWWOBbOWWWWO...",
        "...OWWYWOBBOWYWWO...",
        "...OWWWOOOOOOWWWO...",
        "..OTTWO......OWTTO..",
        ".OTTO..........OTTO.",
        ".OTO............OTO.",
        ".OO..............OO.",
    ],
}


def sprite(name):
    rows = SPRITE_FRAMES[name]
    w = len(rows[0])
    img = Image.new("RGBA", (w, len(rows)), CLEAR)
    px = img.load()
    wing = set()
    for y, row in enumerate(rows):
        assert len(row) == w, f"{name} row {y}: {row!r} ({len(row)})"
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = P(SPRITE_KEY[ch])
            if ch == "W":
                wing.add((x, y))
    # 羽の影：右下へ 2 ドットずらすと羽の外に出る所（右下のふちのかたまり）
    for (x, y) in wing:
        if (x + 2, y + 2) not in wing:
            px[x, y] = P("moth2")
    return img


def sprite_frames():
    """4 コマ：広げる → 上げる → 広げる → 下げる。"""
    return [sprite("spread"), sprite("up"), sprite("spread"), sprite("down")]


# ================================================================ 顔グラフィック（48x48）
def curve(p0, p1, p2, steps=24):
    """2 次ベジェ曲線の点（整数、重複なし）。"""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        q = (round(x), round(y))
        if not pts or pts[-1] != q:
            pts.append(q)
    return pts


def mirror_points(pts):
    return [(47 - x, y) for (x, y) in pts]


def plot(img, pts, color):
    px = img.load()
    for (x, y) in pts:
        if 0 <= x < 48 and 0 <= y < 48:
            px[x, y] = P(color)


# 前羽：先がかぎ状に曲がった形（外のふちは内側へゆるくへこむ）
LEFT_FOREWING = [(22, 16), (16, 11), (9, 7), (3, 4), (0, 5), (0, 9), (2, 13), (3, 17), (6, 21), (11, 24),
                 (17, 25), (22, 23)]
# 後ろ羽：丸い羽から、長い尾が S 字に流れる（尾は別に描く）
LEFT_HINDWING = [(21, 23), (15, 25), (10, 28), (8, 32), (10, 36), (14, 37), (18, 35), (22, 30)]
# 尾：後ろ羽の下のふちから続く、先へ細くなるリボン（外側の曲線と内側の曲線の間を塗る）。
# 細い線 2 本にすると脚に見えるので、根元を羽と同じ幅にして「羽の続き」に見せる
LEFT_TAIL_OUTER = ((8, 33), (1, 40), (3, 48))
LEFT_TAIL_INNER = ((15, 36), (8, 41), (6, 48))


def nemu_portrait(expression):
    pt = Portrait()
    # ---- 尾 → 後ろ羽 → 前羽 の順に、左右とも右下に影
    for side in (1, -1):
        outer, inner = curve(*LEFT_TAIL_OUTER), curve(*LEFT_TAIL_INNER)
        poly = outer + inner[::-1]
        if side == -1:
            poly = mirror_points(poly)
        tail = polygon(poly)
        pt.part(tail, "moth3", shade="moth2", shade_d=(2, 2))
        tip = polygon([(0, 43), (12, 43), (12, 48), (0, 48)] if side == 1 else mirror_points([(0, 43), (12, 43), (12, 48), (0, 48)]))
        from PIL import ImageChops
        pt.fill(minus(ImageChops.multiply(tail, tip), edge_mask(tail, 2, 2)), "moth4")  # 先は光を含んだ明るい色
    for poly in (LEFT_HINDWING, mirror_points(LEFT_HINDWING)):
        pt.part(polygon(poly), "moth2", shade="moth1", shade_d=(3, 3))
    for poly in (LEFT_FOREWING, mirror_points(LEFT_FOREWING)):
        m = polygon(poly)
        # 外のふちを波形にけずる（有機的な羽のふち）
        for (sx, sy) in ((1, 11), (3, 16), (6, 20)):
            if poly is not LEFT_FOREWING:
                sx = 47 - sx
            m = minus(m, ellipse([sx - 2, sy - 1, sx, sy + 1]) if poly is LEFT_FOREWING else ellipse([sx, sy - 1, sx + 2, sy + 1]))
        pt.part(m, "moth3", shade="moth2", shade_d=(3, 3))
    # 前羽の前のふち（光の当たる上の辺）を明るく：上のふちだけ、2 ドット幅のかたまり
    for poly in (LEFT_FOREWING, mirror_points(LEFT_FOREWING)):
        m = polygon(poly)
        top = minus(m, _shift(m, 0, 2))
        pt.fill(minus(top, edge_mask(m, 3, 3)), "moth4")
    # 羽の筋（体から外へ流れる曲線）
    veins = [
        curve((20, 20), (12, 12), (4, 6)),
        curve((20, 22), (11, 17), (3, 13)),
        curve((20, 24), (12, 22), (6, 20)),
        curve((21, 27), (15, 28), (10, 31)),
    ]
    for v in veins:
        plot(pt.img, v, "moth2")
        plot(pt.img, mirror_points(v), "moth2")
    # 目玉模様（前羽）：金の輪＋暗いひとみ＋左上のつや。後ろ羽には小さな金の点
    for (cx, cy) in ((9, 12), (38, 12)):
        pt.fill(ellipse([cx - 3, cy - 3, cx + 3, cy + 3]), SPOT)
        pt.fill(ellipse([cx - 1, cy - 1, cx + 2, cy + 2]), "moth0")
        pt.img.load()[cx - 1, cy - 1] = P("warm6")
    for (cx, cy) in ((13, 32), (34, 32)):
        pt.fill(ellipse([cx - 1, cy - 1, cx + 1, cy + 1]), SPOT)
    # ---- 胴（後ろ羽の間にのぞく）
    body = ellipse([20, 26, 27, 41])
    pt.part(body, "moth4", shade="moth3", shade_d=(2, 2))
    for y in (30, 33, 36):
        plot(pt.img, [(x, y) for x in range(21, 27)], "moth3")
    # ---- 首のふわふわ（襟巻き）：ふちを波形にしたクリーム色
    # 下のふちは大きさのちがう毛のかたまりを並べて、ふぞろいに
    tufts = [(14, 21, 4), (17, 23, 4), (21, 24, 3), (24, 24, 4), (27, 23, 4), (30, 21, 4)]
    ruff = union(ellipse([15, 17, 32, 26]), *[ellipse([x, y, x + r, y + r]) for (x, y, r) in tufts])
    pt.part(ruff, "warm6", shade="warm5", shade_d=(3, 3))
    for x in range(16, 31, 4):  # 毛の流れ（短い線）
        plot(pt.img, [(x + 1, 22), (x + 2, 23)], "warm5")
    # ---- 頭（ビロードのような暗い色）
    head = ellipse([15, 5, 32, 21])
    pt.part(head, "moth2", shade="moth1", shade_d=(3, 3))
    # 目のまわりの明るい毛（顔の表情が読めるように）
    pt.fill(ellipse([18, 13, 29, 20]), "moth3")
    pt.fill(minus(minus(head, _shift(head, 0, 2)), edge_mask(head, 3, 3)), "moth3")  # 頭の上のつや
    # ---- 触角（羽毛のような形）。根元から外へ大きく曲がり、両側に細い毛。先へ行くほど毛が短い
    for side in (1, -1):
        stem = curve((19, 8), (15, 0), (7, 2), steps=30)
        n = len(stem)
        for i, (x, y) in enumerate(stem):
            if i < 3 or i % 2:
                continue
            length = 2 if i < n * 0.75 else 1
            # 外側（上）と内側（下）に毛。曲線の向きに対してななめ
            barbs = [(x - k, y - k) for k in range(1, length + 1)] + [(x + k - 1, y + k) for k in range(1, length + 1)]
            plot(pt.img, barbs if side == 1 else mirror_points(barbs), "warm3")
        plot(pt.img, stem if side == 1 else mirror_points(stem), "warm4")
    # ---- 目と口
    draw_eyes(pt, expression)
    mouth = {
        "normal": [".m..", "..mm"],     # 片方の口角だけ上がる
        "happy": ["m..m", ".mm."],
        "worried": [".mm.", "m..m"],
    }[expression]
    pt.stamp(mouth, {"m": "moth5"}, 22, 17)
    pt.outline("moth0")
    return pt.img


def _shift(m, dx, dy):
    out = Image.new("L", m.size, 0)
    out.paste(m, (dx, dy))
    return out


EYE_KEY = {"O": "moth0", "K": "night0", "G": "warm4", "g": "warm3", "L": "moon3", "l": "moth3", "d": "moth1"}

NEMU_EYES = {
    # 6x6 の大きな複眼。下の方が金色に光る（目の照り返し）。つやは左上
    "normal": [  # 半分まぶたを下ろした、あやしい目。目じりのまつ毛が外へはね上がる
        "O......",
        ".dddddd",
        "OOOOOOO",
        ".KLKKKK",
        ".KKgGGK",
        "..KGGK.",
    ],
    "happy": [  # にっこり（目を細めて弓なり）
        "O......",
        ".OOOOO.",
        "O.....O",
        ".......",
        ".......",
        ".......",
    ],
    "worried": [  # 目を見開く
        "O......",
        "..KKKK.",
        ".KLLKKK",
        ".KLKKKK",
        ".KKgGGK",
        "..KKKK.",
    ],
}


def draw_eyes(pt, expression):
    rows = NEMU_EYES[expression]
    pt.stamp(rows, EYE_KEY, 16, 11)
    # 右目：形は反転、つや（L）は左上のまま
    mirrored = [r[::-1] for r in rows]
    fixed = []
    for r in mirrored:
        fixed.append(r.replace("L", "K"))
    lights = [(x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == "L"]
    fixed = [list(r) for r in fixed]
    for (x, y) in lights:
        fixed[y][x] = "L"
    pt.stamp(["".join(r) for r in fixed], EYE_KEY, 25, 11)



def build(save):
    out = {"sprite": [], "faces": {}}
    for i, img in enumerate(sprite_frames()):
        out["sprite"].append(save(img, "Characters", "Nemu", f"nemu_fly_{i}.png", clean=True))
    for e in ("normal", "happy", "worried"):
        out["faces"][e] = save(nemu_portrait(e), "Faces", f"face_nemu_{e}.png", clean=True)
    return out
