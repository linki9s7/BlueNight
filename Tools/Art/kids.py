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
    "S": Mat("skin2", "skin1", group="SEeIrm"),
    "P": Mat("pj2", "pj1", "pj3", group="P", d=2),
    "T": Mat("tee2", "tee1", "tee3", group="T", d=2),
    "D": Mat("scarf0", "night3", "scarf1", group="D"),
    "R": Mat("red1", "red0", "red2"),
    "F": Mat("hair1", "hair0", "hair2"),
}
DIRECT = {"E": "hair0", "e": "moon3", "I": "iris1", "r": "blush0", "m": "brown1", "a": "skin2", "h": "hair3",
          "L": "stone5", "Y": "warm5", "g": "skin2"}
W, H = 12, 22

# ---------------------------------------------------------------- 8 歳のルリ
RURI_HEAD_DOWN = [
    "............",
    "..H..HH..H..",   # 猫の耳のような寝ぐせ
    "..HHHHHHHH..",
    ".HHhhHHHHHH.",
    ".HHHHHHHHHH.",
    ".HHSHHHHSHH.",   # ぱっつんの前髪
    ".HSEESSEESH.",
    ".HSeISSeISH.",
    ".HSrSSSSrSH.",
    ".HHSSSSSSHH.",
    "..HHSSSSHH..",   # おかっぱ（あごの高さ）
]
RURI_BODY_DOWN = [
    "...PPPPPP...",
    "..PPPPPPPP..",
    ".aPPPPPPPPS.",
    ".aPPPPPPPPS.",
    ".SPPPPPPPPS.",
    "..PPPPPPPP..",
]
RURI_LEGS_STAND = [
    "...SS..SS...",
    "...SS..SS...",
    "...FF..FF...",
    "............",
    "............",
]
RURI_LEGS_SIT = [   # ベンチに座って足をぶらぶら（2 コマ）：ひざから下が前へ出て、足先が交互に揺れる
    ["..SSS..SSS..", "...SS...SS..", "...FF...FF..", "............", "............"],
    ["..SSS..SSS..", "..SS...SS...", "..FF...FF...", "............", "............"],
]
RURI_HEAD_SIDE = [
    "............",
    "...H..HH....",
    "...HHHHHH...",
    "..HhhHHHHH..",
    "..HHHHHHHHH.",
    "..HHHHHHSSH.",
    "..HHHHHSEES.",
    "..HHHHHSeIS.",
    "..HHHHHSrSS.",
    "..HHHHHSSS..",
    "...HHHHSS...",
]
RURI_BODY_SIDE = [   # 走る：上体を少し前へ
    "....PPPP....",
    "...PPPPPP...",
    "...PPPPPPP..",
    "...PPPPPPP..",
    "..PPPPPPPP..",
    "..PPPPPPPP..",
]

# ---------------------------------------------------------------- 8 歳のミオ
MIO_HEAD_DOWN = [
    "........MM..",   # ポニーテールの結び目（右上にのぞく）
    "...MMMMMMM..",
    "..MMggMMMMM.",
    ".MMMMMMMMMM.",
    ".MMMMMMMMMM.",
    ".MSMMMMMMSM.",   # 横に流した前髪
    ".MSEESSEESM.",
    ".MSeISSeISM.",
    ".MSrSSSSrSM.",
    "..SSSmmSSS..",   # 笑っている口
    "...SSSSSS...",
]
MIO_BODY_DOWN = [
    "...TTTTTT...",
    "..TTTTTTTT..",
    ".aTTTTTTTTS.",
    ".aTTTTTTTTL.",   # 右手（画面右）に懐中電灯
    ".STTTTTTTTY.",
    "..DDDDDDDD..",
]
MIO_LEGS_STAND = [
    "...SS..SS...",
    "...SS..SS...",
    "...RR..RR...",
    "............",
    "............",
]
MIO_HEAD_SIDE = [
    "............",
    "...MMMMMM...",
    "..MggMMMMM..",
    "MMMMMMMMMMM.",   # ポニーテールが後ろへなびく
    ".MMMMMMMMSM.",
    "MM.MMMMMSSS.",
    "...MMMMSEES.",
    "...MMMMSeIS.",
    "...MMMMSrSS.",
    "...MMMMSSmS.",
    "....MMSSSS..",
]
MIO_BODY_SIDE = [
    "....TTTT....",
    "...TTTTTT...",
    "...TTTTTTTL.",   # 懐中電灯を前へ
    "...TTTTTTTY.",
    "..DDDDDDDD..",
    "..DDDDDDDD..",
]

