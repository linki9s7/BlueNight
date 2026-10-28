"""回想 1（バス停のベンチ）の 8 歳のルリとミオ（12x22 px）と、二人の足元の影。

台本：docs/STORY.md 9.1。ユーザーの希望で「ゲームの中で動く回想」：思い出の色のバス停で、
ベンチで足をぶらぶらさせる 8 歳のルリのところへ、懐中電灯を持ったミオが来て「影踏みしよ」。二人は街灯の下で影を踏み合う。
**二人とも足元に影がある**（今のルリには無い。その対比が場面の芯）。

描き方は今の人物と同じ（chara.py：輪郭線なし・左上の縁に月明かり・左向きは図を反転してから陰影）。
- 8 歳のルリ：短めのおかっぱ。**猫の耳のような寝ぐせはこのころから**（チャームポイント）。淡い青のワンピース、紺のサンダル。
- 8 歳のミオ：明るい茶色のポニーテール、白い T シャツ、紺の半ズボン、赤い運動ぐつ、懐中電灯。明るく先に話しかける子なので、口は笑っている。
  赤いマフラー（ルリとおそろい）は後年のものなので、ここでは付けない（docs/CHARACTERS.md）。
- 影：絵の形を上下にひっくり返して少し縮め、暗い半透明の色で塗る（街灯は奥＝北にあるので、影は足元から手前へのびる）。
  絵を拡大・縮小しない（行を間引くだけ）ので、ドットの大きさは混ざらない。

記号：H ルリの髪  M ミオの髪  h ルリの髪のつや  g ミオの髪のつや  S 肌  a 光の側の腕（明るい肌）  E 目のふち  e 目のつや  I 瞳  r ほお  m 口
      P ワンピース  F サンダル  T T シャツ  D 半ズボン  R 運動ぐつ  L 懐中電灯  Y 懐中電灯の光る所
"""

from PIL import Image

from chara import Mat, Style, mirror, render
from palette import hex_to_rgba, RAMPS

STYLE = Style("none", rim=True)
MATS = {
    "H": Mat("hair2", "hair1", "hair3", group="Hh", d=2),
    "M": Mat("brown3", "brown2", "skin1", group="Mg", d=2),
    "S": Mat("skin2", "skin1", group="SEeIrmOW"),
    "P": Mat("pj2", "pj1", "pj3", group="P", d=2),
    "T": Mat("tee2", "tee1", "tee3", group="T", d=2),
    "D": Mat("scarf0", "night3", "scarf1", group="D"),
    "R": Mat("red1", "red0", "red2"),
    "F": Mat("hair1", "hair0", "hair2"),
}
DIRECT = {"E": "hair0", "e": "moon3", "I": "iris1", "r": "blush0", "m": "brown1", "a": "skin2", "h": "hair3",
          "L": "stone5", "Y": "warm5", "g": "skin2", "O": "brown0", "W": "tee3"}
W, H = 12, 22

# ---------------------------------------------------------------- 8 歳のルリ
# 8 歳らしく（ユーザーの指摘：大人っぽすぎる）：頭 13 行・胴 5 行・脚 2 行の、頭の大きい形。顔は下ぶくれで、目は低い位置。
RURI_HEAD_DOWN = [
    "..H......H..",   # 猫の耳のような寝ぐせ
    "..HH.HH.HH..",
    ".HHHHHHHHHH.",
    "HHhhHHHHHHHH",
    "HHHHHHHHHHHH",
    "HHHHHHHHHHHH",   # 目の上までの重たい前髪
    "HHSSSSSSSSHH",
    "HSEESSSSEESH",
    "HSeISSSSeISH",
    "HSIISSSSIISH",
    "HHrSSmmSSrHH",
    ".HSSSSSSSSH.",
    "..HSSSSSSH..",   # おかっぱ（あごの高さ）
]
RURI_BODY_DOWN = [
    "...PPPPPP...",
    "..aPPPPPPS..",
    "..aPPPPPPS..",
    "..PPPPPPPP..",
    ".PPPPPPPPPP.",
]
RURI_LEGS_STAND = [
    "...SS..SS...",
    "...FF..FF...",
    "............",
    "............",
]
RURI_LEGS_SIT = [   # ベンチに座って足をぶらぶら（2 コマ）：ひざから下が前へ出て、足先が交互に揺れる
    ["..SSS..SSS..", "...FF...FF..", "............", "............"],
    ["..SSS..SSS..", "..FF...FF...", "............", "............"],
]
RURI_HEAD_SIDE = [
    "...H...H....",
    "...HHHHH....",
    "..HHHHHHHH..",
    ".HhhHHHHHHH.",
    ".HHHHHHHHHHH",
    ".HHHHHHHHHHH",
    ".HHHHHHHSSSH",
    ".HHHHHHSEESS",
    ".HHHHHHSeISS",
    ".HHHHHHSIISS",
    ".HHHHHHSrSmS",
    ".HHHHHHSSSS.",
    "..HHHHSSSS..",
]
RURI_BODY_SIDE = [   # 走る：上体を少し前へ
    "....PPPP....",
    "...PPPPPP...",
    "...PPPPPPP..",
    "..PPPPPPPP..",
    "..PPPPPPPP..",
]

