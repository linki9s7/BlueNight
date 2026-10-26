"""第 1 章「バス停と商店街」の素材：建物の正面、バス停、小物、地面のタイル。

描き方は Tools/Art/STYLE.md のとおり。
- 3/4 ビュー：屋根の上面（瓦・トタン）＋建物の正面。1 階建ての店は 幅 4〜5 タイル × 高さ 5 タイル（屋根 2＋壁 3）。
- 光は画面の左上から：屋根の瓦は筋の左が明るく右が暗い。軒の下の壁には 3 ドットの影のかたまり。
- 参考にしたもの：昭和の商店街（瓦屋根の木造の店、シャッター、オーニング、丸ポスト、電柱、カーブミラー）。
  夜なので、窓の明かりは「起きている人がいる」所だけにする（おばあさんの店の奥、二階の一部屋など）。
"""

from PIL import Image, ImageDraw

from palette import RAMPS, hex_to_rgba

CLEAR = (0, 0, 0, 0)


def P(name):
    """'stone3' → RGBA。"""
    ramp = name.rstrip("0123456789")
    return hex_to_rgba(RAMPS[ramp][int(name[len(ramp):])])


OUT = "night1"  # 輪郭


class Canvas:
    def __init__(self, w, h):
        self.img = Image.new("RGBA", (w, h), CLEAR)
        self.d = ImageDraw.Draw(self.img)
        self.px = self.img.load()
        self.w, self.h = w, h

    def rect(self, x0, y0, x1, y1, c, outline=None):
        self.d.rectangle([x0, y0, x1, y1], fill=P(c), outline=P(outline) if outline else None)

    def line(self, x0, y0, x1, y1, c):
        self.d.line([x0, y0, x1, y1], fill=P(c))

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[x, y] = P(c)

    def dots(self, pts, c):
        for x, y in pts:
            self.dot(x, y, c)

    def stamp(self, rows, key, x0, y0):
        """ピクセルマップを (x0, y0) に置く（'.' は透明＝下を残す）。"""
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != ".":
                    self.dot(x0 + x, y0 + y, key[ch])

    def outline_silhouette(self, c=OUT):
        """不透明な部分のまわり（上下左右）に 1 ドットの輪郭を足す。"""
        src = self.img.copy().load()
        for y in range(self.h):
            for x in range(self.w):
                if src[x, y][3]:
                    continue
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[nx, ny][3]:
                        self.px[x, y] = P(c)
                        break


def from_map(rows, key):
    c = Canvas(len(rows[0]), len(rows))
    for y, row in enumerate(rows):
        assert len(row) == c.w, f"row {y}: {row!r} ({len(row)} != {c.w})"
    c.stamp(rows, key, 0, 0)
    return c.img


# ================================================================ 建物の部品

ROOFS = {
    # (暗, 基本, 明, 棟)：いぶし瓦（青みの灰）、トタン（さびた赤）
    "kawara": ("stone2", "stone3", "stone4", "stone1"),
    "tin": ("red0", "brown2", "red1", "brown1"),
}

WALLS = {
    # (基本, 目地・板の継ぎ目, 明るい縁)
    "wood": ("brown1", "brown0", "brown2"),
    "plaster": ("stone5", "stone4", "stone6"),
    "mortar": ("stone4", "stone3", "stone5"),
}

ROOF_H = 32  # 屋根（棟＋瓦＋軒先）
WALL_H = 48  # 壁（3 タイル）


