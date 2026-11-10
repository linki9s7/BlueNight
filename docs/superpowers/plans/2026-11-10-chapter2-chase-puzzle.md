# 第 2 章 追いかけっこの仕組み（計画 1）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 第 2 章の「作戦 → 実行 → やり直し」の追いかけっこを、仮の絵の試作シーン（`Ch2_Proto.unity`）で遊べるようにする。

**Architecture:** 判定はすべて Unity に頼らない `BlueNight.Logic`（`ShadowGrid`・`GridMap`）に足し、NUnit で確かめる。
ランタン、町の灯り、影の動き、やり直し、逃げられた演出、見渡す操作は、いまのランタイム（`Lantern`・`RunawayShadow`・`CameraFollow2D`・`ScreenFader`・`DialogueRunner`）に足す。
試作シーンは M1 と同じく、エディタスクリプトで ASCII マップから作る。

**Tech Stack:** Unity 2022.3.62f3（URP 2D・Input System）、C#（Logic は .NET 8 で `dotnet test`）、Python（仮の絵）。

**Spec:** `docs/superpowers/specs/2026-11-10-chapter2-design.md`

**この計画の範囲**：設計書は 4 つの独立した部分に分かれる。順番は次のとおり。
1. **追いかけっこの仕組み（この計画）**。遊びの手ざわりがここで決まるので、仮の絵で先に遊んでもらう。
2. 雨と傘（雨の重ね絵、ぬれた地面、水たまりの絵、傘を持つルリ、音）。
3. 新しい人物の絵（海斗・剛・12 歳のルリとミオ・海斗の影）。
4. 第 2 章のマップと演出。台本（傘の出どころ）がストーリー担当と決まってから。

計画 2〜4 は、この計画のあとで別に書く。

## Global Constraints

- Unity 2022.3.62f3。画面は 480×270 のまま（ズームアウトでミクセルを作らない、仕様書 7.6）。
- 判定は `Assets/002_Scripts/Logic/`（noEngineReferences）に置き、テストは `Assets/002_Scripts/Tests/EditMode/` に書く。`dotnet test Tools/LogicTests` で走る。
- **見た目の影と判定は必ず一致**させる（仕様書 9.3）。
- マップは ASCII が唯一の定義（`GridMap` の凡例に新しい記号を書く）。
- 前後の重なりは足元の Y で並べる。固定の正の sortingOrder を入れない。
- 反射神経・時間制限は入れない。ランタンは 1 つ。雨でランタンの火は消えない。
- セリフは 1 行全角 22 字・2 行まで（「／」で改行）。足したら `say` で会話ウィンドウに出し、`screen` で撮って確かめる。
- 新しい絵は `Tools/Art/STYLE.md` を守り、`pixel_check.py` で点検する。仮の絵でも、パレットの外の色は使わない。
- コミットは自分のファイルだけを `git add <パス>` で行う。push はしない。メッセージの最後に `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`。
- Unity を開いたままの確認は `python Tools/Bridge/unity_bridge.py`。`refresh` のあと、コンパイル（20〜30 秒）を待ってから `build`。
- オフラインの型チェックは `sh Tools/CodeCheck/check.sh`。既知のエラー（Volume.weight・ColorAdjustments.colorFilter・Volume.priority）は無視してよい。

## Review Focus

- **影が光の中で待っている**：作戦中に置いたランタンが、待っている影を照らした。期待：影はいちばん近い暗がりへ動き、そこで追いかけっこが始まる。光の中で固まらない。→ Task 9 Step 3 の確認（ランタンを待っている影の上に置く）。
- **やり直しのとき、ランタンが掛けてある・置いてある**：期待：ランタンはルリの手に戻り、町の灯りは最初の状態に、影は最初のマスに戻る。→ Task 9 Step 3 の確認（掛けたまま・置いたままで R）。
- **逃げられた演出の途中でやり直しボタン・見渡すボタン**：期待：無視される。二重のやり直しや、カメラの取り合いが起きない。→ Task 9 Step 3 の確認（演出中に R と C を押す）。
- **抜け道が 2 つとも同じ歩数**：期待：影の向かう先が毎回同じ（遊ぶたびに変わらない）。→ Task 1 のテスト `NearestExitTieIsDeterministic`。
- **ルリが抜け道の上に立っている**：期待：影はそこへ行けない（ルリのほうが先に着く）。抜け道をふさぐ方法の 1 つになる。→ Task 1 のテスト `ExitUnderRuriIsNotReachable`。

