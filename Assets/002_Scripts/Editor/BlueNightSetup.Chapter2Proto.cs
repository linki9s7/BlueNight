using System.Collections.Generic;
using System.Linq;
using BlueNight.Audio;
using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.Interaction;
using BlueNight.LightShadow;
using BlueNight.Logic;
using BlueNight.Player;
using BlueNight.Puzzle;
using BlueNight.Shadows;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using UnityEngine.Tilemaps;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// 第 2 章 追いかけっこの試作シーン（仮の絵）。`Chapter2ProtoMap` から作る。
    /// 置く・門灯を点ける・見渡す・やり直す・逃げられた演出を、遊んで確かめるためのシーン（計画 1 の Task 9）。
    /// 絵はいまある素材の使い回し：抜け道＝側溝のふた、水たまり＝月の映る水たまり、頭の上の看板＝立て看板を高く、門灯＝街灯。
    /// </summary>
    public static partial class BlueNightSetup
    {
        const string Chapter2ProtoScenePath = "Assets/001_Scenes/Ch2_Proto.unity";
        const string FlagCh2ProtoIntro = "c2p_intro";

        [MenuItem("BlueNight/8. 第 2 章 追いかけっこの試作シーンを作成", priority = 27)]
        public static void BuildChapter2ProtoScene()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                return;

            EnsureProjectConfigured();
            EnsureFolder("Assets/001_Scenes");
            EnsureFolder(TileAssetFolder);
            EnsureFolder("Assets/009_Rendering");
            AssetDatabase.ImportAsset(TexturesRoot, ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceUpdate);

            var lit = AssetDatabase.LoadAssetAtPath<Material>(SpriteLitMaterialPath);
            var unlit = AssetDatabase.LoadAssetAtPath<Material>(SpriteUnlitMaterialPath);
            var map = Chapter2ProtoMap.Create();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            Camera camera = CreateCamera();
            CreateMoonlight();
            CreateVolume();

            var root = new GameObject("Ch2 Proto Alley");
            Tilemap overlay = BuildAreaTiles(root, map, lit, unlit, indoor: false, alley: true, home: false);
            var world = new GameObject("Shadow World").AddComponent<ShadowWorld>();
            world.Configure(map.Rows, overlay, LoadTile("overlay_dark"), LoadTile("overlay_cast_shadow"));
            BuildAreaProps(root, map, lit, unlit, indoor: false);

            var props = new GameObject("Ch2 Props");
            var switches = new List<LightSwitch>();
            var exits = new List<ExitMarker>();
            var drain = LoadSprite($"{TexturesRoot}/Tiles/drain.png");
            var glow = LoadSprite($"{TexturesRoot}/Effects/fx_capture_2.png");
            for (int y = 0; y < map.Height; y++)
            {
                for (int x = 0; x < map.Width; x++)
                {
                    var cell = new Cell(x, y);
                    char ch = map.At(cell);
                    Vector3 foot = CellFoot(cell);
                    if (ch == 'o' || ch == 'e')
                    {
                        var puddle = CreateSpriteObject(props, $"Puddle {cell}", "Props/puddle_moon", new Vector3(x + 0.5f, y + 0.2f, 0f), lit);
                        puddle.GetComponent<SpriteRenderer>().sortingOrder = -95; // 地面（-100）と暗がり（-90）のあいだ
                    }
                    if (ch == 'E' || ch == 'e')
                    {
                        var marker = CreateSpriteObject(props, $"Exit {cell}", "Tiles/drain", new Vector3(x + 0.5f, y + 0.5f, 0f), unlit);
                        marker.GetComponent<SpriteRenderer>().sortingOrder = -85; // 暗がりの上：開いているかが見える
                        var exit = marker.AddComponent<ExitMarker>();
                        exit.Configure(cell, drain, drain, glow);
                        exits.Add(exit);
                    }
                    if (ch == 'l')
                        switches.Add(CreateGateLamp(props, cell, lit));
                    if (ch == 'n')
                    {
                        // 頭の上の看板：影を落とすのは足元のマス。絵は頭の高さに
                        var sign = new GameObject($"Overhead Sign {cell}");
                        Caster(sign, ch, props, foot);
                        var picture = CreateSpriteObject(sign, "Sign", "Props/a_sign", foot + new Vector3(0f, 1.6f, 0f), lit);
                        picture.transform.SetParent(sign.transform, true);
                    }
                }
            }

            PlayerController player = CreateRuri(lit, CellFoot(map.Find('P').Single()), withLanternLight: false);
            CreateLanternAndInteractor(player, unlit);
            var lantern = player.GetComponent<PlayerInteractor>().Lantern;
            lantern.SetAllowPlacing(true);
            CreateNemu(lit, player);
            player.gameObject.AddComponent<PlayerAreaSounds>();

            var shadow = CreateGrandmaShadow(map.Find('S').Single(), player.transform, null, unlit);
            shadow.name = "Runaway Shadow (Ch2 proto)";
            shadow.Configure(player.transform, null, LoadFrames($"{TexturesRoot}/Characters/Shadows/shadow_grandma_"),
                new[] { Ne("……つかまえた！", "surprised"), Ne("ちゃんと作戦、／立てたもんね") }, "c2p_captured", "c2p_returned");
            shadow.ConfigureChapter2(exits: true, wait: true, notice: Chapter2ProtoMap.NoticeDistance, pauseAtCorners: 0.35f);

            CreateAudio("ch2_rain_alley", Ambience("rain", 0.6f));
            shadow.gameObject.AddComponent<ChaseMusic>().Configure(shadow, player.transform, "ch2_rain_alley");

            var font = AssetDatabase.LoadAssetAtPath<Font>(DialogueFontPath);
            var dialogue = new GameObject("Dialogue").AddComponent<DialogueRunner>();
            dialogue.Configure(font);
            var faces = AssetDatabase.FindAssets("t:Sprite", new[] { $"{TexturesRoot}/Faces" })
                .Select(AssetDatabase.GUIDToAssetPath)
                .Select(path => AssetDatabase.LoadAssetAtPath<Sprite>(path))
                .Where(sprite => sprite != null && sprite.name.StartsWith("face_"))
                .Select(sprite => new DialogueRunner.Face { name = sprite.name.Substring("face_".Length), sprite = sprite })
                .ToArray();
            dialogue.ConfigureFaces(faces, new DialogueRunner.FaceOutfit[0]);

            new GameObject("Intro").AddComponent<AutoDialogue>().Configure(FlagCh2ProtoIntro,
                N("試作：第 2 章の追いかけっこ"),
                N("F：ランタンを置く・拾う／調べる：門灯を点ける・消す"),
                N("C：路地全体を見渡す／R：最初からやり直す"),
                Ne("抜け道をふさいでから、／近づいてね"));

            var puzzle = new GameObject("Chase Puzzle").AddComponent<ChasePuzzle>();
            puzzle.Configure(shadow, player, lantern, switches.ToArray(), exits.ToArray(),
                new[] { Ne("あっ……あそこから、逃げた", "surprised") },
                new[] { Ne("……一回、やり直す？"), Ne("R で、最初からに／もどせるよ") });
            new GameObject("Overview").AddComponent<OverviewMode>().Configure(player, font);

            var follow = camera.gameObject.AddComponent<CameraFollow2D>();
            follow.Configure(player.transform, new Rect(0f, 0f, map.Width, map.Height));

            EditorSceneManager.SaveScene(scene, Chapter2ProtoScenePath);
            AddSceneToBuildSettings(Chapter2ProtoScenePath);
            Debug.Log($"[BlueNight] {Chapter2ProtoScenePath} を作成しました。再生して、抜け道をふさいでから影を追いつめてください。");
        }

        /// <summary>点け消しできる門灯（l）。最初は消えている。調べると点く。</summary>
        static LightSwitch CreateGateLamp(GameObject parent, Cell cell, Material material)
        {
            // 門柱の上の四角い門灯（Tools/Art/ch2_proto.py）。灯りは白っぽく、ランタンの橙と見分ける
            var lamp = CreateSpriteObject(parent, $"Gate Lamp {cell}", "Props/gate_lamp_off", CellFoot(cell), material);
            var light = CreatePointLight(lamp, "Gate Light", new Vector3(0f, 1.3f, 0f), Hex("#d8ecff"), 1.0f, Chapter2ProtoMap.SmallLampRadius);
            var source = lamp.AddComponent<GridLightSource>();
            source.Configure(Chapter2ProtoMap.SmallLampRadius, light);
            source.SetHeight(Chapter2ProtoMap.SmallLampHeight);
            source.On = false;
            var sw = lamp.AddComponent<LightSwitch>();
            sw.Configure(source);
            sw.ConfigureSprites(lamp.GetComponent<SpriteRenderer>(),
                LoadSprite($"{TexturesRoot}/Props/gate_lamp_on.png"), LoadSprite($"{TexturesRoot}/Props/gate_lamp_off.png"));
            sw.SetRange(1.6f);
            sw.SetPromptOffset(new Vector2(0f, 2.0f));
            return sw;
        }
    }
}
