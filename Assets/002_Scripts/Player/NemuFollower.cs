using UnityEngine;

namespace BlueNight.Player
{
    /// <summary>
    /// 相棒の蛾・ネム。ルリの肩の後ろあたりを、ふわふわ揺れながらついてくる。
    /// ルリの子（ルリの SortingGroup の中）に置き、ルリと一緒に前後が決まる。
    /// 向きはルリに少し遅れて合わせる（正面・背中・横。左向きは専用の絵で、flipX は使わない）。
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class NemuFollower : MonoBehaviour
    {
        [SerializeField] PlayerController target;
        [SerializeField] Vector2 offset = new Vector2(-0.7f, 1.9f);
        [SerializeField] float smoothTime = 0.35f;
        [SerializeField] float bobAmplitude = 0.15f;
        [SerializeField] float bobFrequency = 1.6f;
        [SerializeField] PlayerAnimator.DirectionalFrames flapFrames;
        [SerializeField] float flapFps = 10f;
        [SerializeField] float turnDelay = 0.2f;

        SpriteRenderer spriteRenderer;
        Vector3 position;   // 親（ルリ）が動いても遅れてついてくるよう、ワールド座標を自分で持つ
        Vector3 velocity;
        float time;
        Facing facing = Facing.Down;
        float turnTimer;

        public void Configure(PlayerController follow, PlayerAnimator.DirectionalFrames frames)
        {
            target = follow;
            flapFrames = frames;
        }

        void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            position = transform.position;
        }

        /// <summary>エリアを移動したとき、ルリのそばへすぐ移す。</summary>
        public void SnapToTarget()
        {
            if (target == null)
                return;
            position = target.transform.position + (Vector3)offset;
            transform.position = position;
            velocity = Vector3.zero;
            facing = target.Facing;
        }

        void LateUpdate()
        {
            if (target == null)
                return;

            time += Time.deltaTime;

            // ルリの向きの反対側（背中側）に回り込む
            float side = target.Facing == Facing.Left ? -offset.x : offset.x;
            Vector3 goal = target.transform.position + new Vector3(side, offset.y + Mathf.Sin(time * bobFrequency * Mathf.PI * 2f) * bobAmplitude, 0f);
            position = Vector3.SmoothDamp(position, goal, ref velocity, smoothTime);
            transform.position = position;

            // 向き：ルリが向きを変えてから少し遅れて振り向く
            if (target.Facing != facing)
            {
                turnTimer += Time.deltaTime;
                if (turnTimer >= turnDelay)
                {
                    facing = target.Facing;
                    turnTimer = 0f;
                }
            }
            else
            {
                turnTimer = 0f;
            }

            // ルリの中での前後：ルリがこちらを向いているとネムは背中の向こう（奥）、背中を向けていると手前
            spriteRenderer.sortingOrder = facing == Facing.Down ? -10 : 10;

            var frames = Frames(facing);
            if (frames != null && frames.Length > 0)
                spriteRenderer.sprite = frames[(int)(time * flapFps) % frames.Length];
        }

        Sprite[] Frames(Facing f)
        {
            if (flapFrames == null)
                return null;
            switch (f)
            {
                case Facing.Up: return flapFrames.up;
                case Facing.Left: return flapFrames.left;
                case Facing.Right: return flapFrames.right;
                default: return flapFrames.down;
            }
        }
    }
}
