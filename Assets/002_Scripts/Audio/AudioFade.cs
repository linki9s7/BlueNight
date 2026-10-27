using UnityEngine;

namespace BlueNight.Audio
{
    /// <summary>
    /// 音量の出し入れ。0〜1 の「量」を一定の速さで動かし、実際の音量は等パワーの曲線（sin）にする。
    /// 2 つの音を同時に入れ替えても、まん中で音が痩せない（仕様書 8.3）。
    /// </summary>
    public struct AudioFade
    {
        float level;
        float target;
        float speed;

        public float Level => level;
        public float Target => target;
        public bool IsSilent => level <= 0f && target <= 0f;

        public AudioFade(float start)
        {
            level = start;
            target = start;
            speed = 0f;
        }

        /// <summary>seconds 秒かけて目標の量へ（0 秒ならすぐに）。</summary>
        public void To(float goal, float seconds)
        {
            target = Mathf.Clamp01(goal);
            speed = seconds > 0f ? 1f / seconds : float.PositiveInfinity;
        }

        public void Step(float deltaTime)
        {
            level = Mathf.MoveTowards(level, target, speed * deltaTime);
        }

        /// <summary>等パワーの曲線で、音量（0〜1）にする。</summary>
        public float Gain => Mathf.Sin(level * Mathf.PI * 0.5f);

        public static float DbToGain(float db) => Mathf.Pow(10f, db / 20f);
    }
}
