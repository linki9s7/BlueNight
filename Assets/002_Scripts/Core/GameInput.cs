using UnityEngine.InputSystem;

namespace BlueNight.Core
{
    /// <summary>
    /// ボタン入力のまとめ。WASD 派・矢印キー派のどちらでも押しやすいキーを割り当てる。
    /// 調べる・決定：Space / E / Enter / Z / ゲームパッド南ボタン
    /// ランタン　　：F / X / ゲームパッド西ボタン
    /// </summary>
    public static class GameInput
    {
        public static bool ConfirmPressed
        {
            get
            {
                var keyboard = Keyboard.current;
                if (keyboard != null && (keyboard.spaceKey.wasPressedThisFrame || keyboard.eKey.wasPressedThisFrame
                    || keyboard.enterKey.wasPressedThisFrame || keyboard.numpadEnterKey.wasPressedThisFrame
                    || keyboard.zKey.wasPressedThisFrame))
                    return true;
                var gamepad = Gamepad.current;
                return gamepad != null && gamepad.buttonSouth.wasPressedThisFrame;
            }
        }

        public static bool CancelPressed
        {
            get
            {
                var keyboard = Keyboard.current;
                if (keyboard != null && (keyboard.escapeKey.wasPressedThisFrame || keyboard.backspaceKey.wasPressedThisFrame))
                    return true;
                var gamepad = Gamepad.current;
                return gamepad != null && gamepad.buttonEast.wasPressedThisFrame;
            }
        }

        public static bool MenuPressed
        {
            get
            {
                var keyboard = Keyboard.current;
                if (keyboard != null && keyboard.tabKey.wasPressedThisFrame)
                    return true;
                var gamepad = Gamepad.current;
                return gamepad != null && gamepad.startButton.wasPressedThisFrame;
            }
        }

        /// <summary>メニューのカーソル：このフレームで押された方向（上 = +1、下 = -1 など）。</summary>
        public static int VerticalPressed
        {
            get
            {
                var keyboard = Keyboard.current;
                var gamepad = Gamepad.current;
                if ((keyboard != null && (keyboard.upArrowKey.wasPressedThisFrame || keyboard.wKey.wasPressedThisFrame))
                    || (gamepad != null && gamepad.dpad.up.wasPressedThisFrame))
                    return 1;
                if ((keyboard != null && (keyboard.downArrowKey.wasPressedThisFrame || keyboard.sKey.wasPressedThisFrame))
                    || (gamepad != null && gamepad.dpad.down.wasPressedThisFrame))
                    return -1;
                return 0;
            }
        }

        public static int HorizontalPressed
        {
            get
            {
                var keyboard = Keyboard.current;
                var gamepad = Gamepad.current;
                if ((keyboard != null && (keyboard.rightArrowKey.wasPressedThisFrame || keyboard.dKey.wasPressedThisFrame))
                    || (gamepad != null && gamepad.dpad.right.wasPressedThisFrame))
                    return 1;
                if ((keyboard != null && (keyboard.leftArrowKey.wasPressedThisFrame || keyboard.aKey.wasPressedThisFrame))
                    || (gamepad != null && gamepad.dpad.left.wasPressedThisFrame))
                    return -1;
                return 0;
            }
        }

        public static bool LanternPressed
        {
            get
            {
                var keyboard = Keyboard.current;
                if (keyboard != null && (keyboard.fKey.wasPressedThisFrame || keyboard.xKey.wasPressedThisFrame))
                    return true;
                var gamepad = Gamepad.current;
                return gamepad != null && gamepad.buttonWest.wasPressedThisFrame;
            }
        }
    }
}
