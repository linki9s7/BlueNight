using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.Player;
using BlueNight.Rendering;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UI;

namespace BlueNight.Puzzle
{
    /// <summary>
    /// 第 2 章：路地全体を見渡す（C ／ ゲームパッドの Y）。見ている間は遊びが止まり（GamePause）、
    /// 移動キーでカメラだけを動かす。もう一度 C か、キャンセルで戻る。会話中・逃げられた演出中は入れない。
    /// </summary>
    public class OverviewMode : MonoBehaviour
    {
        [SerializeField] PlayerController player;
        [SerializeField] Font font;
        [SerializeField, Tooltip("カメラを動かす速さ（マス/秒）")] float panSpeed = 14f;

        GameObject label;
        bool active;

        public bool IsActive => active;

        public void Configure(PlayerController ruri, Font labelFont)
        {
            player = ruri;
            font = labelFont;
        }

        void Start() => BuildLabel();

        void OnDisable()
        {
            if (active)
                Exit();
        }

        void Update()
        {
            var camera = CameraFollow2D.Instance;
            if (camera == null || player == null)
                return;

            if (!active)
            {
                if (GameInput.OverviewPressed && !DialogueRunner.IsBusy && !ChasePuzzle.IsBusy && player.InputEnabled)
                    Enter(camera);
                return;
            }

            if (GameInput.OverviewPressed || GameInput.CancelPressed)
            {
                Exit();
                return;
            }
            camera.PanFreeLook(ReadMove() * (panSpeed * Time.unscaledDeltaTime));
        }

        void Enter(CameraFollow2D camera)
        {
            active = true;
            GamePause.IsPaused = true;
            player.InputEnabled = false;
            camera.BeginFreeLook();
            if (label != null)
                label.SetActive(true);
        }

        void Exit()
        {
            active = false;
            GamePause.IsPaused = false;
            if (player != null)
                player.InputEnabled = true;
            if (CameraFollow2D.Instance != null)
                CameraFollow2D.Instance.EndFreeLook(0.25f);
            if (label != null)
                label.SetActive(false);
        }

        static Vector2 ReadMove()
        {
            Vector2 move = Vector2.zero;
            var keyboard = Keyboard.current;
            if (keyboard != null)
            {
                if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed) move.x -= 1f;
                if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed) move.x += 1f;
                if (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed) move.y -= 1f;
                if (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed) move.y += 1f;
            }
            var gamepad = Gamepad.current;
            if (gamepad != null)
                move += gamepad.leftStick.ReadValue() + gamepad.dpad.ReadValue();
            return move.sqrMagnitude > 1f ? move.normalized : move;
        }

        // 画面の右上に小さく「見渡す」と出す（会話ウィンドウと同じ、480×270 の整数倍の UI）
        void BuildLabel()
        {
            var canvasGo = new GameObject("Overview Canvas");
            canvasGo.transform.SetParent(transform, false);
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 1050;
            canvasGo.AddComponent<CanvasScaler>();
            var pixelCanvas = canvasGo.AddComponent<PixelPerfectCanvas>();

            label = new GameObject("Overview Label", typeof(RectTransform));
            label.transform.SetParent(pixelCanvas.Frame, false);
            var rect = (RectTransform)label.transform;
            rect.anchorMin = rect.anchorMax = rect.pivot = new Vector2(1f, 1f);
            rect.anchoredPosition = new Vector2(-8f, -6f);
            rect.sizeDelta = new Vector2(160f, 18f);
            var text = label.AddComponent<Text>();
            text.font = font;
            text.fontSize = 16;
            text.color = new Color(0.86f, 0.93f, 1f, 1f);
            text.alignment = TextAnchor.UpperRight;
            text.raycastTarget = false;
            text.text = "見渡す（C でもどる）";
            var outline = label.AddComponent<Outline>();
            outline.effectColor = new Color(0.03f, 0.04f, 0.1f, 0.9f);
            outline.effectDistance = new Vector2(1f, -1f);
            label.SetActive(false);
        }
    }
}
