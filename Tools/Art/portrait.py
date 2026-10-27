"""会話の顔グラフィック（48x48）を書き出す。

v0.16 のリデザインから、絵そのものは人物ごとのファイルで描く（輪郭線なし・月明かりの縁取り、chara.py）。
- ルリ：ruri.py（portrait）
- おばあさん（ハル）・ランプ屋の主人（青柳）：townsfolk.py
- ネム：nemu.py（build.py の build_nemu で書き出す）
輪郭線が無いので clean_corners はかけない。
"""

import ruri
import townsfolk


def build(save):
    out = {}
    for e in ruri.EXPRESSIONS:
        out[f"ruri_{e}"] = save(ruri.portrait(e), "Faces", f"face_ruri_{e}.png")
    for e in ("normal", "smile"):
        out[f"keeper_{e}"] = save(townsfolk.aoyagi_portrait(e), "Faces", f"face_keeper_{e}.png")
    for e in ("normal", "smile", "teary"):
        out[f"grandma_{e}"] = save(townsfolk.haru_portrait(e), "Faces", f"face_grandma_{e}.png")
    return out
