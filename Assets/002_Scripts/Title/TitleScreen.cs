using System.Collections;
using BlueNight.Audio;
using BlueNight.Core;
using BlueNight.Rendering;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace BlueNight.Title
{
    /// <summary>
    /// タイトル画面のメニュー：はじめから／つづきから／設定／終了。設定では音量 3 種を変えられる。
    /// 上下で選び、決定で進む。キャンセルで戻る。文字はゲーム画面と同じドットの格子に合わせる（PixelPerfectCanvas）。
    /// </summary>
    public class TitleScreen : MonoBehaviour
    {
        [SerializeField] Font font;
        [SerializeField] Sprite cursorSprite;
        [SerializeField, Tooltip("はじめからで開くシーン")] string firstScene = "M1_Prototype";
        [SerializeField] Vector2 menuPosition = new Vector2(150f, -70f);   // 480x270 の枠の中心からの位置（ドット）
        [SerializeField] Color normalColor = new Color(0.86f, 0.9f, 1f);
        [SerializeField] Color selectedColor = new Color(1f, 0.92f, 0.62f);
        [SerializeField] Color disabledColor = new Color(0.45f, 0.5f, 0.65f);

        Text[] items;
        Image cursor;
        int selected;
        bool settings;
        bool busy;
        int[] volumes = new int[3];

        static readonly string[] MainItems = { "はじめから", "つづきから", "設定", "終了" };
        static readonly string[] VolumeNames = { "BGM", "環境音", "効果音" };

        public void Configure(Font menuFont, Sprite cursorImage, string sceneOnNewGame)
        {
            font = menuFont;
            cursorSprite = cursorImage;
            firstScene = sceneOnNewGame;
        }

        void Start()
        {
            AudioPrefs.Load();
            BuildUi();
            Refresh();
            var fader = ScreenFader.Get();
            fader.SetDark(true);
            StartCoroutine(fader.FadeIn(1.5f));
            selected = SaveSystem.HasSave ? 1 : 0;
            Refresh();
        }

        void BuildUi()
        {
            var canvasGo = new GameObject("Title Menu");
            canvasGo.transform.SetParent(transform, false);
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 50;
            canvasGo.AddComponent<CanvasScaler>();
            var pixel = canvasGo.AddComponent<PixelPerfectCanvas>();

            items = new Text[4];
            for (int i = 0; i < items.Length; i++)
            {
                var go = new GameObject($"Item {i}", typeof(RectTransform));
                go.transform.SetParent(pixel.Frame, false);
                var rect = (RectTransform)go.transform;
                rect.sizeDelta = new Vector2(120f, 18f);
                rect.anchoredPosition = menuPosition + new Vector2(0f, -18f * i);
                var text = go.AddComponent<Text>();
                text.font = font;
                text.fontSize = 16;
                text.alignment = TextAnchor.MiddleLeft;
                text.horizontalOverflow = HorizontalWrapMode.Overflow;
                text.raycastTarget = false;
                items[i] = text;
            }

            var cursorGo = new GameObject("Cursor", typeof(RectTransform));
            cursorGo.transform.SetParent(pixel.Frame, false);
            ((RectTransform)cursorGo.transform).sizeDelta = new Vector2(7f, 7f);
            cursor = cursorGo.AddComponent<Image>();
            cursor.sprite = cursorSprite;
            cursor.raycastTarget = false;
        }

        void Refresh()
        {
            for (int i = 0; i < items.Length; i++)
            {
                string label;
                bool enabled = true;
                if (!settings)
                {
                    label = MainItems[i];
                    enabled = i != 1 || SaveSystem.HasSave;
                }
                else
                {
                    label = i < 3 ? $"{VolumeNames[i]}　◀ {new string('|', volumes[i])}{new string('.', AudioPrefs.Steps - volumes[i])} ▶" : "もどる";
                }
                items[i].text = label;
                items[i].color = !enabled ? disabledColor : i == selected ? selectedColor : normalColor;
            }
            var rect = (RectTransform)cursor.transform;
            rect.anchoredPosition = ((RectTransform)items[selected].transform).anchoredPosition + new Vector2(-66f, 0f);
        }

        void Update()
        {
            if (busy)
                return;

            int move = -GameInput.VerticalPressed;
            if (move != 0)
            {
                selected = (selected + move + items.Length) % items.Length;
                if (!settings && selected == 1 && !SaveSystem.HasSave)
                    selected = (selected + move + items.Length) % items.Length;
                SoundEffects.Play("cursor", 0.6f, 0f);
                Refresh();
            }

            if (settings)
            {
                int h = GameInput.HorizontalPressed;
                if (h != 0 && selected < 3)
                {
                    volumes[selected] = Mathf.Clamp(volumes[selected] + h, 0, AudioPrefs.Steps);
                    AudioPrefs.Set(volumes[0], volumes[1], volumes[2]);
                    SoundEffects.Play("cursor", 0.8f, 0f);
                    Refresh();
                }
                if (GameInput.CancelPressed || (GameInput.ConfirmPressed && selected == 3))
                {
                    settings = false;
                    selected = 2;
                    SoundEffects.Play("cancel", 0.8f, 0f);
                    Refresh();
                }
                return;
            }

            if (!GameInput.ConfirmPressed)
                return;
            SoundEffects.Play("decide", 0.8f, 0f);
            switch (selected)
            {
                case 0:
                    GameFlags.Load(null);
                    SaveSystem.Pending = null;
                    StartCoroutine(LoadScene(firstScene));
                    break;
                case 1:
                    var save = SaveSystem.Load();
                    if (save == null)
                        break;
                    SaveSystem.Pending = save;
                    StartCoroutine(LoadScene(string.IsNullOrEmpty(save.scene) ? firstScene : save.scene));
                    break;
                case 2:
                    settings = true;
                    selected = 0;
                    volumes = new[] { AudioPrefs.Music, AudioPrefs.Ambience, AudioPrefs.Effects };
                    Refresh();
                    break;
                case 3:
                    Application.Quit();
                    break;
            }
        }

        IEnumerator LoadScene(string scene)
        {
            busy = true;
            MusicDirector.Instance?.Stop(1.5f);
            yield return ScreenFader.Get().FadeOut(1.5f);
            SceneManager.LoadScene(scene);
        }
    }
}
