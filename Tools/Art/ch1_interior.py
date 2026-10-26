"""ランプ屋の中（第 1 章：ルリがネムと古いランタンに出会う場所）。

描き方は Tools/Art/STYLE.md のとおり。
- 3/4 ビュー：家具は「上の面（明るい）＋正面（暗い）」。右の 2 列は影のかたまり。
- 床は板張り、壁は上が土壁（しっくい）、下が板の腰壁。壁は 3 タイル（48 px）の高さ。
- 店は閉まっていて暗い。棚のランプはほとんど消えていて、いくつかだけ残り火のように灯る。
  カウンターの上の古いランタン（ネムの住みか）だけが、ぼんやり明るい。
- 参考にしたもの：古い道具屋・時計屋の店内（板の間、ガラスの引き戸、壁一面の棚、作業台、柱時計）。
"""

from ch1_assets import OUT, Canvas, frame_box, lattice_door

# ================================================================ 床と壁（16x16 のタイル）


def floor_wood(variant):
    """板張りの床：板は 4 ドット幅で横向き。継ぎ目は暗い 1 本線（同じ色にはさまれる）、板の端は互い違い。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "brown1")
    for y in (3, 7, 11, 15):
        cv.line(0, y, 15, y, "brown0")
    joints = [(5, 0), (12, 4), (2, 8), (9, 12)] if variant == 0 else [(10, 0), (3, 4), (13, 8), (6, 12)]
    for (x, y) in joints:
        cv.line(x, y, x, y + 2, "brown0")
    if variant == 1:  # 節（2x1 のかたまり）
        cv.rect(7, 9, 8, 9, "brown0")
    return cv.img


def wall_plaster(variant):
    """土壁（しっくい）：平らな塗りに、小さなひび（variant 1）。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "stone5")
    if variant == 1:
        cv.dots([(4, 5), (5, 6), (5, 7), (6, 8)], "stone4")
    return cv.img


def wall_wainscot():
    """腰壁（壁の下の板張り）：上に 2 ドットの見切り（明るい上面＋暗い正面）、縦の板の継ぎ目。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "brown1")
    cv.rect(0, 0, 15, 1, "brown2")       # 見切りの上面
    cv.rect(0, 2, 15, 3, "brown0")       # 見切りの正面（影）
    for x in (3, 9, 15):
        cv.line(x, 4, x, 15, "brown0")
    return cv.img


def wall_top_inner():
    """部屋のまわりの壁の上面（天井の高さの切り口）。暗い梁。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "night2")
    cv.rect(0, 12, 15, 15, "brown0")
    cv.line(0, 11, 15, 11, OUT)
    return cv.img


# ================================================================ 家具・小物

LAMP_SMALL = {  # 棚に並ぶ小さなランプ（5x6 前後）。つやは左上
    "oil": ["..O..", ".OSO.", "OSssO", "OsssO", ".OOO."],
    "hurricane": [".OOO.", "OSssO", "OsssO", "OsssO", "OOOOO"],
    "bulb": [".OO..", "OSsO.", "OssO.", ".OO..", ".OO.."],
}


def shelf_lamps():
    """壁一面の棚（32x40）：3 段の棚板に古いランプ。ほとんど消えていて、2 つだけ残り火。"""
    cv = Canvas(32, 40)
    cv.rect(0, 0, 31, 39, OUT)
    cv.rect(1, 1, 30, 38, "brown0")            # 棚の奥（暗い）
    cv.rect(1, 1, 2, 38, "brown1")             # 左右の側板
    cv.rect(29, 1, 30, 38, "brown1")
    for y in (12, 25, 37):                     # 棚板：上面 2 行（明るい）＋下に輪郭の線（奥の暗い色との間に帯を作らない）
        cv.rect(1, y - 2, 30, y - 1, "brown2")
        cv.line(1, y, 30, y, OUT)
    lit = {(1, 2), (2, 0)}
    kinds = ["oil", "hurricane", "bulb", "oil"]
    for shelf, base in enumerate((9, 22, 35)):
        for k in range(4):
            rows = LAMP_SMALL[kinds[(k + shelf) % 4]]
            on = (shelf, k) in lit
            key = {"O": OUT, "S": "warm5" if on else "stone4", "s": "warm4" if on else "stone3"}
            cv.stamp(rows, key, 4 + k * 6, base - len(rows) + 1)
    return cv.img


