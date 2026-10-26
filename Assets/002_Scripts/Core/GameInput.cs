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