---

### Task 1: 抜け道と「開いた抜け道を目指す」逃げ方（Logic）

**Files:**
- Modify: `Assets/002_Scripts/Logic/ShadowGrid.cs`
- Modify: `Assets/002_Scripts/Logic/GridMap.cs`（凡例・`IsAlley`・`CreateGrid`）
- Test: `Assets/002_Scripts/Tests/EditMode/EscapeExitTests.cs`（新規）

**Interfaces:**
- Produces:
  - `ShadowGrid.SetExit(Cell c, bool value = true)`
  - `bool ShadowGrid.IsExit(Cell c)`
  - `IReadOnlyCollection<Cell> ShadowGrid.Exits`
  - `bool ShadowGrid.TryFindOpenExit(Cell shadow, int[] playerDistances, float speedRatio, out Cell exit)`
  - `Cell ShadowGrid.ChaseStep(Cell shadow, int[] playerDistances, float speedRatio = 1f)`
  - `bool ShadowGrid.HasEscaped(Cell shadow)`
  - `GridMap` の新しい記号 `E`＝抜け道。路地のマスで、ルリも影も通れる。`IsAlley('E') == true`。`CreateGrid` で `SetExit` する。

- [ ] **Step 1: 失敗するテストを書く**（`EscapeExitTests`、20×5 の開けたグリッドに壁で 1 本の通路を作る）
  - `ShadowHeadsForOpenExit`：通路 (1..18, 2)、抜け道 (18, 2)、影 (10, 2)、ルリ (2, 2)。`ChaseStep` は (11, 2)。
  - `ShadowPrefersExitOverFleeingFarther`：抜け道を (5, 2)、ルリを (1, 2)、影を (8, 2) にする。影はルリへ近づく向きでも、ルリより先に着けるので (7, 2) へ。
  - `LitExitIsClosed`：抜け道 (18, 2) に半径 1 の光。`TryFindOpenExit` は false。`ChaseStep` は `FleeStep` と同じ結果。
  - `ExitUnderRuriIsNotReachable`：ルリが抜け道 (18, 2) の上にいる。`TryFindOpenExit` は false。
  - `NearestExitTieIsDeterministic`：影 (10, 2) から同じ歩数の抜け道 (5, 2)・(15, 2)。ルリは届かない所。`ChaseStep` を 10 回呼んで、毎回同じマスを返す。
  - `HasEscapedOnlyOnDarkExit`：抜け道の上で暗ければ true。照らされていれば false。抜け道でないマスなら false。
  - `GridMapLegendE`：`new GridMap(new[]{"#####","#,E,#","#####"}).CreateGrid().IsExit(new Cell(2,1))` が true。`GridMap.IsAlley('E')` も true。

- [ ] **Step 2: 走らせて失敗を確かめる**
  Run: `dotnet test Tools/LogicTests --filter EscapeExitTests`
  Expected: コンパイルエラー（`SetExit` が無い）

- [ ] **Step 3: 実装する**
  - 抜け道は `HashSet<Cell>` で持つ。
  - `TryFindOpenExit` は `FleeStep` と同じ幅優先探索で探す。条件も同じで、暗いマスだけを通り、「ルリのほうが先に着くマス（`k >= player * speedRatio`）は通れない」。見つけた中で歩数がいちばん少ない抜け道を返す。同じ歩数なら、探索で先に見つかったもの（`Cell.Directions` の順）にする。影がもう抜け道の上にいれば、その抜け道を返す。
  - `ChaseStep` は、抜け道があればそこへの最初の 1 歩を返し、無ければ `FleeStep(shadow, playerDistances, speedRatio)` を返す。経路の復元は `FleeStep` と同じ parent 方式にする。
  - `HasEscaped` は `IsExit(shadow) && IsDark(shadow)`。

