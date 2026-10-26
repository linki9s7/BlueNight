"""BGM をまとめて書き出す。

使い方（リポジトリのルートで）:
    python3 Tools/Music/build_bgm.py            # 全曲
    python3 Tools/Music/build_bgm.py title_ruri_theme ch1_shopping_street   # 指定した曲だけ
"""

import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tracks"))

from blue_song import build  # noqa: E402

TRACKS = [
    "title_ruri_theme",
    "ch1_shopping_street",
    "ch2_rain_alley",
    "ch3_night_school",
    "ch4_lighthouse_harbor",
    "ch5_dawn_hill",
    "shadow_chase",
    "shadow_words",
    "stinger_shadow_capture",
]


def main(names):
    for name in names or TRACKS:
        song = importlib.import_module(name).compose()
        info = build(song)
        layers = ", ".join(layer["name"] for layer in info["layers"])
        length = f"前奏 {info['introSeconds']:.1f}s + ループ {info['loopSeconds']:.1f}s" if info["loop"] else "ループなし"
        print(f"{song.name:26s} {length:28s} {info['loudnessLufs']:6.1f} LUFS  [{layers}]")


if __name__ == "__main__":
    main(sys.argv[1:])
