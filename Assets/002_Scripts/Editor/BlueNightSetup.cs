using System.Collections.Generic;
using System.Linq;
using BlueNight.Core;
using BlueNight.Player;
using BlueNight.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.Tilemaps;
using PixelPerfectCamera = UnityEngine.Experimental.Rendering.Universal.PixelPerfectCamera;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// M0 環境整備をメニューから一括で行う。
    /// BlueNight > M0 セットアップ（すべて実行）
    /// </summary>
    public static partial class BlueNightSetup
    {
        const string Renderer2DPath = "Assets/Settings/Renderer2D.asset";
        const string PostProcessDataGuid = "41439944d30ece34e96484bdb6645b55";
        const string PostProcessDataFallbackPath = "Packages/com.unity.render-pipelines.universal/Runtime/Data/PostProcessData.asset";
        const string SpriteLitMaterialPath = "Packages/com.unity.render-pipelines.universal/Runtime/Materials/Sprite-Lit-Default.mat";

        const string TexturesRoot = "Assets/005_Textures";
        const string TileAssetFolder = "Assets/007_Data/Tiles";
        const string VolumeProfilePath = "Assets/009_Rendering/M0_NightProfile.asset";
        const string ScenePath = "Assets/001_Scenes/M0_Test.unity";

        const int PixelsPerUnit = 16;
        const int RefResolutionX = 480;
        const int RefResolutionY = 270;

        // 部屋の範囲（タイル = 1 unit）
        static readonly RectInt MapRect = new RectInt(-20, -12, 40, 24);

        [MenuItem("BlueNight/M0 セットアップ（すべて実行）", priority = 0)]
        public static void RunAll()
        {
            ConfigureProject();
            BuildM0Scene();
        }

        // ------------------------------------------------------------------ プロジェクト設定

        [MenuItem("BlueNight/1. プロジェクトを 2D 用に設定", priority = 20)]
        public static void ConfigureProject()
        {
            Renderer2DData renderer = CreateOrUpdateRenderer2D();
            int count = AssignRendererToAllUrpAssets(renderer);

            PlayerSettings.defaultScreenWidth = 1920;
            PlayerSettings.defaultScreenHeight = 1080;

            // 2D Renderer と同じ並べ方（足元の Y）を、ほかの描画（Scene ビューなど）にも
            GraphicsSettings.transparencySortMode = TransparencySortMode.CustomAxis;
            GraphicsSettings.transparencySortAxis = new Vector3(0f, 1f, 0f);

            AssetDatabase.SaveAssets();
            Debug.Log($"[BlueNight] 2D Renderer を {count} 個の URP アセットに設定しました。");
        }

        /// <summary>
        /// シーンを作る前に、メニュー 1 の設定（2D Renderer・足元の Y で前後を並べる）を必ず済ませる。
        /// 済んでいないと 3D 用の描き方のままになり、前後の並びも 2D の明かりも効かない。
        /// </summary>
        static void EnsureProjectConfigured()
        {
            bool ready = AssetDatabase.FindAssets("t:UniversalRenderPipelineAsset", new[] { "Assets" })
                .Select(guid => AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(AssetDatabase.GUIDToAssetPath(guid)))
                .Where(asset => asset != null)
                .All(asset =>
                {
                    var list = new SerializedObject(asset).FindProperty("m_RendererDataList");
                    return list.arraySize == 1 && list.GetArrayElementAtIndex(0).objectReferenceValue is Renderer2DData;
                });
            if (!ready || GraphicsSettings.transparencySortMode != TransparencySortMode.CustomAxis)
                ConfigureProject();
        }

        static Renderer2DData CreateOrUpdateRenderer2D()
        {
            var renderer = AssetDatabase.LoadAssetAtPath<Renderer2DData>(Renderer2DPath);
            if (renderer == null)
            {
                renderer = ScriptableObject.CreateInstance<Renderer2DData>();
                AssetDatabase.CreateAsset(renderer, Renderer2DPath);
            }

            var so = new SerializedObject(renderer);

            // 足元の Y 座標で前後を並べ替える（下にいるものほど手前）
            SetEnumIndex(so, "m_TransparencySortMode", (int)TransparencySortMode.CustomAxis);
            SetVector3(so, "m_TransparencySortAxis", new Vector3(0f, 1f, 0f));

            var postProcess = so.FindProperty("m_PostProcessData");
            if (postProcess != null && postProcess.objectReferenceValue == null)
                postProcess.objectReferenceValue = LoadPostProcessData();
            else if (postProcess == null)
                Debug.LogWarning("[BlueNight] Renderer2DData.m_PostProcessData が見つかりません。ポストエフェクトが効かない場合は 2D Renderer の Post-processing を手動で有効にしてください。");

            so.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(renderer);
            return renderer;
        }

        static PostProcessData LoadPostProcessData()
        {
            string path = AssetDatabase.GUIDToAssetPath(PostProcessDataGuid);
            var data = string.IsNullOrEmpty(path) ? null : AssetDatabase.LoadAssetAtPath<PostProcessData>(path);
            return data != null ? data : AssetDatabase.LoadAssetAtPath<PostProcessData>(PostProcessDataFallbackPath);
        }

        static int AssignRendererToAllUrpAssets(Renderer2DData renderer)
        {
            int count = 0;
            foreach (string guid in AssetDatabase.FindAssets("t:UniversalRenderPipelineAsset", new[] { "Assets" }))
            {
                var asset = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(AssetDatabase.GUIDToAssetPath(guid));
                if (asset == null)
                    continue;

                var so = new SerializedObject(asset);
                var list = so.FindProperty("m_RendererDataList");
                list.arraySize = 1;
                list.GetArrayElementAtIndex(0).objectReferenceValue = renderer;
                so.FindProperty("m_DefaultRendererIndex").intValue = 0;

                // ドット絵なので MSAA は不要。ブルームのために HDR は使う。
                SetInt(so, "m_MSAA", 1);
                SetBool(so, "m_SupportsHDR", true);

                so.ApplyModifiedPropertiesWithoutUndo();
                EditorUtility.SetDirty(asset);
                count++;
            }
            return count;
        }

        // ------------------------------------------------------------------ M0 テストシーン

        [MenuItem("BlueNight/2. M0 テストシーンを作成", priority = 21)]
        public static void BuildM0Scene()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                return;

            EnsureProjectConfigured();

            EnsureFolder("Assets/001_Scenes");
            EnsureFolder(TileAssetFolder);
            EnsureFolder("Assets/009_Rendering");

            // 取り込み設定（BlueNightTextureImporter）を確実に反映させる
            AssetDatabase.ImportAsset(TexturesRoot, ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceUpdate);

            var spriteMaterial = AssetDatabase.LoadAssetAtPath<Material>(SpriteLitMaterialPath);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            Camera camera = CreateCamera();
            CreateMoonlight();
            CreateVolume();
            CreateGround(spriteMaterial);
            CreateMapEdges();
            CreateProps(spriteMaterial);
            PlayerController player = CreateRuri(spriteMaterial, new Vector3(0f, 2f, 0f));
            CreateNemu(spriteMaterial, player);

            var follow = camera.gameObject.AddComponent<CameraFollow2D>();
            follow.Configure(player.transform, new Rect(MapRect.x, MapRect.y, MapRect.width, MapRect.height));

            EditorSceneManager.SaveScene(scene, ScenePath);
            AddSceneToBuildSettings(ScenePath);
            Debug.Log($"[BlueNight] {ScenePath} を作成しました。再生して WASD / 矢印キーで歩けます（Shift で小走り）。");
        }

        static Camera CreateCamera()
        {
            var go = new GameObject("Main Camera");
            go.tag = "MainCamera";
            go.transform.position = new Vector3(0f, 0f, -10f);

            var camera = go.AddComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = RefResolutionY / (2f * PixelsPerUnit);
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Hex("#07070f");
            go.AddComponent<AudioListener>();

            var cameraData = camera.GetUniversalAdditionalCameraData();
            cameraData.renderPostProcessing = true;
            cameraData.antialiasing = AntialiasingMode.None;

            // 480x270 で描いてから整数倍に拡大。割り切れない解像度では周囲に黒帯。
            // ※ URP 14 の 2D Renderer では、この設定のときポストエフェクトも 480x270 のまま処理される。
            var ppc = go.AddComponent<PixelPerfectCamera>();
            ppc.assetsPPU = PixelsPerUnit;
            ppc.refResolutionX = RefResolutionX;
            ppc.refResolutionY = RefResolutionY;
            ppc.gridSnapping = PixelPerfectCamera.GridSnapping.UpscaleRenderTexture;
            ppc.cropFrame = PixelPerfectCamera.CropFrame.Windowbox;

            return camera;
        }

        static void CreateMoonlight()
        {
            // 月明かり：画面全体を照らす青い光
            var light = new GameObject("Moonlight (Global Light 2D)").AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = Hex("#7f97e0");
            light.intensity = 0.55f;
        }

        static void CreateVolume()
        {
            var volume = new GameObject("Global Volume").AddComponent<Volume>();
            volume.isGlobal = true;
            volume.sharedProfile = CreateOrResetNightProfile();
        }

        /// <summary>夜の画面効果のプロファイル。既にあれば中身だけ作り直す（他のシーンからの参照を切らさない）。</summary>
        static VolumeProfile CreateOrResetNightProfile()
        {
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(VolumeProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(profile, VolumeProfilePath);
            }
            else
            {
                foreach (var component in profile.components.ToList())
                    Object.DestroyImmediate(component, true);
                profile.components.Clear();
            }

            var bloom = AddOverride<Bloom>(profile);
            bloom.threshold.Override(0.85f);
            bloom.intensity.Override(1.2f);
            bloom.scatter.Override(0.7f);
            bloom.tint.Override(Hex("#ffe2c0"));

            var tonemapping = AddOverride<Tonemapping>(profile);
            tonemapping.mode.Override(TonemappingMode.Neutral);

            var colorAdjustments = AddOverride<ColorAdjustments>(profile);
            colorAdjustments.postExposure.Override(0.1f);
            colorAdjustments.contrast.Override(12f);
            colorAdjustments.saturation.Override(-8f);

            // 暗部は青、明部は暖色へ（スプリットトーン）
            var splitToning = AddOverride<SplitToning>(profile);
            splitToning.shadows.Override(Hex("#2a3f8f"));
            splitToning.highlights.Override(Hex("#e0a060"));
            splitToning.balance.Override(-15f);

            var whiteBalance = AddOverride<WhiteBalance>(profile);
            whiteBalance.temperature.Override(-12f);

            var vignette = AddOverride<Vignette>(profile);
            vignette.color.Override(Hex("#05060f"));
            vignette.intensity.Override(0.32f);
            vignette.smoothness.Override(0.45f);

            var grain = AddOverride<FilmGrain>(profile);
            grain.type.Override(FilmGrainLookup.Thin1);
            grain.intensity.Override(0.12f);
            grain.response.Override(0.8f);

            var chromatic = AddOverride<ChromaticAberration>(profile);
            chromatic.intensity.Override(0.08f);

            EditorUtility.SetDirty(profile);
            AssetDatabase.SaveAssets();
            return profile;
        }

        static T AddOverride<T>(VolumeProfile profile) where T : VolumeComponent
        {
            var component = profile.Add<T>(true);
            component.name = typeof(T).Name;
            AssetDatabase.AddObjectToAsset(component, profile);
            return component;
        }

        static void CreateGround(Material spriteMaterial)
        {
            var grid = new GameObject("Grid").AddComponent<Grid>();
            grid.cellSize = Vector3.one;

            var tilemapGo = new GameObject("Ground");
            tilemapGo.transform.SetParent(grid.transform, false);
            var tilemap = tilemapGo.AddComponent<Tilemap>();
            var tilemapRenderer = tilemapGo.AddComponent<TilemapRenderer>();
            tilemapRenderer.sortingOrder = -100;
            if (spriteMaterial != null)
                tilemapRenderer.sharedMaterial = spriteMaterial;

            Tile road0 = LoadTile("road_0"), road1 = LoadTile("road_1"), roadLine = LoadTile("road_line");
            Tile side0 = LoadTile("sidewalk_0"), side1 = LoadTile("sidewalk_1"), curb = LoadTile("curb");

            var random = new System.Random(42);
            for (int y = MapRect.yMin; y < MapRect.yMax; y++)
            {
                for (int x = MapRect.xMin; x < MapRect.xMax; x++)
                {
                    Tile tile;
                    if (y == -1 || y == -10)
                        tile = curb;                                     // 縁石
                    else if (y <= -2 && y >= -9)
                        tile = y == -6 && (x & 1) == 0 ? roadLine        // 車道と中央線
                             : random.NextDouble() < 0.15 ? road1 : road0;
                    else
                        tile = random.NextDouble() < 0.2 ? side1 : side0; // 歩道
                    tilemap.SetTile(new Vector3Int(x, y, 0), tile);
                }
            }
        }

        static Tile LoadTile(string name) => LoadTileFrom($"Tiles/{name}", name);

        /// <summary>Assets/005_Textures からの相対パス（拡張子なし）の絵をタイルにする。</summary>
        static Tile LoadTileFrom(string texture, string assetName)
        {
            var sprite = LoadSprite($"{TexturesRoot}/{texture}.png");
            string path = $"{TileAssetFolder}/{assetName}.asset";
            var tile = AssetDatabase.LoadAssetAtPath<Tile>(path);
            if (tile == null)
            {
                tile = ScriptableObject.CreateInstance<Tile>();
                tile.sprite = sprite;
                AssetDatabase.CreateAsset(tile, path);
            }
            else
            {
                tile.sprite = sprite;
                EditorUtility.SetDirty(tile);
            }
            return tile;
        }

        static void CreateMapEdges()
        {
            var root = new GameObject("Map Edges");
            var r = MapRect;
            AddWall(root, "Top", new Vector2(r.center.x, r.yMax + 0.5f), new Vector2(r.width + 2f, 1f));
            AddWall(root, "Bottom", new Vector2(r.center.x, r.yMin - 0.5f), new Vector2(r.width + 2f, 1f));
            AddWall(root, "Left", new Vector2(r.xMin - 0.5f, r.center.y), new Vector2(1f, r.height + 2f));
            AddWall(root, "Right", new Vector2(r.xMax + 0.5f, r.center.y), new Vector2(1f, r.height + 2f));
        }

        static void AddWall(GameObject parent, string name, Vector2 position, Vector2 size)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent.transform, false);
            go.transform.position = position;
            go.AddComponent<BoxCollider2D>().size = size;
        }

        static void CreateProps(Material spriteMaterial)
        {
            var root = new GameObject("Props");

            // 街灯（歩道の縁石ぎわに並べる）。1 本だけ古くて瞬く。
            float[] lampXs = { -14f, -4f, 6f, 16f };
            for (int i = 0; i < lampXs.Length; i++)
            {
                var lamp = CreateSpriteObject(root, $"Street Lamp {i + 1}", "Props/lamp", new Vector3(lampXs[i], 0.2f, 0f), spriteMaterial);
                AddFootCollider(lamp, new Vector2(0.5f, 0.3f));
                var light = CreatePointLight(lamp, "Lamp Light", new Vector3(0f, 2.4f, 0f), Hex("#ffc98a"), 1.1f, 5.5f);
                if (i == 2)
                    light.gameObject.AddComponent<LightFlicker2D>();
            }

            // 自販機：商品ケースの冷たい白い光
            var vending = CreateSpriteObject(root, "Vending Machine", "Props/vending", new Vector3(-9f, 5f, 0f), spriteMaterial);
            AddFootCollider(vending, new Vector2(1f, 0.6f));
            CreatePointLight(vending, "Vending Light", new Vector3(0f, 0.8f, 0f), Hex("#cfe8ff"), 0.9f, 3.5f);

            // 月が映る水たまり（地面の一部として、キャラより奥に描く）
            var puddle = CreateSpriteObject(root, "Puddle (Moon)", "Props/puddle_moon", new Vector3(3f, 4f, 0f), spriteMaterial);
            puddle.GetComponent<SpriteRenderer>().sortingOrder = -50;
        }

        static PlayerController CreateRuri(Material spriteMaterial, Vector3 position, bool withLanternLight = true)
        {
            var go = new GameObject("Ruri");
            go.transform.position = position;

            var body = go.AddComponent<Rigidbody2D>();
            body.bodyType = RigidbodyType2D.Dynamic;
            body.gravityScale = 0f;
            body.freezeRotation = true;
            body.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
            body.interpolation = RigidbodyInterpolation2D.Interpolate;

            var collider = go.AddComponent<BoxCollider2D>();
            collider.size = new Vector2(0.6f, 0.35f);
            collider.offset = new Vector2(0f, 0.18f);

            var controller = go.AddComponent<PlayerController>();

            var renderer = go.AddComponent<SpriteRenderer>();
            renderer.spriteSortPoint = SpriteSortPoint.Pivot;
            if (spriteMaterial != null)
                renderer.sharedMaterial = spriteMaterial;
            // 持っているランタンとネムは子にして、ルリの足元の Y でまとめて前後を決める
            // （番号だけで手前にすると、ルリが人や建物の後ろに回っても手前に出てしまう）
            go.AddComponent<SortingGroup>();

            var idle = LoadDirectionalFrames("idle");
            var walk = LoadDirectionalFrames("walk");
            renderer.sprite = idle.down.FirstOrDefault();
            go.AddComponent<PlayerAnimator>().Configure(controller, idle, walk,
                LoadDirectionalFrames("run"), LoadDirectionalFrames("inspect"),
                LoadDirectionalFrames("hang"), LoadDirectionalFrames("place"));

            // ランタンの光（手元から）。M1 以降はランタンを独立したオブジェクトにする
            if (withLanternLight)
                CreatePointLight(go, "Lantern Light", new Vector3(0.3f, 0.8f, 0f), Hex("#ffb866"), 1.15f, 4.5f);
            return controller;
        }

        static PlayerAnimator.DirectionalFrames LoadDirectionalFrames(string anim, string prefix = "Ruri/ruri")
        {
            return new PlayerAnimator.DirectionalFrames
            {
                down = LoadFrames($"{TexturesRoot}/Characters/{prefix}_{anim}_down_"),
                up = LoadFrames($"{TexturesRoot}/Characters/{prefix}_{anim}_up_"),
                right = LoadFrames($"{TexturesRoot}/Characters/{prefix}_{anim}_right_"),
                left = LoadFrames($"{TexturesRoot}/Characters/{prefix}_{anim}_left_"),
            };
        }

        static void CreateNemu(Material spriteMaterial, PlayerController player)
        {
            var go = new GameObject("Nemu");
            // ルリの子（ルリの SortingGroup の中）。ルリより手前か奥かは NemuFollower が向きで決める
            go.transform.SetParent(player.transform, false);
            go.transform.position = player.transform.position + new Vector3(-0.7f, 1.9f, 0f);
            var renderer = go.AddComponent<SpriteRenderer>();
            if (spriteMaterial != null)
                renderer.sharedMaterial = spriteMaterial;

            var frames = LoadDirectionalFrames("fly", "Nemu/nemu");
            renderer.sprite = frames.down.FirstOrDefault();
            go.AddComponent<NemuFollower>().Configure(player, frames);
        }

        // ------------------------------------------------------------------ 共通

        static GameObject CreateSpriteObject(GameObject parent, string name, string texture, Vector3 position, Material material)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent.transform, false);
            go.transform.position = position;
            var renderer = go.AddComponent<SpriteRenderer>();
            renderer.sprite = LoadSprite($"{TexturesRoot}/{texture}.png");
            renderer.spriteSortPoint = SpriteSortPoint.Pivot;
            if (material != null)
                renderer.sharedMaterial = material;
            return go;
        }

        static void AddFootCollider(GameObject go, Vector2 size)
        {
            var collider = go.AddComponent<BoxCollider2D>();
            collider.size = size;
            collider.offset = new Vector2(0f, size.y * 0.5f);
        }

        static Light2D CreatePointLight(GameObject parent, string name, Vector3 localPosition, Color color, float intensity, float radius)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent.transform, false);
            go.transform.localPosition = localPosition;
            var light = go.AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Point;
            light.color = color;
            light.intensity = intensity;
            light.pointLightInnerRadius = radius * 0.15f;
            light.pointLightOuterRadius = radius;
            light.falloffIntensity = 0.6f;
            return light;
        }

        static Sprite LoadSprite(string path)
        {
            var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(path);
            if (sprite == null)
                Debug.LogWarning($"[BlueNight] スプライトが見つかりません: {path}（Tools/Art/build.py を実行してください）");
            return sprite;
        }

        static Sprite[] LoadFrames(string prefix)
        {
            var frames = new List<Sprite>();
            for (int i = 0; ; i++)
            {
                var sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{prefix}{i}.png");
                if (sprite == null)
                    break;
                frames.Add(sprite);
            }
            if (frames.Count == 0)
                Debug.LogWarning($"[BlueNight] コマが見つかりません: {prefix}0.png");
            return frames.ToArray();
        }

        /// <summary>ビルドのシーン一覧に入れる。タイトル画面はいつも先頭（ゲームを起動すると最初に開く）。</summary>
        static void AddSceneToBuildSettings(string path)
        {
            var scenes = EditorBuildSettings.scenes
                .Where(s => s.path != path && System.IO.File.Exists(s.path))
                .ToList();
            var entry = new EditorBuildSettingsScene(path, true);
            if (path == TitleScenePath)
                scenes.Insert(0, entry);
            else
                scenes.Add(entry);
            EditorBuildSettings.scenes = scenes.ToArray();
        }

        static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path))
                return;
            string parent = System.IO.Path.GetDirectoryName(path).Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, System.IO.Path.GetFileName(path));
        }

        static Color Hex(string hex)
        {
            ColorUtility.TryParseHtmlString(hex, out var color);
            return color;
        }

        static void SetEnumIndex(SerializedObject so, string name, int index)
        {
            var p = so.FindProperty(name);
            if (p != null) p.enumValueIndex = index;
            else Debug.LogWarning($"[BlueNight] {so.targetObject.GetType().Name}.{name} が見つかりません");
        }

        static void SetVector3(SerializedObject so, string name, Vector3 value)
        {
            var p = so.FindProperty(name);
            if (p != null) p.vector3Value = value;
            else Debug.LogWarning($"[BlueNight] {so.targetObject.GetType().Name}.{name} が見つかりません");
        }

        static void SetInt(SerializedObject so, string name, int value)
        {
            var p = so.FindProperty(name);
            if (p != null) p.intValue = value;
        }

        static void SetBool(SerializedObject so, string name, bool value)
        {
            var p = so.FindProperty(name);
            if (p != null) p.boolValue = value;
        }
    }
}
