"""会話の顔グラフィック（48x48）を書き出す。

v0.16 のリデザインから、絵そのものは人物ごとのファイルで描く（輪郭線なし・月明かりの縁取り、chara.py）。
- ルリ：ruri.py（portrait。序章の服の顔と、ルリの影の顔も）
- 回想 1 の 8 歳のルリとミオ：kids.py（portrait）
- おばあさん（ハル）・ランプ屋の主人（青柳）：townsfolk.py
- ネム：nemu.py（build.py の build_nemu で書き出す）
輪郭線が無いので clean_corners はかけない。
"""

import kids
import ruri
import townsfolk


def build(save):
    out = {}
    for e in ruri.EXPRESSIONS:
        out[f"ruri_{e}"] = save(ruri.portrait(e), "Faces", f"face_ruri_{e}.png")
        # 序章の服（v0.19）：パジャマ、マフラー無しのワンピース。会話ウィンドウがフラグで選ぶ
        for outfit in ("pajama", "noscarf"):
            out[f"ruri_{outfit}_{e}"] = save(ruri.portrait(e, outfit), "Faces", f"face_ruri_{outfit}_{e}.png")
    out["ruri_shadow_normal"] = save(ruri.shadow_portrait(), "Faces", "face_ruri_shadow_normal.png")
    # 回想 1 の 8 歳の二人
    for e in ("normal", "smile"):
        out[f"mio_kid_{e}"] = save(kids.portrait("mio", e), "Faces", f"face_mio_kid_{e}.png")
    for e in ("normal", "sad"):
        out[f"ruri_kid_{e}"] = save(kids.portrait("ruri", e), "Faces", f"face_ruri_kid_{e}.png")
    for e in ("normal", "smile"):
        out[f"keeper_{e}"] = save(townsfolk.aoyagi_portrait(e), "Faces", f"face_keeper_{e}.png")
    for e in ("normal", "smile", "teary"):
        out[f"grandma_{e}"] = save(townsfolk.haru_portrait(e), "Faces", f"face_grandma_{e}.png")
    return out
