"""第 1 章の人物と影：ランプ屋の主人、ルリの影、のら猫と猫の影（落とし影）。

主人と猫の絵は townsfolk.py（v0.16：輪郭線なし・月明かりの縁取り）。影は「真っ黒＋水色のふち」。
- ランプ屋の主人：影が逃げたことに唯一気づいている老人。はげ頭に白い横髪、丸めがね、白い口ひげ、革の前かけ。
- ルリの影：逃げた影と同じ「真っ黒＋水色のふち」。ただしいたずら好きなので、目が 2 つ光る（下・横向きのとき）。
- のら猫：商店街の環境の生き物。その影は「落とし影」（3.6）として捕まえられる。
"""

from PIL import Image

import ruri
import townsfolk
from m1_assets import silhouette
from palette import RAMPS, hex_to_rgba

CLEAR = (0, 0, 0, 0)


def P(name):
    ramp = name.rstrip("0123456789")
    return hex_to_rgba(RAMPS[ramp][int(name[len(ramp):])])


# ---------------------------------------------------------------- ランプ屋の主人
def keeper_frames():
    """2 コマ：ふつう／ゆっくりうなずく（絵は townsfolk.py）。"""
    return townsfolk.aoyagi_frames()


# ---------------------------------------------------------------- ルリの影
def fill_holes(img):
    """外につながっていない透明の穴（腕と体のすき間など）を埋める。影の中に水色のふちの点ができないように。"""
    px = img.load()
    w, h = img.size
    outside = set()
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in outside or not (0 <= x < w and 0 <= y < h) or px[x, y][3]:
            continue
        outside.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in range(h):
        for x in range(w):
            if not px[x, y][3] and (x, y) not in outside:
                px[x, y] = (0, 0, 0, 255)


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
        fill_holes(body)
        img = silhouette(body, wobble=[0, 1, 0, -1][i % 4])
        out = img.load()
        for (x, y) in eyes:
            out[x + 1, y + 1] = P("moon2")  # silhouette は 1 ドット外側に広がる
        frames.append(img)
    return frames


# ---------------------------------------------------------------- のら猫
def cat_frames():
    """4 コマ：座る／まばたき／しっぽを振る／座る（絵は townsfolk.py）。"""
    return townsfolk.goma_frames()


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
        out["keeper"].append(save(img, "Characters", "Keeper", f"keeper_idle_{i}.png"))
    for i, img in enumerate(cat_frames()):
        out["cat"].append(save(img, "Characters", "Cat", f"cat_idle_{i}.png"))
    rim = [RAMPS["moon"][0], RAMPS["moon"][1]]
    for i, img in enumerate(cat_shadow_frames()):
        out["cat_shadow"].append(save(img, "Characters", "Shadows", f"shadow_cat_{i}.png", clean=True, outline=rim))
    for anim in ("idle", "walk", "run"):
        for direction in ("down", "up", "right", "left"):
            imgs = []
            for i, img in enumerate(ruri_shadow_frames(anim, direction)):
                imgs.append(save(img, "Characters", "Shadows", f"shadow_ruri_{anim}_{direction}_{i}.png", clean=True, outline=rim))
            out["ruri_shadow"][(anim, direction)] = imgs
    return out