- [ ] **Step 4: 走らせて通ることを確かめる**
  Run: `dotnet test Tools/LogicTests`
  Expected: 全部 PASS（いまの 25 件も）

- [ ] **Step 5: コミット**
  `git add Assets/002_Scripts/Logic/ShadowGrid.cs Assets/002_Scripts/Logic/GridMap.cs Assets/002_Scripts/Tests/EditMode/EscapeExitTests.cs`（`.meta` は Unity が作ったら一緒に）
  `git commit -m "第 2 章：抜け道（E）と、開いた抜け道を目指す逃げ方"`

### Task 2: 水たまりの逆さの影（Logic）

**Files:**
- Modify: `Assets/002_Scripts/Logic/ShadowGrid.cs`
- Modify: `Assets/002_Scripts/Logic/GridMap.cs`
- Test: `Assets/002_Scripts/Tests/EditMode/PuddleReflectionTests.cs`（新規）

**Interfaces:**
- Produces:
  - `ShadowGrid.SetPuddle(Cell c, bool value = true)`
  - `bool ShadowGrid.IsPuddle(Cell c)`
  - `bool ShadowGrid.IsReflection(Cell c)`（最後の `Compute` で逆さの影になったマス。絵を置くのに使う）
  - `GridMap` の新しい記号 `o`＝水たまり。路地のマスで、ルリも影も通れる。`IsAlley('o') == true`。

**ルール（この計画で決める）**：水たまりには、モノの影が**光のほうへ**逆さに映る。
- 光とモノの組ごとに、ふつうの影（`AddCastShadow`）と同じ長さで、向きだけ逆（モノ → 光の向き）のマスを数える。
- そのうち水たまりのマスだけを「逆さの影」にする。
- 逆さの影は、光が当たっていても `CastShadow`（影が通れる）になる。光より強い。
- 消えている光は、逆さの影も作らない。

- [ ] **Step 1: 失敗するテストを書く**
  - 共通：20×5、モノ (10, 2)（高さ 1.5、solid）、光 (4, 2)（半径 12）。
  - `ReflectionPointsTowardLight`：水たまり (8, 2)・(9, 2)。両方 `CastShadow` で `IsReflection` が true。(11, 2) はふつうの影（`CastShadow`、`IsReflection` は false）。
  - `NoPuddleNoReflection`：水たまり無し。(9, 2) は `Lit`。
  - `PuddleAwayFromLightSideHasNoReflection`：水たまり (12, 2)（光と反対側）。ふつうの影なので `CastShadow` で、`IsReflection` は false。
  - `MovingLightChangesReflection`：光を (16, 2) に動かすと、水たまり (8, 2)・(9, 2) は `IsReflection` が false。
  - `SwitchedOffLightMakesNoReflection`：光の `On = false`。`IsReflection` はどこも false。
  - `ReflectionLengthMatchesCastShadowLength`：水たまりを (1..9, 2) に敷く。逆さの影のマスの数が、水たまり無しのときのふつうの影の長さと同じ。

- [ ] **Step 2: 走らせて失敗を確かめる**
  Run: `dotnet test Tools/LogicTests --filter PuddleReflectionTests`
  Expected: コンパイルエラー

- [ ] **Step 3: 実装する**
  - `AddCastShadow` に向きの引数（`+1`／`-1`）を足し、`-1` のときは水たまりのマスだけを結果に入れる。壁に当たったら止まるのは同じ。
  - `Compute` では、逆さの影を `reflected[]` に集める。状態を決める順番は「`Blocked` → `reflected` なら `CastShadow` → `Lit` → `CastShadow` → `Dark`」。

- [ ] **Step 4: 走らせて通ることを確かめる**
  Run: `dotnet test Tools/LogicTests`
  Expected: 全部 PASS

