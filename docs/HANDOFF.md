# 引き継ぎ書（クラウド → 自分の PC の Claude Code）

作成：2026-10-27。クラウドのセッションで作ったものは、すべてブランチ **`claude/admiring-thompson-yv4rbm`** に push 済み。
このファイルと `CLAUDE.md` を読めば、続きから作業できるようにしてある。

---

## 1. 最初に PC でやること

```bash
git clone <このリポジトリの URL> BlueNight
cd BlueNight
git checkout claude/admiring-thompson-yv4rbm
```

| 道具 | 用途 | 入れ方の例（Windows） |
| --- | --- | --- |
| Unity 2022.3.62f3 | ゲーム本体 | Unity Hub |
| Python 3.10 以上 ＋ Pillow・numpy | ドット絵・作曲の生成 | `pip install pillow numpy pyflakes` |
| FluidSynth | 作曲（MIDI → 音） | `winget install FluidSynth.FluidSynth` か公式のビルドを PATH に |
| ffmpeg | 音の書き出し（ogg） | `winget install Gyan.FFmpeg` |
| MuseScore General（.sf3） | 楽器の音（MIT） | MuseScore の配布ページから `MuseScore_General.sf3` を入手し、環境変数 `BLUENIGHT_SOUNDFONT` にその場所を設定 |
| .NET SDK 8 | Unity なしのコンパイル確認（任意） | `winget install Microsoft.DotNet.SDK.8` |

- ドット絵：`python Tools/Art/build.py` → `python Tools/Art/pixel_check.py`
- 曲：`python Tools/Music/build_bgm.py`、環境音 `ambience.py`、効果音 `sfx.py`、ループ確認 `check_loops.py`（`Tools/Music/README.md`）
- Unity：メニュー **BlueNight** の 1〜6（プロジェクト設定・M0・M1・第 1 章の素材を並べたシーン・音のデータ・タイトル画面）
- PC では Unity のバッチモードでコンパイルとテストを確かめられる（`CLAUDE.md`「確認方法」。Unity を閉じてから）

---

## 2. 新しいセッションに貼るプロンプト（そのままコピー）

```
BlueNight の開発をクラウドのセッションから引き継ぎます。
まず CLAUDE.md、docs/HANDOFF.md、docs/SPEC.md（とくに 11.1 の決定事項）、docs/M2_PLAN.md を読んでください。
物語は docs/STORY.md と docs/CHARACTERS.md、ドット絵のルールは Tools/Art/STYLE.md、曲のルールは Tools/Music/designs/bgm_plan.md です。
読み終えたら、いまの状況と次にやること（HANDOFF.md の 5 章）を、専門用語を避けて日本語で短くまとめてください。
そのあと、人物を描き直したので、Unity で「BlueNight > 4. 第 1 章の素材を並べたシーンを作成」と M1 プロトタイプを開いて、
見え方の確認方法を教えてください。確認が終わったら M2（第 1 章の本番版）のマップ作りに進みます。
```

---

## 3. ユーザーとの約束（必ず守る）

- **日本語で、専門用語を避けてわかりやすく**。結論から。仕上がりはプレビュー画像・試聴ファイルで見せる。
- **ドット絵と音楽は Claude が作る**（ユーザーの決定）。迷ったら案を 2〜4 つ出して選んでもらう。決まったら仕様書 11.1 に書く。
- 決定事項を変えるときは `docs/SPEC.md`（11.1 と変更履歴）も更新する。
- コミットはこまめに、ブランチ `claude/admiring-thompson-yv4rbm` へ。PR はユーザーが頼んだときだけ。
- 物語（STORY.md・CHARACTERS.md）は **ユーザーの感想待ち**。勝手に大きく変えない。セリフは CHARACTERS.md の話し方と STORY.md 18 節の約束を守る。
- **忘れてはいけない TODO**：虫の声は合成のまま。PC に移ったので、商用利用できる録音（Freesound の CC0、Sonniss GDC バンドルなど）に差し替える。
  素材を足したら `docs/CREDITS.md` と `Tools/Music/sources/README.md` に記録する。
