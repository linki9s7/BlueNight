"""ルリの家（序章・終章：坂の上の古いアパートの一室）。マップは Chapter1Maps.RoomRows（18x10）。

描き方は Tools/Art/STYLE.md とランプ屋の中（ch1_interior.py）にそろえる。
- 3/4 ビュー：家具は「上の面（明るい）＋正面（暗い）」。右の 2〜3 列は影のかたまり。1 ドットの紺の輪郭＋clean_corners。
- ランプ屋より明るく、生活の色：白っぽいしっくいの壁と巾木、部屋は畳、台所はクッションフロア、玄関は土間（たたき）。
- 母と二人暮らし。物は少なく、きちんとしている（母は夜勤。書き置きでしか話さない家）。
- 台本（docs/STORY.md 8 節＝序章・14 節＝終章）で使うもの：ふとん、机（伏せたスマホ・3 時 12 分の目覚まし・引き出し）、
  湾と高架道路の見える窓、冷蔵庫の書き置き、玄関の椅子にかけた青いマフラー。
  v0.19：部屋の整理だんす（パジャマからワンピースに着がえる）。
- 参考にしたもの：昭和の終わりごろのアパートの 2K（畳の部屋＋台所＋小さな玄関）。
"""

from ch1_assets import OUT, Canvas, frame_box

# ================================================================ 床と壁（16x16 のタイル）


def tatami(variant):
    """畳：平らな若草色に、細い目（4 ドットおきの横線）。variant 1 は上のふちに畳のへり（2 ドット）。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "green2")
    for y in (5, 9, 13):
        cv.line(0, y, 15, y, "green1")
    if variant == 1:
        cv.rect(0, 0, 15, 1, "brown1")
        cv.line(0, 1, 15, 1, "brown0")
    return cv.img


def floor_vinyl():
    """台所のクッションフロア：明るい灰色に、8 ドットの格子の目地。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "stone4")
    for v in (7, 15):
        cv.line(0, v, 15, v, "stone3")
        cv.line(v, 0, v, 15, "stone3")
    return cv.img


def tataki():
    """玄関の土間（たたき）：コンクリートに、小石（2x2、左上が明るい）。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "stone2")
    for (x, y) in [(4, 4), (11, 10)]:
        cv.dot(x, y, "stone3")
        cv.dot(x + 1, y, "stone2")
        cv.dot(x, y + 1, "stone2")
        cv.dot(x + 1, y + 1, "stone1")
    return cv.img


def wall(variant):
    """しっくいの壁（ランプ屋の土壁より明るい）。variant 1 は小さなカレンダーの釘あと。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "stone6")
    if variant == 1:
        cv.dot(7, 6, "stone4")
    return cv.img


def wall_base():
    """壁の下：しっくい＋木の巾木（上に 1 ドットの明るい面、正面は 3 ドット）。"""
    cv = Canvas(16, 16)
    cv.rect(0, 0, 15, 15, "stone6")
    cv.line(0, 11, 15, 11, "brown2")
    cv.rect(0, 12, 15, 15, "brown1")
    return cv.img


# ================================================================ 家具・小物


def futon():
    """ふとん（32x20、床に敷く）：白い敷きぶとん、まくら、青い掛けぶとん。右上がめくれている（さっき起きた）。"""
    cv = Canvas(32, 20)
    cv.rect(0, 0, 31, 19, OUT)
    cv.rect(1, 1, 30, 18, "tee2")
    cv.rect(28, 1, 30, 18, "pj1")                  # 敷きぶとんの右の影
    cv.rect(3, 2, 12, 6, OUT)                      # まくら
    cv.rect(4, 3, 11, 5, "tee3")
    cv.line(4, 5, 11, 5, "pj2")
    cv.rect(1, 8, 27, 18, "pj1")                   # 掛けぶとん（敷きぶとんより一段濃い青）
    for y in (12, 15):                             # 縫い目
        cv.line(3, y, 24, y, "pj0")
    cv.rect(25, 13, 27, 18, "pj0")                 # 掛けぶとんの右の影
    # めくれた角（さっき起きた）：裏地の明るい三角。斜めのふちは 2 ドットずつ下がる段（ダブらないように）
    for k, x0 in enumerate((19, 21, 23, 25)):
        cv.line(x0, 8 + k, x0 + 1, 8 + k, OUT)
        cv.line(x0 + 2, 8 + k, 27, 8 + k, "pj3")
    cv.rect(1, 8, 18, 8, "pj2")                    # 掛けぶとんの上のふち（光の側）
    return cv.img