def draw_roof(cv, kind, x0, x1, y0=0, h=ROOF_H):
    dark, base, light, ridge = ROOFS[kind]
    cv.rect(x0, y0, x1, y0 + h - 1, base)
    # 棟（いちばん上）：3 行
    cv.rect(x0, y0, x1, y0 + 2, ridge)
    cv.rect(x0, y0 + 3, x1, y0 + 4, dark)  # 棟の下の影（2 行）
    if kind == "kawara":
        # 丸瓦の筋：4 ドットごとに「明・基本・基本・暗」（左が明るい）。輪郭のすぐ内側（x0+1）は基本の色にする
        for x in range(x0, x1 + 1):
            k = (x - x0) % 4
            if k == 0:
                cv.line(x, y0 + 5, x, y0 + h - 5, light)
            elif k == 3:
                cv.line(x, y0 + 5, x, y0 + h - 5, dark)
        # 瓦の段の重なり（同じ色にはさまれた 1 本線）
        for y in range(y0 + 9, y0 + h - 5, 6):
            for x in range(x0, x1 + 1):
                if (x - x0) % 4 in (1, 2):
                    cv.dot(x, y, dark)
        # 軒先瓦：丸い瓦の先が並ぶ（明 2・基本 1・暗 1。暗い所は上の筋とまっすぐつなげる）
        for x in range(x0, x1 + 1):
            k = (x - x0) % 4
            cv.line(x, y0 + h - 4, x, y0 + h - 2, light if k in (1, 2) else (base if k == 0 else dark))
    else:
        # トタンの波板：6 ドットごとに明るい山と暗い谷
        for x in range(x0, x1 + 1):
            k = (x - x0 - 1) % 6
            if k in (0, 1):
                cv.line(x, y0 + 5, x, y0 + h - 4, light)
            elif k == 3:
                cv.line(x, y0 + 5, x, y0 + h - 4, dark)
        # さびのかたまり（右下寄り）
        for (sx, sy) in ((x1 - 9, y0 + h - 9), (x0 + 14, y0 + 12)):
            cv.rect(sx, sy, sx + 2, sy + 1, dark)
        cv.rect(x0, y0 + h - 3, x1, y0 + h - 2, dark)  # 軒先の影（2 行）
    cv.line(x0, y0 + h - 1, x1, y0 + h - 1, OUT)


def draw_wall(cv, kind, x0, x1, y0=ROOF_H, h=WALL_H):
    base, seam, light = WALLS[kind]
    y1 = y0 + h - 1
    cv.rect(x0, y0, x1, y1, base)
    if kind == "wood":
        for x in range(x0 + 4, x1, 6):  # 縦の板張り
            cv.line(x, y0, x, y1, seam)
    elif kind == "mortar":
        for (sx, sy) in ((x0 + 6, y0 + 20), (x1 - 12, y0 + 30)):  # 小さなひび
            cv.dots([(sx, sy), (sx + 1, sy + 1), (sx + 1, sy + 2), (sx + 2, sy + 3)], seam)
    # 軒の下の影（3 行のかたまり）
    cv.rect(x0, y0, x1, y0 + 2, "night3")
    # 基礎（コンクリート）
    cv.rect(x0, y1 - 4, x1, y1 - 3, "stone3")  # 基礎の上面（光が当たる、2 行）
    cv.rect(x0, y1 - 2, x1, y1, "stone2")


def frame_box(cv, x0, y0, x1, y1, fill, frame="brown2"):
    """窓や戸の枠：外側 1 ドットの輪郭＋ 2 ドットの木枠（左上が明るい）。中を fill で塗る。"""
    cv.rect(x0, y0, x1, y1, OUT)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, frame)
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, fill)


def lattice_door(cv, x0, y0, x1, y1, glass="night3", bar="brown1", lit=False):
    """格子戸（引き戸 2 枚）。"""
    frame_box(cv, x0, y0, x1, y1, glass)
    mid = (x0 + x1) // 2
    cv.line(mid, y0 + 1, mid, y1 - 1, OUT)
    # 格子：それぞれの戸のガラスの中に、両端に 2 ドット以上のすき間を残して 3 ドットおき
    for a, b in ((x0 + 3, mid - 1), (mid + 1, x1 - 3)):
        x = a + 2
        while x <= b - 2:
            cv.line(x, y0 + 3, x, y1 - 3, bar)
            x += 3
    for y in range(y0 + 10, y1 - 3, 9):
        cv.line(x0 + 3, y, x1 - 3, y, bar)
    cv.rect(x0 + 3, y1 - 8, x1 - 3, y1 - 3, "brown1")  # 腰板
    cv.line(mid, y1 - 8, mid, y1 - 3, OUT)
    if lit:  # 奥の明かりが格子ごしにもれる（左上に寄せたかたまり）
        for y in range(y0 + 3, y0 + 10):
            for x in range(x0 + 3, mid - 1):
                if cv.px[x, y] == P(glass):
                    cv.dot(x, y, "warm3")


