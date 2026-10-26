using UnityEngine;
using UnityEngine.UI;

namespace BlueNight.Rendering
{
    /// <summary>
    /// UI を「ゲーム画面と同じドットの格子」に合わせる。
    /// 拡大率を 480×270 の整数倍（Pixel Perfect Camera の Windowbox と同じ）に固定し、
    /// 中身は 480×270 の枠（Frame）の中に置く。半端な拡大率で文字のドットの大きさがばらつく（ミクセル）のを防ぐ。
    /// ポストエフェクトは UI にかけない（Overlay のまま）。
    /// </summary>
    [RequireComponent(typeof(Canvas))]
    public class PixelPerfectCanvas : MonoBehaviour
    {
        public const int ReferenceWidth = 480;
        public const int ReferenceHeight = 270;

        Canvas canvas;
        CanvasScaler scaler;
        int lastWidth, lastHeight;

        public RectTransform Frame { get; private set; }

        public static int ScaleFor(int screenWidth, int screenHeight)
        {
            return Mathf.Max(1, Mathf.Min(screenWidth / ReferenceWidth, screenHeight / ReferenceHeight));
        }

        void Awake()
        {
            canvas = GetComponent<Canvas>();
            // CanvasScaler があると毎フレーム canvas.scaleFactor を上書きするので、scaler 側に整数の拡大率を渡す
            scaler = GetComponent<CanvasScaler>();
            if (scaler != null)
                scaler.uiScaleMode = CanvasScaler.ScaleMode.ConstantPixelSize;

            var frameGo = new GameObject("Frame", typeof(RectTransform));
            frameGo.transform.SetParent(transform, false);
            Frame = (RectTransform)frameGo.transform;
            Frame.anchorMin = Frame.anchorMax = Frame.pivot = new Vector2(0.5f, 0.5f);
            Frame.sizeDelta = new Vector2(ReferenceWidth, ReferenceHeight);
            Apply();
        }

        void LateUpdate()
        {
            if (Screen.width != lastWidth || Screen.height != lastHeight)
                Apply();
        }

        void Apply()
        {
            lastWidth = Screen.width;
            lastHeight = Screen.height;
            int scale = ScaleFor(lastWidth, lastHeight);
            if (scaler != null)
                scaler.scaleFactor = scale;
            else
                canvas.scaleFactor = scale;

            // 画面の大きさと枠の差が奇数だと、枠が半ドットずれる。1 ドット単位にそろえる
            float offsetX = ((lastWidth - ReferenceWidth * scale) * 0.5f) % 1f;
            float offsetY = ((lastHeight - ReferenceHeight * scale) * 0.5f) % 1f;
            Frame.anchoredPosition = new Vector2(-offsetX, -offsetY) / scale;
        }
    }
}