def desk():
    """机（32x30）：上の面に伏せたスマホ・3 時 12 分の目覚まし・消えた電気スタンド・本。正面に引き出し（父の絵はがき）。"""
    cv = Canvas(32, 30)
    cv.rect(0, 8, 31, 23, OUT)
    cv.rect(1, 9, 30, 14, "brown2")                # 上の面
    cv.line(0, 15, 31, 15, OUT)
    cv.rect(1, 16, 30, 22, "brown1")               # 正面
    cv.rect(28, 16, 30, 22, "brown0")              # 右の影
    cv.rect(3, 17, 14, 21, OUT)                    # 引き出し
    cv.rect(4, 18, 13, 20, "brown2")
    cv.rect(8, 19, 9, 19, "stone5")                # 取っ手
    for x in (2, 27):                              # 脚
        cv.rect(x - 1, 23, x + 2, 29, OUT)
        cv.rect(x, 23, x + 1, 28, "brown1")
    # 電気スタンド（消えている）
    cv.stamp([
        ".OOOO.",
        "OSSSSO",
        "OOOOOO",
        "..OO..",
        "..OO..",
        ".OOOO.",
    ], {"O": OUT, "S": "stone4"}, 23, 2)
    # 本（2 冊、背を見せて）
    cv.rect(17, 7, 21, 12, OUT)
    cv.rect(18, 8, 18, 11, "scarf0")
    cv.rect(20, 8, 20, 11, "red1")
    # 伏せたスマホ
    cv.rect(4, 10, 9, 12, OUT)
    cv.line(5, 11, 8, 11, "night2")
    # 目覚まし（白い文字盤。3 時 12 分：短針は右、長針は少し右上）
    cv.stamp([
        ".OOOO.",
        "OWWWWO",
        "OWOWWO",
        "OWOOOO",
        "OWWWWO",
        ".OOOO.",
    ], {"O": OUT, "W": "stone7"}, 11, 5)
    return cv.img


def window_bay():
    """湾の見える窓（32x24）：夜空・満月のはし・湾をまたぐ高架道路の灯り。左右に青いカーテン。"""
    cv = Canvas(32, 24)
    frame_box(cv, 0, 0, 31, 23, "night1", frame="brown2")
    cv.rect(3, 3, 28, 12, "night2")                # 空（上は少し明るい）
    cv.stamp([".WWW", "WWWW", "WWMW", ".WWW"], {"W": "moon3", "M": "moon2"}, 22, 4)   # 満月（窓のはしに）
    cv.line(3, 15, 28, 15, "night3")               # 高架道路
    for x in range(5, 28, 5):
        cv.dot(x, 14, "warm5")                     # 道路の灯り
    cv.dot(9, 16, "moon1")                         # 車の光
    cv.line(15, 3, 15, 20, "brown2")               # 窓の桟
    cv.line(16, 3, 16, 20, "brown1")
    cv.rect(0, 0, 3, 23, "pj1")                    # カーテン（左右。光の側が明るい）
    cv.line(1, 0, 1, 23, "pj2")
    cv.rect(28, 0, 31, 23, "pj1")
    cv.line(30, 0, 30, 23, "pj2")
    cv.line(0, 0, 0, 23, OUT)
    cv.line(31, 0, 31, 23, OUT)
    return cv.img


