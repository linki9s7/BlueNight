using System;
using UnityEngine;

namespace BlueNight.Player
{
    /// <summary>
    /// 4 方向のスプライトアニメーション。左向きは専用の絵（形だけ反転し、陰影は左上からの光のまま描き直したもの）を使う。
    /// flipX で反転すると影の位置まで反転して光の向きが逆になるので、反転はしない。
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class PlayerAnimator : MonoBehaviour
    {
        [Serializable]
        public class DirectionalFrames
        {
            public Sprite[] down = Array.Empty<Sprite>();
            public Sprite[] up = Array.Empty<Sprite>();
            public Sprite[] right = Array.Empty<Sprite>();
            public Sprite[] left = Array.Empty<Sprite>();

            public Sprite[] For(Facing facing)
            {
                switch (facing)
                {
                    case Facing.Up: return up;
                    case Facing.Left: return left;
                    case Facing.Right: return right;
                    default: return down;
                }
            }
        }

        /// <summary>1 回だけ再生する動き。</summary>
        public enum Action { None, Inspect, Hang, Place }

        [SerializeField] PlayerController controller;
        [SerializeField] DirectionalFrames idle = new DirectionalFrames();
        [SerializeField] DirectionalFrames walk = new DirectionalFrames();
        [SerializeField, Tooltip("小走り（無ければ歩きを速く再生する）")] DirectionalFrames run = new DirectionalFrames();
        [SerializeField] DirectionalFrames inspect = new DirectionalFrames();
        [SerializeField] DirectionalFrames hang = new DirectionalFrames();
        [SerializeField] DirectionalFrames place = new DirectionalFrames();
        [SerializeField] float idleFps = 3f;
        [SerializeField] float walkFps = 10f;
        [SerializeField] float runFps = 12f;
        [SerializeField] float runFpsScale = 1.5f;
        [SerializeField] float actionFps = 10f;

        SpriteRenderer spriteRenderer;
        float time;
        bool wasMoving;
        bool wasRunning;
        Facing lastFacing;
        Action action;
        float actionTime;

        public void Configure(PlayerController owner, DirectionalFrames idleFrames, DirectionalFrames walkFrames,
            DirectionalFrames runFrames = null, DirectionalFrames inspectFrames = null,
            DirectionalFrames hangFrames = null, DirectionalFrames placeFrames = null)
        {
            controller = owner;
            idle = idleFrames;
            walk = walkFrames;
            run = runFrames ?? new DirectionalFrames();
            inspect = inspectFrames ?? new DirectionalFrames();
            hang = hangFrames ?? new DirectionalFrames();
            place = placeFrames ?? new DirectionalFrames();
        }

        /// <summary>調べる・ランタンを掛ける・置くの動きを 1 回だけ再生する。歩き出すと止まる。</summary>
        public void PlayAction(Action kind)
        {
            if (FramesOf(kind)?.For(controller != null ? controller.Facing : Facing.Down).Length > 0)
            {
                action = kind;
                actionTime = 0f;
            }
        }

        DirectionalFrames FramesOf(Action kind)
        {
            switch (kind)
            {
                case Action.Inspect: return inspect;
                case Action.Hang: return hang;
                case Action.Place: return place;
                default: return null;
            }
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
            bool running = moving && controller.IsRunning;
            Facing facing = controller.Facing;

            if (action != Action.None)
            {
                if (moving)
                {
                    action = Action.None;
                }
                else
                {
                    Sprite[] actionFrames = FramesOf(action).For(facing);
                    actionTime += Time.deltaTime;
                    int frame = (int)(actionTime * actionFps);
                    if (frame < actionFrames.Length)
                    {
                        spriteRenderer.sprite = actionFrames[frame];
                        return;
                    }
                    action = Action.None;
                    time = 0f;
                }
            }

            // 歩き出し・立ち止まり・走り出し・振り向きのときは 1 コマ目から再生する
            if (moving != wasMoving || running != wasRunning || facing != lastFacing)
                time = 0f;
            wasMoving = moving;
            wasRunning = running;
            lastFacing = facing;

            Sprite[] runFrames = run.For(facing);
            bool useRun = running && runFrames != null && runFrames.Length > 0;
            Sprite[] frames = useRun ? runFrames : (moving ? walk : idle).For(facing);
            if (frames == null || frames.Length == 0)
                return;

            float fps = useRun ? runFps : moving ? walkFps * (running ? runFpsScale : 1f) : idleFps;
            time += Time.deltaTime;
            int index = (int)(time * fps) % frames.Length;

            spriteRenderer.sprite = frames[index];
        }
    }
}
