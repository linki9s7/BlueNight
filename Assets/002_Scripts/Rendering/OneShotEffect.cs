using System;
using UnityEngine;

namespace BlueNight.Rendering
{
    /// <summary>コマを 1 回だけ再生して消える演出（影を捕まえた光、影が戻る光のつぶなど）。</summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class OneShotEffect : MonoBehaviour
    {
        [SerializeField] Sprite[] frames = Array.Empty<Sprite>();
        [SerializeField] float fps = 12f;
        [SerializeField, Tooltip("オンなら最後まで再生したら最初から繰り返す（素材を並べたシーンでの確認用）")] bool loop;

        SpriteRenderer spriteRenderer;
        float time;

        /// <summary>position に演出を 1 回出す。</summary>
        public static OneShotEffect Spawn(Sprite[] effectFrames, Vector3 position, float framesPerSecond, Material material, int sortingOrder = 30)
        {
            if (effectFrames == null || effectFrames.Length == 0)
                return null;
            var go = new GameObject("Effect");
            go.transform.position = position;
            var renderer = go.AddComponent<SpriteRenderer>();
            renderer.sortingOrder = sortingOrder;
            if (material != null)
                renderer.sharedMaterial = material;
            var effect = go.AddComponent<OneShotEffect>();
            effect.Configure(effectFrames, framesPerSecond, false);
            return effect;
        }

        public void Configure(Sprite[] effectFrames, float framesPerSecond, bool repeat)
        {
            frames = effectFrames;
            fps = framesPerSecond;
            loop = repeat;
        }

        void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
        }

        void Update()
        {
            if (frames.Length == 0)
                return;
            time += Time.deltaTime;
            int index = (int)(time * fps);
            if (index >= frames.Length)
            {
                if (!loop)
                {
                    Destroy(gameObject);
                    return;
                }
                index %= frames.Length;
            }
            spriteRenderer.sprite = frames[index];
        }
    }
}
