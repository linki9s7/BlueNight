using System.Collections;
using UnityEngine;
using UnityEngine.Rendering;

namespace BlueNight.Rendering
{
    /// <summary>
    /// 回想の「思い出の色」：暖かく、少し色を抜き、ふちを暗くする画面効果（Volume の重みを 0〜1 で出し入れする）。
    /// 夜の画面効果（Global Volume）より優先度が高い別の Volume に付ける。演出の台本（CutsceneStep.Memory）から使う。
    /// </summary>
    [RequireComponent(typeof(Volume))]
    public class MemoryEffect : MonoBehaviour
    {
        public static MemoryEffect Instance { get; private set; }

        Volume volume;
        Coroutine fading;

        void Awake()
        {
            Instance = this;
            volume = GetComponent<Volume>();
            volume.weight = 0f;
        }

        void OnDestroy()
        {
            if (Instance == this)
                Instance = null;
        }

        /// <summary>思い出の色の強さを seconds 秒で to（0〜1）へ。</summary>
        public void FadeTo(float to, float seconds)
        {
            if (fading != null)
                StopCoroutine(fading);
            fading = StartCoroutine(Fade(to, seconds));
        }

        IEnumerator Fade(float to, float seconds)
        {
            float from = volume.weight;
            for (float t = 0f; t < seconds; t += Time.deltaTime)
            {
                volume.weight = Mathf.Lerp(from, to, t / seconds);
                yield return null;
            }
            volume.weight = to;
            fading = null;
        }
    }
}
