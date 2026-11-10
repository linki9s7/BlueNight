using System;
using BlueNight.Audio;
using BlueNight.Core;
using BlueNight.Player;
using BlueNight.Rendering;
using UnityEngine;
using UnityEngine.UI;

namespace BlueNight.Dialogue
{
    /// <summary>
    /// 画面下の会話ウィンドウ。1 文字ずつ表示し、決定ボタンで進める。
    /// UI は起動時にコードで組み立てる（480x270 基準で拡大）。
    /// 話し手の顔グラフィック（48x48）をウィンドウの左に出す（ユーザーの希望：名前だけでは一目で分かりにくい）。
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
        [SerializeField, Tooltip("顔グラフィック（名前 → 絵）")] Face[] faces = Array.Empty<Face>();
        [SerializeField, Tooltip("服で顔を替える（序章のパジャマ・マフラー無し）。上から順に、untilFlag が立つまで使う")]
        FaceOutfit[] outfits = Array.Empty<FaceOutfit>();

        [Serializable]
        public class Face
        {
            public string name;
            public Sprite sprite;
        }

        /// <summary>prefix で始まる顔を、untilFlag が立つまで replacement で始まる顔に替える（例：ruri_ → ruri_pajama_）。替えの絵が無ければそのまま。</summary>
        [Serializable]
        public class FaceOutfit
        {
            public string prefix;
            public string untilFlag;
            public string replacement;
        }

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
        Image faceImage;
        RectTransform speakerRect;
        RectTransform bodyRect;
        Vector2 bodyBasePosition;

        // 本文の位置（ウィンドウの左上から、480x270 のドット）。名前があるときは名前の欄の下、無いときは上から
        static readonly Vector2 BodyWithSpeaker = new Vector2(10f, -21f);
        static readonly Vector2 BodyWithoutSpeaker = new Vector2(10f, -8f);

        // 顔グラフィック（48x48）はウィンドウの左、上下の真ん中。顔があるときは、名前と本文をその右から書く
        const float FaceSize = 48f;
        const float FaceLeft = 8f;
        const float TextLeftWithFace = FaceLeft + FaceSize + 8f;

        public void Configure(Font dialogueFont) => font = dialogueFont;

        public void ConfigureFaces(Face[] faceSprites, FaceOutfit[] outfitRules)
        {
            faces = faceSprites ?? Array.Empty<Face>();
            outfits = outfitRules ?? Array.Empty<FaceOutfit>();
        }

        Sprite FindFace(string name)
        {
            if (string.IsNullOrEmpty(name))
                return null;
            foreach (var rule in outfits)
            {
                if (string.IsNullOrEmpty(rule.prefix) || !name.StartsWith(rule.prefix)
                    || string.IsNullOrEmpty(rule.untilFlag) || GameFlags.Has(rule.untilFlag))
                    continue;
                var dressed = FaceNamed(rule.replacement + name.Substring(rule.prefix.Length));
                if (dressed != null)
                    return dressed;
            }
            return FaceNamed(name);
        }

