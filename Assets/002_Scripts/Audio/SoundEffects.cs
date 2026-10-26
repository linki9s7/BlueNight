using System.Collections.Generic;
using UnityEngine;

namespace BlueNight.Audio
{
    /// <summary>
    /// 効果音。名前（se_manifest.json のグループ名）で鳴らす。
    /// 同じグループでは前回と違うファイルを選び、音の高さもほんの少しゆらして、くり返しの機械っぽさを消す。
    /// </summary>
    public class SoundEffects : MonoBehaviour
    {
        public static SoundEffects Instance { get; private set; }

        [SerializeField] AudioLibrary library;
        [SerializeField, Range(0f, 1f)] float volume = 0.9f;
        [SerializeField] int voices = 10;

        readonly List<AudioSource> pool = new List<AudioSource>();
        readonly Dictionary<string, int> lastIndex = new Dictionary<string, int>();
        int next;

        public static float VolumeScale = 1f;   // 設定画面の「効果音の音量」

        public void Configure(AudioLibrary audioLibrary) => library = audioLibrary;

        void Awake()
        {
            Instance = this;
            for (int i = 0; i < voices; i++)
            {
                var source = gameObject.AddComponent<AudioSource>();
                source.playOnAwake = false;
                pool.Add(source);
            }
        }

        void OnDestroy()
        {
            if (Instance == this)
                Instance = null;
        }

        /// <summary>効果音を 1 回鳴らす（シーンに SoundEffects が無ければ何もしない）。</summary>
        public static void Play(string group, float soundVolume = 1f, float pitchJitter = 0.03f)
        {
            if (Instance != null)
                Instance.PlayInternal(group, soundVolume, pitchJitter);
        }

        /// <summary>くり返し鳴らす音（影の気配など）。音量は呼んだ側で動かす。</summary>
        public static AudioSource CreateLoop(string group, Transform parent)
        {
            if (Instance == null)
                return null;
            var clip = Instance.Pick(group);
            if (clip == null)
                return null;
            var source = parent.gameObject.AddComponent<AudioSource>();
            source.clip = clip;
            source.loop = true;
            source.volume = 0f;
            source.playOnAwake = false;
            source.Play();
            return source;
        }

        public static float LoopVolume(float soundVolume) => Instance != null ? Instance.volume * VolumeScale * soundVolume : 0f;

        void PlayInternal(string group, float soundVolume, float pitchJitter)
        {
            var clip = Pick(group);
            if (clip == null)
                return;
            var source = pool[next];
            next = (next + 1) % pool.Count;
            source.pitch = 1f + Random.Range(-pitchJitter, pitchJitter);
            source.PlayOneShot(clip, volume * VolumeScale * soundVolume);
        }

        AudioClip Pick(string group)
        {
            var sound = library != null ? library.FindSound(group) : null;
            if (sound == null || sound.clips.Length == 0)
            {
                Debug.LogWarning($"[BlueNight] 効果音が見つかりません: {group}");
                return null;
            }
            int index = 0;
            if (sound.clips.Length > 1)
            {
                lastIndex.TryGetValue(group, out int last);
                index = Random.Range(0, sound.clips.Length - 1);
                if (index >= last)
                    index++;  // 前回と同じファイルを続けて選ばない
                lastIndex[group] = index;
            }
            return sound.clips[index];
        }
    }
}