def counter():
    """カウンター（48x26）：上面（明るい板）＋正面（板張り）。上に古いランタン、呼び鈴、開いた帳面。"""
    cv = Canvas(48, 26)
    cv.rect(0, 8, 47, 25, OUT)
    cv.rect(1, 9, 46, 13, "brown2")            # 上面
    cv.line(0, 14, 47, 14, OUT)
    cv.rect(1, 15, 46, 24, "brown1")           # 正面
    for x in (12, 24, 36):
        cv.line(x, 15, x, 24, "brown0")
    cv.rect(44, 15, 46, 24, "brown0")          # 右のふちの影（3 列）
    # 帳面（白い紙、文字は短い線）
    cv.rect(4, 8, 15, 12, OUT)
    cv.rect(5, 9, 14, 11, "stone7")
    cv.line(9, 9, 9, 11, "stone5")
    cv.line(6, 10, 8, 10, "stone5")
    cv.line(11, 10, 13, 10, "stone5")
    # 呼び鈴
    cv.stamp([".OO.", "OYyO", "OOOO"], {"O": OUT, "Y": "warm4", "y": "warm3"}, 19, 8)
    # 古いランタン（ネムの住みか）：ぼんやり灯る
    lantern = [
        "..OOOO..",
        ".O....O.",
        "..OOOO..",
        ".OwwwwO.",
        "OOOOOOOO",
        "OyyYYYYO",
        "OyYYYYYO",
        "OYYYYYYO",
        "OOOOOOOO",
        ".OwwwwO.",
    ]
    cv.stamp(lantern, {"O": OUT, "w": "night4", "Y": "warm4", "y": "warm5"}, 32, 0)
    return cv.img


def workbench():
    """作業台（32x24）：分解したランプの部品と道具。"""
    cv = Canvas(32, 24)
    cv.rect(0, 6, 31, 17, OUT)
    cv.rect(1, 7, 30, 12, "brown2")            # 上面
    cv.line(0, 13, 31, 13, OUT)
    cv.rect(1, 14, 30, 16, "brown1")           # 正面
    cv.rect(28, 14, 30, 16, "brown0")
    for x in (2, 27):                          # 脚
        cv.rect(x - 1, 17, x + 2, 23, OUT)
        cv.rect(x, 17, x + 1, 22, "brown1")
    # 部品：ガラスのほや、ねじ回し、ねじ
    cv.stamp([".OO.", "OSsO", "OssO", ".OO."], {"O": OUT, "S": "moon2", "s": "night5"}, 4, 4)
    cv.line(12, 9, 18, 9, "stone6")
    cv.rect(19, 9, 20, 9, "red1")
    cv.dots([(23, 10), (25, 9)], "stone6")
    return cv.img


def grandfather_clock():
    """柱時計（16x40）：木の箱、白い文字盤、振り子の窓。"""
    cv = Canvas(16, 40)
    cv.rect(1, 0, 14, 39, OUT)
    cv.rect(2, 1, 13, 38, "brown1")
    cv.rect(11, 1, 13, 38, "brown0")           # 右の影
    cv.rect(2, 1, 13, 2, "brown2")             # 上の面
    cv.stamp([
        "..OOOOO..",
        ".OWWWWWO.",
        "OWWWOWWWO",
        "OWWWOWWWO",
        "OWWWOOOWO",
        "OWWWWWWWO",
        ".OWWWWWO.",
        "..OOOOO..",
    ], {"O": OUT, "W": "stone7"}, 3, 4)
    frame_box(cv, 4, 16, 10, 34, "night2", frame="brown2")
    cv.line(7, 19, 7, 28, "warm3")             # 振り子
    cv.rect(6, 29, 8, 30, "warm4")
    return cv.img


