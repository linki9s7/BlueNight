using UnityEngine;

namespace BlueNight.Audio
{
    /// <summary>音量の設定（BGM・環境音・効果音、0〜10）。PlayerPrefs に保存し、起動時に読み込む。</summary>
    public static class AudioPrefs
    {
        public const int Steps = 10;
        static bool loaded;

        public static int Music { get; private set; } = 8;
        public static int Ambience { get; private set; } = 8;
        public static int Effects { get; private set; } = 8;

        public static void Load()
        {
            if (loaded)
                return;
            loaded = true;
            Music = PlayerPrefs.GetInt("volume_music", 8);
            Ambience = PlayerPrefs.GetInt("volume_ambience", 8);
            Effects = PlayerPrefs.GetInt("volume_effects", 8);
            Apply();
        }

        public static void Set(int music, int ambience, int effects)
        {
            Music = Mathf.Clamp(music, 0, Steps);
            Ambience = Mathf.Clamp(ambience, 0, Steps);
            Effects = Mathf.Clamp(effects, 0, Steps);
            PlayerPrefs.SetInt("volume_music", Music);
            PlayerPrefs.SetInt("volume_ambience", Ambience);
            PlayerPrefs.SetInt("volume_effects", Effects);
            PlayerPrefs.Save();
            Apply();
        }

        // 人の耳に自然に聞こえるよう、目盛りは音量の 2 乗にする
        static float Scale(int step) => Mathf.Pow(step / (float)Steps, 2f);

        static void Apply()
        {
            MusicDirector.VolumeScale = Scale(Music) / Scale(8);
            AmbiencePlayer.VolumeScale = Scale(Ambience) / Scale(8);
            SoundEffects.VolumeScale = Scale(Effects) / Scale(8);
        }
    }
}
