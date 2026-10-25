using System;
using UnityEngine;

namespace BlueNight.Rendering
{
    /// <summary>コマを順番に切り替えるだけのアニメーション（NPC の待機など）。</summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class SimpleSpriteAnimator : MonoBehaviour
    {
        [SerializeField] Sprite[] frames = Array.Empty<Sprite>();
        [SerializeField] float fps = 2f;
        [SerializeField, Tooltip("開始タイミングをずらして、同じ NPC がそろって動かないようにする")] bool randomOffset = true;

        SpriteRenderer spriteRenderer;
        float time;

        public void Configure(Sprite[] animationFrames, float framesPerSecond)
        {
            frames = animationFrames;
            fps = framesPerSecond;
        }

        void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            if (randomOffset)
                time = UnityEngine.Random.value * 10f;
        }

        void Update()
        {
            if (frames.Length == 0)
                return;
            time += Time.deltaTime;
            spriteRenderer.sprite = frames[(int)(time * fps) % frames.Length];
        }
    }
}
