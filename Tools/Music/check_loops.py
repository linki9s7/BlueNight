"""書き出したループ曲の継ぎ目を確認する（長さが正確か、ループ点で音が途切れたり跳ねたりしないか）。

使い方: python3 Tools/Music/check_loops.py
"""

import json
import os
import subprocess

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BGM = os.path.join(ROOT, "Assets", "006_Audio", "BGM")


def decode(path, rate):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(rate), "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def main():
    manifest = json.load(open(os.path.join(BGM, "music_manifest.json"), encoding="utf-8"))
    for track in manifest["tracks"]:
        if not track["loop"]:
            continue
        rate = track["sampleRate"]
        expected = round(track["loopSeconds"] * rate)
        for layer in track["layers"]:
            x = decode(os.path.join(BGM, layer["loop"]), rate)
            step = np.abs(np.diff(x, axis=0)).max(axis=1)
            seam = np.abs(x[0] - x[-1]).max()
            # 継ぎ目の段差が、曲の中の普通のサンプル間の変化（上位 1%）に収まっているか
            typical = np.percentile(step, 99)
            win = int(0.05 * rate)
            rms_end = np.sqrt(np.mean(x[-win:] ** 2))
            rms_start = np.sqrt(np.mean(x[:win] ** 2))
            ok = len(x) == expected and seam <= typical * 1.5
            print(f"{'OK ' if ok else 'NG '} {layer['loop']:40s} samples {len(x)}/{expected}  "
                  f"seam {seam:.4f} (typical {typical:.4f})  rms end/start {rms_end:.3f}/{rms_start:.3f}")


if __name__ == "__main__":
    main()