def sink():
    """流し台（32x30）：ステンレスの天板と流し、蛇口、伏せたコップ 1 つ。正面はクリーム色の戸。"""
    cv = Canvas(32, 30)
    cv.rect(0, 6, 31, 29, OUT)
    cv.rect(1, 7, 30, 12, "stone6")                # 天板
    cv.rect(10, 8, 21, 11, OUT)                    # 流し
    cv.rect(11, 9, 20, 11, "stone4")
    cv.stamp(["OOO", "O..", "O.."], {"O": "stone4"}, 13, 3)   # 蛇口
    cv.line(16, 3, 16, 7, OUT)
    cv.rect(24, 7, 26, 9, "moon1")                 # 伏せたコップ（1 つだけ）
    cv.line(0, 13, 31, 13, OUT)
    cv.rect(1, 14, 30, 28, "tee2")                 # 戸
    cv.rect(27, 14, 30, 28, "stone5")              # 右の影
    cv.line(15, 14, 15, 28, OUT)
    cv.dots([(12, 20), (18, 20)], "stone4")        # 取っ手
    return cv.img


def fridge():
    """冷蔵庫（16x38）：古い白い 2 ドア。上の戸に母の書き置き（黄色い紙、丸い字）と赤いマグネット。"""
    cv = Canvas(16, 38)
    cv.rect(0, 0, 15, 37, OUT)
    cv.rect(1, 1, 14, 3, "stone7")                 # 上の面
    cv.rect(1, 4, 14, 36, "stone6")                # 正面
    cv.rect(12, 4, 14, 36, "stone5")               # 右の影
    cv.line(1, 4, 14, 4, OUT)
    cv.line(1, 15, 14, 15, OUT)                    # 戸の境目
    cv.line(2, 7, 2, 12, "stone4")                 # 取っ手
    cv.line(2, 18, 2, 26, "stone4")
    cv.rect(5, 7, 11, 13, "warm5")                 # 書き置き
    cv.line(6, 9, 10, 9, "warm3")
    cv.line(6, 11, 9, 11, "warm3")
    cv.rect(7, 6, 8, 7, "red2")                    # マグネット
    return cv.img


def kitchen_table():
    """台所のテーブル（32x22）：二人用。上にラップをかけた皿は無い（おかずは冷蔵庫）。箸立てだけ。"""
    cv = Canvas(32, 22)
    cv.rect(0, 4, 31, 13, OUT)
    cv.rect(1, 5, 30, 9, "brown3")                 # 上の面（明るい木）
    cv.line(0, 10, 31, 10, OUT)
    cv.rect(1, 11, 30, 12, "brown2")
    cv.rect(28, 11, 30, 12, "brown1")
    for x in (3, 27):                              # 脚
        cv.rect(x - 1, 13, x + 1, 21, OUT)
        cv.line(x, 13, x, 20, "brown2")
    cv.rect(21, 1, 23, 6, OUT)                     # 箸立て
    cv.line(22, 2, 22, 5, "green1")
    return cv.img


def chair(with_scarf):
    """椅子（14x22）。with_scarf：背もたれに青いマフラー（ミオの手編み）がかかっている。"""
    cv = Canvas(14, 22)
    cv.rect(1, 0, 12, 3, OUT)                      # 背もたれ
    cv.rect(2, 1, 11, 2, "brown2")
    for x in (1, 11):
        cv.rect(x, 3, x + 1, 12, OUT)
    cv.rect(0, 11, 13, 15, OUT)                    # 座面
    cv.rect(1, 12, 12, 13, "brown2")
    cv.line(1, 14, 12, 14, "brown1")
    for x in (1, 10):                              # 脚
        cv.rect(x, 15, x + 2, 21, OUT)
        cv.line(x + 1, 15, x + 1, 20, "brown1")
    if with_scarf:
        cv.stamp([
            "OOOOOOOOOOO",
            "OSSssssssSO",
            "OsSssssssOO",
            ".OssO.OssO.",
            ".OssO.OsSO.",
            ".OssO.OssO.",
            ".OssO.OssO.",
            ".OsdO.OsdO.",
            ".OddO.OddO.",
            ".OOOO.OOOO.",
            "..F.F..F.F.",
        ], {"O": OUT, "S": "scarf2", "s": "scarf1", "d": "scarf0", "F": "scarf1"}, 1, 0)
    return cv.img