- [ ] **Step 5: コミット**
  `git commit -m "第 2 章：水たまりに映る逆さの影（灯りの位置で変わる）"`

### Task 3: 試作マップと、作戦が要ることのテスト（Logic）

**Files:**
- Create: `Assets/002_Scripts/Logic/Chapter2ProtoMap.cs`
- Modify: `Assets/002_Scripts/Logic/GridMap.cs`（記号 `l`）
- Modify: `Assets/002_Scripts/Tests/EditMode/ShadowGridTests.cs`（`Chase` を抜け道対応に）
- Test: `Assets/002_Scripts/Tests/EditMode/Chapter2ProtoMapTests.cs`（新規）

**Interfaces:**
- Consumes: Task 1・2 の API
- Produces:
  - `GridMap` の記号 `l`＝点け消しできる街灯（最初は消えている。柱は通れない＝`IsSolid`）。
  - `static class Chapter2ProtoMap`：
    - `string[] Rows`
    - `const float TownLampRadius = 4.5f`
    - `const float LanternRadius = 3f`
    - `GridMap Create()`
  - `enum ChaseResult { Caught, Escaped, Timeout }`（テストの中）
  - `ShadowGridTests.ChaseWithExits(ShadowGrid grid, Cell player, Cell shadow, int maxTurns) -> ChaseResult`：いまの `Chase` と同じ追い方。影の 1 歩は `ChaseStep` で、`HasEscaped` になったら `Escaped`。

- [ ] **Step 1: 失敗するテストを書く**（`Chapter2ProtoMapTests`）
  - `NoLightsShadowEscapes`：町の灯りは全部消え、ランタンはルリの手（光は追いかけっこの間ルリと動くが、テストでは光無しで近似する）。結果は `Escaped`。
  - `AllTownLampsOnStillFails`：`l` を全部点け、ランタンは無し。結果は `Caught` ではない。水たまりの逆さの影か、モノの影の道から逃げられる。**全部点ければ解ける、にならないこと**を確かめる。
  - `PlannedSolutionCatches`：設計した答え（点ける `l` の組とランタンを置くマス。マップのコメントに書く）で `Caught`。
  - `EverySolutionNeedsTheLantern`：`l` の点け方を全部（2^n 通り）試して、ランタン無しでは `Caught` にならない。置く練習の意味があることを確かめる。
  - `ShadowOnlyReachesAlleyCells`：影が行けるのは路地のマス（`IsAlley`）だけ。

- [ ] **Step 2: 走らせて失敗を確かめる**
  Run: `dotnet test Tools/LogicTests --filter Chapter2ProtoMapTests`
  Expected: コンパイルエラー（`Chapter2ProtoMap` が無い）

- [ ] **Step 3: マップを作る**
  - 大きさは 30×17 マス前後で、画面（30×16.9）より少し大きくする。見渡す操作が要るようにするため。
  - 入れるもの：抜け道 `E` 2〜3 か所、水たまり `o`、影を落とすモノ（`A`・`T`）、点け消しできる街灯 `l` 2〜3 本、ランタン掛け `H` 0〜1 個、`P`・`S`。
  - 答えは 1〜2 通りにする。上のテストが全部通るまで、マップを直す。
  - 答えはクラスのコメントに書く（例：「`l` の北を点け、ランタンを (x, y) に置く」）。

- [ ] **Step 4: 走らせて通ることを確かめる**
  Run: `dotnet test Tools/LogicTests`
  Expected: 全部 PASS

- [ ] **Step 5: コミット**
  `git commit -m "第 2 章：試作マップ（全部点けても解けない・ランタンが要る）"`

### Task 4: ランタンを置く・拾う

**Files:**
- Modify: `Assets/002_Scripts/Player/Lantern.cs`
- Create: `Assets/002_Scripts/Interaction/PlacedLantern.cs`
- Modify: `Assets/002_Scripts/Player/PlayerInteractor.cs`