# ---------------------------------------------------------------- 8 歳のミオ
# ルリと別の顔つき（性格を出す）：おでこを出した前髪、まんまるの茶色の目（O）、歯を見せて笑う口（W）、頭の右上のポニーテール。
MIO_HEAD_DOWN = [
    ".....M......",   # 頭のてっぺんのはね毛
    "...MMMMMM.RM",   # ポニーテールの赤い髪ゴム（右上）
    "..MMggMMMMMM",
    ".MMMMMMMMMMM",
    ".MMMMMMMMMMM",
    ".MMMMSSSSSMM",   # 横に流した前髪（おでこが出る）
    ".MMSSSSSSSSM",
    ".MSOeSSSOeSM",
    ".MSOOSSSOOSM",
    ".MSrSSSSSrSM",
    "..SSSmWWmSS.",   # 歯を見せて笑う
    "..SSSSmmSSS.",
    "...SSSSSSS..",
]
MIO_BODY_DOWN = [
    "...TTTTTT...",
    "..aTTTTTTL..",   # 右手（画面右）に懐中電灯
    "..aTTTTTTY..",
    "..DDDDDDDD..",
    "..DDDDDDDD..",
]
MIO_LEGS_STAND = [
    "...SS..SS...",
    "...RR..RR...",
    "............",
    "............",
]
MIO_HEAD_SIDE = [
    "....M.......",
    "...MMMMMM...",
    "..MggMMMMM..",
    "MMMMMMMMMMM.",   # ポニーテールが後ろへなびく
    "MMMMMMMMSSM.",
    "M..MMMMSSSS.",
    "...MMMMSSSS.",
    "...MMMSSOeS.",
    "...MMMSSOOS.",
    "...MMMSrSSS.",
    "...MMMSSmWS.",
    "....MMSSSS..",
    ".....SSSS...",
]
MIO_BODY_SIDE = [
    "....TTTT....",
    "...TTTTTTL..",   # 懐中電灯を前へ
    "...TTTTTTY..",
    "..DDDDDDDD..",
    "..DDDDDDDD..",
]


# 走る脚（横向き、4 行 × 4 コマ）。shoe は靴の記号
def run_legs(shoe):
    s = shoe
    return [
        ["...SS..SS...", "..SS....SS..", f".{s}{s}......{s}{s}.", "............"],
        ["....SSSS....", "....S..S....", f"...{s}{s}..{s}{s}...", "............"],
        ["...SS..SS...", "..S.....SS..", f"..{s}.......{s}{s}", "............"],
        ["....SSSS....", "....S..SS...", f"....{s}...{s}{s}..", "............"],
    ]


RUN_BOB = (0, 1, 0, 1)   # 走ると 1 ドット上下にはねる（足が地面をけるコマで沈む）


def compose(head, body, legs, bob=0):
    rows = head + body + legs
    rows = rows[:H]
    while len(rows) < H:
        rows.append("." * W)
    if bob:
        rows = ["." * W] * bob + rows[:H - bob]
    return rows


def to_image(rows):
    return render(rows, MATS, DIRECT, STYLE)


def shadow_of(img, keep=3, drop_every=4, alpha=150):
    """足元の影：絵の形を上下にひっくり返し、drop_every 行ごとに 1 行間引いて短くし、暗い半透明の色で塗る（拡大・縮小しない）。"""
    w, h = img.size
    src = img.load()
    rows = []
    for y in range(h - 1, -1, -1):          # 足元（下）から頭へ
        if (h - 1 - y) % drop_every == drop_every - 1:
            continue
        rows.append([src[x, y][3] > 0 for x in range(w)])
    # 足元の空き行（透明）を取る
    while rows and not any(rows[0]):
        rows.pop(0)
    out = Image.new("RGBA", (w, len(rows) + keep), (0, 0, 0, 0))
    r, g, b, _ = hex_to_rgba(RAMPS["night"][0])
    px = out.load()
    for y, row in enumerate(rows):
        for x, on in enumerate(row):
            if on:
                px[x, y] = (r, g, b, alpha)
    return out


