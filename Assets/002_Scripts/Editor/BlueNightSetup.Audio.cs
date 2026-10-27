using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using BlueNight.Audio;
using UnityEditor;
using UnityEngine;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// 音のデータ（AudioLibrary）を、Tools/Music が書き出した manifest（JSON）から作る。
    /// BlueNight > 5. 音のデータを作成
    /// </summary>
    public static partial class BlueNightSetup
    {
        const string AudioRoot = "Assets/006_Audio";
        const string AudioLibraryPath = "Assets/007_Data/Audio/AudioLibrary.asset";

        // ---- manifest の形（JsonUtility で読む）
        [Serializable] public class MusicManifest { public MusicJson[] tracks; }
        [Serializable] public class MusicJson { public string name; public string title; public float bpm; public int beatsPerBar; public bool loop; public LayerJson[] layers; }
        [Serializable] public class LayerJson { public string name; public string intro; public string loop; public string full; }
        [Serializable] public class AmbientManifest { public AmbientJson[] sounds; }
        [Serializable] public class AmbientJson { public string name; public string title; public string file; }
        [Serializable] public class SoundManifest { public SoundJson[] groups; }
        [Serializable] public class SoundJson { public string name; public string title; public string[] files; public bool loop; public bool randomOrder; }

        [MenuItem("BlueNight/5. 音のデータを作成", priority = 24)]
        public static void BuildAudioLibraryMenu()
        {
            var library = BuildAudioLibrary();
            Selection.activeObject = library;
            Debug.Log($"[BlueNight] {AudioLibraryPath} を作成しました（曲 {library.music.Length}・環境音 {library.ambience.Length}・効果音 {library.sounds.Length}）。");
        }

        /// <summary>音のデータを作る（既にあれば中身だけ作り直す。シーンからの参照は切れない）。</summary>
        public static AudioLibrary BuildAudioLibrary()
        {
            AssetDatabase.ImportAsset(AudioRoot, ImportAssetOptions.ImportRecursive);
            EnsureFolder("Assets/007_Data/Audio");

            var library = AssetDatabase.LoadAssetAtPath<AudioLibrary>(AudioLibraryPath);
            if (library == null)
            {
                library = ScriptableObject.CreateInstance<AudioLibrary>();
                AssetDatabase.CreateAsset(library, AudioLibraryPath);
            }

            var music = ReadJson<MusicManifest>($"{AudioRoot}/BGM/music_manifest.json");
            library.music = (music?.tracks ?? new MusicJson[0]).Select(t => new AudioLibrary.MusicTrack
            {
                name = t.name,
                title = t.title,
                bpm = t.bpm,
                beatsPerBar = t.beatsPerBar,
                loops = t.loop,
                layers = (t.layers ?? new LayerJson[0]).Select(l => new AudioLibrary.MusicLayer
                {
                    name = l.name,
                    intro = Clip($"BGM/{l.intro}"),
                    // 1 回だけの曲（スティンガー）は full を loop の欄に入れる
                    loop = Clip($"BGM/{(string.IsNullOrEmpty(l.loop) ? l.full : l.loop)}"),
                }).ToArray(),
            }).ToArray();

            var ambient = ReadJson<AmbientManifest>($"{AudioRoot}/Ambient/ambient_manifest.json");
            library.ambience = (ambient?.sounds ?? new AmbientJson[0]).Select(a => new AudioLibrary.AmbientSound
            {
                name = a.name,
                title = a.title,
                clip = Clip($"Ambient/{a.file}"),
            }).ToArray();

            var sounds = ReadJson<SoundManifest>($"{AudioRoot}/SE/se_manifest.json");
            library.sounds = (sounds?.groups ?? new SoundJson[0]).Select(g => new AudioLibrary.SoundGroup
            {
                name = g.name,
                title = g.title,
                clips = (g.files ?? new string[0]).Select(f => Clip($"SE/{f}")).Where(c => c != null).ToArray(),
                loop = g.loop,
                randomOrder = g.randomOrder,
            }).ToArray();

            EditorUtility.SetDirty(library);
            AssetDatabase.SaveAssets();
            return library;
        }

        static T ReadJson<T>(string path) where T : class
        {
            if (!File.Exists(path))
            {
                Debug.LogWarning($"[BlueNight] 見つかりません: {path}（Tools/Music の書き出しを実行してください）");
                return null;
            }
            return JsonUtility.FromJson<T>(File.ReadAllText(path));
        }

        static AudioClip Clip(string relative)
        {
            if (string.IsNullOrEmpty(relative) || relative.EndsWith("/"))
                return null;
            var clip = AssetDatabase.LoadAssetAtPath<AudioClip>($"{AudioRoot}/{relative}");
            if (clip == null)
                Debug.LogWarning($"[BlueNight] 音が見つかりません: {AudioRoot}/{relative}");
            return clip;
        }

        /// <summary>シーンに音の係（BGM・環境音・効果音）を置く。</summary>
        static void CreateAudio(string startTrack, params AmbiencePlayer.StartSound[] ambience)
        {
            var library = BuildAudioLibrary();
            var go = new GameObject("Audio");
            go.AddComponent<MusicDirector>().Configure(library, startTrack);
            go.AddComponent<AmbiencePlayer>().Configure(library, ambience);
            go.AddComponent<SoundEffects>().Configure(library);
        }

        static AmbiencePlayer.StartSound Ambience(string name, float volume) =>
            new AmbiencePlayer.StartSound { name = name, volume = volume };
    }
}
