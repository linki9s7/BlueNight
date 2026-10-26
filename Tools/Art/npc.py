"""第 1 章の人物と影：ランプ屋の主人、ルリの影、のら猫と猫の影（落とし影）。

描き方は Tools/Art/STYLE.md のとおり（光は左上、影は右下にかたまり、1 ドットの輪郭）。
- ランプ屋の主人：影が逃げたことに唯一気づいている老人。はげ頭に白い横髪、丸めがね、白い口ひげ、革の前かけ。
- ルリの影：逃げた影と同じ「真っ黒＋水色のふち」。ただしいたずら好きなので、目が 2 つ光る（下・横向きのとき）。
- のら猫：商店街の環境の生き物。その影は「落とし影」（3.6）として捕まえられる。
"""

from PIL import Image

import ruri
from m1_assets import silhouette
from palette import RAMPS, hex_to_rgba

CLEAR = (0, 0, 0, 0)


def P(name):
    ramp = name.rstrip("0123456789")
    return hex_to_rgba(RAMPS[ramp][int(name[len(ramp):])])


def from_map(rows, key):
    w = len(rows[0])
    img = Image.new("RGBA", (w, len(rows)), CLEAR)
    px = img.load()
    for y, row in enumerate(rows):
        assert len(row) == w, f"row {y}: {row!r} ({len(row)} != {w})"
        for x, ch in enumerate(row):
            if ch != ".":
                px[x, y] = P(key[ch])
    return img


# ---------------------------------------------------------------- ランプ屋の主人（16x30）
KEEPER_KEY = {
    "O": "night1",
    "S": "skin2", "s": "skin1", "m": "skin0",
    "H": "stone7", "h": "stone5",     # 白い横髪
    "L": "moon1",                     # めがねのレンズ（月明かりの照り返し）
    "W": "stone7", "w": "stone5",     # 口ひげ
    "C": "coat2", "c": "coat1",       # シャツ
    "A": "brown2", "a": "brown1",     # 革の前かけ
    "P": "stone3", "p": "stone2",     # ズボン
    "F": "night3",                    # 靴
}

KEEPER = [
    "................",
    ".....OOOOO......",
    "....OSSSSSO.....",
    "...OSSSSSSsO....",
    "..OHHSSSSSsHO...",
    "..OHHSSSSSshO...",
    "..OHOOOSOOOhO...",
    "..OhOLOSOLOhO...",
    "..OhSOOSOOsshO..",
    "...OSSSSSssO....",
    "...OSWWWWwsO....",
    "....OSWmwsO.....",
    "....OOSSSOO.....",
    "...OCCOSOCcO....",
    "..OCCAACAAccO...",
    ".OCCAAACAAaccO..",
    ".OCCAAAAAAaccO..",
    ".OCOAAAAAAaOcO..",
    ".OSOAAAAAaaOsO..",
    ".OSOAAAAAaaOsO..",
    "..OOAAAAAaaOO...",
    "...OAAAAAaaO....",
    "...OAAAAAaaO....",
    "...OPPPOPppO....",
    "...OPPPOPppO....",
    "...OPPPOPppO....",
    "..OFFFFOFFFFO...",
    "..OFFFFOFFFFO...",
    "..OOOOOOOOOOO...",
]


def keeper_frames():
    """2 コマ：ふつう／ゆっくりうなずく（頭が 1 ドット下がる）。"""
    nod = ["." * 16] + KEEPER[:12] + KEEPER[13:]
    return [from_map(KEEPER, KEEPER_KEY), from_map(nod, KEEPER_KEY)]


# ---------------------------------------------------------------- ルリの影
def ruri_shadow_frames(anim, direction):
    """ルリのコマから作る逃げた影。下向き・横向きは目が光る（ルリの目の位置、ふちと同じ水色の明るい色）。"""
    frames = []
    for i, rows in enumerate(ruri.frames(anim, direction)):
        body = Image.new("RGBA", (16, 32), CLEAR)
        px = body.load()
        eyes = []
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != ".":
                    px[x, y] = (0, 0, 0, 255)
                if ch == "E" and direction != "up":
                    eyes.append((x, y))
        img = silhouette(body, wobble=[0, 1, 0, -1][i % 4])
        out = img.load()
        for (x, y) in eyes:
            out[x + 1, y + 1] = P("moon2")  # silhouette は 1 ドット外側に広がる
        frames.append(img)
    return frames


# ---------------------------------------------------------------- のら猫（16x12、横向き・座り）
CAT_KEY = {
    "O": "night1",
    "C": "stone5", "c": "stone4",   # 灰色の毛（左上が明るい）
    "W": "stone7",                  # 胸の白
    "E": "warm4",                   # 夜に光る目
    "n": "red2",                    # 鼻
}

CAT = [
    "..O.O...........",
    ".OCOCO..........",
    ".OCCCO..........",
    ".OECEO......OO..",
    ".OCnCO.....OcO..",
    "..OWOOOOO..OcO..",
    "..OWCCCCcO.OcO..",
    ".OWWCCCCccOOcO..",
    ".OWWCCCCcccOO...",
    ".OWCCCCccccO....",
    ".OOCOOCOcOcO....",
    "..OOOOOOOOOO....",
]

CAT_BLINK = CAT[:3] + [".OCCCO......OO.."] + CAT[4:]
CAT_TAIL = CAT[:3] + [
    ".OECEO..........",
    ".OCnCO.....OOO..",
    "..OWOOOOO.OccO..",
    "..OWCCCCcOOcO...",
] + CAT[7:]


def cat_frames():
    """4 コマ：座る／まばたき／しっぽを振る／座る。"""
    return [from_map(CAT, CAT_KEY), from_map(CAT_BLINK, CAT_KEY), from_map(CAT_TAIL, CAT_KEY), from_map(CAT, CAT_KEY)]


def cat_shadow_frames():
    """猫の影（落とし影）：猫と同じ形の逃げた影。目が 2 つ光る。"""
    frames = []
    for i, img in enumerate(cat_frames()[:2] + cat_frames()[2:3] + cat_frames()[:1]):
        body = img.copy()
        sil = silhouette(body, wobble=[0, 1, 0, -1][i])
        px = sil.load()
        if i != 1:  # 2 コマ目はまばたき
            px[2 + 1, 3 + 1] = P("moon2")
            px[4 + 1, 3 + 1] = P("moon2")
        frames.append(sil)
    return frames


def build(save):
    out = {"keeper": [], "cat": [], "cat_shadow": [], "ruri_shadow": {}}
    for i, img in enumerate(keeper_frames()):
        out["keeper"].append(save(img, "Characters", "Keeper", f"keeper_idle_{i}.png", clean=True))
    for i, img in enumerate(cat_frames()):
        out["cat"].append(save(img, "Characters", "Cat", f"cat_idle_{i}.png", clean=True))
    rim = [RAMPS["moon"][0], RAMPS["moon"][1]]
    for i, img in enumerate(cat_shadow_frames()):
        out["cat_shadow"].append(save(img, "Characters", "Shadows", f"shadow_cat_{i}.png", clean=True, outline=rim))
    for anim in ("idle", "walk"):
        for direction in ("down", "up", "right", "left"):
            imgs = []
            for i, img in enumerate(ruri_shadow_frames(anim, direction)):
                imgs.append(save(img, "Characters", "Shadows", f"shadow_ruri_{anim}_{direction}_{i}.png", clean=True, outline=rim))
            out["ruri_shadow"][(anim, direction)] = imgs
    return out
