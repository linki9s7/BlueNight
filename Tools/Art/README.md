# Tools/Art

BlueNight のドット絵を Python（Pillow）で生成するスクリプト。

```
python3 Tools/Art/build.py        # 素材とプレビューを書き出す
python3 Tools/Art/pixel_check.py  # 点検（ダブり・バンディング・光の向き・パレット）→ report/
```

**ゲーム全体で必要なドット絵の一覧と進み具合は `art_plan.md`**。**描き方のルールは `STYLE.md`**（参考資料、マップごとのパレット、輪郭と clean_corners、ダブり・バンディング・
ピローシェーディング・浮いた AA・網点の使いすぎ・ミクセルを避ける）。

- `palette.py` … パレット（色のランプ）
- `ruri.py` … ルリのピクセルマップ（頭・胴・脚のパーツと、コマの組み合わせ）。左向きは `relight_mirror`（形だけ反転し、陰影は左上からの光のまま）
- `m1_assets.py` … M1 の素材（おばあさん・逃げた影・ランタン掛け・ランタン・壁など）
- `ch1_assets.py` … 第 1 章の建物（`Buildings/`）・小物・地面のタイル。建物は横に並べるとき輪郭を 1 ドット重ねる
- `npc.py` … ランプ屋の主人・のら猫・猫の影・ルリの影（ルリのコマから作る）
- `portrait.py` … 顔グラフィック 48×48（`Faces/`）。部品の図形を重ね、右下に影のかたまり
- `ui_title.py` … UI の部品（`UI/`、ウィンドウと名前札は 9 スライス・ふち 4 ドット）とタイトルの一枚絵・ロゴ・車の光（`Title/`）
- `build.py` … 全素材の書き出しとプレビュー作成。`save(..., clean=True)` で輪郭のダブりを取る
- `pixel_check.py` … 点検と `clean_corners`。結果は `report/pixel_report.md`（絵ごとの記録）と `report/clean_corners.json`
- 出力先：`Assets/005_Textures/`（Unity 取り込み用）、`Tools/Art/preview/`（拡大プレビュー）

Unity への取り込み設定（Point / 圧縮なし / PPU 16 / ピボット）は
`Assets/002_Scripts/Editor/BlueNightTextureImporter.cs` が自動で行う。
