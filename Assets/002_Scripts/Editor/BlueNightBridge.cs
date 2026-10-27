using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// 開いている Unity エディタを、外（Claude Code など）から動かすための小さな窓口。
    /// Temp/BlueNightBridge/request.json に命令を書くと、エディタが実行して response.json に結果を書く。
    /// Unity 6 の公式の窓口（com.unity.pipeline）が 2022.3 では使えないための代わり。Temp の中だけを使い、外へは何も送らない。
    ///
    /// 命令（command）：
    ///   refresh                ファイルの変更を取り込む（スクリプトならコンパイル）
    ///   build                  arg = gallery / m1 / title：メニュー 4・3・6 のシーンを作る
    ///   open                   arg = シーンのパス
    ///   play / stop            再生・停止
    ///   capture                Main Camera の絵を PNG に（arg = 保存先。scale 倍に拡大）
    ///   move                   再生中のルリを (x, y) へ動かす（素材シーンを見て回る）
    ///   face                   再生中のルリの向き（arg = down / up / left / right）
    ///   invoke                 arg = 「名前空間.型.メソッド」の static メソッドを引数なしで呼ぶ
    ///   logs                   最近の警告・エラー
    /// </summary>
    [InitializeOnLoad]
    static class BlueNightBridge
    {
        const string Folder = "Temp/BlueNightBridge";
        static readonly string RequestPath = Path.Combine(Folder, "request.json");
        static readonly string ResponsePath = Path.Combine(Folder, "response.json");
        static readonly List<string> Logs = new List<string>();
        static double nextPoll;

        [Serializable]
        class Request
        {
            public string id = "";
            public string command = "";
            public string arg = "";
            public float x;
            public float y;
            public int scale = 2;
        }

        [Serializable]
        class Response
        {
            public string id;
            public bool ok;
            public string message;
            public bool playing;
            public string scene;
        }

        static BlueNightBridge()
        {
            Directory.CreateDirectory(Folder);
            EditorApplication.update += Poll;
            Application.logMessageReceived += (text, stack, type) =>
            {
                if (type == LogType.Log)
                    return;
                Logs.Add($"[{type}] {text}");
                if (Logs.Count > 60)
                    Logs.RemoveAt(0);
            };
        }

        static void Poll()
        {
            if (EditorApplication.timeSinceStartup < nextPoll)
                return;
            nextPoll = EditorApplication.timeSinceStartup + 0.25;
            if (!File.Exists(RequestPath))
                return;

            Request request;
            try
            {
                request = JsonUtility.FromJson<Request>(File.ReadAllText(RequestPath));
                File.Delete(RequestPath);
            }
            catch (IOException)
            {
                return; // 書き込みの途中。次の回に読む
            }

            var response = new Response { id = request.id };
            try
            {
                response.message = Run(request);
                response.ok = true;
            }
            catch (Exception e)
            {
                response.message = e.ToString();
            }
            response.playing = EditorApplication.isPlaying;
            response.scene = EditorSceneManager.GetActiveScene().path;
            File.WriteAllText(ResponsePath, JsonUtility.ToJson(response, true));
        }

        static string Run(Request r)
        {
            switch (r.command)
            {
                case "refresh":
                    AssetDatabase.Refresh();
                    return "refreshed";
                case "build":
                    StopPlaying();
                    switch (r.arg)
                    {
                        case "gallery": BlueNightSetup.BuildArtGalleryScene(); break;
                        case "m1": BlueNightSetup.BuildM1Scene(); break;
                        case "title": BlueNightSetup.BuildTitleScene(); break;
                        default: throw new ArgumentException($"unknown scene: {r.arg}");
                    }
                    return $"built {r.arg}";
                case "open":
                    StopPlaying();
                    EditorSceneManager.OpenScene(r.arg);
                    return $"opened {r.arg}";
                case "play":
                    Application.runInBackground = true; // エディタが裏にあっても止まらないように
                    EditorApplication.isPlaying = true;
                    return "entering play mode";
                case "stop":
                    EditorApplication.isPlaying = false;
                    return "stopping";
                case "capture":
                    return Capture(string.IsNullOrEmpty(r.arg) ? Path.Combine(Folder, "capture.png") : r.arg, Mathf.Max(1, r.scale));
                case "move":
                    return MovePlayer(new Vector2(r.x, r.y));
                case "face":
                    return Face(r.arg);
                case "invoke":
                    return Invoke(r.arg);
                case "logs":
                    var text = string.Join("\n", Logs);
                    Logs.Clear();
                    return text;
                default:
                    throw new ArgumentException($"unknown command: {r.command}");
            }
        }

        static void StopPlaying()
        {
            if (EditorApplication.isPlaying)
                throw new InvalidOperationException("再生中は実行できません。先に stop してください。");
        }

        /// <summary>Main Camera を 480x270 のまま描いて、scale 倍（最近傍）で保存する。</summary>
        static string Capture(string path, int scale)
        {
            var camera = Camera.main;
            if (camera == null)
                throw new InvalidOperationException("Main Camera がありません。");
            var rt = RenderTexture.GetTemporary(480, 270, 24, RenderTextureFormat.ARGB32);
            var previousTarget = camera.targetTexture;
            var previousActive = RenderTexture.active;
            try
            {
                camera.targetTexture = rt;
                camera.Render();
                RenderTexture.active = rt;
                var small = new Texture2D(480, 270, TextureFormat.RGBA32, false);
                small.ReadPixels(new Rect(0, 0, 480, 270), 0, 0);
                small.Apply();
                var src = small.GetPixels32();
                var big = new Texture2D(480 * scale, 270 * scale, TextureFormat.RGBA32, false);
                var dst = new Color32[480 * scale * 270 * scale];
                for (int y = 0; y < 270 * scale; y++)
                    for (int x = 0; x < 480 * scale; x++)
                    {
                        var c = src[(y / scale) * 480 + x / scale];
                        c.a = 255;
                        dst[y * 480 * scale + x] = c;
                    }
                big.SetPixels32(dst);
                Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path)));
                File.WriteAllBytes(path, big.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(small);
                UnityEngine.Object.DestroyImmediate(big);
                return Path.GetFullPath(path);
            }
            finally
            {
                camera.targetTexture = previousTarget;
                RenderTexture.active = previousActive;
                RenderTexture.ReleaseTemporary(rt);
            }
        }

        static BlueNight.Player.PlayerController Player()
        {
            if (!EditorApplication.isPlaying)
                throw new InvalidOperationException("再生中にだけ使えます。");
            var player = UnityEngine.Object.FindObjectOfType<BlueNight.Player.PlayerController>();
            if (player == null)
                throw new InvalidOperationException("ルリが見つかりません。");
            return player;
        }

        static string MovePlayer(Vector2 to)
        {
            var player = Player();
            var body = player.GetComponent<Rigidbody2D>();
            if (body != null)
                body.position = to;
            player.transform.position = to;
            foreach (var nemu in UnityEngine.Object.FindObjectsOfType<BlueNight.Player.NemuFollower>())
                nemu.SnapToTarget();
            var follow = UnityEngine.Object.FindObjectOfType<BlueNight.Core.CameraFollow2D>();
            if (follow != null)
                follow.transform.position = new Vector3(to.x, to.y, follow.transform.position.z);
            return $"moved to {to}";
        }

        static string Face(string direction)
        {
            var player = Player();
            var facing = (BlueNight.Player.Facing)Enum.Parse(typeof(BlueNight.Player.Facing), direction, true);
            player.Face(facing);
            return $"facing {facing}";
        }

        static string Invoke(string fullName)
        {
            int dot = fullName.LastIndexOf('.');
            string typeName = fullName.Substring(0, dot), methodName = fullName.Substring(dot + 1);
            var type = AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType(typeName)).FirstOrDefault(t => t != null)
                ?? throw new ArgumentException($"type not found: {typeName}");
            var method = type.GetMethod(methodName, BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic, null, Type.EmptyTypes, null)
                ?? throw new ArgumentException($"method not found: {methodName}");
            return Convert.ToString(method.Invoke(null, null)) ?? "done";
        }
    }
}
