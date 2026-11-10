using UnityEditor;
using UnityEngine;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// Assets/006_Audio の取り込み設定。
    /// - BGM・環境音：読み込み時に展開（ループのつなぎ目をサンプル単位で正確にする）。シーンを開いただけでは読み込まず、
    ///   鳴らす直前に読み込む（MusicDirector が LoadAudioData を呼ぶ）。
    /// - 効果音：短いので、展開してすぐ鳴らせるようにしておく。
    /// </summary>
    public class BlueNightAudioImporter : AssetPostprocessor
    {
        const string Root = "Assets/006_Audio/";

        void OnPreprocessAudio()
        {
            if (!assetPath.StartsWith(Root))
                return;

            var importer = (AudioImporter)assetImporter;
            bool music = assetPath.Contains("/BGM/") || assetPath.Contains("/Ambient/");
            importer.forceToMono = false;
            importer.loadInBackground = music;

            var settings = importer.defaultSampleSettings;
#if UNITY_2022_2_OR_NEWER
            // 2022.2 から preloadAudioData は SampleSettings 側に移った（Unity なしの確認は古い参照 DLL なので下を使う）
            settings.preloadAudioData = !music;
#else
            importer.preloadAudioData = !music;
#endif
            settings.loadType = AudioClipLoadType.DecompressOnLoad;
            settings.compressionFormat = AudioCompressionFormat.Vorbis;
            settings.quality = music ? 0.8f : 0.7f;
            settings.sampleRateSetting = AudioSampleRateSetting.PreserveSampleRate;
            importer.defaultSampleSettings = settings;
        }
    }
}
