using UnityEngine;
using UnityEngine.InputSystem;

namespace BlueNight.Player
{
    public enum Facing { Down, Up, Left, Right }

    /// <summary>
    /// 見下ろし視点の 8 方向移動。WASD / 矢印キー / 左スティック / 十字キーに対応。
    /// 1 unit = 16 px。
    /// </summary>
    [RequireComponent(typeof(Rigidbody2D))]
    public class PlayerController : MonoBehaviour
    {
        [SerializeField] float walkSpeed = 3.5f;
        [SerializeField] float runSpeed = 6f;
        [SerializeField, Range(0f, 0.5f)] float stickDeadZone = 0.2f;

        Rigidbody2D body;
        Vector2 moveInput;

        public Facing Facing { get; private set; } = Facing.Down;
        public bool IsMoving => moveInput.sqrMagnitude > 0.0001f;
        public bool IsRunning { get; private set; }

        /// <summary>会話中・演出中などは false にして操作を止める。</summary>
        public bool InputEnabled { get; set; } = true;

        void Awake()
        {
            body = GetComponent<Rigidbody2D>();
            body.gravityScale = 0f;
            body.freezeRotation = true;
            body.interpolation = RigidbodyInterpolation2D.Interpolate;
        }

        void Update()
        {
            moveInput = InputEnabled ? ReadMove() : Vector2.zero;
            IsRunning = InputEnabled && IsMoving && ReadRun();

            if (IsMoving)
                Facing = ToFacing(moveInput);
        }

        void FixedUpdate()
        {
            float speed = IsRunning ? runSpeed : walkSpeed;
            body.velocity = moveInput * speed;
        }

        Vector2 ReadMove()
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
            {
                Vector2 stick = gamepad.leftStick.ReadValue();
                if (stick.magnitude < stickDeadZone)
                    stick = Vector2.zero;
                move += stick + gamepad.dpad.ReadValue();
            }

            // 斜めでも速さが変わらないよう、長さ 1 を超えたら正規化する
            return move.sqrMagnitude > 1f ? move.normalized : move;
        }

        static bool ReadRun()
        {
            var keyboard = Keyboard.current;
            if (keyboard != null && (keyboard.leftShiftKey.isPressed || keyboard.rightShiftKey.isPressed))
                return true;

            var gamepad = Gamepad.current;
            return gamepad != null && gamepad.rightTrigger.isPressed;
        }

        // 斜め移動中は左右の向きを優先する
        static Facing ToFacing(Vector2 move)
        {
            if (Mathf.Abs(move.x) >= Mathf.Abs(move.y))
                return move.x < 0f ? Facing.Left : Facing.Right;
            return move.y < 0f ? Facing.Down : Facing.Up;
        }
    }
}