def shoe_cabinet():
    """靴箱（32x24）：木の戸 2 枚。上に鍵の小皿と、小さな鉢植え。"""
    cv = Canvas(32, 24)
    cv.rect(0, 6, 31, 23, OUT)
    cv.rect(1, 7, 30, 9, "brown2")                 # 上の面
    cv.line(0, 10, 31, 10, OUT)
    cv.rect(1, 11, 30, 22, "brown1")
    cv.rect(28, 11, 30, 22, "brown0")
    cv.line(15, 11, 15, 22, OUT)
    cv.dots([(12, 16), (18, 16)], "brown3")        # 取っ手
    cv.rect(4, 5, 9, 7, OUT)                       # 鍵の小皿
    cv.line(5, 6, 8, 6, "stone5")
    cv.dot(6, 5, "warm4")                          # 鍵
    cv.stamp([".GG.", "GGgG", ".OO.", ".OO."], {"G": "green2", "g": "green1", "O": "brown0"}, 22, 2)   # 鉢植え
    return cv.img


def tansu(folded):
    """小さな整理だんす（16x32、ルリの部屋）：引き出し 3 段。上の面にたたんだ服。序章でここで着がえる（v0.19）。
    folded="dress"：たたんだワンピース（淡い青、すそに白いレース）。"pajama"：着がえたあと、たたんだパジャマ（淡いピンク）。"""
    cv = Canvas(16, 32)
    cv.rect(0, 8, 15, 31, OUT)
    cv.rect(1, 9, 14, 11, "brown2")                # 上の面
    cv.line(0, 12, 15, 12, OUT)
    cv.rect(1, 13, 14, 30, "brown1")               # 正面
    cv.rect(13, 13, 14, 30, "brown0")              # 右の影
    for y0 in (14, 20, 26):                        # 引き出し
        cv.rect(2, y0, 12, y0 + 4, OUT)
        cv.rect(3, y0 + 1, 11, y0 + 3, "brown2")
        cv.dot(7, y0 + 2, "stone5")                # 取っ手
    # たたんだ服（上の面にのせる）
    ramp = ("pj1", "pj2", "pj3", "tee3") if folded == "dress" else ("slp1", "slp2", "slp3", "tee3")
    cv.rect(2, 5, 12, 10, OUT)
    cv.rect(3, 6, 11, 7, ramp[2])                  # たたんだ上の面
    cv.rect(3, 8, 11, 9, ramp[1])                  # 重ねた厚み
    cv.line(10, 6, 11, 6, ramp[1])
    cv.line(3, 9, 11, 9, ramp[3] if folded == "dress" else ramp[0])   # ワンピースはすそのレース、パジャマは影
    return cv.img


def floor_tile(x, row):
    """床のタイル（マップの x と、上からの行）。部屋（x 1〜7）は畳：2 行で 1 枚、上の行にへり。
    台所と玄関の上がり口はクッションフロア、玄関の戸の前（下の 2 行、x 14 以上）は土間。
    Unity の BlueNightSetup.Chapter1（RoomFloor）も同じ決め方。"""
    if x <= 7:
        return "tatami_1" if row % 2 == 1 else "tatami_0"
    if x >= 14 and row >= 7:
        return "tataki"
    return "floor_vinyl"


def build(save):
    tiles = {
        "tatami_0": tatami(0), "tatami_1": tatami(1), "floor_vinyl": floor_vinyl(), "tataki": tataki(),
        "home_wall_0": wall(0), "home_wall_1": wall(1), "home_wall_base": wall_base(),
    }
    out = {}
    for name, img in tiles.items():
        out[name] = save(img, "Home", "Tiles", f"{name}.png")
    things = {
        "futon": futon(), "desk": desk(), "window_bay": window_bay(), "sink": sink(), "fridge": fridge(),
        "kitchen_table": kitchen_table(), "chair": chair(False), "chair_scarf": chair(True),
        "shoe_cabinet": shoe_cabinet(), "tansu_dress": tansu("dress"), "tansu_pajama": tansu("pajama"),
    }
    for name, img in things.items():
        out[name] = save(img, "Home", f"{name}.png", clean=True)
    return out