**Interfaces:**
- Produces:
  - `enum LanternState { Carried, Hung, Placed }`、`Lantern.State`
  - `Lantern.IsCarried`（いまと同じ意味で残す。`AreaManager` がエリア移動で呼ぶ `TakeBack` は、置いてあるときもそのまま効くので、`AreaManager` は変えない）
  - `void Lantern.PlaceAt(Vector3 foot)`（足元の位置に置く。ルリの SortingGroup から外し、sortingOrder 0、光の `Anchor` は置いた所）
  - `Lantern.TakeBack()`（置いたときも掛けたときも、手に戻す）
  - `bool Lantern.CanPlace`：`GameFlags.Has("c1_got_lantern_stand")`、またはシーンで `allowPlacing` が true。
  - `PlacedLantern : Interactable`：置いたランタンの所で `CanInteract`。決定かランタンボタンで `TakeBack`。音は `lantern_take`。

- [ ] **Step 1: 実装する**
  - `PlayerInteractor.Update` で、`GameInput.LanternPressed` かつ `current` がランタン掛けでない、かつ `lantern.IsCarried && lantern.CanPlace` のとき、`PlayAction(Place)` してから `PlaceAt` する。
  - 置く所はルリの足元のマスの中心（`ShadowWorld.CellToWorld` に足元の補正を足す）。
  - 歩けないマス（`IsBlocked`）には置かない。
  - 音は `lantern_hang` を使う（置く音は計画 2 で作る）。

- [ ] **Step 2: 型チェック**
  Run: `sh Tools/CodeCheck/check.sh`
  Expected: 既知の 3 件のほかにエラー無し

- [ ] **Step 3: Unity で確かめる**（M1 シーンで `allowPlacing` を true にして試す）
  - `refresh` のあと `build m1`、`play`。
  - `move` で路地へ行き、F を押す（`invoke` か、実機ならユーザー）。
  - `state` で、ランタンの状態が Placed で、置いたマスが明るいことを見る。
  - `capture` で撮る。
  - もう一度 F で拾えて、光がルリについてくることを見る。

- [ ] **Step 4: コミット**
  `git commit -m "ランタンを地面に置く・拾う（ランタン立て）"`

### Task 5: 点け消しできる町の灯り

**Files:**
- Create: `Assets/002_Scripts/Interaction/LightSwitch.cs`

**Interfaces:**
- Produces:
  - `LightSwitch : Interactable`：`[SerializeField] GridLightSource target`。`Interact` で `target.On = !target.On`。音は `light_on`／`light_off`。
  - `bool LightSwitch.InitialOn`（やり直しで戻す値。`Awake` で覚える）
  - `void LightSwitch.ResetToInitial()`

- [ ] **Step 1: 実装する**
  調べるアイコンは今の 🔍 を使う。ルリの動きは `Inspect`。

- [ ] **Step 2: 型チェック**（Task 4 と同じ）

- [ ] **Step 3: コミット**
  `git commit -m "点け消しできる町の灯り（LightSwitch）"`

### Task 6: 海斗の影の動き（待つ・抜け道を目指す・角で止まる・抜け道から逃げる）

**Files:**
- Modify: `Assets/002_Scripts/RunawayShadow/RunawayShadow.cs`
- Create: `Assets/002_Scripts/Core/GamePause.cs`

**Interfaces:**
- Consumes: `ShadowGrid.ChaseStep`、`HasEscaped`
- Produces（`RunawayShadow`）：
  - `[SerializeField] bool useExits`（第 2 章の影は true。第 1 章はいまのまま `FleeStep`）
  - `[SerializeField] bool waitUntilNoticed`、`[SerializeField] float noticeDistance = 4f`
  - `[SerializeField] float cornerPause = 0.35f`（向きが変わるマスで、この秒数だけ止まる。0 で止まらない）
  - `event Action<Cell> ReachedExit`
  - `void EscapeThroughExit(Action finished)`：抜け道の外側（となりの壁か塀の向き）へ消える。いまの `UpdateEscaping` の動きを使う。会話もフラグも無い。消えたら `finished`。
  - `void ResetTo(Cell cell)`：見える状態・不透明・待つ状態にして、そのマスへ置き直す。
  - `bool IsWaiting`
  - `static class GamePause { public static bool IsPaused { get; set; } }`（`Core/GamePause.cs`。Task 7・8 も使う）