# 走る脚（横向き、5 行 × 4 コマ）。shoe は靴の記号
def run_legs(shoe):
    return [
        ["...SS..SS...", "..SS....SS..", ".SS......S..", f".{shoe}........{shoe}.", "............"],
        ["....SSSS....", "....S..S....", "...SS..S....", f"...{shoe}...{shoe}....", "............"],
        ["...SS..SS...", "..S....SS...", "..S.....SS..", f"..{shoe}......{shoe}{shoe}.", "............"],
        ["....SSSS....", "....S..S....", "....S..SS...", f"....{shoe}...{shoe}...", "............"],
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
# 今のルリの顔（ruri.portrait）と同じ目・眉・口を使い、顔を少し丸く、髪を子どもの形にする。
def portrait(who="mio", expression="normal"):
    """who：mio（明るい茶色のポニーテール・白い T シャツ）／ruri（おかっぱ・猫の耳のような寝ぐせ・淡い青のワンピース）。"""
    import ruri
    from chara import Canvas
    c = Canvas(48, 48)
    if who == "mio":
        c.poly([(33, 12), (40, 16), (42, 30), (38, 40), (35, 30), (33, 20)], "M")   # ポニーテール（向かって右、頭のうしろ）
        c.poly(ruri.SHOULDERS, "T")
        c.rect((20, 30, 27, 38), "S")
        c.ellipse((17, 34, 30, 40), "S", only="T")                                   # 丸首
        c.ellipse((11, 5, 37, 33), "M")
        c.ellipse((13, 11, 35, 37), "S")
        c.poly([(11, 8), (37, 8), (37, 14), (28, 16), (20, 19), (13, 21), (11, 18)], "M", only="S.M")  # 斜めに流した前髪
        c.line([(14, 12), (19, 9), (25, 8)], "g", only="M")                          # 髪のつや
        c.rect((33, 13, 34, 14), "R")                                                # 赤い髪ゴム
        c.rect((12, 18, 13, 30), "M")
        c.rect((35, 18, 36, 28), "M")
        mats = dict(ruri.FACE_MATS, M=MATS["M"], T=Mat("tee2", "tee1", "tee3", group="T", d=3), R=MATS["R"])
        direct = dict(ruri.FACE_DIRECT, i="brown1", I="brown0", o="brown2", g="skin2", q="brown1")
    else:
        c.poly(ruri.SHOULDERS, "P")
        c.rect((20, 30, 27, 38), "S")
        c.ellipse((16, 34, 31, 40), "S", only="P")
        c.ellipse((10, 4, 38, 33), "H")
        c.rect((10, 16, 38, 34), "H", only=".")                                     # おかっぱ（あごの下で切りそろえる）
        c.ellipse((13, 11, 35, 37), "S")
        c.rect((12, 7, 36, 19), "H", only="S.H")                                     # ぱっつん前髪
        c.poly([(12, 9), (14, 2), (18, 6)], "H", only=".")                           # 猫の耳のような寝ぐせ（このころから）
        c.poly([(30, 6), (34, 2), (36, 9)], "H", only=".")
        c.line([(13, 12), (17, 9), (23, 8)], "h", only="H")
        mats = ruri.FACE_MATS
        direct = ruri.FACE_DIRECT
    left_brow, right_brow, by = ruri.BROWS[expression]
    c.stamp(left_brow, 16, by)
    c.stamp(right_brow, 27, by)
    eyes = ruri.EYES[expression]
    left, right = eyes if isinstance(eyes, tuple) else (eyes, eyes)
    c.stamp(left, 16, 23)
    c.stamp(right, 26, 23)
    c.stamp(["rr"], 15, 31)
    c.stamp(["rr"], 31, 31)
    mouth = ruri.MOUTHS[expression]
    c.stamp(mouth, 24 - len(mouth[0]) // 2, 33)
    return render(c.rows(), mats, direct, STYLE)
