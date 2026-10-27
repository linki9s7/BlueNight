using System.Collections.Generic;
using BlueNight.Dialogue;
using UnityEngine;

namespace BlueNight.Audio
{
    /// <summary>
    /// BGM の再生（仕様書 8.3）。
    /// - 前奏 → ループを PlayScheduled でつなぐ（すき間なし）。
    /// - 曲の入れ替えは等パワーのフェード。エリア移動は「フェードアウト → 間 → フェードイン」、似た曲はクロスフェード。
    /// - 層のある曲（影を追う）は、全部の層を同時に鳴らし、層ごとの音量を出し入れする（曲は切り替えない）。
    /// - 会話中は約 -4 dB 下げる（0.5 秒）、終わったら 1 秒で戻す。
    /// - 時間はゲームの一時停止に左右されない unscaledDeltaTime で進める。
    /// </summary>
    public class MusicDirector : MonoBehaviour
    {
        public static MusicDirector Instance { get; private set; }

        [SerializeField] AudioLibrary library;
        [SerializeField, Range(0f, 1f)] float volume = 0.8f;
        [SerializeField] float dialogueDuckDb = -4f;
        [SerializeField, Tooltip("シーンが始まったときに流す曲（空なら流さない）")] string startTrack;
        [SerializeField] float startFadeIn = 2f;

        class Layer
        {
            public string name;
            public AudioSource intro;
            public AudioSource loop;
            public AudioFade fade;
        }

        class Deck
        {
            public AudioLibrary.MusicTrack track;
            public readonly List<Layer> layers = new List<Layer>();
            public AudioFade fade;
            public double startDsp;
            public GameObject root;
        }

        Deck current;
        readonly List<Deck> leaving = new List<Deck>();
        AudioSource stingerSource;
        AudioFade duck = new AudioFade(0f);

        public static float VolumeScale = 1f;   // 設定画面の「BGM の音量」
        public string CurrentTrack => current?.track.name;
        public AudioLibrary Library => library;

        public void Configure(AudioLibrary audioLibrary, string trackOnStart)
        {
            library = audioLibrary;
            startTrack = trackOnStart;
        }

        void Awake()
        {
            Instance = this;
            AudioPrefs.Load();
            stingerSource = gameObject.AddComponent<AudioSource>();
            stingerSource.playOnAwake = false;
        }

        void OnDestroy()
        {
            if (Instance == this)
                Instance = null;
        }

        void Start()
        {
            if (!string.IsNullOrEmpty(startTrack))
                Play(startTrack, 0f, 0f, startFadeIn);
        }

        // ------------------------------------------------------------------ 操作

        /// <summary>
        /// 曲を変える。いまの曲を fadeOut 秒で消し、gap 秒おいて fadeIn 秒で入れる（gap を 0 にするとクロスフェード）。
        /// layersOn で最初に鳴らす層を選べる（null ならすべて）。同じ曲なら何もしない。
        /// </summary>
        public void Play(string trackName, float fadeOut = 2.5f, float gap = 0.5f, float fadeIn = 2f, params string[] layersOn)
        {
            if (library == null || CurrentTrack == trackName)
                return;
            var track = library.FindMusic(trackName);
            if (track == null)
            {
                Debug.LogWarning($"[BlueNight] 曲が見つかりません: {trackName}");
                return;
            }

            if (current != null)
            {
                current.fade.To(0f, fadeOut);
                leaving.Add(current);
            }
            current = CreateDeck(track, AudioSettings.dspTime + 0.1 + gap, layersOn);
            current.fade = new AudioFade(0f);
            current.fade.To(1f, fadeIn);
            // 間（gap）のあいだは音量 0 のまま待つ
            if (gap > 0f)
                StartCoroutine(DelayFade(current, gap, fadeIn));
        }

        /// <summary>クロスフェードで曲を変える（影を捕まえて「影の言葉」へ、など）。</summary>
        public void CrossFade(string trackName, float seconds, params string[] layersOn) =>
            Play(trackName, seconds, 0f, seconds, layersOn);

