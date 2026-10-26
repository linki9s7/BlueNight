# Tools/Music

BlueNight の曲を、楽譜（MIDI）から作るスクリプト。

```
python3 Tools/Music/build_bgm.py        # BGM 全曲（曲名を付けるとその曲だけ）
python3 Tools/Music/ambience.py         # 環境音
python3 Tools/Music/check_loops.py      # ループの継ぎ目の確認
python3 Tools/Music/ruri_theme.py       # 最初の 30 秒スケッチ（参考）
```

- `designs/bgm_plan.md` … **全曲の一覧と、聴き心地のルール**
- `designs/` … 曲の設計書（場面・感情・テンポ・モチーフ・和音進行）
- `blue_song.py` … BGM エンジン（複数パート・継ぎ目のないループ・レイヤー・マスター EQ／コンプレッサー）
- `tracks/` … 1 曲 1 ファイルの楽譜
- `ambience.py` … 環境音（雨・波・遠いハイウェイ・虫）の合成
- `blue_music.py` … 共通処理（演奏の揺らぎ・ルバート・ペダル → MIDI → 音源で WAV 化 → 残響・テープ感・ラウドネス調整）
- `ruri_theme.py` … ルリのテーマ（30 秒スケッチ）
- `out/` … MIDI、`out/preview/` に試聴用 MP3（前奏＋ループ 2 回）
- Unity 用の OGG は `Assets/006_Audio/BGM/`（前奏とループを別ファイル）と `Assets/006_Audio/Ambient/` に書き出す

## 必要なもの（Ubuntu）

```
apt-get install fluidsynth ffmpeg musescore-general-soundfont
pip install pretty_midi pyloudnorm scipy numpy
```

## 音源

- 楽器：MuseScore General SoundFont（MIT、S. Christian Collins）。
- 環境音の素材：`sources/` の録音（ライセンスは `sources/README.md`）。
- クレジット表記は `docs/CREDITS.md`。
