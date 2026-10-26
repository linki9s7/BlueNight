"""ドット絵の点検と、輪郭の段差のダブりを取る clean_corners。

使い方（リポジトリのルートで）:
    python3 Tools/Art/pixel_check.py        # Assets/005_Textures の全 PNG を点検し、Tools/Art/report/ に記録する

点検すること（Tools/Art/STYLE.md のルール）
- ダブり（重複ドット）：輪郭線の段差で 2 ドットが重なる所（L 字の角）。clean_corners で取れる数を数える。目安 10 以下。
- バンディング：幅 1 ドットの色の帯が、両側の別の色に挟まれて平行に続く所（輪郭の内側 1 列の影もこれ）。3 ドット以上続くものを数える。
- 浮いたアンチエイリアス：同じ色の仲間が周りに無い、ぽつんとした中間色のドット。
- ディザリング：市松模様のドットの割合。ノイズ：周りに同じ色が無い孤立したドットの割合（面がザラつく原因）。
- 光の向き：同じ系統の色の「暗い色」が「明るい色」より右下にあるか（光はどの向きの絵でも画面の左上から）。
- パレット：マップ・用途ごとの専用パレットだけを使っているか。
"""

import json
import os
import sys
from collections import Counter

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import MAP_PALETTES, OUTLINE_COLORS, RAMPS, hex_to_rgba  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEX = os.path.join(ROOT, "Assets", "005_Textures")
REPORT = os.path.join(ROOT, "Tools", "Art", "report")
DOUBLES_LIMIT = 10

# 目で確かめて「直さなくてよい」と決めたもの（ファイル名の頭 → 理由）。点検の数字は残し、レポートに理由を並べて書く。
REVIEWED = {
    "Characters/Ruri/": "顔の肌の帯（目と髪のあいだ・あご）、口・マフラーのつや・靴のつやの点は形の細部で、陰影の帯や AA ではない",
    "Characters/Ruri/ruri_walk_left_0": "靴下の光の向き：奥の脚を暗くしているのは奥行きの表現",
    "Characters/Ruri/ruri_walk_right_0": "靴下の光の向き：奥の脚を暗くしているのは奥行きの表現",
    "Characters/Grandma/": "あごの肌の帯は口まわりの形。2 コマ目の右肩の影は手との境目",
    "Characters/Keeper/": "顔の帯（めがね・口ひげ・鼻のまわり）は形の細部で、陰影の帯ではない",
    "Characters/Nemu/": "羽の目玉模様（1 ドット）とそのまわりは模様で、陰影の帯ではない",
    "Props/puddle_moon": "光の向き：水面の揺らぎ（明るい線）は映り込みで、陰影ではない",
    "Buildings/": "光の向き：建物は屋根・壁・窓・基礎で素材が違い、系統全体の重心では判断できない（部品ごとに左上の光を確認済み）。"
                  "窓の明かりは光源なので陰影の向きとは関係ない",
    "Props/power_pole": "光の向き：足元の黄色と黒の巻き標識はしま模様で、陰影ではない",
}


def reviewed_note(rel):
    return " ／ ".join(note for prefix, note in REVIEWED.items() if rel.startswith(prefix))


RAMP_OF = {}
for _ramp, _colors in RAMPS.items():
    for _i, _h in enumerate(_colors):
        RAMP_OF[hex_to_rgba(_h)[:3]] = (_ramp, _i)


