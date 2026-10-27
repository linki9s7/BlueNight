#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docs/STORY.md の会話ウィンドウの文字数を数える。

台本の記法（STORY.md 0.2 節）:
  > 話者「本文」            … 会話ウィンドウ 1 つ。
  本文の中の ／             … ウィンドウ内の改行（＝ 2 行目）。
  >（……）                 … ト書き（画面に出ない。数えない）。

ルール（会話ウィンドウ 1 つにつき）:
  - 1 行の幅は 22 まで（全角を 1、半角 ASCII を 0.5 として数える）。
  - 1 ウィンドウは 2 行まで（／ で分けたとき、3 つ以上に割れていたら違反）。

実測（別セッションの確認）: 本文の幅は 436 ドット・16 ドットの字で 1 行最大 27 字。
顔グラフィックを左に置く分を見込んで、1 行 22 字・2 行までを目安にする。

使い方:
  python Tools/Story/count_lines.py [STORY.md のパス]
終了コード: 違反が無ければ 0、あれば 1。
"""

import sys
import os

MAX_WIDTH = 22.0          # 1 行の幅（全角 22 文字分）
MAX_LINES = 2             # 1 ウィンドウの行数
MAX_SPEAKER = 8           # 話者名の長さの上限（これを超える「 行は本文とみなさず飛ばす）


def char_width(ch):
    """全角は 1、半角 ASCII は 0.5。"""
    return 0.5 if ord(ch) < 0x80 else 1.0


def line_width(s):
    return sum(char_width(c) for c in s)


def iter_windows(path):
    """(行番号, 話者, 本文) を返す。"""
    with open(path, encoding="utf-8") as f:
        for no, raw in enumerate(f.readlines(), start=1):
            line = raw.rstrip("\n").rstrip("\r")
            stripped = line.lstrip()
            if not stripped.startswith(">"):
                continue
            body = stripped[1:].lstrip()        # 「>」と、そのあとの空白を外す
            if body.startswith("（") or body.startswith("("):
                continue                        # ト書き
            if "「" not in body:
                continue                        # セリフではない（ト書き・設計の文など）
            speaker, _, rest = body.partition("「")
            if len(speaker) > MAX_SPEAKER:
                continue                        # 本文中の「」を含む散文など
            # 最後の 」 までを本文とする（本文中の 『 』 はそのまま数える）
            if "」" not in rest:
                continue
            content = rest[: rest.rindex("」")]
            yield no, speaker.strip(), content


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "..", "docs", "STORY.md")
    path = os.path.normpath(path)

    total = 0
    problems = []
    for no, speaker, content in iter_windows(path):
        total += 1
        segments = content.split("／")
        if len(segments) > MAX_LINES:
            problems.append((no, speaker, content, "行数 %d（2 行まで）" % len(segments)))
        for seg in segments:
            w = line_width(seg)
            if w > MAX_WIDTH:
                problems.append((no, speaker, content,
                                 "幅 %g（22 まで）「%s」" % (w, seg)))

    print("STORY: %s" % path)
    print("会話ウィンドウ: %d 個を確認" % total)
    if not problems:
        print("OK: 22 文字・2 行を超えるウィンドウはありません。")
        return 0
    print("NG: %d 件の違反" % len(problems))
    for no, speaker, content, why in problems:
        print("  %d 行目  %s「%s」 … %s" % (no, speaker, content, why))
    return 1


if __name__ == "__main__":
    sys.exit(main())