        Sprite FaceNamed(string name)
        {
            foreach (var f in faces)
                if (f.name == name)
                    return f.sprite;
            return null;
        }

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
                int before = (int)shown;
                shown = Mathf.Min(total, shown + charactersPerSecond * Time.unscaledDeltaTime);
                bodyText.text = line.text.Substring(0, (int)shown);
                // 文字送りの音：2 文字に 1 回（空白・句読点では鳴らさない）
                for (int i = before; i < (int)shown; i++)
                    if (i % 2 == 0 && !char.IsWhiteSpace(line.text[i]) && "、。！？…「」".IndexOf(line.text[i]) < 0)
                    {
                        SoundEffects.Play("text_blip", line.shadowVoice ? 0.5f : 0.7f, 0.04f);
                        break;
                    }
            }

            bool done = shown >= total;
            nextMark.enabled = done && Mathf.Repeat(Time.unscaledTime, 0.8f) < 0.5f;

            // 影の声は、ことばが不安定に揺れる
            bodyRect.anchoredPosition = line.shadowVoice
                ? bodyBasePosition + new Vector2(Mathf.Round(Mathf.Sin(Time.unscaledTime * 23f)), 0f)  // 1 ドット単位で震える（半ドットはミクセルになる）
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

            SoundEffects.Play("decide", 0.6f, 0f);
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
            bool hasSpeaker = !string.IsNullOrEmpty(line.speaker);
            speakerText.enabled = hasSpeaker;
            // 名前の無いト書き・画面の文字は、名前の欄の高さを詰めて上から書く（1 行目の上に空き行ができないように）
            bodyBasePosition = hasSpeaker ? BodyWithSpeaker : BodyWithoutSpeaker;
            var face = FindFace(line.face);
            faceImage.enabled = face != null;
            faceImage.sprite = face;
            float left = face != null ? TextLeftWithFace : BodyWithSpeaker.x;
            bodyBasePosition.x = left;
            bodyRect.sizeDelta = new Vector2(-left - 10f, bodyRect.sizeDelta.y);
            speakerRect.anchoredPosition = new Vector2(left, speakerRect.anchoredPosition.y);
            speakerRect.sizeDelta = new Vector2(-left - 10f, speakerRect.sizeDelta.y);
            bodyRect.anchoredPosition = bodyBasePosition;
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
            // 暗転（ScreenFader：1000）より手前。回想や章のタイトルは、暗転した画面の上に言葉を出す
            canvas.sortingOrder = 1100;
            canvasGo.AddComponent<CanvasScaler>();
            // 拡大率は 480×270 の整数倍に固定（文字もゲーム画面と同じドットの大きさになる）
            var pixelCanvas = canvasGo.AddComponent<PixelPerfectCanvas>();

            window = new GameObject("Window", typeof(RectTransform));
            window.transform.SetParent(pixelCanvas.Frame, false);
            var windowRect = (RectTransform)window.transform;
            windowRect.anchorMin = new Vector2(0f, 0f);
            windowRect.anchorMax = new Vector2(1f, 0f);
            windowRect.pivot = new Vector2(0.5f, 0f);
            // 高さは「名前の欄＋本文 2 行」が収まるように（DotGothic16 は行の間隔が広いので、本文は lineSpacing で詰める）
            windowRect.sizeDelta = new Vector2(-24f, 72f);
            windowRect.anchoredPosition = new Vector2(0f, 8f);
            var background = window.AddComponent<Image>();
            background.color = new Color(0.03f, 0.04f, 0.1f, 0.88f);
            var outline = window.AddComponent<Outline>();
            outline.effectColor = new Color(0.62f, 0.82f, 1f, 0.6f);
            outline.effectDistance = new Vector2(1f, -1f);

            var faceGo = new GameObject("Face", typeof(RectTransform));
            faceGo.transform.SetParent(window.transform, false);
            var faceRect = (RectTransform)faceGo.transform;
            faceRect.anchorMin = faceRect.anchorMax = new Vector2(0f, 0.5f);
            faceRect.pivot = new Vector2(0f, 0.5f);
            faceRect.anchoredPosition = new Vector2(FaceLeft, 0f);
            faceRect.sizeDelta = new Vector2(FaceSize, FaceSize);
            faceImage = faceGo.AddComponent<Image>();
            faceImage.raycastTarget = false;
            faceImage.enabled = false;

            speakerText = CreateText("Speaker", window.transform, new Vector2(10f, -3f), new Vector2(-20f, 18f), speakerColor);
            speakerRect = (RectTransform)speakerText.transform;
            bodyText = CreateText("Body", window.transform, BodyWithSpeaker, new Vector2(-20f, 48f), textColor);
            bodyText.lineSpacing = 0.85f;
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