def frames():
    """{名前: [画像]}。走る左向きは図を反転してから陰影（光は左上のまま）。"""
    out = {}
    out["kid_ruri_sit_down"] = [to_image(compose(RURI_HEAD_DOWN, RURI_BODY_DOWN, legs)) for legs in RURI_LEGS_SIT]
    out["kid_ruri_idle_down"] = [to_image(compose(RURI_HEAD_DOWN, RURI_BODY_DOWN, RURI_LEGS_STAND, bob))
                                 for bob in (0, 0)]
    out["kid_mio_idle_down"] = [to_image(compose(MIO_HEAD_DOWN, MIO_BODY_DOWN, MIO_LEGS_STAND, bob)) for bob in (0, 0)]
    for who, head, body, shoe in (("ruri", RURI_HEAD_SIDE, RURI_BODY_SIDE, "F"), ("mio", MIO_HEAD_SIDE, MIO_BODY_SIDE, "R")):
        right = [compose(head, body, legs, RUN_BOB[i]) for i, legs in enumerate(run_legs(shoe))]
        out[f"kid_{who}_run_right"] = [to_image(r) for r in right]
        out[f"kid_{who}_run_left"] = [to_image(mirror(r)) for r in right]
    # 立っているときの呼吸：2 コマ目は頭を 1 ドット下げる代わりに、そのまま（小さい絵なので動かさない）
    return out


def build(save):
    out = {}
    for name, imgs in frames().items():
        out[name] = []
        for i, img in enumerate(imgs):
            out[name].append(save(img, "Characters", "Kids", f"{name}_{i}.png"))
            if "_sit_" not in name:   # 座っているときの影はベンチの影にまぎれるので作らない
                save(shadow_of(img), "Characters", "Kids", f"{name}_shadow_{i}.png")
    return out


# ================================================================ 顔グラフィック（48x48、回想 1 の会話ウィンドウ）
# 8 歳らしく（ユーザーの指摘：大人っぽすぎる）：頭を大きく丸く、顔は下ぶくれ、目は大きく低い位置、口と鼻は小さく、肩は細い。
# ミオはルリと別の顔つきに（性格を出す）：ルリ＝おかっぱの前髪が目の上まで・下を向きがちな青い目・小さな口（人見知り）。
# ミオ＝高いポニーテール・おでこを出した前髪・太い眉・まんまるで光の多い茶色の目・歯を見せて笑う・ほおのばんそうこう（元気で先に話しかける）。
KID_FACE_DIRECT = {"E": "hair0", "e": "moon3", "r": "blush0", "m": "skin0", "n": "skin1", "W": "tee3", "d": "red1",
                   "q": "hair1"}
KID_EYES = {
    # ルリ：上のふちが濃く、下は開いた大きな目。瞳は上が濃く下が明るい（今のルリと同じ色の付け方）
    ("ruri", "normal"): [".EEEEE.", "EEeeiiE", "EeeiiIE", ".iiIII.", ".iIIoI.", ".iIooI.", "..III.."],
    ("ruri", "sad"): ["......", ".......", "..EEEE.", ".EeiiE.", ".iiIII.", ".iIooI.", "..III.."],   # 伏し目
    # ミオ：ふちで丸く囲んだ、まんまるの目。つやが 2 つ（きらきら）
    ("mio", "normal"): [".EEEE.", "EeeIIE", "EeIIIE", "EIIIeE", "EIIIIE", ".EEEE."],
    ("mio", "smile"): ["......", "......", ".EEEE.", "E....E", "......", "......"],              # にっこり目を閉じる
}
KID_MOUTHS = {
    ("ruri", "normal"): [".mm."],
    ("ruri", "sad"): [".mm.", "m..m"],
    ("mio", "normal"): ["mmmmmm", "mWWWWm", ".mddm.", "..mm.."],      # 歯を見せて笑う
    ("mio", "smile"): ["mmmmmm", "mWWWWm", ".mddm.", "..mm.."],
}
KID_SHOULDERS = [(8, 47), (12, 44), (18, 42), (30, 42), (36, 44), (40, 47)]