ランタイムの動きなので、Logic のテストは足さない（判定は Task 1 のテストで済んでいる）。確かめるのは Task 9 の遊びの確認。

- [ ] **Step 1: 実装する**
  - 待つ：`waitUntilNoticed` なら、ルリが `noticeDistance` 以内に来るか、影のマスが照らされるまで動かない。そのとき `Surprised` を 1 回出して、追いかけっこを始める。
  - 次のマスは `useExits ? grid.ChaseStep(...) : grid.FleeStep(...)`。
  - マスに着いたとき `grid.HasEscaped(current)` なら、`ReachedExit(current)` を出して止まる（自分では消えない。消えるのは `ChasePuzzle` が `EscapeThroughExit` を呼んだとき）。
  - 角で止まる：前の 1 歩と向きが違う 1 歩を始める前に `cornerPause` 秒待つ。
  - 角で止まる間・待つ間も、触れたら捕まる判定（`touchDistance`）は今のまま。
  - `GamePause.IsPaused` の間は、動かず、捕まる判定もしない。

- [ ] **Step 2: テストと型チェック**
  Run: `dotnet test Tools/LogicTests`、`sh Tools/CodeCheck/check.sh`
  Expected: PASS／既知の 3 件のみ

- [ ] **Step 3: コミット**
  `git commit -m "第 2 章の影：待つ・開いた抜け道を目指す・角で一度止まる"`

### Task 7: やり直しと「逃げられた」演出（ChasePuzzle）

**Files:**
- Create: `Assets/002_Scripts/Puzzle/ChasePuzzle.cs`
- Create: `Assets/002_Scripts/Puzzle/ExitMarker.cs`
- Modify: `Assets/002_Scripts/Core/GameInput.cs`（`ResetPressed`）

**Interfaces:**
- Consumes: Task 4〜6 の API。
  - `ScreenFader.Get().FadeOut(s)`／`FadeIn(s)`
  - `CameraFollow2D.Instance.LookAt(point, smooth)`／`LookBack(smooth)`
  - `DialogueRunner.Instance.Play(lines, done)`
  - `SoundEffects.Play("shadow_escape")`
- Produces:
  - `GameInput.ResetPressed`：R キー／ゲームパッドの select。
  - `ChasePuzzle : MonoBehaviour`（追いかけっこ 1 つに 1 個）：
    - `Configure(RunawayShadow shadow, PlayerController player, Lantern lantern, LightSwitch[] switches, ExitMarker[] exits, DialogueLine[] escapeLines, DialogueLine[] hintLines)`
    - `static bool IsBusy`（演出中。やり直し・見渡すを受けつけない）
    - `int EscapeCount`
    - `void ResetPuzzle(bool withEscapeScene)`
  - `ExitMarker : MonoBehaviour`（抜け道 1 つに 1 個）：
    - `Cell Cell`
    - `void ShowEscaped(float seconds)`（逃げた印をぼんやり光らせ、`seconds` かけて消す）
    - 開いている（暗い）ときと、ふさがっている（明るい）ときで見た目を変える（`ShadowWorld.Recomputed` で更新）。

**決まった流れ（設計書 3.1）**：逃げられたとき（`ReachedExit`）は次の順で見せる。
1. `ChasePuzzle.IsBusy = true`、ルリの `InputEnabled = false`。`Time.timeScale = 0.35` を、実時間 0.6 秒（2 回目からは 0.3 秒）。カメラは抜け道へ `LookAt(…, 0.35)`。
2. `timeScale = 1` に戻し、`shadow.EscapeThroughExit`。効果音 `shadow_escape`。
3. 消えたら `ExitMarker.ShowEscaped(6f)`。1・2 回目だけ、ネムの `escapeLines` を出す（`DialogueRunner`。決定で閉じる）。
4. `FadeOut(0.35)` → 最初の状態に戻す → `FadeIn(0.35)` → `LookBack(0.2)` → `IsBusy = false`。