def luminance(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


class Grid:
    def __init__(self, img, outline=None):
        self.img = img.convert("RGBA")
        self.w, self.h = self.img.size
        self.px = self.img.load()
        outline = OUTLINE_COLORS if outline is None else outline
        self.outline = {hex_to_rgba(c)[:3] for c in outline}

    def color(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            r, g, b, a = self.px[x, y]
            return None if a == 0 else (r, g, b)
        return None

    def is_outline(self, x, y):
        c = self.color(x, y)
        return c is not None and c in self.outline


# ---------------------------------------------------------------- ダブりと clean_corners

def _arm(g, x, y, dx, dy):
    n = 0
    while g.is_outline(x + dx * (n + 1), y + dy * (n + 1)):
        n += 1
    return n


def find_double(g, x, y):
    """(x, y) が輪郭の L 字の角（段差のダブり）なら True。長い辺どうしの直角の角（箱の角）は意図した角として残す。"""
    if not g.is_outline(x, y):
        return False
    hs = [d for d in (-1, 1) if g.is_outline(x + d, y)]
    vs = [d for d in (-1, 1) if g.is_outline(x, y + d)]
    if len(hs) != 1 or len(vs) != 1:
        return False
    dx, dy = hs[0], vs[0]
    if g.is_outline(x + dx, y + dy):
        return False  # 2x2 のかたまりは別扱い
    if _arm(g, x, y, dx, 0) >= 3 and _arm(g, x, y, 0, dy) >= 3:
        return False
    return True


def clean_corners(img, outline=None):
    """輪郭の段差のダブりを取る。取った点は、周りで多い色（外側なら透明、内側なら塗りの色）で埋める。(新しい画像, 取った数) を返す。"""
    g = Grid(img.convert("RGBA").copy(), outline)
    removed = 0
    changed = True
    while changed:
        changed = False
        for y in range(g.h):
            for x in range(g.w):
                if not find_double(g, x, y):
                    continue
                around = []
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < g.w and 0 <= ny < g.h and not g.is_outline(nx, ny):
                        around.append(g.px[nx, ny] if g.px[nx, ny][3] else (0, 0, 0, 0))
                    elif not (0 <= nx < g.w and 0 <= ny < g.h):
                        around.append((0, 0, 0, 0))
                g.px[x, y] = Counter(around).most_common(1)[0][0] if around else (0, 0, 0, 0)
                removed += 1
                changed = True
    return g.img, removed


def count_doubles(img, outline=None):
    return clean_corners(img, outline)[1]


# ---------------------------------------------------------------- そのほかの点検

def banding(g):
    """
    バンディング：幅 1 ドットの帯が別の 2 色に挟まれて 3 ドット以上続き、
    (a) 輪郭線に沿っている（輪郭の内側 1 列の影など）か、(b) 段差になって斜めに続いている所。
    箱の棚板のような、輪郭に接しないまっすぐな線は「線」として数えない。(帯の数, ドット数, 帯の色の例)
    """
    marked, touches_outline = set(), set()
    for y in range(g.h):
        for x in range(g.w):
            b = g.color(x, y)
            if b is None or b in g.outline:
                continue
            for dx, dy in ((1, 0), (0, 1)):
                a, c = g.color(x + dx, y + dy), g.color(x - dx, y - dy)
                if a is None or c is None:
                    continue
                if a != b and c != b and a != c:
                    marked.add((x, y))
                    if a in g.outline or c in g.outline:
                        touches_outline.add((x, y))
    seen, segments, pixels, colors = set(), 0, 0, Counter()
    for p in marked:
        if p in seen:
            continue
        stack, comp = [p], []
        seen.add(p)
        while stack:
            q = stack.pop()
            comp.append(q)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    r = (q[0] + dx, q[1] + dy)
                    if r in marked and r not in seen and g.color(*r) == g.color(*p):
                        seen.add(r)
                        stack.append(r)
        xs, ys = {q[0] for q in comp}, {q[1] for q in comp}
        stepped = len(xs) > 1 and len(ys) > 1
        along_outline = sum(1 for q in comp if q in touches_outline) >= 3
        if len(comp) >= 3 and (stepped or along_outline):
            segments += 1
            pixels += len(comp)
            colors["#%02x%02x%02x" % g.color(*p)] += len(comp)
    return segments, pixels, [c for c, _ in colors.most_common(3)]


def isolated(g):
    """(浮いたアンチエイリアスの候補, ノイズの点) の数。"""
    floating = noise = 0
    for y in range(g.h):
        for x in range(g.w):
            c = g.color(x, y)
            if c is None or c in g.outline:
                continue
            n8 = [g.color(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
            if c in n8:
                continue
            noise += 1
            n4 = [k for k in (g.color(x - 1, y), g.color(x + 1, y), g.color(x, y - 1), g.color(x, y + 1)) if k is not None]
            if len(set(n4)) >= 2:
                lums = [luminance(k) for k in n4]
                if min(lums) < luminance(c) < max(lums):
                    floating += 1
    return floating, noise


def dithering(g):
    count = opaque = 0
    for y in range(g.h):
        for x in range(g.w):
            c = g.color(x, y)
            if c is None:
                continue
            opaque += 1
            n4 = {g.color(x - 1, y), g.color(x + 1, y), g.color(x, y - 1), g.color(x, y + 1)}
            d4 = {g.color(x - 1, y - 1), g.color(x + 1, y - 1), g.color(x - 1, y + 1), g.color(x + 1, y + 1)}
            if len(n4) == 1 and None not in n4 and c not in n4 and d4 == {c}:
                count += 1
    return count, opaque


def light_direction(g):
    """系統ごとに「いちばん暗い色の重心 − いちばん明るい色の重心」。右下（+x, +y）を向いていれば左上からの光と合う。"""
    by_ramp = {}
    for y in range(g.h):
        for x in range(g.w):
            c = g.color(x, y)
            if c is None or c in g.outline or c not in RAMP_OF:
                continue
            ramp, i = RAMP_OF[c]
            by_ramp.setdefault(ramp, {}).setdefault(i, []).append((x, y))
    result = {}
    for ramp, levels in by_ramp.items():
        if len(levels) < 2:
            continue
        dark, light = levels[min(levels)], levels[max(levels)]
        if len(dark) < 3 or len(light) < 3:
            continue
        dx = sum(p[0] for p in dark) / len(dark) - sum(p[0] for p in light) / len(light)
        dy = sum(p[1] for p in dark) / len(dark) - sum(p[1] for p in light) / len(light)
        result[ramp] = (round(dx, 1), round(dy, 1))
    return result


def palette_violations(g, allowed):
    allowed = {hex_to_rgba(h)[:3] for h in allowed}
    used = {g.color(x, y) for y in range(g.h) for x in range(g.w)} - {None}
    return sorted("#%02x%02x%02x" % c for c in used - allowed), len(used)


def group_of(rel):
    if rel.startswith("Characters"):
        return "characters"
    if rel.startswith("UI"):
        return "ui"
    if rel.startswith(("Tiles", "Props", "Buildings")):
        return "street_night"
    return None


def check_image(path):
    rel = os.path.relpath(path, TEX).replace(os.sep, "/")
    # 逃げた影は、水色のふちが輪郭線
    outline = [RAMPS["moon"][0], RAMPS["moon"][1]] if "/Shadows/" in f"/{rel}" else None
    g = Grid(Image.open(path), outline)
    group = group_of(rel)
    bad, ncolors = palette_violations(g, MAP_PALETTES[group]) if group else ([], 0)
    bands, band_px, band_colors = banding(g)
    floating, noise = isolated(g)
    dither, opaque = dithering(g)
    light = light_direction(g)
    wrong_light = {r: v for r, v in light.items() if v[0] < -0.5 or v[1] < -0.5}
    return {
        "file": rel, "group": group, "colors": ncolors, "offPalette": bad,
        "doubles": count_doubles(g.img, outline), "banding": bands, "bandingPixels": band_px, "bandingColors": band_colors,
        "floatingAA": floating, "noisePercent": round(100 * noise / max(1, opaque), 1),
        "ditherPercent": round(100 * dither / max(1, opaque), 1), "lightWrong": wrong_light,
        "reviewed": reviewed_note(rel),
    }


def main():
    rows = []
    for base, _, files in os.walk(TEX):
        for name in sorted(files):
            if name.endswith(".png") and name != "Palette.png":
                rows.append(check_image(os.path.join(base, name)))
    rows.sort(key=lambda r: r["file"])
    os.makedirs(REPORT, exist_ok=True)
    with open(os.path.join(REPORT, "pixel_report.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    lines = ["# ドット絵の点検結果", "", "`python3 Tools/Art/pixel_check.py` で更新する。ダブりの目安は 10 以下。", "",
             "数字は機械的な候補。目で確かめて直さないと決めたものは「確認済み」に理由を書く（`REVIEWED`）。", "",
             "| 絵 | 色数 | パレット外 | ダブり | バンディング（帯/ドット） | 浮いた AA 候補 | ノイズ % | 網点 % | 光の向きが逆の系統 | 確認済み |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['file']} | {r['colors']} | {len(r['offPalette']) or ''} | {r['doubles']}"
                     f"{' ⚠' if r['doubles'] > DOUBLES_LIMIT else ''} | {r['banding']}/{r['bandingPixels']} | {r['floatingAA']} | "
                     f"{r['noisePercent']} | {r['ditherPercent']} | {', '.join(r['lightWrong']) or ''} | {r['reviewed']} |")
    with open(os.path.join(REPORT, "pixel_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    keys = ["doubles", "banding", "floatingAA"]
    total = {k: sum(r[k] for r in rows) for k in keys}
    over = [r["file"] for r in rows if r["doubles"] > DOUBLES_LIMIT]
    print(f"{len(rows)} 枚：ダブり合計 {total['doubles']}（目安超え {len(over)} 枚）、バンディング {total['banding']} 帯、"
          f"浮いた AA 候補 {total['floatingAA']}、パレット外 {sum(1 for r in rows if r['offPalette'])} 枚、"
          f"光の向きが逆 {sum(1 for r in rows if r['lightWrong'])} 枚"
          f"（うち確認済みの絵 {sum(1 for r in rows if r['reviewed'] and (r['banding'] or r['floatingAA'] or r['lightWrong']))} 枚）")
    return rows


if __name__ == "__main__":
    main()
