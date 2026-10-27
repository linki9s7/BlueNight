using System.Linq;
using BlueNight.Audio;
using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.Interaction;
using BlueNight.LightShadow;
using BlueNight.Logic;
using BlueNight.Player;
using BlueNight.Rendering;
using BlueNight.Shadows;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using UnityEngine.Tilemaps;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// M1 プロトタイプ：「光を置く → 影の逃げ道をふさぐ → 影を捕まえて言葉を聞く → 持ち主に返す」を通しで遊べるシーン。
    /// マップは BlueNight.Logic.M1Map（テストと同じ定義）から組み立てる。
    /// </summary>
    public static partial class BlueNightSetup
    {
        const string M1ScenePath = "Assets/001_Scenes/M1_Prototype.unity";
        const string SpriteUnlitMaterialPath = "Packages/com.unity.render-pipelines.universal/Runtime/Materials/Sprite-Unlit-Default.mat";
        const string DialogueFontPath = "Assets/008_Fonts/DotGothic16-Regular.ttf";

        const string FlagIntro = "m1_intro_done";
        const string FlagTalkedGrandma = "m1_talked_grandma";
        const string FlagCaptured = "m1_shadow_captured";
        const string FlagReturned = "m1_shadow_returned";

        [MenuItem("BlueNight/3. M1 プロトタイプシーンを作成", priority = 22)]
        public static void BuildM1Scene()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                return;

            EnsureFolder("Assets/001_Scenes");
            EnsureFolder(TileAssetFolder);
            EnsureFolder("Assets/009_Rendering");
            AssetDatabase.ImportAsset(TexturesRoot, ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceUpdate);

            var lit = AssetDatabase.LoadAssetAtPath<Material>(SpriteLitMaterialPath);
            var unlit = AssetDatabase.LoadAssetAtPath<Material>(SpriteUnlitMaterialPath);
            var map = M1Map.Create();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            Camera camera = CreateCamera();
            CreateMoonlight();
            CreateVolume();

            Tilemap overlay = CreateM1Tilemaps(map, lit, unlit);
            var world = new GameObject("Shadow World").AddComponent<ShadowWorld>();
            world.Configure(M1Map.Rows, overlay, LoadTile("overlay_dark"), LoadTile("overlay_cast_shadow"));

            var props = new GameObject("Props");
            var lamps = map.Find('L').ToList();
            for (int i = 0; i < lamps.Count; i++)
                CreateStreetLamp(props, lamps[i], lit, flicker: lamps[i].Y == map.Height - 2);
            foreach (var cell in map.Find('H').Concat(map.Find('h')))
                CreateLanternHook(props, cell, lit);
            foreach (var cell in map.Find('V'))
                CreateVendingMachine(props, cell, lit);

            Transform grandma = CreateGrandma(map.Find('G').Single(), lit);

            PlayerController player = CreateRuri(lit, CellFoot(map.Find('P').Single()), withLanternLight: false);
            CreateLanternAndInteractor(player, unlit);
            CreateNemu(lit, player);
            player.gameObject.AddComponent<PlayerAreaSounds>();
            var shadow = CreateGrandmaShadow(map.Find('S').Single(), player.transform, grandma, unlit);

            // 音：町の曲、夜の虫と遠くのハイウェイ。影に近づくと「影を追う」曲へ
            CreateAudio("ch1_shopping_street", Ambience("crickets", 0.55f), Ambience("highway", 0.35f));
            shadow.gameObject.AddComponent<ChaseMusic>().Configure(shadow, player.transform, "ch1_shopping_street");

            var dialogue = new GameObject("Dialogue").AddComponent<DialogueRunner>();
            dialogue.Configure(AssetDatabase.LoadAssetAtPath<Font>(DialogueFontPath));
            CreateIntro();

            var follow = camera.gameObject.AddComponent<BlueNight.Core.CameraFollow2D>();
            follow.Configure(player.transform, new Rect(0f, 0f, map.Width, map.Height));

            EditorSceneManager.SaveScene(scene, M1ScenePath);
            AddSceneToBuildSettings(M1ScenePath);
            Debug.Log($"[BlueNight] {M1ScenePath} を作成しました。再生して、おばあさんの影を捕まえてください。");
        }

        /// <summary>マスの足元（スプライトのピボットを置く位置）。</summary>
        static Vector3 CellFoot(Cell cell) => new Vector3(cell.X + 0.5f, cell.Y + 0.1f, 0f);

        // ------------------------------------------------------------------ 地面・壁・暗がり

        static Tilemap CreateM1Tilemaps(GridMap map, Material lit, Material unlit)
        {
            var grid = new GameObject("Grid").AddComponent<Grid>();

            Tilemap ground = CreateTilemap(grid, "Ground", -100, lit);
            Tilemap walls = CreateTilemap(grid, "Walls", -80, lit);
            Tilemap overlay = CreateTilemap(grid, "Darkness", -90, unlit);

            Tile road0 = LoadTile("road_0"), road1 = LoadTile("road_1");
            Tile side0 = LoadTile("sidewalk_0"), side1 = LoadTile("sidewalk_1");
            Tile wall = LoadTile("wall_top");
            wall.colliderType = Tile.ColliderType.Grid;
            EditorUtility.SetDirty(wall);

            var random = new System.Random(7);
            for (int y = 0; y < map.Height; y++)
            {
                for (int x = 0; x < map.Width; x++)
                {
                    var cell = new Cell(x, y);
                    char ch = map.At(cell);
                    var position = new Vector3Int(x, y, 0);
                    if (GridMap.IsWall(ch))
                        walls.SetTile(position, wall);
                    else if (GridMap.IsAlley(ch))
                        ground.SetTile(position, random.NextDouble() < 0.15 ? road1 : road0);
                    else
                        ground.SetTile(position, random.NextDouble() < 0.2 ? side1 : side0);
                }
            }

            // 壁の当たり判定（タイルをまとめて 1 つの形にする）
            var body = walls.gameObject.AddComponent<Rigidbody2D>();
            body.bodyType = RigidbodyType2D.Static;
            var tilemapCollider = walls.gameObject.AddComponent<TilemapCollider2D>();
            var composite = walls.gameObject.AddComponent<CompositeCollider2D>();
            composite.geometryType = CompositeCollider2D.GeometryType.Polygons;
            tilemapCollider.usedByComposite = true;

            return overlay;
        }

        static Tilemap CreateTilemap(Grid grid, string name, int sortingOrder, Material material)
        {
            var go = new GameObject(name);
            go.transform.SetParent(grid.transform, false);
            var tilemap = go.AddComponent<Tilemap>();
            var renderer = go.AddComponent<TilemapRenderer>();
            renderer.sortingOrder = sortingOrder;
            if (material != null)
                renderer.sharedMaterial = material;
            return tilemap;
        }

        // ------------------------------------------------------------------ 小物

        static void CreateStreetLamp(GameObject parent, Cell cell, Material material, bool flicker)
        {
            var lamp = CreateSpriteObject(parent, $"Street Lamp {cell}", "Props/lamp", CellFoot(cell), material);
            AddFootCollider(lamp, new Vector2(0.5f, 0.3f));
            var light = CreatePointLight(lamp, "Lamp Light", new Vector3(0f, 2.4f, 0f), Hex("#ffc98a"), 1.1f, M1Map.StreetLampRadius);
            lamp.AddComponent<GridLightSource>().Configure(M1Map.StreetLampRadius, light);
            AddMoths(lamp, new Vector3(0f, 2.3f, 0f));
            if (flicker)
            {
                // 古い街灯：光がゆらぎ、ガラスの絵も暗く／消えた色に変わる
                light.gameObject.AddComponent<LightFlicker2D>().ConfigureSprites(lamp.GetComponent<SpriteRenderer>(),
                    LoadSprite($"{TexturesRoot}/Props/lamp.png"), LoadSprite($"{TexturesRoot}/Props/lamp_dim.png"),
                    LoadSprite($"{TexturesRoot}/Props/lamp_off.png"));
            }
        }

        /// <summary>街灯に集まる小さな蛾の群れ。</summary>
        static void AddMoths(GameObject lamp, Vector3 localPosition)
        {
            var moths = new GameObject("Moths");
            moths.transform.SetParent(lamp.transform, false);
            moths.transform.localPosition = localPosition;
            var renderer = moths.AddComponent<SpriteRenderer>();
            renderer.sortingOrder = 15;
            moths.AddComponent<SimpleSpriteAnimator>().Configure(LoadFrames($"{TexturesRoot}/Effects/fx_moths_"), 8f);
        }

        static void CreateLanternHook(GameObject parent, Cell cell, Material material)
        {
            var hook = CreateSpriteObject(parent, $"Lantern Hook {cell}", "Props/hook", CellFoot(cell), material);
            hook.AddComponent<LanternHook>().SetPromptOffset(new Vector2(0f, 1.9f));
        }

        static void CreateVendingMachine(GameObject parent, Cell cell, Material material)
        {
            var vending = CreateSpriteObject(parent, "Vending Machine", "Props/vending", CellFoot(cell), material);
            AddFootCollider(vending, new Vector2(0.9f, 0.6f));
            vending.AddComponent<GridShadowCaster>().Configure(M1Map.VendingHeight, Vector2Int.one);
            CreatePointLight(vending, "Vending Light", new Vector3(0f, 0.8f, 0f), Hex("#cfe8ff"), 0.7f, 2f);
        }

        // ------------------------------------------------------------------ 登場人物

        static Transform CreateGrandma(Cell cell, Material material)
        {
            var root = new GameObject("Props (Characters)");
            var grandma = CreateSpriteObject(root, "Grandma", "Characters/Grandma/grandma_idle_0", CellFoot(cell), material);
            AddFootCollider(grandma, new Vector2(0.7f, 0.4f));
            grandma.AddComponent<SimpleSpriteAnimator>().Configure(LoadFrames($"{TexturesRoot}/Characters/Grandma/grandma_idle_"), 1.2f);

            // 影が戻ったら：足元に影が出て、居眠りをはじめる
            var footShadow = CreateSpriteObject(grandma, "Foot Shadow", "Effects/foot_shadow", grandma.transform.position, material);
            footShadow.GetComponent<SpriteRenderer>().sortingOrder = -40;
            footShadow.SetActive(false);
            grandma.AddComponent<FlagReaction>().Configure(FlagReturned, new[] { footShadow }, null,
                grandma.GetComponent<SimpleSpriteAnimator>(), LoadFrames($"{TexturesRoot}/Characters/Grandma/grandma_doze_"), 0.8f);

            var talk = grandma.AddComponent<TalkInteractable>();
            talk.SetPromptOffset(new Vector2(0f, 2.0f));
            talk.Configure(
                new ConditionalDialogue
                {
                    requiresFlag = FlagReturned,
                    lines = new[] { new DialogueLine("おばあさん", "……すう……すう……") },
                },
                new ConditionalDialogue
                {
                    requiresFlag = FlagCaptured,
                    setsFlag = FlagReturned,
                    lines = new[]
                    {
                        new DialogueLine("おばあさん", "まあ……それは、あたしの影かい。"),
                        new DialogueLine("ルリ", "この影が……『ありがとう』って。"),
                        new DialogueLine("ルリ", "だれかに、ずっと言えなかったみたいです。"),
                        new DialogueLine("おばあさん", "……そうかい。じいさんに、ちゃんと言えずじまいだったからねえ。"),
                        new DialogueLine("おばあさん", "ありがとう。……ありがとうね。なんだか、ひさしぶりに眠くなってきたよ。"),
                        new DialogueLine("ネム", "影が、帰っていく……。"),
                        new DialogueLine("", "M1 プロトタイプはここまでです。遊んでくれてありがとう！"),
                    },
                },
                new ConditionalDialogue
                {
                    setsFlag = FlagTalkedGrandma,
                    lines = new[]
                    {
                        new DialogueLine("おばあさん", "おや……こんな夜ふけに、どうしたんだい。"),
                        new DialogueLine("おばあさん", "あたしの影がね、いなくなってしまったんだよ。"),
                        new DialogueLine("おばあさん", "あの路地のほうへ、すうっと……。追いかける元気は、もう無くてねえ。"),
                        new DialogueLine("ルリ", "……さがしてきます。"),
                    },
                });
            return grandma.transform;
        }

        static void CreateLanternAndInteractor(PlayerController player, Material unlit)
        {
            var lanternGo = new GameObject("Lantern");
            lanternGo.transform.position = player.transform.position + new Vector3(0.42f, 0.35f, 0f);
            var sprite = lanternGo.AddComponent<SpriteRenderer>();
            sprite.sprite = LoadSprite($"{TexturesRoot}/Props/lantern.png");
            sprite.spriteSortPoint = SpriteSortPoint.Pivot;
            sprite.sortingOrder = 1;
            if (unlit != null)
                sprite.sharedMaterial = unlit; // ガラスの灯りは月明かりに左右されず明るく見せる

            var light = CreatePointLight(lanternGo, "Lantern Light", new Vector3(0f, 0.4f, 0f), Hex("#ffb866"), 1.15f, M1Map.LanternRadius);
            var gridLight = lanternGo.AddComponent<GridLightSource>();
            gridLight.Configure(M1Map.LanternRadius, light);

            var lantern = lanternGo.AddComponent<Lantern>();
            lantern.Configure(player, sprite, gridLight);

            var marker = new GameObject("Interact Prompt").AddComponent<SpriteRenderer>();
            marker.sprite = LoadSprite($"{TexturesRoot}/UI/prompt.png");
            marker.sortingOrder = 20;
            marker.enabled = false;
            if (unlit != null)
                marker.sharedMaterial = unlit;

            player.gameObject.AddComponent<PlayerInteractor>().Configure(lantern, marker);
        }

        static RunawayShadow CreateGrandmaShadow(Cell cell, Transform player, Transform owner, Material unlit)
        {
            var go = new GameObject("Runaway Shadow (Grandma)");
            go.transform.position = CellFoot(cell);
            var renderer = go.AddComponent<SpriteRenderer>();
            var frames = new[] { 0, 1, 2, 3 }.Select(i => LoadSprite($"{TexturesRoot}/Characters/Shadows/shadow_grandma_{i}.png")).ToArray();
            renderer.sprite = frames.FirstOrDefault();
            renderer.spriteSortPoint = SpriteSortPoint.Pivot;
            if (unlit != null)
                renderer.sharedMaterial = unlit; // 光に関係なく、真っ黒と水色のふちで見せる

            var shadow = go.AddComponent<RunawayShadow>();
            string s = $"{TexturesRoot}/Characters/Shadows/shadow_grandma_";
            shadow.ConfigureAnimations(LoadFrames(s + "move_down_"), LoadFrames(s + "move_up_"),
                LoadFrames(s + "move_left_"), LoadFrames(s + "move_right_"),
                LoadFrames(s + "surprised_"), LoadFrames(s + "caught_"),
                LoadFrames($"{TexturesRoot}/Effects/fx_capture_"), LoadFrames($"{TexturesRoot}/Effects/fx_return_"), unlit);
            shadow.Configure(player, owner, frames,
                new[]
                {
                    new DialogueLine("", "……ありがとう、って。", shadowVoice: true),
                    new DialogueLine("", "あの人に、ずっと言えなかった。", shadowVoice: true),
                    new DialogueLine("ネム", "つかまえた！ これ、あのおばあさんの影だよ。返しにいこう。"),
                },
                FlagCaptured, FlagReturned);
            return shadow;
        }

        static void CreateIntro()
        {
            var intro = new GameObject("Intro").AddComponent<AutoDialogue>();
            intro.Configure(FlagIntro,
                new DialogueLine("ネム", "ねえルリ、あの路地……なにか黒いものが動いてる。"),
                new DialogueLine("ネム", "逃げた影だ。きっと、だれかの影だよ。"),
                new DialogueLine("ネム", "影は光の中には入れないんだ。だから、ランタンを持って近づくと逃げちゃう。"),
                new DialogueLine("ネム", "路地の角にある『ランタン掛け』にランタンを掛ければ、そこはずっと明るいまま。逃げ道をふさげるよ。"),
                new DialogueLine("ネム", "逃げ道をふさいだら、暗いところで追いつめよう。"),
                new DialogueLine("", "移動：WASD／矢印キー　調べる：Space・E（Z）\nランタン：F（X）　小走り：Shift"));
        }
    }
}
