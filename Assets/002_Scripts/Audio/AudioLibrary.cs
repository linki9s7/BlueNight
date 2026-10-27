using System;
using System.Linq;
using UnityEngine;

namespace BlueNight.Audio
{
    /// <summary>
    /// 曲・環境音・効果音の一覧。Tools/Music の書き出し（*_manifest.json）から、
    /// エディタのメニュー「BlueNight > 5. 音のデータを作成」で作る。
    /// </summary>
    [CreateAssetMenu(menuName = "BlueNight/Audio Library")]
    public class AudioLibrary : ScriptableObject
    {
        [Serializable]
        public class MusicLayer
        {
            public string name;
            [Tooltip("前奏（無い曲もある）")] public AudioClip intro;
            [Tooltip("くり返す部分。スティンガーなど 1 回だけの曲はここに全体を入れる")] public AudioClip loop;
        }

        [Serializable]
        public class MusicTrack
        {
            public string name;
            public string title;
            public float bpm = 80f;
            public int beatsPerBar = 4;
            public bool loops = true;
            public MusicLayer[] layers = Array.Empty<MusicLayer>();

            public float BarSeconds => bpm > 0f ? 60f / bpm * beatsPerBar : 2f;
        }

        [Serializable]
        public class AmbientSound
        {
            public string name;
            public string title;
            public AudioClip clip;
        }

        [Serializable]
        public class SoundGroup
        {
            public string name;
            public string title;
            public AudioClip[] clips = Array.Empty<AudioClip>();
            public bool loop;
            public bool randomOrder = true;
        }

        public MusicTrack[] music = Array.Empty<MusicTrack>();
        public AmbientSound[] ambience = Array.Empty<AmbientSound>();
        public SoundGroup[] sounds = Array.Empty<SoundGroup>();

        public MusicTrack FindMusic(string name) => music.FirstOrDefault(t => t.name == name);
        public AmbientSound FindAmbience(string name) => ambience.FirstOrDefault(a => a.name == name);
        public SoundGroup FindSound(string name) => sounds.FirstOrDefault(s => s.name == name);
    }
}
