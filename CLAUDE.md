# BlueNight — Claude 向けメモ

ドット絵・見下ろし型のストーリーアドベンチャー。逃げ出した「影」をランタンの光で追いつめ、
影が抱えていた「言えなかった言葉」を持ち主に届ける。詳細は **`docs/SPEC.md`**（仕様書・決定事項・進捗）を必ず読むこと。

## ユーザーとのやり取り

- 日本語で、専門用語を避けてわかりやすく説明する。
- 決定事項は `docs/SPEC.md` の 11.1 にまとめてある。変更するときは仕様書も更新する。
- ドット絵と音楽は Claude が制作する（ユーザーの決定）。仕上がりはプレビュー画像・試聴ファイルで確認してもらう。

## 構成

| 場所 | 内容 |
| --- | --- |
| `Assets/002_Scripts/Logic/` | 光と影のグリッド・マップ定義。**Unity 非依存**（`BlueNight.Logic.asmdef`、noEngineReferences） |
| `Assets/002_Scripts/Tests/EditMode/` | Logic の NUnit テスト（追いかけっこのシミュレーションを含む） |
| `Assets/002_Scripts/{Core,Player,Interaction,LightShadow,RunawayShadow,Dialogue,Rendering,Audio,World,Story,Title}/` | ランタイム（Assembly-CSharp）。World＝エリアの移動、Story＝演出の台本、Title＝タイトル画面 |
| `Assets/002_Scripts/Editor/` | メニュー **BlueNight**（M0／M1 シーン・第 1 章の素材を並べたシーンの自動生成）、テクスチャ・フォントの取り込み規則 |
| `Tools/Art/` | ドット絵生成（Python / Pillow）。`python Tools/Art/build.py` → `Assets/005_Textures/` と `Tools/Art/preview/`。点検は `pixel_check.py`。**描き方のルールは `Tools/Art/STYLE.md`（必ず守る）** |
| `Tools/Music/` | 作曲（MIDI → FluidSynth → 仕上げ）。`python Tools/Music/build_bgm.py`、`ambience.py`、`check_loops.py`。全曲の一覧とルールは `Tools/Music/designs/bgm_plan.md` |

- 名前空間は `BlueNight.*`。クラス名と同じ名前空間は作らない（例：逃げた影は `BlueNight.Shadows.RunawayShadow`）。
- マップは `M1Map.Rows`（ASCII）が唯一の定義。シーン生成・テスト・プレビュー画像がすべてここを読む。
- シーンは手作業ではなくエディタスクリプトで生成する（再現できるように）。

## 確認方法（Unity 2022.3.62f3）

Unity エディタでプロジェクトを開いたままだとバッチモードは使えない（プロジェクトがロックされる）。
実行前にユーザーに Unity を閉じてもらうか、エディタ上での確認をお願いする。

```
# コンパイル確認＋EditMode テスト（Windows の例。パスは環境に合わせる）
"C:\Program Files\Unity\Hub\Editor\2022.3.62f3\Editor\Unity.exe" -batchmode -nographics -projectPath . ^
  -runTests -testPlatform EditMode -testResults Logs/test-results.xml -logFile Logs/unity.log

# M1 シーンの生成
"...\Unity.exe" -batchmode -nographics -projectPath . -executeMethod BlueNight.EditorTools.BlueNightSetup.BuildM1Scene -quit -logFile Logs/unity.log
```

コンパイルエラーは `Logs/unity.log` の `error CS` を探す。

Unity が無い環境（クラウドなど）では `sh Tools/CodeCheck/check.sh` で、Unity の参照 DLL（NuGet の Unity3D.SDK 2021.1）と
URP・Input System・UI の代用品（`Tools/CodeCheck/Stubs.cs`）を使って、型まで含めたコンパイルを確かめられる（Logic のテストは別に `dotnet test`）。

## 現在の状況と次の作業

- M0（2D 環境）：完了。M1（光と影のプロトタイプ）：**ユーザーが遊んで確認済み（「めっちゃ面白かった」）**。
- BGM 8 曲＋スティンガー＋環境音 4 種＋効果音（`Assets/006_Audio/SE/`、`se_manifest.json`、一覧は `Tools/Music/designs/se_plan.md`）は制作済み。
  Unity 側の再生も実装済み（`Assets/002_Scripts/Audio/`：`MusicDirector`・`ChaseMusic`・`AmbiencePlayer`・`SoundEffects`・`AreaZone`・`PlayerAreaSounds`、仕様書 8.8）。M1 と素材を並べたシーンに入っている。AudioMixer は使わない。
- ドット絵（第 1 章分）：商店街の建物・小物・タイル（`ch1_assets.py`）、人物と影（`npc.py`）、顔グラフィック 48×48（`portrait.py`）、UI・タイトル（`ui_title.py`）を制作済み。建物は横に並べるとき輪郭を 1 ドット重ねる。シーンへの配置（M2）はまだ。全体の一覧と残りは `Tools/Art/art_plan.md`。第 1 章の素材は Unity のメニュー「BlueNight > 4. 第 1 章の素材を並べたシーンを作成」（`BlueNightSetup.Gallery.cs` → `Assets/001_Scenes/Ch1_ArtGallery.unity`）で並べて確認できる。
- M2（第 1 章の本番版）進行中：計画 `docs/M2_PLAN.md`（ユーザー確認済み）、物語の設計図と台本 `docs/STORY.md`・人物のプロフィール `docs/CHARACTERS.md`（v1.0、ユーザーの感想待ち。セリフを書くときは CHARACTERS.md の話し方と STORY.md 18 節の約束を守る）。
  土台（エリアの移動・演出の台本・タイトル画面・オートセーブ・音量設定）はできた。次はマップ（ASCII）→ 会話 → ことば帳・メニュー。
- メニュー：1 プロジェクト設定、2 M0、3 M1、4 第 1 章の素材、5 音のデータ、6 タイトル画面。
- ポストエフェクトは 480×270 のまま処理する（ミクセルを作らないため。2 段カメラ構成は採らない、仕様書 7.6）。
- ドット絵：光はどの向きでも左上から。左向きは専用の絵（`ruri_*_left_*`）で、`flipX` は使わない。新しい絵を足したら `pixel_check.py` でダブり・バンディングを確認し、直さないものは理由を `REVIEWED` に書く。
- 音源：楽器は MuseScore General（MIT）。Salamander Grand Piano はユーザーの判断で不採用（低音がリズムに合わせて「ドシン」と響くのが不快）。クレジットは `docs/CREDITS.md`。
- 環境音は `Tools/Music/sources/` の録音を素材に組み立てる。**雨と波は確定（変えない）**。0 A.D. の素材は使わない（ユーザーの判断）。
- **TODO（ユーザーの依頼・忘れないこと）：虫の声は合成のまま。ローカル環境に切り替えたら、商用利用できる録音（Freesound CC0、Sonniss GDC バンドルなど）に差し替える。**ローカル環境では Sonniss GDC バンドルや Freesound（CC0）でさらに質を上げられる（仕様書 8.6）。素材を足したら `docs/CREDITS.md` と `sources/README.md` に記録する。