def hanging_lamp(on):
    """天井から下がるランプ（8x16）。"""
    cv = Canvas(8, 16)
    cv.line(3, 0, 3, 5, OUT)
    cv.stamp([
        "..OOO...",
        ".OSSSO..",
        "OSSSSSO.",
        "OOOOOOO.",
        ".OGGGO..",
        ".OgGGO..",
        "..OOO...",
    ], {"O": OUT, "S": "brown2", "G": "warm5" if on else "night4", "g": "warm6" if on else "night5"}, 0, 6)
    return cv.img


def crate():
    """木箱（16x14）：上面は明るく、正面の板の継ぎ目、右の影。"""
    cv = Canvas(16, 14)
    cv.rect(0, 0, 15, 13, OUT)
    cv.rect(1, 1, 14, 4, "brown2")
    cv.line(0, 5, 15, 5, OUT)
    cv.rect(1, 6, 14, 12, "brown1")
    cv.line(1, 9, 14, 9, "brown0")
    cv.rect(13, 6, 14, 12, "brown0")
    return cv.img


def stool():
    """腰かけ（12x12）。"""
    cv = Canvas(12, 12)
    cv.rect(0, 0, 11, 5, OUT)
    cv.rect(1, 1, 10, 3, "brown2")
    cv.line(1, 4, 10, 4, "brown1")
    for x in (1, 8):
        cv.rect(x, 5, x + 2, 11, OUT)
        cv.rect(x + 1, 5, x + 1, 10, "brown1")
    return cv.img


def rug():
    """床の敷物（48x24）：赤い地に、2 ドット幅の縁取りと、まん中の模様。"""
    cv = Canvas(48, 24)
    cv.rect(2, 1, 45, 22, "red0")
    cv.rect(4, 3, 43, 20, "red1")
    cv.rect(8, 7, 39, 16, "red0")
    cv.rect(10, 9, 37, 14, "red1")
    for x in range(14, 36, 6):                 # 菱形の小さな模様
        cv.stamp([".Y.", "YYY", ".Y."], {"Y": "warm3"}, x, 10)
    for x in range(2, 46, 3):                  # 房（上下のふち）
        cv.dot(x, 0, "stone6")
        cv.dot(x, 23, "stone6")
    return cv.img


def window_inner():
    """店の奥の窓（32x20）：外は夜。ガラスに月明かりの照り返し。"""
    cv = Canvas(32, 20)
    frame_box(cv, 0, 0, 31, 19, "night3", frame="brown2")
    cv.line(15, 3, 15, 16, "brown2")
    cv.line(16, 3, 16, 16, "brown1")
    cv.dots([(5, 5), (6, 5), (5, 6)], "night5")
    cv.dots([(20, 5), (21, 5), (20, 6)], "night5")
    return cv.img


def door_inner():
    """出入り口（店の格子戸を内側から見たところ、32x36）。"""
    cv = Canvas(32, 36)
    lattice_door(cv, 0, 0, 31, 35, glass="night2", bar="brown1")
    return cv.img


def doormat():
    """戸口のマット（32x12）。"""
    cv = Canvas(32, 12)
    cv.rect(0, 0, 31, 11, OUT)
    cv.rect(1, 1, 30, 10, "green1")
    cv.rect(3, 3, 28, 8, "green0")
    return cv.img


def build(save):
    tiles = {
        "floor_wood_0": floor_wood(0), "floor_wood_1": floor_wood(1),
        "wall_plaster_0": wall_plaster(0), "wall_plaster_1": wall_plaster(1),
        "wall_wainscot": wall_wainscot(), "wall_top_inner": wall_top_inner(),
    }
    out = {}
    for name, img in tiles.items():
        out[name] = save(img, "Interior", "Tiles", f"{name}.png")
    things = {
        "shelf_lamps": shelf_lamps(), "counter": counter(), "workbench": workbench(),
        "grandfather_clock": grandfather_clock(), "hanging_lamp_on": hanging_lamp(True),
        "hanging_lamp_off": hanging_lamp(False), "crate": crate(), "stool": stool(), "rug": rug(),
        "window_inner": window_inner(), "door_inner": door_inner(), "doormat": doormat(),
    }
    for name, img in things.items():
        out[name] = save(img, "Interior", f"{name}.png", clean=True)
    return out