        /// <summary>いまの曲の層を出し入れする（影を追う曲の太鼓・弦など）。</summary>
        public void SetLayer(string layerName, bool on, float seconds = 1.5f)
        {
            if (current == null)
                return;
            foreach (var layer in current.layers)
                if (layer.name == layerName && !Mathf.Approximately(layer.fade.Target, on ? 1f : 0f))
                    layer.fade.To(on ? 1f : 0f, seconds);
        }

        public bool IsLayerOn(string layerName)
        {
            if (current == null)
                return false;
            foreach (var layer in current.layers)
                if (layer.name == layerName)
                    return layer.fade.Target > 0f;
            return false;
        }

        /// <summary>短いフレーズ（スティンガー）を 1 回鳴らす。曲の上に重なる。</summary>
        public void PlayStinger(string trackName)
        {
            var track = library != null ? library.FindMusic(trackName) : null;
            if (track == null || track.layers.Length == 0 || track.layers[0].loop == null)
                return;
            stingerSource.volume = volume * VolumeScale;
            stingerSource.PlayOneShot(track.layers[0].loop);
        }

        public void Stop(float fadeOut = 2.5f)
        {
            if (current == null)
                return;
            current.fade.To(0f, fadeOut);
            leaving.Add(current);
            current = null;
        }

        // ------------------------------------------------------------------ 内部

        System.Collections.IEnumerator DelayFade(Deck deck, float gap, float fadeIn)
        {
            deck.fade.To(0f, 0f);
            yield return new WaitForSecondsRealtime(gap);
            deck.fade.To(1f, fadeIn);
        }

        Deck CreateDeck(AudioLibrary.MusicTrack track, double startDsp, string[] layersOn)
        {
            var deck = new Deck { track = track, startDsp = startDsp, root = new GameObject($"Music: {track.name}") };
            deck.root.transform.SetParent(transform, false);
            bool allOn = layersOn == null || layersOn.Length == 0;

            foreach (var source in track.layers)
            {
                var layer = new Layer { name = source.name };
                bool on = allOn || System.Array.IndexOf(layersOn, source.name) >= 0;
                layer.fade = new AudioFade(on ? 1f : 0f);

                double loopStart = startDsp;
                if (source.intro != null)
                {
                    source.intro.LoadAudioData();
                    layer.intro = NewSource(deck.root, source.intro, false);
                    layer.intro.PlayScheduled(startDsp);
                    loopStart = startDsp + (double)source.intro.samples / source.intro.frequency;
                }
                if (source.loop != null)
                {
                    source.loop.LoadAudioData();
                    layer.loop = NewSource(deck.root, source.loop, track.loops);
                    layer.loop.PlayScheduled(loopStart);
                }
                deck.layers.Add(layer);
            }
            return deck;
        }

        static AudioSource NewSource(GameObject parent, AudioClip clip, bool loop)
        {
            var source = parent.AddComponent<AudioSource>();
            source.clip = clip;
            source.loop = loop;
            source.playOnAwake = false;
            source.volume = 0f;
            source.spatialBlend = 0f;
            return source;
        }

        void Update()
        {
            float dt = Time.unscaledDeltaTime;

            // 会話中は少し下げる（0.5 秒で下げ、1 秒で戻す）
            bool talking = DialogueRunner.IsBusy;
            if (talking && duck.Target < 1f) duck.To(1f, 0.5f);
            if (!talking && duck.Target > 0f) duck.To(0f, 1f);
            duck.Step(dt);
            float duckGain = AudioFade.DbToGain(dialogueDuckDb * duck.Level);

            if (current != null)
                Apply(current, dt, duckGain);
            for (int i = leaving.Count - 1; i >= 0; i--)
            {
                Apply(leaving[i], dt, duckGain);
                if (leaving[i].fade.IsSilent)
                {
                    Destroy(leaving[i].root);
                    leaving.RemoveAt(i);
                }
            }
        }

        void Apply(Deck deck, float dt, float duckGain)
        {
            deck.fade.Step(dt);
            float deckGain = deck.fade.Gain * duckGain * volume * VolumeScale;
            foreach (var layer in deck.layers)
            {
                layer.fade.Step(dt);
                float gain = deckGain * layer.fade.Gain;
                if (layer.intro != null) layer.intro.volume = gain;
                if (layer.loop != null) layer.loop.volume = gain;
            }
        }
    }
}
