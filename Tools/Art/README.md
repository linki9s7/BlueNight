# Tools/Art

BlueNight のドット絵を Python（Pillow）で生成するスクリプト。

```
python3 Tools/Art/build.py
```

- `palette.py` … パレット（色のランプ）
- `ruri.py` … ルリのピクセルマップ（頭・胴・脚のパーツと、コマの組み合わせ）
- `build.py` … 全素材の書き出しとプレビュー作成
- 出力先：`Assets/005_Textures/`（Unity 取り込み用）、`Tools/Art/preview/`（拡大プレビュー）

Unity への取り込み設定（Point / 圧縮なし / PPU 16 / ピボット）は
`Assets/002_Scripts/Editor/BlueNightTextureImporter.cs` が自動で行う。
