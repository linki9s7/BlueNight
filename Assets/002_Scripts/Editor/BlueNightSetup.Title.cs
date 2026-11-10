using BlueNight.Title;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// タイトル画面：満月と高架のハイウェイの一枚絵、ロゴ、流れる車の光、メニュー（はじめから／つづきから／設定／終了）。
    /// BlueNight > 6. タイトル画面を作成
    /// </summary>
    public static partial class BlueNightSetup
    {
        const string TitleScenePath = "Assets/001_Scenes/Title.unity";

        [MenuItem("BlueNight/6. タイトル画面を作成", priority = 25)]
        public static void BuildTitleScene()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                return;

            EnsureProjectConfigured();

            EnsureFolder("Assets/001_Scenes");
            EnsureFolder("Assets/009_Rendering");
            AssetDatabase.ImportAsset(TexturesRoot, ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceUpdate);
            var unlit = AssetDatabase.LoadAssetAtPath<Material>(SpriteUnlitMaterialPath);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            CreateCamera();
            CreateVolume();

            // 一枚絵（480x270）は画面ちょうど。ロゴは絵の左上（36, 52 ドット）に合わせる
            var root = new GameObject("Title");
            var bg = CreateSpriteObject(root, "Background", "Title/title_bg", Vector3.zero, unlit);
            bg.GetComponent<SpriteRenderer>().sortingOrder = -10;
            var logoSprite = LoadSprite($"{TexturesRoot}/Title/title_logo.png");
            if (logoSprite != null)
            {
                float cx = 36f + logoSprite.rect.width / 2f, cy = 52f + logoSprite.rect.height / 2f;
                CreateSpriteObject(root, "Logo", "Title/title_logo", ImageToWorld(cx, cy), unlit)
                    .GetComponent<SpriteRenderer>().sortingOrder = 10;
            }

            // 車の光：高架の道路（絵の中で、左端 y=150、右端 y=168 ドットの線のすぐ下）
            var cars = new GameObject("Car Lights").AddComponent<CarLights>();
            cars.Configure(LoadSprite($"{TexturesRoot}/Title/title_car_head.png"), LoadSprite($"{TexturesRoot}/Title/title_car_tail.png"),
                ImageToWorld(0f, 151.5f), ImageToWorld(480f, 169.5f), unlit);

            var menu = new GameObject("Title Screen").AddComponent<TitleScreen>();
            menu.Configure(AssetDatabase.LoadAssetAtPath<Font>(DialogueFontPath), LoadSprite($"{TexturesRoot}/UI/ui_cursor.png"),
                System.IO.Path.GetFileNameWithoutExtension(Chapter1ScenePath));   // 「はじめから」で序章・第 1 章へ

            CreateAudio("title_ruri_theme", Ambience("highway", 0.3f));

            EditorSceneManager.SaveScene(scene, TitleScenePath);
            AddSceneToBuildSettings(TitleScenePath);
            if (System.IO.File.Exists(Chapter1ScenePath))
                AddSceneToBuildSettings(Chapter1ScenePath);
            else
                Debug.LogWarning("[BlueNight] 第 1 章のシーンがまだありません。先にメニュー 7 で作ってください（「はじめから」で開くシーン）。");
            Debug.Log($"[BlueNight] {TitleScenePath} を作成しました。再生すると、タイトルから序章・第 1 章を始められます。");
        }

        /// <summary>480x270 の絵の中の位置（左上が原点、ドット）を、カメラの中心を原点としたワールド座標に。</summary>
        static Vector3 ImageToWorld(float x, float y) => new Vector3((x - 240f) / PixelsPerUnit, (135f - y) / PixelsPerUnit, 0f);
    }
}
