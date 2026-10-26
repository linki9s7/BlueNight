using System.Collections;
using UnityEngine;
using UnityEngine.UI;

namespace BlueNight.Core
{
    /// <summary>画面の暗転（エリアの移動・章の切り替わり・演出）。一時停止に左右されない時間で動く。</summary>
    public class ScreenFader : MonoBehaviour
    {
        public static ScreenFader Instance { get; private set; }

        Image cover;
        float alpha;

        public bool IsDark => alpha >= 1f;

        /// <summary>シーンに無ければ作る。</summary>
        public static ScreenFader Get()
        {
            if (Instance != null)
                return Instance;
            return new GameObject("Screen Fader").AddComponent<ScreenFader>();
        }

        void Awake()
        {
            Instance = this;
            var canvas = gameObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 1000;
            var go = new GameObject("Cover", typeof(RectTransform));
            go.transform.SetParent(transform, false);
            var rect = (RectTransform)go.transform;
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.offsetMin = rect.offsetMax = Vector2.zero;
            cover = go.AddComponent<Image>();
            cover.color = new Color(0.02f, 0.02f, 0.05f, 0f);
            cover.raycastTarget = false;
        }

        void OnDestroy()
        {
            if (Instance == this)
                Instance = null;
        }

        public void SetDark(bool dark) => Set(dark ? 1f : 0f);

        public IEnumerator FadeOut(float seconds) => FadeTo(1f, seconds);
        public IEnumerator FadeIn(float seconds) => FadeTo(0f, seconds);

        IEnumerator FadeTo(float target, float seconds)
        {
            float start = alpha;
            for (float t = 0f; t < seconds; t += Time.unscaledDeltaTime)
            {
                Set(Mathf.Lerp(start, target, Mathf.SmoothStep(0f, 1f, t / seconds)));
                yield return null;
            }
            Set(target);
        }

        void Set(float value)
        {
            alpha = value;
            var c = cover.color;
            c.a = value;
            cover.color = c;
        }
    }
}
