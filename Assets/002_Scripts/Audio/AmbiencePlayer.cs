using System.Collections.Generic;
using UnityEngine;

namespace BlueNight.Audio
{
    /// <summary>
    /// 環境音（虫・遠くのハイウェイ・雨・波）。いくつでも重ねて鳴らせ、それぞれゆっくり出し入れする。
    /// 屋内に入ると、こもらせて（ローパス）音量を下げる（仕様書 8.3）。
    /// </summary>
    public class AmbiencePlayer : MonoBehaviour
    {
        public static AmbiencePlayer Instance { get; private set; }

        [System.Serializable]
        public class StartSound
        {
            public string name;
            [Range(0f, 1f)] public float volume = 0.6f;
        }

        [SerializeField] AudioLibrary library;
        [SerializeField, Range(0f, 1f)] float volume = 0.8f;
        [SerializeField] StartSound[] startSounds = new StartSound[0];
        [SerializeField] float indoorCutoff = 1200f;
        [SerializeField] float indoorDb = -8f;

        class Bed
        {
            public AudioSource source;
            public AudioLowPassFilter filter;
            public AudioFade fade;
            public float volume;
        }

        readonly Dictionary<string, Bed> beds = new Dictionary<string, Bed>();
        AudioFade indoor = new AudioFade(0f);

        public static float VolumeScale = 1f;   // 設定画面の「環境音の音量」

        public void Configure(AudioLibrary audioLibrary, params StartSound[] sounds)
        {
            library = audioLibrary;
            startSounds = sounds;
        }

        void Awake() => Instance = this;

        void OnDestroy()
        {
            if (Instance == this)
                Instance = null;
        }

        void Start()
        {
            foreach (var s in startSounds)
                Set(s.name, s.volume, 3f);
        }

        /// <summary>環境音を volume まで seconds 秒で上げる（0 なら消す）。</summary>
        public void Set(string soundName, float soundVolume, float seconds = 3f)
        {
            if (!beds.TryGetValue(soundName, out var bed))
            {
                var sound = library != null ? library.FindAmbience(soundName) : null;
                if (sound == null || sound.clip == null)
                {
                    Debug.LogWarning($"[BlueNight] 環境音が見つかりません: {soundName}");
                    return;
                }
                var go = new GameObject($"Ambience: {soundName}");
                go.transform.SetParent(transform, false);
                sound.clip.LoadAudioData();
                var source = go.AddComponent<AudioSource>();
                source.clip = sound.clip;
                source.loop = true;
                source.volume = 0f;
                source.playOnAwake = false;
                // 同じ環境音を何度鳴らし始めても、いつも同じ所から始まらないように
                source.timeSamples = Random.Range(0, Mathf.Max(1, sound.clip.samples - 1));
                source.Play();
                bed = new Bed { source = source, filter = go.AddComponent<AudioLowPassFilter>(), fade = new AudioFade(0f) };
                bed.filter.cutoffFrequency = 22000f;
                beds[soundName] = bed;
            }
            if (soundVolume > 0f)
                bed.volume = soundVolume;
            bed.fade.To(soundVolume > 0f ? 1f : 0f, seconds);
        }

        /// <summary>屋内（こもった音）にする／戻す。</summary>
        public void SetIndoor(bool inside, float seconds = 1f) => indoor.To(inside ? 1f : 0f, seconds);

        void Update()
        {
            float dt = Time.unscaledDeltaTime;
            indoor.Step(dt);
            float cutoff = Mathf.Lerp(22000f, indoorCutoff, indoor.Level);
            float indoorGain = AudioFade.DbToGain(indoorDb * indoor.Level);
            foreach (var bed in beds.Values)
            {
                bed.fade.Step(dt);
                bed.source.volume = bed.fade.Gain * bed.volume * volume * VolumeScale * indoorGain;
                bed.filter.cutoffFrequency = cutoff;
            }
        }
    }
}
