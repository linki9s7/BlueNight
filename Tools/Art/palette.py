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
