"""開いている Unity エディタへ命令を送る（Assets/002_Scripts/Editor/BlueNightBridge.cs が受け取る）。

使い方（リポジトリのルートで）:
    python Tools/Bridge/unity_bridge.py refresh
    python Tools/Bridge/unity_bridge.py build gallery        # gallery / m1 / title
    python Tools/Bridge/unity_bridge.py play
    python Tools/Bridge/unity_bridge.py move 12 -3            # 再生中のルリを (12, -3) へ
    python Tools/Bridge/unity_bridge.py face left
    python Tools/Bridge/unity_bridge.py capture Logs/shots/a.png --scale 2
    python Tools/Bridge/unity_bridge.py logs

エディタが裏にあると、Unity は数秒に 1 回しか動かないことがある。待ち時間は --timeout（秒）で変えられる。
"""

import argparse
import json
import os
import sys
import time
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FOLDER = os.path.join(ROOT, "Temp", "BlueNightBridge")


def send(command, arg="", x=0.0, y=0.0, scale=2, timeout=60.0):
    os.makedirs(FOLDER, exist_ok=True)
    request_id = uuid.uuid4().hex
    response_path = os.path.join(FOLDER, "response.json")
    if os.path.exists(response_path):
        os.remove(response_path)
    tmp = os.path.join(FOLDER, "request.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"id": request_id, "command": command, "arg": arg, "x": x, "y": y, "scale": scale}, f)
    os.replace(tmp, os.path.join(FOLDER, "request.json"))
    deadline = time.time() + timeout
    while time.time() < deadline:
        if os.path.exists(response_path):
            try:
                with open(response_path, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                time.sleep(0.2)
                continue
            if data.get("id") == request_id:
                return data
        time.sleep(0.2)
    raise TimeoutError(f"Unity から {timeout:.0f} 秒返事がありません（エディタが開いているか、コンパイル中でないかを確認）")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command")
    p.add_argument("args", nargs="*")
    p.add_argument("--scale", type=int, default=2)
    p.add_argument("--timeout", type=float, default=60.0)
    a = p.parse_args()
    arg, x, y = "", 0.0, 0.0
    if a.command == "move":
        x, y = float(a.args[0]), float(a.args[1])
    elif a.args:
        arg = a.args[0]
    data = send(a.command, arg, x, y, a.scale, a.timeout)
    print(json.dumps(data, ensure_ascii=False, indent=1))
    sys.exit(0 if data.get("ok") else 1)


if __name__ == "__main__":
    main()