def portrait(who="mio", expression="normal"):
    """who：mio（明るい茶色のポニーテール・白い T シャツ）／ruri（おかっぱ・猫の耳のような寝ぐせ・淡い青のワンピース）。"""
    from chara import Canvas
    c = Canvas(48, 48)
    if who == "mio":
        c.poly([(30, 7), (37, 3), (43, 7), (45, 16), (43, 26), (40, 20), (37, 13)], "M")   # 高いポニーテール（頭の右上から下がる）
        c.poly(KID_SHOULDERS, "T")
        c.rect((20, 39, 27, 43), "S")
        c.ellipse((7, 4, 41, 38), "M")
        c.ellipse((10, 12, 38, 44), "S")
        # 前髪：おでこを出して横へ流す（向かって左が長い）
        c.poly([(8, 9), (40, 9), (40, 14), (31, 13), (23, 15), (15, 19), (10, 23), (8, 19)], "M", only="S.M")
        c.poly([(21, 1), (24, 0), (26, 4), (23, 5)], "M", only=".")               # 頭のてっぺんのはね毛
        c.line([(12, 12), (17, 8), (24, 7)], "g", only="M")                      # 髪のつや
        c.rect((35, 5, 37, 7), "R")                                              # 赤い髪ゴム
        c.rect((8, 20, 10, 32), "M")
        c.rect((38, 20, 40, 30), "M")
        c.stamp(["qqqq", "q..."], 14, 21)                                        # 太い眉
        c.stamp(["qqqq", "...q"], 29, 21)
        c.stamp(KID_EYES[("mio", expression)], 14, 24)
        c.stamp(KID_EYES[("mio", expression)], 28, 24)
        c.stamp(["rrr"], 11, 32)
        c.stamp(["WWWW", "WnWW"], 32, 31)                                        # ほおのばんそうこう
        c.stamp(["n"], 24, 31)
        c.stamp(KID_MOUTHS[("mio", expression)], 21, 34)
        mats = {"M": MATS["M"], "S": Mat("skin2", "skin1", group="SEemnrWdq", d=2),
                "T": Mat("tee2", "tee1", "tee3", group="T", d=3), "R": MATS["R"]}
        direct = dict(KID_FACE_DIRECT, i="brown1", I="brown0", o="brown2", g="skin2", q="brown0")
    else:
        c.poly(KID_SHOULDERS, "P")
        c.ellipse((16, 40, 32, 47), "l")                                         # 丸い白い襟
        c.rect((21, 39, 26, 42), "S")
        c.ellipse((6, 3, 42, 40), "H")
        c.rect((6, 20, 42, 40), "H", only=".")                                  # おかっぱ（あごの下で切りそろえる）
        c.ellipse((10, 13, 38, 44), "S")
        c.rect((7, 22, 11, 40), "H")                                             # 顔の横の髪
        c.rect((37, 22, 41, 40), "H")
        c.rect((9, 7, 39, 22), "H", only="S.H")                                  # 目の上までの重たい前髪
        for x in (18, 29):                                                       # 毛先のすき間
            c.line([(x, 21), (x, 22)], "S", only="H")
        c.poly([(9, 9), (11, 0), (16, 5)], "H", only=".")                        # 猫の耳のような寝ぐせ（このころから）
        c.poly([(32, 5), (37, 0), (39, 9)], "H", only=".")
        c.line([(11, 11), (16, 7), (23, 6)], "h", only="H")
        c.stamp(KID_EYES[("ruri", expression)], 13, 24)
        c.stamp(KID_EYES[("ruri", expression)], 28, 24)
        c.stamp(["rrr"], 11, 33)
        c.stamp(["rrr"], 34, 33)
        c.stamp(["n"], 24, 32)
        c.stamp(KID_MOUTHS[("ruri", expression)], 22, 35)
        mats = {"H": Mat("hair2", "hair1", "hair3", group="Hh", d=2), "S": Mat("skin2", "skin1", group="SEeiIomnr", d=2),
                "P": Mat("pj2", "pj1", "pj3", group="P", d=3), "l": Mat("tee3", "tee2", group="l", d=2)}
        direct = dict(KID_FACE_DIRECT, i="iris0", I="iris1", o="iris2", h="hair3")
    return render(c.rows(), mats, direct, STYLE)