- ユーザーが不採用にしたもの：Salamander Grand Piano（低音がリズムに合わせて「ドシン」と響くのが不快）、0 A.D. の素材、ネムに紫。
- **雨と波の環境音は確定**（変えない）。

---

## 4. いまの状況

| もの | 状態 |
| --- | --- |
| M0（2D 環境）・M1（光と影のプロトタイプ） | 完了。M1 はユーザーが遊んで「めっちゃ面白かった」 |
| 音 | BGM 8 曲＋スティンガー・環境音 4 種・効果音、Unity での再生（`Audio/`）まで完成 |
| ドット絵（第 1 章） | 商店街の建物・小物・タイル・ランプ屋の中・演出・UI・タイトル。**人物は v0.16 で描き直した**（下の 6 章） |
| M2 の土台 | エリアの移動・演出の台本・タイトル画面・オートセーブ・音量設定（コードはできている） |
| 物語 | `STORY.md` v1.0（全章の設計と第 1 章の台本）、`CHARACTERS.md`（全員のプロフィール）。ユーザーの感想待ち |
| 人物の描き直し（v0.16） | ルリ・ネム・ハル・青柳・ゴマ・影を新しい描き方で Assets に入れた。**Unity 上ではまだ見ていない** |

## 5. 次にやること（順番）

1. **Unity で新しい人物の見え方を確かめる**（メニュー 4 の素材シーン・M1）。明かり（Light 2D）の下での色、透けるネムの羽、左向きの絵。
   PC なので Unity のバッチモードでコンパイル・EditMode テストも通しておく。
2. **M2：第 1 章のマップ**（`docs/M2_PLAN.md` 3 章）。家の前〜バス停、商店街、ランプ屋の中、路地その 1・その 2。
   ASCII の定義が唯一の元（M1 と同じ）。追いつめの手ごたえは Logic のシミュレーションのテストで確かめる。
3. 会話（台本は STORY.md 7・8 節）→ 演出 → ことば帳・メニュー → タイトルの「はじめから」を第 1 章へ。
4. 虫の声を録音に差し替え（3 章の TODO）。
5. 通しで遊んでもらって調整。

---

## 6. ドット絵の記法（いちばん大事なところ）

詳しくは **`Tools/Art/STYLE.md`**（必ず守る）と `Tools/Art/art_plan.md`。要点：

- 絵はすべて Python で 1 ドットずつ作る。**記号の図（1 文字 = 1 ドット）** を書き、記号を色に置きかえる。
- 画面は 480×270。PPU 16、Point、圧縮なし、足元ピボット。**拡大・縮小しない（ミクセルを作らない）**。ポストエフェクトも 480×270 のまま。
- **光はどの向きの絵でも左上（月）から**。影は右下に「かたまり」で置く。左向きは専用の絵（Unity の flipX は使わない）。
- マップ・用途ごとのパレット（`palette.py` の `MAP_PALETTES`）以外の色は使わない。
- 避けること：ダブり（目安 10 以下）、バンディング、ピローシェーディング、浮いた AA、網点の使いすぎ、ミクセル、ノイズの点々。
- 新しい絵を足したら `pixel_check.py`。直さないと決めたものは理由を `REVIEWED` に書く。
- **建物・小物・タイル・UI**：1 ドットの紺の輪郭線＋`clean_corners`。平らな塗り＋小さな模様。
- **人物（v0.16〜）**：**輪郭線を引かない**。明暗の差と、**左上の縁に当たる月明かり**で形を見せる（`Tools/Art/chara.py`）。
  - 陰影は自動：素材ごとに「右下へ d ずらすと部品の外に出る所」を影の色に、「左か上が外の所」を縁の光にする。
  - 左向きは記号の図を反転してから陰影を付ける（光は左上のまま）。
  - 1 ドット幅の腕・脚は、光の側（画面左）を明るい肌に。clean_corners はかけない。
  - 新しい人物（第 2 章以降の海斗・早瀬先生・源三・航・ミオ・母）も同じ描き方。`townsfolk.py` を手本に。
