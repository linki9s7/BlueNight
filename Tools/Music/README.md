# Tools/Music

BlueNight の曲を、楽譜（MIDI）から作るスクリプト。

```
python3 Tools/Music/ruri_theme.py
```

- `designs/` … 曲の設計書（場面・感情・テンポ・モチーフ・和音進行）
- `blue_music.py` … 共通処理（演奏の揺らぎ・ルバート・ペダル → MIDI → 音源で WAV 化 → 残響・テープ感・ラウドネス調整）
- `ruri_theme.py` … ルリのテーマ（30 秒スケッチ）
- `out/` … MIDI と試聴用 MP3
- Unity 用の OGG は `Assets/006_Audio/BGM/` に書き出す

## 必要なもの（Ubuntu）

```
apt-get install fluidsynth ffmpeg musescore-general-soundfont
pip install pretty_midi pyloudnorm scipy numpy
```

## 音源

- MuseScore General SoundFont（MIT ライセンス、S. Christian Collins）。
  リリース時はクレジットとライセンス表記を入れる。