1〜3 の間に決定ボタンを押したら、4 へ飛ぶ。

自分でやり直すとき（`ResetPressed`）は、4 だけ。`IsBusy`・会話中・`GamePause.IsPaused` の間は受けつけない。

**最初の状態**（シーンが始まって最初の `Update` で覚える）
- ルリの位置と向き（戻すときは `Rigidbody2D.position` も合わせる）
- ランタン（ルリの手に戻す。`TakeBack`）
- 各 `LightSwitch` を `ResetToInitial`
- 影を `ResetTo(最初のマス)`

**ネムのヒント**：やり直してから 60 秒、捕まえられずにいたら、`hintLines` を 1 回だけ出す（やり直すと数え直す）。

**セリフ**（`Ne(...)` で作る。顔は surprised／normal）
- `escapeLines`：`Ne("あっ……あそこから、逃げた", "surprised")`
- `hintLines`：`Ne("……一回、やり直す？")`、`Ne("R で、最初からに／もどせるよ")`

- [ ] **Step 1: 実装する**（`GameInput.ResetPressed`・`ExitMarker`・`ChasePuzzle`）
  - 演出のコルーチンは `WaitForSecondsRealtime` で待つ（`timeScale` を下げるため）。
  - `OnDisable` で必ず `timeScale = 1`・`IsBusy = false` に戻す。

- [ ] **Step 2: 型チェック**
  Run: `sh Tools/CodeCheck/check.sh`
  Expected: 既知の 3 件のみ

- [ ] **Step 3: コミット**
  `git commit -m "第 2 章：やり直しボタンと、逃げられたと分かる演出"`

### Task 8: 見渡す

**Files:**
- Modify: `Assets/002_Scripts/Core/CameraFollow2D.cs`
- Modify: `Assets/002_Scripts/Core/GameInput.cs`（`OverviewPressed`）
- Create: `Assets/002_Scripts/Puzzle/OverviewMode.cs`

**Interfaces:**
- Consumes: `GamePause.IsPaused`（Task 6）、`ChasePuzzle.IsBusy`（Task 7）
- Produces:
  - `GameInput.OverviewPressed`：C キー／ゲームパッドの north（Y）。
  - `CameraFollow2D.BeginFreeLook()`、`void PanFreeLook(Vector2 delta)`、`EndFreeLook(float smooth)`。範囲は今の `Clamp`、位置は今の `Snap`。
  - `OverviewMode : MonoBehaviour`：
    - `OverviewPressed` で入る：`GamePause.IsPaused = true`、ルリの `InputEnabled = false`、`BeginFreeLook`。
    - 入っている間は、移動キーで 14 マス/秒で動かす。
    - もう一度 `OverviewPressed`、または `CancelPressed` で出る：`EndFreeLook(0.25)`、元に戻す。
    - 会話中・`ChasePuzzle.IsBusy` の間は入れない。
    - 画面の右上に小さく「見渡す」と出す（`DialogueRunner` と同じフォントの UI テキスト。全角 4 字なので、ウィンドウの確認は不要）。

- [ ] **Step 1: 実装する**
  `PlayerController` は `InputEnabled` でもう止まる。`RunawayShadow` は Task 6 で `GamePause.IsPaused` を見ている。

- [ ] **Step 2: 型チェック**（Task 7 と同じ）

- [ ] **Step 3: コミット**
  `git commit -m "第 2 章：路地全体を見渡す（そのあいだ影は止まる）"`

### Task 9: 試作シーン（仮の絵）

**Files:**
- Create: `Assets/002_Scripts/Editor/BlueNightSetup.Chapter2Proto.cs`
- Modify: `Assets/002_Scripts/Editor/BlueNightBridge.cs`（`build ch2proto`）
- Create: `Tools/Art/ch2_proto.py`（水たまりのタイル `puddle_0`、抜け道の印 `exit_open`／`exit_closed`／`exit_escaped`、消えた街灯）
- Modify: `Tools/Art/build.py`（`ch2_proto` を呼ぶ）

