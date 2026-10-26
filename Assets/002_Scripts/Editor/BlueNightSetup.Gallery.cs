using System.Linq;
using BlueNight.Core;
using BlueNight.Player;
using BlueNight.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using UnityEngine.Tilemaps;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// 第 1 章の素材（ドット絵）を Unity の画面で確かめるためのシーン。
    /// 商店街の建物・小物・人物・影の動き・演出・ランプ屋の中・顔グラフィック・UI・タイトルを並べ、
    /// ルリを歩かせて見て回れる（WASD／矢印キー、Shift で小走り）。動きはすべてくり返し再生する。
    /// </summary>
    public static partial class BlueNightSetup
    {
        const string GalleryScenePath = "Assets/001_Scenes/Ch1_ArtGallery.unity";
        static readonly Rect GalleryBounds = new Rect(-4f, -62f, 80f, 74f);

        [MenuItem("BlueNight/4. 第 1 章の素材を並べたシーンを作成", priority = 23)]
        public static void BuildArtGalleryScene()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                return;

            EnsureFolder("Assets/001_Scenes");
            EnsureFolder(TileAssetFolder);
            EnsureFolder("Assets/009_Rendering");
            AssetDatabase.ImportAsset(TexturesRoot, ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceUpdate);

            var lit = AssetDatabase.LoadAssetAtPath<Material>(SpriteLitMaterialPath);
            var unlit = AssetDatabase.LoadAssetAtPath<Material>(SpriteUnlitMaterialPath);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            Camera camera = CreateCamera();
            CreateMoonlight();
            CreateVolume();
            CreateGalleryGround(lit);

            GalleryStreet(lit);
            GalleryProps(lit, unlit);
            GalleryCharacters(lit, unlit);
            GalleryRuriActions(lit);
            GalleryEffects(unlit);
            GalleryLampShop(lit);
            GalleryFacesAndUi(unlit);

            PlayerController player = CreateRuri(lit, new Vector3(2f, 0.5f, 0f));
            CreateNemu(lit, player);

            var follow = camera.gameObject.AddComponent<CameraFollow2D>();
            follow.Configure(player.transform, GalleryBounds);

            EditorSceneManager.SaveScene(scene, GalleryScenePath);
            AddSceneToBuildSettings(GalleryScenePath);
            Debug.Log($"[BlueNight] {GalleryScenePath} を作成しました。再生して、ルリを歩かせて素材を見て回れます。");
        }

        // ------------------------------------------------------------------ 地面

        static void CreateGalleryGround(Material lit)
        {
            var grid = new GameObject("Grid").AddComponent<Grid>();
            var ground = CreateTilemap(grid, "Ground", -100, lit);

            Tile side0 = LoadTile("sidewalk_0"), side1 = LoadTile("sidewalk_1"), curb = LoadTile("curb");
            Tile road0 = LoadTile("road_0"), road1 = LoadTile("road_1"), line = LoadTile("road_line");
            Tile cross0 = LoadTile("crosswalk_0"), cross1 = LoadTile("crosswalk_1"), manhole = LoadTile("manhole");
            Tile drain0 = LoadTile("drain_0"), drain1 = LoadTile("drain_1"), block = LoadTile("block_wall");
            var random = new System.Random(3);

            for (int y = -26; y < 8; y++)
            {
                for (int x = -4; x < 76; x++)
                {
                    Tile tile;
                    if (y == -15) tile = curb;
                    else if (y < -15 && y >= -22)
                    {
                        if (x >= 30 && x <= 32) tile = (x + y) % 3 == 0 ? cross1 : cross0;
                        else if (y == -19 && (x & 1) == 0) tile = line;
                        else if (x == 12 && y == -18) tile = manhole;
                        else tile = random.NextDouble() < 0.15 ? road1 : road0;
                    }
                    else if (y == -23) tile = (x & 1) == 0 ? drain0 : drain1;
                    else if (y < -23) tile = block;
                    else tile = random.NextDouble() < 0.2 ? side1 : side0;
                    ground.SetTile(new Vector3Int(x, y, 0), tile);
                }
            }

            // 草：歩道のすき間に重ねる
            var weeds = CreateTilemap(grid, "Weeds", -99, lit);
            Tile weed = LoadTile("weeds");
            foreach (var p in new[] { new Vector3Int(3, 1, 0), new Vector3Int(11, -4, 0), new Vector3Int(25, 3, 0), new Vector3Int(34, -9, 0) })
                weeds.SetTile(p, weed);

            // ランプ屋の中（右下）：床と壁
            var inside = CreateTilemap(grid, "Lamp Shop Inside", -98, lit);
            Tile floor0 = LoadTileFrom("Interior/Tiles/floor_wood_0", "floor_wood_0");
            Tile floor1 = LoadTileFrom("Interior/Tiles/floor_wood_1", "floor_wood_1");
            Tile plaster0 = LoadTileFrom("Interior/Tiles/wall_plaster_0", "wall_plaster_0");
            Tile plaster1 = LoadTileFrom("Interior/Tiles/wall_plaster_1", "wall_plaster_1");
            Tile wainscot = LoadTileFrom("Interior/Tiles/wall_wainscot", "wall_wainscot");
            Tile wallTop = LoadTileFrom("Interior/Tiles/wall_top_inner", "wall_top_inner");
            for (int x = 44; x < 59; x++)
            {
                inside.SetTile(new Vector3Int(x, -38, 0), wallTop);
                inside.SetTile(new Vector3Int(x, -39, 0), x % 5 == 2 ? plaster1 : plaster0);
                inside.SetTile(new Vector3Int(x, -40, 0), plaster0);
                inside.SetTile(new Vector3Int(x, -41, 0), wainscot);
                for (int y = -47; y <= -42; y++)
                    inside.SetTile(new Vector3Int(x, y, 0), (x * 3 + y) % 5 == 0 ? floor1 : floor0);
            }
        }

        // ------------------------------------------------------------------ 商店街の建物

        static void GalleryStreet(Material lit)
        {
            var root = new GameObject("Buildings");
            // 建物は横に並べるとき輪郭を 1 ドット重ねる（1/16 unit）
            string[] names = { "house", "shutter_shop_0", "lamp_shop", "grandma_shop", "shutter_shop_1", "house" };
            float left = 0f;
            foreach (var name in names)
            {
                var sprite = LoadSprite($"{TexturesRoot}/Buildings/{name}.png");
                if (sprite == null)
                    continue;
                float width = sprite.rect.width / PixelsPerUnit;
                var go = CreateSpriteObject(root, name, $"Buildings/{name}", new Vector3(left + width / 2f, 6f, 0f), lit);
                AddFootCollider(go, new Vector2(width, 0.8f));
                left += width - 1f / PixelsPerUnit;
            }
            var shelter = CreateSpriteObject(root, "Bus Shelter", "Buildings/bus_shelter", new Vector3(left + 2f, 5f, 0f), lit);
            AddFootCollider(shelter, new Vector2(3f, 0.5f));

            // 明かりのついている窓
            CreatePointLight(root, "Grandma Shop Light", new Vector3(17f, 7.5f, 0f), Hex("#ffb866"), 0.9f, 3f);
            CreatePointLight(root, "House Window Light", new Vector3(31f, 10f, 0f), Hex("#ffb866"), 0.6f, 2.5f);
        }

        // ------------------------------------------------------------------ 小物

        static void GalleryProps(Material lit, Material unlit)
        {
            var root = new GameObject("Props");
            float x = 0f;

            // 街灯 3 本（1 本は明滅して、ガラスの絵も変わる）。蛾が集まる
            for (int i = 0; i < 3; i++)
            {
                var lamp = CreateSpriteObject(root, $"Street Lamp {i + 1}", "Props/lamp", new Vector3(x += 3f, 2f, 0f), lit);
                AddFootCollider(lamp, new Vector2(0.5f, 0.3f));
                var light = CreatePointLight(lamp, "Lamp Light", new Vector3(0f, 2.4f, 0f), Hex("#ffc98a"), 1.1f, 4.5f);
                AddMoths(lamp, new Vector3(0f, 2.3f, 0f));
                if (i == 1)
                {
                    light.gameObject.AddComponent<LightFlicker2D>().ConfigureSprites(lamp.GetComponent<SpriteRenderer>(),
                        LoadSprite($"{TexturesRoot}/Props/lamp.png"), LoadSprite($"{TexturesRoot}/Props/lamp_dim.png"),
                        LoadSprite($"{TexturesRoot}/Props/lamp_off.png"));
                }
            }

            string[] props =
            {
                "vending", "hook", "mailbox", "bench", "power_pole", "curve_mirror", "trash_bin", "pot_plant",
                "beer_crates", "a_sign", "bicycle", "extinguisher_box", "bus_sign", "lantern",
            };
            x += 1f;
            foreach (var name in props)
            {
                var sprite = LoadSprite($"{TexturesRoot}/Props/{name}.png");
                if (sprite == null)
                    continue;
                float width = sprite.rect.width / PixelsPerUnit;
                x += width / 2f + 1f;
                var go = CreateSpriteObject(root, name, $"Props/{name}", new Vector3(x, 2f, 0f), name == "lantern" ? unlit : lit);
                AddFootCollider(go, new Vector2(Mathf.Max(0.4f, width * 0.8f), 0.3f));
                x += width / 2f;
            }
            CreatePointLight(root, "Vending Light", new Vector3(7.5f, 3f, 0f), Hex("#cfe8ff"), 0.8f, 3f);

            // 月が映る水たまりと、波紋（くり返し）
            var puddle = CreateSpriteObject(root, "Puddle (Moon)", "Props/puddle_moon", new Vector3(20f, -12f, 0f), lit);
            puddle.GetComponent<SpriteRenderer>().sortingOrder = -50;
            var ripple = CreateLoop(root, "Ripple", "Effects/fx_ripple_", new Vector3(20.6f, -11.6f, 0f), unlit, 6f);
            ripple.GetComponent<SpriteRenderer>().sortingOrder = -49;
        }

        // ------------------------------------------------------------------ 人物と影

        static void GalleryCharacters(Material lit, Material unlit)
        {
            var root = new GameObject("Characters");
            const float y = -3f;
            CreateLoopWithFootShadow(root, "Grandma", "Characters/Grandma/grandma_idle_", new Vector3(2f, y, 0f), lit, 1.2f);
            CreateLoopWithFootShadow(root, "Grandma (Dozing)", "Characters/Grandma/grandma_doze_", new Vector3(4f, y, 0f), lit, 0.8f);
            CreateLoopWithFootShadow(root, "Keeper", "Characters/Keeper/keeper_idle_", new Vector3(6f, y, 0f), lit, 0.8f);
            CreateLoopWithFootShadow(root, "Cat", "Characters/Cat/cat_idle_", new Vector3(8f, y, 0f), lit, 1.5f);

            // 逃げた影（unlit：光に関係なく真っ黒と水色のふち）
            string s = "Characters/Shadows/";
            CreateLoop(root, "Cat Shadow", s + "shadow_cat_", new Vector3(10f, y, 0f), unlit, 6f);
            float x = 12f;
            foreach (var d in new[] { "down", "up", "right", "left" })
                CreateLoop(root, $"Grandma Shadow (Move {d})", s + $"shadow_grandma_move_{d}_", new Vector3(x += 1.6f, y, 0f), unlit, 10f);
            CreateLoop(root, "Grandma Shadow (Surprised)", s + "shadow_grandma_surprised_", new Vector3(x += 1.8f, y, 0f), unlit, 4f);
            CreateLoop(root, "Grandma Shadow (Caught)", s + "shadow_grandma_caught_", new Vector3(x += 1.8f, y, 0f), unlit, 6f);
            x += 1f;
            foreach (var anim in new[] { "walk", "run" })
                foreach (var d in new[] { "down", "up", "right", "left" })
                    CreateLoop(root, $"Ruri's Shadow ({anim} {d})", s + $"shadow_ruri_{anim}_{d}_", new Vector3(x += 1.4f, y, 0f), unlit, anim == "run" ? 12f : 8f);
        }

        static void GalleryRuriActions(Material lit)
        {
            // 動き 6 種 × 4 向き を横に並べる（腕をのばす動きは絵が広いので、間をあける）
            var root = new GameObject("Ruri Actions");
            foreach (var anim in new[] { "idle", "walk", "run", "inspect", "hang", "place" })
            {
                float fps = anim == "idle" ? 3f : anim == "walk" ? 8f : anim == "run" ? 12f : 6f;
                float step = anim == "hang" || anim == "place" || anim == "inspect" ? 2.4f : 1.6f;
                float x = AnimColumn(anim);
                foreach (var d in new[] { "down", "up", "right", "left" })
                    CreateLoop(root, $"Ruri ({anim} {d})", $"Characters/Ruri/ruri_{anim}_{d}_", new Vector3(x += step, -8f, 0f), lit, fps);
            }
        }

        static float AnimColumn(string anim)
        {
            switch (anim)
            {
                case "walk": return 8f;
                case "run": return 16f;
                case "inspect": return 24f;
                case "hang": return 35f;
                case "place": return 46f;
                default: return 0f;
            }
        }

        // ------------------------------------------------------------------ 演出

        static void GalleryEffects(Material unlit)
        {
            var root = new GameObject("Effects");
            const float y = -13f;
            CreateLoop(root, "Capture Flash", "Effects/fx_capture_", new Vector3(2f, y, 0f), unlit, 10f);
            CreateLoop(root, "Return Motes", "Effects/fx_return_", new Vector3(5f, y, 0f), unlit, 8f);
            CreateLoop(root, "Sparkle", "Effects/fx_sparkle_", new Vector3(7f, y, 0f), unlit, 6f);
            CreateLoop(root, "Moths", "Effects/fx_moths_", new Vector3(9f, y, 0f), unlit, 8f);
            CreateSpriteObject(root, "Foot Shadow", "Effects/foot_shadow", new Vector3(11f, y, 0f), unlit);
        }

        // ------------------------------------------------------------------ ランプ屋の中

        static void GalleryLampShop(Material lit)
        {
            var root = new GameObject("Lamp Shop Inside");
            string i = "Interior/";
            Vector3 P(float x, float y) => new Vector3(x, y, 0f);
            CreateSpriteObject(root, "Window", i + "window_inner", P(51.5f, -39.2f), lit);
            CreateSpriteObject(root, "Shelf 1", i + "shelf_lamps", P(45.8f, -41f), lit);
            CreateSpriteObject(root, "Shelf 2", i + "shelf_lamps", P(47.9f, -41f), lit);
            CreateSpriteObject(root, "Shelf 3", i + "shelf_lamps", P(55f, -41f), lit);
            CreateSpriteObject(root, "Clock", i + "grandfather_clock", P(57.5f, -41f), lit);
            var rug = CreateSpriteObject(root, "Rug", i + "rug", P(51.5f, -45.8f), lit);
            rug.GetComponent<SpriteRenderer>().sortingOrder = -60;
            AddFootCollider(CreateSpriteObject(root, "Workbench", i + "workbench", P(46.5f, -43f), lit), new Vector2(2f, 0.4f));
            CreateSpriteObject(root, "Stool", i + "stool", P(46.5f, -44f), lit);
            AddFootCollider(CreateSpriteObject(root, "Counter", i + "counter", P(54.5f, -43.4f), lit), new Vector2(3f, 0.5f));
            CreateSpriteObject(root, "Crate 1", i + "crate", P(57.5f, -42.5f), lit);
            CreateSpriteObject(root, "Crate 2", i + "crate", P(58f, -43.5f), lit);
            var mat = CreateSpriteObject(root, "Doormat", i + "doormat", P(51.5f, -48f), lit);
            mat.GetComponent<SpriteRenderer>().sortingOrder = -60;
            CreateSpriteObject(root, "Hanging Lamp (off)", i + "hanging_lamp_off", P(48.5f, -38.8f), lit);
            var lamp = CreateSpriteObject(root, "Hanging Lamp (on)", i + "hanging_lamp_on", P(53.5f, -38.8f), lit);
            CreatePointLight(lamp, "Light", new Vector3(0f, 0.3f, 0f), Hex("#ffc98a"), 0.9f, 4f);
            var counterLight = new GameObject("Old Lantern Light");
            counterLight.transform.SetParent(root.transform, false);
            CreatePointLight(counterLight, "Light", new Vector3(55.2f, -42.6f, 0f), Hex("#ffb866"), 0.8f, 3.5f);
            CreateLoopWithFootShadow(root, "Keeper", "Characters/Keeper/keeper_idle_", P(55.5f, -42.2f), lit, 0.8f);
        }

        // ------------------------------------------------------------------ 顔グラフィック・UI・タイトル

        static void GalleryFacesAndUi(Material unlit)
        {
            var root = new GameObject("Faces and UI");
            var faces = AssetDatabase.FindAssets("t:Sprite", new[] { $"{TexturesRoot}/Faces" })
                .Select(AssetDatabase.GUIDToAssetPath).OrderBy(p => p).ToArray();
            float x = 0f;
            foreach (var path in faces)
            {
                string name = System.IO.Path.GetFileNameWithoutExtension(path);
                CreateSpriteObject(root, name, $"Faces/{name}", new Vector3(x += 3.4f, -30f, 0f), unlit);
            }

            var ui = AssetDatabase.FindAssets("t:Sprite", new[] { $"{TexturesRoot}/UI" })
                .Select(AssetDatabase.GUIDToAssetPath).OrderBy(p => p).ToArray();
            x = 0f;
            foreach (var path in ui)
            {
                string name = System.IO.Path.GetFileNameWithoutExtension(path);
                CreateSpriteObject(root, name, $"UI/{name}", new Vector3(x += 2f, -34f, 0f), unlit);
            }

            // タイトル（一枚絵＋ロゴ）
            CreateSpriteObject(root, "Title", "Title/title_bg", new Vector3(16f, -50f, 0f), unlit).GetComponent<SpriteRenderer>().sortingOrder = -10;
            CreateSpriteObject(root, "Title Logo", "Title/title_logo", new Vector3(7.5f, -45f, 0f), unlit).GetComponent<SpriteRenderer>().sortingOrder = -9;
        }

        // ------------------------------------------------------------------ 共通

        /// <summary>コマ（prefix0.png, prefix1.png, ...）をくり返し再生するもの。</summary>
        static GameObject CreateLoop(GameObject parent, string name, string prefix, Vector3 position, Material material, float fps)
        {
            var frames = LoadFrames($"{TexturesRoot}/{prefix}");
            var go = new GameObject(name);
            go.transform.SetParent(parent.transform, false);
            go.transform.position = position;
            var renderer = go.AddComponent<SpriteRenderer>();
            renderer.sprite = frames.FirstOrDefault();
            renderer.spriteSortPoint = SpriteSortPoint.Pivot;
            if (material != null)
                renderer.sharedMaterial = material;
            go.AddComponent<SimpleSpriteAnimator>().Configure(frames, fps);
            return go;
        }

        /// <summary>影のある人（足元に影を置く）。</summary>
        static GameObject CreateLoopWithFootShadow(GameObject parent, string name, string prefix, Vector3 position, Material material, float fps)
        {
            var go = CreateLoop(parent, name, prefix, position, material, fps);
            var shadow = CreateSpriteObject(go, "Foot Shadow", "Effects/foot_shadow", position + new Vector3(0f, 0.05f, 0f), material);
            shadow.GetComponent<SpriteRenderer>().sortingOrder = -40;
            AddFootCollider(go, new Vector2(0.6f, 0.3f));
            return go;
        }
    }
}
