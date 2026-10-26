using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace BlueNight.Rendering
{
    /// <summary>
    /// 古い街灯のような、ゆらぎとたまの瞬断。
    /// </summary>
    [RequireComponent(typeof(Light2D))]
    public class LightFlicker2D : MonoBehaviour
    {
        [SerializeField, Range(0f, 1f)] float noiseAmount = 0.12f;
        [SerializeField] float noiseSpeed = 3f;
        [SerializeField, Tooltip("1 秒あたりの瞬断の起きやすさ")] float dropoutChance = 0.08f;
        [SerializeField] float dropoutDuration = 0.08f;

        [Header("街灯の絵（任意）：明るさに合わせてガラスの色を変える")]
        [SerializeField] SpriteRenderer lampRenderer;
        [SerializeField] Sprite lampOn;
        [SerializeField] Sprite lampDim;
        [SerializeField] Sprite lampOff;

        Light2D light2D;
        float baseIntensity;
        float seed;
        float dropoutTimer;

        public void ConfigureSprites(SpriteRenderer renderer, Sprite on, Sprite dim, Sprite off)
        {
            lampRenderer = renderer;
            lampOn = on;
            lampDim = dim;
            lampOff = off;
        }

        void Awake()
        {
            light2D = GetComponent<Light2D>();
            baseIntensity = light2D.intensity;
            seed = Random.value * 100f;
        }

        void Update()
        {
            float noise = (Mathf.PerlinNoise(seed, Time.time * noiseSpeed) - 0.5f) * 2f * noiseAmount;

            if (dropoutTimer > 0f)
                dropoutTimer -= Time.deltaTime;
            else if (Random.value < dropoutChance * Time.deltaTime)
                dropoutTimer = dropoutDuration;

            float dropout = dropoutTimer > 0f ? 0.25f : 1f;
            light2D.intensity = baseIntensity * (1f + noise) * dropout;

            if (lampRenderer != null)
            {
                Sprite sprite = dropout < 1f ? lampOff : noise < -noiseAmount * 0.6f ? lampDim : lampOn;
                if (sprite != null)
                    lampRenderer.sprite = sprite;
            }
        }
    }
}
