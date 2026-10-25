using System;
using UnityEngine;

namespace BlueNight.Player
{
    /// <summary>
    /// 4 方向のスプライトアニメーション。横向きは右向きの絵を用意し、左向きは反転して使う。
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class PlayerAnimator : MonoBehaviour
    {
        [Serializable]
        public class DirectionalFrames
        {
            public Sprite[] down = Array.Empty<Sprite>();
            public Sprite[] up = Array.Empty<Sprite>();
            public Sprite[] side = Array.Empty<Sprite>();

            public Sprite[] For(Facing facing)
            {
                switch (facing)
                {
                    case Facing.Up: return up;
                    case Facing.Left:
                    case Facing.Right: return side;
                    default: return down;
                }
            }
        }

        [SerializeField] PlayerController controller;
        [SerializeField] DirectionalFrames idle = new DirectionalFrames();
        [SerializeField] DirectionalFrames walk = new DirectionalFrames();
        [SerializeField] float idleFps = 3f;
        [SerializeField] float walkFps = 10f;
        [SerializeField] float runFpsScale = 1.5f;

        SpriteRenderer spriteRenderer;
        float time;
        bool wasMoving;
        Facing lastFacing;

        public void Configure(PlayerController owner, DirectionalFrames idleFrames, DirectionalFrames walkFrames)
        {
            controller = owner;
            idle = idleFrames;
            walk = walkFrames;
        }

        void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            if (controller == null)
                controller = GetComponentInParent<PlayerController>();
        }

        void LateUpdate()
        {
            if (controller == null)
                return;

            bool moving = controller.IsMoving;
            Facing facing = controller.Facing;

            // 歩き出し・立ち止まり・振り向きのときは 1 コマ目から再生する
            if (moving != wasMoving || facing != lastFacing)
                time = 0f;
            wasMoving = moving;
            lastFacing = facing;

            Sprite[] frames = (moving ? walk : idle).For(facing);
            if (frames == null || frames.Length == 0)
                return;

            float fps = moving ? walkFps * (controller.IsRunning ? runFpsScale : 1f) : idleFps;
            time += Time.deltaTime;
            int index = (int)(time * fps) % frames.Length;

            spriteRenderer.sprite = frames[index];
            spriteRenderer.flipX = facing == Facing.Left;
        }
    }
}