def shutter(cv, x0, y0, x1, y1, base="stone5", ridge="stone6", groove="stone4"):
    """シャッター：上にシャッターボックス、下に 3 ドットごとの波（明るい山 1 本、それ以外は同じ色）。"""
    cv.rect(x0, y0, x1, y1, OUT)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 5, groove)  # ボックス
    cv.line(x0, y0 + 6, x1, y0 + 6, OUT)
    cv.rect(x0 + 1, y0 + 7, x1 - 1, y1 - 1, base)
    for y in range(y0 + 9, y1 - 3, 3):  # 輪郭の隣に 1 行だけの色を作らない
        cv.line(x0 + 1, y, x1 - 1, y, ridge)
    cv.rect(x0 + 1, y1 - 2, x1 - 1, y1 - 1, groove)  # 下の座板
    # 取っ手と鍵穴
    mx = (x0 + x1) // 2
    cv.rect(mx - 2, y1 - 2, mx + 1, y1 - 1, "stone2")


def hanging_sign(cv, x0, y0, w, h, board="brown2", text="stone7", kind="dash"):
    """看板（板）。文字は読めない大きさなので、太い短い線で「文字らしさ」だけ出す。"""
    cv.rect(x0, y0, x0 + w - 1, y0 + h - 1, OUT)
    cv.rect(x0 + 1, y0 + 1, x0 + w - 2, y0 + h - 2, board)
    if kind == "dash":
        x = x0 + 3
        while x + 3 < x0 + w - 3:
            cv.rect(x, y0 + 3, x + 2, y0 + h - 4, text)
            x += 5


def outline_box(cv, x0, y0, x1, y1):
    cv.d.rectangle([x0, y0, x1, y1], outline=P(OUT))


# ================================================================ 建物

def finish(cv):
    """建物のまわりに 1 ドットの輪郭。建物を横に並べるときは 1 ドット重ねる（輪郭が 2 本にならない）。"""
    outline_box(cv, 0, 0, cv.w - 1, cv.h - 1)
    return cv.img


def building_lamp_shop():
    """ランプ屋（閉店後）。木造・いぶし瓦。ショーウィンドウに古いランプ、戸の横にランタンを掛ける腕木。80x80。"""
    W = 80
    cv = Canvas(W, ROOF_H + WALL_H)
    draw_roof(cv, "kawara", 0, W - 1)
    draw_wall(cv, "wood", 0, W - 1)
    # 看板：ランプの絵（文字の代わり）
    cv.rect(25, 34, 55, 42, OUT)  # 板張りの継ぎ目から 2 ドット以上はなす
    cv.rect(26, 35, 54, 41, "brown2")
    lamp_icon = [
        ".OO.",
        "OyyO",
        "OYYO",
        ".OO.",
    ]
    for x in (31, 40, 49):
        cv.stamp(lamp_icon, {"O": OUT, "y": "warm4", "Y": "warm3"}, x - 1, 36)
    # ショーウィンドウ（暗いガラス＋棚に並んだ消えたランプ）
    frame_box(cv, 4, 45, 37, 70, "night3")
    cv.rect(7, 61, 34, 62, "brown1")  # 棚板（2 行）
    unlit = [  # つやは左上
        "..O..",
        ".OOO.",
        "OSssO",
        "OsssO",
        ".OOO.",
    ]
    for x in (7, 14, 21):
        cv.stamp(unlit, {"O": "night1", "s": "stone3", "S": "stone4"}, x, 56)
    # 一つだけ、かすかに残り火のついたランプ（物語のランタンの仲間）
    cv.stamp(unlit, {"O": "night1", "s": "warm1", "S": "warm2"}, 28, 56)
    # ガラスに映る月明かり（左上の 2 ドットの斜めのかたまり）
    cv.dots([(8, 48), (9, 48), (8, 49)], "night5")
    # 格子戸
    lattice_door(cv, 44, 44, 71, 74)
    # ランタン掛けの腕木（戸の右）
    cv.rect(73, 46, 78, 47, "brown0")
    cv.dot(77, 48, "stone5")
    cv.dot(77, 49, "stone5")
    return finish(cv)