**Interfaces:**
- Consumes: Task 3〜8 のすべて。
  - M1 の作り方（`CreateCamera`・`CreateMoonlight`・`CreateVolume`・`CreateRuri`・`CreateLanternAndInteractor`・`CreateNemu`・`CreateStreetLamp`・`CreateLanternHook`・`CreateAudio`）
  - `Chapter1Story` の `Ne(...)`
  - 顔の設定 `ConfigureFaces`
- Produces:
  - メニュー「BlueNight/8. 第 2 章 追いかけっこの試作シーンを作成」→ `Assets/001_Scenes/Ch2_Proto.unity`
  - `python Tools/Bridge/unity_bridge.py build ch2proto`

- [ ] **Step 1: 仮の絵を作る**
  - 雨の路地のパレットの中で描く。水たまりは路地の色を少し明るく、ふちに 1 ドットの光。
  - 抜け道の印は 3 種類：開いている（暗い所でうっすら見える矢印）、ふさがっている（薄い）、逃げた（ぼんやり光る）。
  - Run: `python Tools/Art/build.py` → `python Tools/Art/pixel_check.py`
  - Expected: 新しい絵に指摘無し（あれば直すか、`REVIEWED` に理由を書く）
  - 画素の変わらない PNG は元に戻してからコミットする。

- [ ] **Step 2: シーンを作るスクリプトを書く**
  - `Chapter2ProtoMap` から作る。対応は次のとおり。
    - `l`：消えた街灯＋`LightSwitch`
    - `E`：`ExitMarker`
    - `o`：水たまりのタイル
    - `H`：ランタン掛け
  - 影は今の第 1 章の影の絵を使う（海斗の影の絵は計画 3）。`useExits = true`、`waitUntilNoticed = true`、`cornerPause = 0.35`、`speed = 6.5`。
  - ランタンは `allowPlacing = true`。
  - 曲は `ch2_rain_alley`、環境音は `ambient_rain`。
  - 捕まえたら、ネム「……つかまえた」の 1 行で終わり（試作なので）。

- [ ] **Step 3: 作って遊ぶ（自分で）**
  - `refresh` → 待つ → `build ch2proto` → `play`。
  - 何もせず影に近づき、逃げられた演出が 1〜4 の順で出て、最初の状態に戻ることを確かめる。`screen` で 3 枚撮る（止まった所・印とネムのセリフ・戻った所）。
  - R でやり直せること、C で見渡せて、その間は影が止まることを確かめる。
  - ランタンを掛けたまま・置いたままで R を押す。ランタンがルリの手に戻り、街灯も最初の状態に戻ること。
  - 逃げられた演出の途中で R と C を押す。どちらも無視されること。
  - 待っている影の上にランタンを置く。影が近くの暗がりへ動いて、追いかけっこが始まること。
  - 答え（Task 3 のコメント）どおりに置いて、捕まえられることを確かめる。
  - 60 秒待って、ネムのヒントが出ることを確かめる。

- [ ] **Step 4: セリフをウィンドウで確かめる**
  `say` でネムの 3 行（`escapeLines`・`hintLines`）をそれぞれ出し、`screen` で撮る。はみ出しが無いこと。

- [ ] **Step 5: コミット**
  `git commit -m "第 2 章 追いかけっこの試作シーン（仮の絵）"`

### Task 10: ユーザーに遊んでもらう

- [ ] **Step 1**：撮った画面と遊び方（F で置く・拾う、調べて街灯を点ける、C で見渡す、R でやり直す）を日本語でまとめて、ユーザーに試してもらう。
- [ ] **Step 2**：感想（難しさ・逃げられた演出の長さ・見渡しやすさ）を受けて直す。決まったことは `docs/SPEC.md` 11.1 に書く。
