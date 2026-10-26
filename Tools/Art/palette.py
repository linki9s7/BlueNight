"""BlueNight のパレット定義（40 色前後）。

色は「ランプ（同系色の明暗の並び）」ごとにまとめる。
画面全体は青い月明かり（Global Light 2D）で照らされるので、素材そのものの色は少し明るめに置く。
"""

RAMPS = {
    # 夜空・遠景・影の基調色（暗 → 明）
    "night": ["#07070f", "#0b0f26", "#121a3a", "#1a2550", "#243266", "#2f4280", "#3d5599", "#5068b0"],
    # 石・アスファルト・コンクリート
    "stone": ["#1c1f33", "#272b45", "#343a59", "#454c6e", "#5a6285", "#757d9e", "#9aa1bd", "#c3c8dc"],
    # 街灯・窓明かり・ランタンの暖色
    "warm": ["#5c2e1f", "#8a4a24", "#c2702c", "#e89a3c", "#f5c46a", "#fde9a8", "#fffbe8"],
    # 月・逃げた影のふちの光
    "moon": ["#5fb3ff", "#9fd2ff", "#cfe8ff", "#f4f6ff"],
    # 肌
    "skin": ["#a8665a", "#d99a7c", "#f2c9a8"],
    # ルリの髪（紺がかった黒）
    "hair": ["#141430", "#232448", "#34366a", "#4d5291"],
    # ルリのマフラー
    "scarf": ["#1f4fa8", "#3b7bd9", "#78b4f0"],
    # ルリのコート（明るいグレー）
    "coat": ["#6a6c91", "#9497b8", "#c9cbe0"],
    # 植物
    "green": ["#1d3b3a", "#2c5650", "#3f7466"],
    # 差し色（自販機・看板）
    "red": ["#7a2340", "#b0384f", "#e05a6a"],
    # 革・木
    "brown": ["#3b2626", "#5a3a32", "#80544a"],
}


def hex_to_rgba(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def color(ramp, index):
    return hex_to_rgba(RAMPS[ramp][index])


def all_colors():
    return [hex_to_rgba(h) for ramp in RAMPS.values() for h in ramp]


def _pick(*names):
    """'night3' のような名前（系統＋明るさの番号）から色を集める。"""
    out = []
    for name in names:
        ramp = name.rstrip("0123456789")
        out.append(RAMPS[ramp][int(name[len(ramp):])])
    return out


# 輪郭線に使う色（点検で「線」として扱う）
OUTLINE_COLORS = _pick("hair0", "night0", "night1", "night2")

# マップ・用途ごとの専用パレット（この中の色だけで描く）
MAP_PALETTES = {
    # 夜の商店街（第 1 章・M1 の地面・建物・小物）：32 色
    "street_night": _pick("night0", "night1", "night2", "night3", "night4", "night5",
                          "stone1", "stone2", "stone3", "stone4", "stone5", "stone6", "stone7",
                          "warm1", "warm2", "warm3", "warm4", "warm5", "warm6", "moon0", "moon1", "moon2", "moon3",
                          "red0", "red1", "red2", "brown0", "brown1", "brown2", "green0", "green1", "green2"),
    # 登場人物（どのマップにも出るので共通）
    "characters": _pick("hair0", "hair1", "hair2", "hair3", "skin0", "skin1", "skin2",
                        "scarf0", "scarf1", "scarf2", "coat0", "coat1", "coat2",
                        "night0", "night1", "night2", "night3", "red0", "red1", "brown1", "brown2",
                        "stone2", "stone3", "stone4", "stone5", "stone7", "warm4", "warm5", "red2",
                        "warm3", "moon0", "moon1", "moon2", "moon3"),  # moon2：逃げた影の光る目、moon3：顔グラの目のつや
    # UI
    "ui": _pick("night1", "moon3"),
}