def building_grandma_shop():
    """おばあさんの店（小さな商店）。トタン屋根、しま模様の日よけ、半分下ろしたシャッター、奥の明かり。80x80。"""
    W = 80
    cv = Canvas(W, ROOF_H + WALL_H)
    draw_roof(cv, "tin", 0, W - 1)
    draw_wall(cv, "mortar", 0, W - 1)
    # 看板（横長、文字らしい線）
    hanging_sign(cv, 6, 34, 52, 9, board="moon2", text="red1")
    # 日よけ（しま模様：赤と白を 4 ドットずつ。下のふちは波形）
    y0, y1 = 44, 50
    cv.rect(2, y0, 59, y1, OUT)
    for x in range(3, 59):
        c = "red1" if ((x - 3) // 4) % 2 == 0 else "stone7"
        cv.line(x, y0 + 1, x, y1 - 1, c)
    cv.rect(3, y0 + 1, 58, y0 + 2, "red2")  # 上の面（光が当たる、2 行）
    for x in range(3, 59):
        if ((x - 3) // 4) % 2 == 0:
            cv.dot(x, y1, "red0")
        if (x - 3) % 4 == 1:
            cv.dot(x, y1 + 1, OUT)
    # 半分下ろしたシャッター（下に奥の明かりがもれる）
    shutter(cv, 4, 52, 57, 66)
    cv.rect(4, 67, 57, 74, OUT)
    cv.rect(5, 67, 56, 74, "warm3")
    cv.rect(5, 67, 56, 68, "warm2")  # シャッターの下の影
    # 店先の商品棚（明かりの中のシルエット）
    for x in (9, 21, 33, 45):
        cv.rect(x, 71, x + 6, 74, "warm1")
        cv.rect(x, 71, x + 6, 71, "warm2")
    # 右の小窓（起きている人がいる）
    frame_box(cv, 63, 50, 76, 64, "warm4")
    cv.rect(66, 53, 68, 55, "warm5")  # 左上のつや
    cv.line(69, 53, 69, 61, "brown1")  # 格子
    # 植木鉢（店先）
    cv.stamp([".gg.", "gGgg", "OrrO", ".rr."], {"g": "green1", "G": "green2", "O": OUT, "r": "brown1"}, 62, 72)
    return finish(cv)


def building_shutter_shop(variant):
    """シャッターの閉まった店。variant 0：灰色のシャッター＋青い看板、1：さびたシャッター＋赤い看板。64x80。"""
    W = 64
    cv = Canvas(W, ROOF_H + WALL_H)
    draw_roof(cv, "kawara" if variant == 0 else "tin", 0, W - 1)
    draw_wall(cv, "plaster" if variant == 0 else "mortar", 0, W - 1)
    if variant == 0:
        hanging_sign(cv, 4, 34, 56, 9, board="night5", text="moon2")
        shutter(cv, 4, 45, 59, 74)
    else:
        hanging_sign(cv, 4, 34, 56, 9, board="red0", text="warm4")
        shutter(cv, 4, 45, 59, 74, base="stone4", ridge="stone5", groove="stone3")
        # さびのかたまり（右下）
        for (sx, sy) in ((48, 66), (50, 64), (12, 70)):
            cv.rect(sx, sy, sx + 2, sy + 1, "brown1")
        # 貼り紙
        cv.rect(20, 57, 27, 66, OUT)  # シャッターの山の行にそろえる（すき間に 1 行だけの帯を作らない）
        cv.rect(21, 58, 26, 65, "stone7")
        cv.line(22, 60, 25, 60, "stone5")
        cv.line(22, 62, 24, 62, "stone5")
    return finish(cv)


def building_house():
    """二階建ての家（商店街の裏）。二階の一部屋だけ明かり。64x112。"""
    W, H = 64, ROOF_H + 80
    cv = Canvas(W, H)
    draw_roof(cv, "kawara", 0, W - 1)
    draw_wall(cv, "plaster", 0, W - 1, h=80)
    # 一階と二階の境目（小さなひさし）
    cv.rect(0, 70, W - 1, 72, "stone3")
    cv.line(0, 70, W - 1, 70, "stone4")
    cv.line(0, 73, W - 1, 73, OUT)
    cv.rect(0, 74, W - 1, 75, "night3")
    # 二階の窓：左は暗い（カーテン）、右は明かり
    frame_box(cv, 6, 42, 25, 62, "night3", frame="stone6")
    cv.rect(9, 45, 14, 59, "night4")  # カーテン
    frame_box(cv, 38, 42, 57, 62, "warm4", frame="stone6")
    cv.rect(41, 45, 44, 48, "warm5")
    cv.line(47, 43, 47, 61, "stone6")
    # 一階：玄関と小窓
    lattice_door(cv, 34, 80, 57, 106, glass="night3", bar="stone4")
    frame_box(cv, 6, 82, 23, 96, "night3", frame="stone6")
    cv.line(14, 83, 14, 95, "stone6")
    # 表札・郵便受け
    cv.rect(27, 86, 30, 91, OUT)
    cv.rect(28, 87, 29, 90, "brown2")
    return finish(cv)


def bus_shelter():
    """バス停の待合所：トタンのひさし、2 本の柱、ベンチ、時刻表。48x48。"""
    cv = Canvas(48, 48)
    # ひさし（上面）。継ぎ目は 6 ドットおき
    cv.rect(0, 2, 47, 9, "stone4")
    cv.rect(0, 2, 47, 3, "stone5")
    for x in range(5, 44, 6):
        cv.line(x, 4, x, 9, "stone3")
    cv.rect(0, 10, 47, 11, "stone2")  # 前のふち
    # 奥の壁（板）
    cv.rect(5, 12, 42, 32, "night3")
    for x in range(11, 38, 6):
        cv.line(x, 12, x, 32, "night2")
    # 柱（2 ドットの平らな塗り）
    for x in (3, 43):
        cv.rect(x, 12, x + 1, 45, "stone5")
    # 時刻表
    cv.rect(30, 15, 38, 25, OUT)
    cv.rect(31, 16, 37, 24, "stone7")
    for y in (18, 20, 22):
        cv.line(32, y, 36, y, "stone5")
    # ベンチ：座面の上（明るい 3 行）＋正面（暗い 2 行）
    cv.rect(8, 31, 39, 33, "brown2")
    cv.rect(8, 34, 39, 35, "brown0")
    for x in (10, 36):
        cv.rect(x, 36, x + 1, 43, "stone3")
    cv.outline_silhouette()
    return cv.img


# ================================================================ 小物（ピクセルマップ）

BUS_SIGN = [  # バス停の標識（丸い板＋ポール＋重りの台）
    "....OOOOOO......",
    "...OmmmmmmO.....",
    "..OmmOOOOmmO....",
    "..OmOrrrrOmO....",
    "..OmOrrrrOmO....",
    "..OmmOOOOmMO....",
    "...OmmmmmMO.....",
    "....OOOOOO......",
    "......OsO.......",
    "......OsO.......",
    ".....OOsOO......",
    ".....OwwwO......",
    ".....OwYwO......",
    ".....OwwwO......",
    ".....OwYwO......",
    ".....OwwwO......",
    ".....OOsOO......",
    "......OsO.......",
    "......OsO.......",
    "......OsO.......",
    "......OsO.......",
    "......OsO.......",
    "......OsO.......",
    "......OsO.......",
    "......OsO.......",
    "......OsO.......",
    "....OOOsOOO.....",
    "....OcccccO.....",
    "....OcccCCO.....",
    "....OOOOOOO.....",
]
BUS_SIGN_KEY = {"O": "night1", "m": "stone7", "M": "stone6", "r": "red1", "s": "stone5", "w": "stone7",
                "Y": "stone5", "c": "stone4", "C": "stone3"}

MAILBOX = [  # 丸ポスト（赤）。つやは左上、影は右に 2 列
    "....OOOOOO......",
    "...ORRrrrrO.....",
    "..ORRrrrrddO....",
    "..ORrrrrrddO....",
    "..OOOOOOOOOO....",
    "..OrrOOOOddO....",
    "..ORRrrrrddO....",
    "..ORRrrrrddO....",
    "..ORRrrrrddO....",
    "..OrrrrrrddO....",
    "..OrwwwwrddO....",
    "..OrwwwwrddO....",
    "..OrrrrrrddO....",
    "..OrrrrrrddO....",
    "..OrrrrrrddO....",
    "..OrrrrrrddO....",
    "..OrrrrrrddO....",
    "..OOOOOOOOOO....",
    "...OssssssO.....",
    "...OOOOOOOO.....",
]
MAILBOX_KEY = {"O": "night1", "r": "red1", "R": "red2", "d": "red0", "w": "stone7", "s": "stone3"}

BENCH = [  # 木のベンチ（3/4 ビュー：座面の上 2 枚の板＋正面）
    "................................",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
    "OhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhO",
    "OhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhO",
    "OwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwO",
    "OhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhO",
    "OhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhO",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
    "OddddddddddddddddddddddddddddddO",
    "OddddddddddddddddddddddddddddddO",
    "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
    "..OmmO..................OmmO....",
    "..OmmO..................OmmO....",
    "..OOOO..................OOOO....",
]
BENCH_KEY = {"O": "night1", "h": "brown2", "w": "brown1", "d": "brown0", "m": "stone5", "M": "stone3"}

POWER_POLE = [  # 電柱（腕木・がいし・変圧器）。上の電線は別に描く
    "..........OO..........",
    ".........OssO.........",
    "OOOOOOOOOOssOOOOOOOOOO",
    "OaaaaaaaaaaaaaaaaaaaaO",
    "OOOOOOOOOsssOOOOOOOOOO",
    ".OwO.....OssO.....OwO.",
    ".OOO.....OssO.....OOO.",
    ".........OssO.........",
    ".........OssO.........",
    ".......OOOssOOO.......",
    "......OtttsstttO......",
    "......OtttsstttO......",
    "......OtttsstttO......",
    "......OtttsstttO......",
    "......OtttsstttO......",
    ".......OOOssOOO.......",
    ".........OssO.........",
    ".........OssO.........",
    ".........OssO.........",
    ".........OssO.........",
    ".........OssO.........",
    "........OOOOOO........",
    "........ObbbbO........",
    "........ObwwbO........",
    "........ObbbbO........",
    "........ObwbbO........",
    "........ObbbbO........",
    "........OOOOOO........",
    ".........OssO.........",
]
POWER_POLE_KEY = {"O": "night1", "s": "stone5", "a": "stone4", "w": "stone7", "t": "stone4", "b": "night5"}  # b：番地の札（青）


def power_pole():
    """電柱 22x96。上の部品の下に柱を伸ばす。柱は左が明るい 2 ドット。黄色と黒の巻き標識つき。"""
    top = POWER_POLE
    H = 96
    cv = Canvas(22, H)
    for y in range(len(top), H - 1):
        cv.stamp([".........OssO........."], {"O": OUT, "s": "stone5"}, 0, y)
    cv.stamp(top, POWER_POLE_KEY, 0, 0)
    cv.line(9, H - 1, 12, H - 1, OUT)
    # 巻き標識（黄・黒のしま、足元近く）
    for y in range(H - 24, H - 12):
        cv.dot(10, y, "warm4" if (y // 2) % 2 == 0 else "night2")
        cv.dot(11, y, "warm3" if (y // 2) % 2 == 0 else "night2")
    return cv.img


CURVE_MIRROR = [  # カーブミラー（オレンジの柱に丸い鏡）
    "...OOOOOOOO.....",
    "..OwwwwwwwwO....",
    ".OwmmmmmmmmwO...",
    ".OwMMmmmmmmwO...",
    ".OwMmmmmmmmwO...",
    ".OwmmmmmmmnwO...",
    ".OwmmmmmmnnwO...",
    ".OwmmmmmnnnwO...",
    "..OwwwwwwwwO....",
    "...OOOOOOOO.....",
    "......OoO.......",
]
CURVE_MIRROR_KEY = {"O": "night1", "w": "night1", "m": "night4", "M": "moon1", "n": "night3", "o": "warm2"}


def curve_mirror():
    cv = Canvas(16, 48)
    cv.stamp(CURVE_MIRROR, CURVE_MIRROR_KEY, 0, 0)
    for y in range(len(CURVE_MIRROR), 47):
        cv.stamp(["......OoO......."], {"O": OUT, "o": "warm2"}, 0, y)
    cv.stamp(["....OOOOOOO.....", "....OOOOOOO....."], {"O": OUT}, 0, 46)
    return cv.img


TRASH_BIN = [  # 金網のごみかご：網は市松（網点）にせず、格子の線＋穴のかたまり
    "................",
    "...OOOOOOOOOO...",
    "..OggggggggggO..",
    "..OOOOOOOOOOOO..",
    "..OnddnddnddnO..",
    "..OnddnddnddnO..",
    "..OnnnnnnnnnnO..",
    "..OnddnddnddnO..",
    "..OnddnddnddnO..",
    "..OnnnnnnnnnnO..",
    "..OnddnddnddnO..",
    "..OOOOOOOOOOOO..",
    "...OO......OO...",
]
TRASH_BIN_KEY = {"O": "night1", "g": "green1", "n": "green2", "d": "green0"}

POT_PLANT = [  # 植木鉢（ゼラニウム風、2 色の葉）
    "....OOO.OO......",
    "...OGGgOggO.....",
    "..OGGgggggO.....",
    "..OGgggpgggO....",
    ".OOggggggdgO....",
    ".OggppggddgO....",
    "..OggggddOO.....",
    "...OOOOOOO......",
    "...OrrrrrO......",
    "....OrrdO.......",
    "....OOOOO.......",
]
POT_PLANT_KEY = {"O": "night1", "G": "green2", "g": "green1", "d": "green0", "p": "red2", "r": "brown2"}

BEER_CRATES = [  # 積んだプラスチックのケース（店の裏）
    "OOOOOOOOOOOOOO..",
    "OyyyyyyyyyyyyO..",
    "OYOYOYOYOYOYdO..",
    "OYYYYYYYYYYYdO..",
    "OOOOOOOOOOOOOO..",
    "OyyyyyyyyyyyyO..",
    "OYOYOYOYOYOYdO..",
    "OYYYYYYYYYYYdO..",
    "OOOOOOOOOOOOOO..",
]
BEER_CRATES_KEY = {"O": "night1", "y": "warm4", "Y": "warm3", "d": "warm2"}

A_SIGN = [  # 立て看板（黒板）
    "..OOOOOOOOOO....",
    "..ObbbbbbbbO....",
    "..ObwwbbbbbO....",
    "..ObbbwwwbbO....",
    "..ObwwwbbbbO....",
    "..ObbbbwwbbO....",
    "..ObbbbbbbbO....",
    "..OOOOOOOOOO....",
    "..OfO....OfO....",
    "..OfO....OfO....",
    "..OOO....OOO....",
]
A_SIGN_KEY = {"O": "night1", "b": "green0", "w": "stone6", "f": "brown1"}

BICYCLE = [  # 止めてある自転車（横から）
    "........................",
    "................OOO.....",
    "....OOO.........OhO.....",
    "...OsssO.......OOO......",
    "....OOrOOOOOOOOOrO......",
    ".....OrrrrrrrrrrO.......",
    "....OOOrOOOOOOOrOOO.....",
    "...OwwwOrO...OrOwwwO....",
    "..OwOOOwOrO.OrOwOOOwO...",
    "..OwO.OwOOrrrOOwO.OwO...",
    "..OwOOOwO.OOO.OwOOOwO...",
    "...OwwwO.......OwwwO....",
    "....OOO.........OOO.....",
]
BICYCLE_KEY = {"O": "night1", "s": "brown1", "r": "red1", "h": "stone5", "w": "stone4"}

EXTINGUISHER_BOX = [  # 消火器ボックス（赤）
    ".OOOOOOOO.......",
    "ORRRrrrrrO......",
    "ORRrrrrddO......",
    "OrrwwwrddO......",
    "OrrwrwrddO......",
    "OrrwwwrddO......",
    "OrrrrrrddO......",
    "OrrrrrrddO......",
    "OOOOOOOOOO......",
]
EXTINGUISHER_BOX_KEY = {"O": "night1", "r": "red1", "R": "red2", "d": "red0", "w": "stone7"}


# ================================================================ 地面のタイル（16x16）

def tile_crosswalk(variant=0):
    """横断歩道：道路と同じ向きの白い太線（8 ドット）が 8 ドットおきに並ぶ。横に並べると線がつながる。すり減ったかたまりつき。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "stone2")
    cv.rect(0, 4, 15, 11, "stone6")
    if variant == 0:
        cv.rect(5, 7, 6, 8, "stone4")
        cv.dot(7, 8, "stone4")
    else:
        cv.rect(11, 9, 13, 10, "stone4")
    return cv.img


def tile_manhole():
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "stone2")
    cv.d.ellipse([2, 2, 13, 13], fill=P("night1"))
    cv.d.ellipse([3, 3, 12, 12], fill=P("stone3"))
    for v in (6, 9):  # 格子模様
        cv.line(4, v, 11, v, "stone2")
        cv.line(v, 4, v, 11, "stone2")
    cv.rect(4, 4, 5, 5, "stone4")  # 左上のつや
    return cv.img


def tile_drain(variant=0):
    """側溝のふた（コンクリート）。variant 0：穴が 2 つ、1：穴なし。交互に並べる。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "stone3")
    cv.rect(0, 0, 15, 1, "stone4")
    cv.rect(0, 14, 15, 15, "stone2")
    cv.line(15, 0, 15, 15, "stone1")
    if variant == 0:
        for x in (5, 9):
            cv.rect(x, 5, x + 1, 10, "night1")
    return cv.img


def tile_block_wall():
    """ブロック塀の正面（16x16）：ブロック 8x4、目地は暗い 1 本線、上のふちに笠木。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "stone4")
    for y in (3, 7, 11, 15):
        cv.line(0, y, 15, y, "stone3")
    for i, y in enumerate((0, 4, 8, 12)):
        off = 0 if i % 2 == 0 else 4
        cv.line(off + 3, y, off + 3, y + 2, "stone3")
        cv.line(off + 11, y, off + 11, y + 2, "stone3")
    # 透かしブロックの穴
    cv.line(6, 5, 8, 5, "night2")
    return cv.img


def tile_block_wall_top():
    """ブロック塀の上面（笠木）。"""
    cv = Canvas(16, 16)
    cv.rect(0, 10, 15, 12, "stone5")
    cv.rect(0, 13, 15, 15, "stone4")
    cv.line(0, 9, 15, 9, OUT)
    for x in (7, 15):
        cv.line(x, 10, x, 12, "stone4")
    return cv.img


def tile_weeds():
    """歩道のすき間の草（敷石の上に重ねるタイル。透明の上に草のかたまりだけ）。葉先の左上が明るい。"""
    cv = Canvas(16, 16)
    tuft = [
        ".G..G.",
        ".Gg.gg",
        "GggGgg",
        "ggggdd",
        ".gddd.",
    ]
    key = {"g": "green1", "G": "green2", "d": "green0"}
    cv.stamp(tuft, key, 1, 10)
    cv.stamp(tuft[1:], key, 10, 2)
    return cv.img


# ================================================================ 書き出し

def build(save):
    out = {}
    buildings = {
        "lamp_shop": building_lamp_shop(),
        "grandma_shop": building_grandma_shop(),
        "shutter_shop_0": building_shutter_shop(0),
        "shutter_shop_1": building_shutter_shop(1),
        "house": building_house(),
        "bus_shelter": bus_shelter(),
    }
    for name, img in buildings.items():
        out[name] = save(img, "Buildings", f"{name}.png", clean=True)

    props = {
        "bus_sign": from_map(BUS_SIGN, BUS_SIGN_KEY),
        "mailbox": from_map(MAILBOX, MAILBOX_KEY),
        "bench": from_map(BENCH, BENCH_KEY),
        "power_pole": power_pole(),
        "curve_mirror": curve_mirror(),
        "trash_bin": from_map(TRASH_BIN, TRASH_BIN_KEY),
        "pot_plant": from_map(POT_PLANT, POT_PLANT_KEY),
        "beer_crates": from_map(BEER_CRATES, BEER_CRATES_KEY),
        "a_sign": from_map(A_SIGN, A_SIGN_KEY),
        "bicycle": from_map(BICYCLE, BICYCLE_KEY),
        "extinguisher_box": from_map(EXTINGUISHER_BOX, EXTINGUISHER_BOX_KEY),
    }
    for name, img in props.items():
        out[name] = save(img, "Props", f"{name}.png", clean=True)

    tiles = {
        "crosswalk_0": tile_crosswalk(0),
        "crosswalk_1": tile_crosswalk(1),
        "manhole": tile_manhole(),
        "drain_0": tile_drain(0),
        "drain_1": tile_drain(1),
        "block_wall": tile_block_wall(),
        "block_wall_top": tile_block_wall_top(),
        "weeds": tile_weeds(),
    }
    for name, img in tiles.items():
        out[name] = save(img, "Tiles", f"{name}.png", clean=True)
    return out
