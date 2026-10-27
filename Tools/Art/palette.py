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
    # ネムの羽（オオミズアオの淡い青緑。月明かりのようにほの白い）：暗 → 明
    "moth": ["#24484c", "#3f7a78", "#78b3a8", "#b5e0d2", "#e1f3ea"],
    # 植物
    "green": ["#1d3b3a", "#2c5650", "#3f7466"],
    # 差し色（自販機・看板）
    "red": ["#7a2340", "#b0384f", "#e05a6a"],
    # 革・木
    "brown": ["#3b2626", "#5a3a32", "#80544a", "#a47366"],   # brown3：革・木の縁の月明かり（v0.16 の人物）
    # ---- 人物のリデザイン（v0.16、Tools/Art/ruri.py の説明）
    # 白（夜の青を含んだ白）：ワンピースのすそのレース
    "tee": ["#5b6384", "#8e97b8", "#d6dcec", "#f3f5fb"],
    # ルリのワンピース（淡い青のコットン）
    "pj": ["#5d6e92", "#8c9ec1", "#bccbe4", "#e3ebf7"],
    # ルリの瞳（上が濃く、下が明るい）
    "iris": ["#16306e", "#2d5bc0", "#6aa2ee"],
    # ほおの赤み
    "blush": ["#d98a86"],
    # ネムの羽（ほのかに光る青緑）・毛（白）
    "glow": ["#3f8f8a", "#7fd1c0", "#c8f5e6", "#f2fff9"],
    "fluff": ["#9aa6bf", "#d3dbe8", "#f4f6fb"],
    # おばあさん（ハル）のカーディガン（ばら色。夜の青で少しくすむ）
    "rose": ["#5a2c3e", "#86475a", "#b06c7b", "#d39aa3"],
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
OUTLINE_COLORS = _pick("hair0", "night0", "night1", "night2", "moth0")  # moth0：ネムの羽の輪郭（やわらかい暗い青緑）

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
                        "warm3", "warm6", "moon0", "moon1", "moon2", "moon3",
                        "moth0", "moth1", "moth2", "moth3", "moth4",  # moon2：逃げた影の光る目、moon3：顔グラの目のつや、moth：ネムの羽
                        # v0.16 のルリ：ワンピース・レース・瞳・ほお。ネム：光る羽・白い毛
                        "pj1", "pj2", "pj3", "tee2", "tee3", "iris0", "iris1", "iris2", "blush0",
                        "glow0", "glow1", "glow2", "glow3", "fluff0", "fluff1", "fluff2",
                        # v0.16 の町の人：ハルのカーディガン、革・木の縁、白いシャツ・髪の縁
                        "rose1", "rose2", "rose3", "brown0", "brown3", "stone1", "stone6", "night5"),
    # ランプ屋の中（第 1 章）：木・しっくい・消えたランプ・灯り
    "lamp_shop": _pick("night0", "night1", "night2", "night3", "night4", "night5", "stone3", "stone4", "stone5",
                       "stone6", "stone7", "brown0", "brown1", "brown2", "warm3", "warm4", "warm5", "warm6",
                       "red0", "red1", "red1", "green0", "green1", "moon2"),
    # 演出（光の輪・つぶ・波紋・小さな蛾・足元の影）
    "effects": _pick("night0", "night4", "night5", "moon0", "moon1", "moon2", "moon3", "stone7", "warm4", "warm5"),
    # UI（会話ウィンドウ・アイコン）：10 色
    "ui": _pick("night0", "night1", "night2", "moon1", "moon3", "scarf0", "scarf1", "stone7", "warm4", "warm5"),
    # タイトルの一枚絵（夜空・月・ハイウェイ・遠くの町＋小さなルリ）：32 色
    "title": _pick("night0", "night1", "night2", "night3", "night4", "night5", "moon1", "moon2", "moon3",
                   "stone1", "stone2", "stone3", "stone5", "stone7", "warm3", "warm4", "warm5", "warm6", "red0", "red2",
                   "hair0", "hair1", "hair2", "hair3", "skin1", "skin2", "scarf0", "scarf1", "coat1", "coat2",
                   "brown1", "brown2", "pj1", "pj2", "pj3", "tee2", "tee3"),  # pj・tee：街灯の下のルリ（v0.16 のワンピース）
}
