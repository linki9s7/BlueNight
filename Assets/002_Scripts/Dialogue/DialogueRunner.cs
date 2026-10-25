using System;
using BlueNight.Core;
using BlueNight.Player;
using UnityEngine;
using UnityEngine.UI;

namespace BlueNight.Dialogue
{
    /// <summary>
    /// 画面下の会話ウィンドウ。1 文字ずつ表示し、決定ボタンで進める。
    /// UI は起動時にコードで組み立てる（480x270 基準で拡大）。
    /// </summary>
    public class DialogueRunner : MonoBehaviour
    {
        public static DialogueRunner Instance { get; private set; }

        /// <summary>会話中は true。プレイヤーの操作や調べるを止めるのに使う。</summary>
        public static bool IsBusy => Instance != null && Instance.lines != null;

        /// <summary>このフレームで会話が閉じた（同じボタン押しで次の会話が始まらないように）。</summary>
        public static bool ClosedThisFrame => Instance != null && Instance.closedFrame == Time.frameCount;

        [SerializeField] Font font;
        [SerializeField] float charactersPerSecond = 28f;
        [SerializeField] Color speakerColor = new Color(0.99f, 0.91f, 0.66f);
        [SerializeField] Color textColor = new Color(0.96f, 0.96f, 1f);
        [SerializeField] Color shadowTextColor = new Color(0.62f, 0.82f, 1f);

        DialogueLine[] lines;
        Action onComplete;
        int index;
        float shown;
        int closedFrame = -1;
        int openedFrame = -1;
        PlayerController player;

        GameObject window;
        Text speakerText;
        Text bodyText;
        Text nextMark;
        RectTransform bodyRect;
        Vector2 bodyBasePosition;

        public void Configure(Font dialogueFont) => font = dialogueFont;

        void Awake()
        {
            Instance = this;
            BuildUi();
            window.SetActive(false);
        }

        void OnDestroy()
        {
            if (Instance == this)
                Instance = null;
        }

        public void Play(DialogueLine[] dialogue, Action completed = null)
        {
            if (dialogue == null || dialogue.Length == 0)
            {
                completed?.Invoke();
                return;
            }
            if (IsBusy)
                return;

            lines = dialogue;
            onComplete = completed;
            index = 0;
            shown = 0f;
            openedFrame = Time.frameCount;
            window.SetActive(true);

            if (player == null)
                player = FindObjectOfType<PlayerController>();
            if (player != null)
                player.InputEnabled = false;

            ShowLine();
        }

        void Update()
        {
            if (lines == null)
                return;

            var line = lines[index];
            int total = line.text.Length;
            if (shown < total)
            {
                shown = Mathf.Min(total, shown + charactersPerSecond * Time.unscaledDeltaTime);
                bodyText.text = line.text.Substring(0, (int)shown);
            }

            bool done = shown >= total;
            nextMark.enabled = done && Mathf.Repeat(Time.unscaledTime, 0.8f) < 0.5f;

            // 影の声は、ことばが不安定に揺れる
            bodyRect.anchoredPosition = line.shadowVoice
                ? bodyBasePosition + new Vector2(Mathf.Round(Mathf.Sin(Time.unscaledTime * 23f)), 0f) * 0.5f
                : bodyBasePosition;

            // 会話を開いたボタン押しで 1 行目を飛ばさない
            if (Time.frameCount == openedFrame || !GameInput.ConfirmPressed)
                return;

            if (!done)
            {
                shown = total;
                bodyText.text = line.text;
                return;
            }

            index++;
            if (index < lines.Length)
                ShowLine();
            else
                Close();
        }

        void ShowLine()
        {
            var line = lines[index];
            shown = 0f;
            speakerText.text = line.speaker;
            speakerText.enabled = !string.IsNullOrEmpty(line.speaker);
            bodyText.text = string.Empty;
            bodyText.color = line.shadowVoice ? shadowTextColor : textColor;
        }

        void Close()
        {
            lines = null;
            closedFrame = Time.frameCount;
            window.SetActive(false);
            if (player != null)
                player.InputEnabled = true;

            var callback = onComplete;
            onComplete = null;
            callback?.Invoke();
        }

        // ------------------------------------------------------------------ UI

        void BuildUi()
        {
            var canvasGo = new GameObject("Dialogue Canvas");
            canvasGo.transform.SetParent(transform, false);
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 100;
            var scaler = canvasGo.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(480f, 270f);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = 1f;

            window = new GameObject("Window", typeof(RectTransform));
            window.transform.SetParent(canvasGo.transform, false);
            var windowRect = (RectTransform)window.transform;
            windowRect.anchorMin = new Vector2(0f, 0f);
            windowRect.anchorMax = new Vector2(1f, 0f);
            windowRect.pivot = new Vector2(0.5f, 0f);
            windowRect.sizeDelta = new Vector2(-24f, 64f);
            windowRect.anchoredPosition = new Vector2(0f, 8f);
            var background = window.AddComponent<Image>();
            background.color = new Color(0.03f, 0.04f, 0.1f, 0.88f);
            var outline = window.AddComponent<Outline>();
            outline.effectColor = new Color(0.62f, 0.82f, 1f, 0.6f);
            outline.effectDistance = new Vector2(1f, -1f);

            speakerText = CreateText("Speaker", window.transform, new Vector2(10f, -5f), new Vector2(-20f, 18f), speakerColor);
            bodyText = CreateText("Body", window.transform, new Vector2(10f, -23f), new Vector2(-20f, 38f), textColor);
            bodyRect = (RectTransform)bodyText.transform;
            bodyBasePosition = bodyRect.anchoredPosition;

            nextMark = CreateText("Next", window.transform, new Vector2(0f, 0f), new Vector2(16f, 16f), speakerColor);
            var markRect = (RectTransform)nextMark.transform;
            markRect.anchorMin = markRect.anchorMax = new Vector2(1f, 0f);
            markRect.pivot = new Vector2(1f, 0f);
            markRect.anchoredPosition = new Vector2(-6f, 2f);
            nextMark.text = "▼";
            nextMark.alignment = TextAnchor.LowerRight;
        }

        Text CreateText(string name, Transform parent, Vector2 position, Vector2 size, Color color)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var rect = (RectTransform)go.transform;
            rect.anchorMin = new Vector2(0f, 1f);
            rect.anchorMax = new Vector2(1f, 1f);
            rect.pivot = new Vector2(0f, 1f);
            rect.anchoredPosition = position;
            rect.sizeDelta = size;

            var text = go.AddComponent<Text>();
            text.font = font;
            text.fontSize = 16;
            text.lineSpacing = 1.05f;
            text.color = color;
            text.alignment = TextAnchor.UpperLeft;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Overflow;
            text.raycastTarget = false;
            return text;
        }
    }
}