- **ルリの決定デザイン**（`ruri.py`）：紺のぱっつんロング（前髪は眉の高さ・毛先のすき間）、**猫の耳のような寝ぐせ（チャームポイント、絶対に消さない）**、
  大きな青い目（瞳は上が濃く下が明るい、つやは左上）、眉、ほおの赤み、淡い青のルームワンピース（すそに白いレース）、素足に紺のサンダル、青いマフラー。
  「静かで大人っぽいのに、まだあどけなさが残る」。
- **ネム**（`nemu.py`）：オオミズアオ。ほのかに光る青緑の羽（少し透ける）、赤茶の帯、目玉模様、外へふくらむ尾。**口は描かない**（成虫には口がない＝物語の要）。
  ユーザーの好み：オオミズアオの美しさは羽の大きさと透明感、頭と体は小さく。尾がまっすぐ下だと脚に見える。
- リデザインの経緯と全部の案は `Tools/Art/concept_chars.py` と `Tools/Art/preview/concepts/`。

## 7. BGM・音で重視すること

詳しくは **`Tools/Music/designs/bgm_plan.md`**・`se_plan.md`・`Tools/Music/README.md`。要点：

- **聴き心地が最優先**：話し声の帯域（1 kHz 付近）を少し下げて一歩後ろへ。耳に刺さる高音とお腹に響く重低音を取る。ゆるいコンプ、全曲 −16 LUFS。
- 旋律は主張させない（和音の循環が主役）。サビで急に盛り上げない（A と B の差は楽器 1 つ）。BPM 60〜80（影を追う場面だけ 100）。
- 強いドラムを避ける（ブラシ・リム・シェイカー）。音色はアコースティック、こもったピアノ（5.5〜7 kHz のローパス）、ローファイなエレピ、薄いパッド。
- **ループは継ぎ目で途切れない**：2 回演奏して 2 回目を切り出し、終わり 50 ms をクロスフェード。`check_loops.py` で確認。
- モチーフ：**ルリのテーマ**（ソ・ド・レ・ミ。上がりきらずに止まる＝言いかけてやめる。最終章でだけ解決する）、**影のモチーフ**（半音で沈むため息）。
- 楽器は MuseScore General（MIT）。環境音は `Tools/Music/sources/` の録音から組み立てる（−26 LUFS）。クレジットは `docs/CREDITS.md`。
- Unity 側：`MusicDirector`（前奏→ループを PlayScheduled、等パワーのフェード、会話中 −4 dB）、`ChaseMusic`（距離で層を出し入れ）、
  `AmbiencePlayer`（屋内はこもる）、`SoundEffects`。AudioMixer は使わない。

## 8. 大事なファイルの地図

| ファイル | 中身 |
| --- | --- |
| `CLAUDE.md` | Claude 向けのメモ（構成・確認方法・状況） |
| `docs/SPEC.md` | 仕様書。11.1 が決定事項、冒頭が変更履歴（いま v0.16） |
| `docs/M2_PLAN.md` | 第 1 章の作り方（ユーザー確認済み） |
| `docs/STORY.md`・`docs/CHARACTERS.md` | 物語の設計図と台本、人物のプロフィール |
| `docs/CREDITS.md` | 素材のクレジット |
| `Tools/Art/STYLE.md`・`art_plan.md` | ドット絵のルールと、作ったもの・残りの一覧 |
| `Tools/Art/chara.py`・`ruri.py`・`nemu.py`・`townsfolk.py` | 人物の描き方としくみ |
| `Tools/Music/designs/bgm_plan.md`・`se_plan.md` | 曲・効果音の一覧とルール |
| `Tools/CodeCheck/` | Unity なしで C# のコンパイルを確かめる（`sh Tools/CodeCheck/check.sh`） |
