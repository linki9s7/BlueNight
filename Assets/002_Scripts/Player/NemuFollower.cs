using UnityEngine;

namespace BlueNight.Player
{
    /// <summary>
    /// 相棒の蛾・ネム。ルリの肩の後ろあたりを、ふわふわ揺れながらついてくる。
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class NemuFollower : MonoBehaviour
    {
        [SerializeField] PlayerController target;
        [SerializeField] Vector2 offset = new Vector2(-0.7f, 1.9f);
        [SerializeField] float smoothTime = 0.35f;
        [SerializeField] float bobAmplitude = 0.15f;
        [SerializeField] float bobFrequency = 1.6f;
        [SerializeField] Sprite[] flapFrames = new Sprite[0];
        [SerializeField] float flapFps = 12f;

        SpriteRenderer spriteRenderer;
        Vector3 velocity;
        float time;

        public void Configure(PlayerController follow, Sprite[] frames)
        {
            target = follow;
            flapFrames = frames;
        }

        void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
        }

        /// <summary>エリアを移動したとき、ルリのそばへすぐ移す。</summary>
        public void SnapToTarget()
        {
            if (target == null)
                return;
            transform.position = target.transform.position + (Vector3)offset;
            velocity = Vector3.zero;
        }

        void LateUpdate()
        {
            if (target == null)
                return;

            time += Time.deltaTime;

            // ルリの向きの反対側（背中側）に回り込む
            float side = target.Facing == Facing.Left ? -offset.x : offset.x;
            Vector3 goal = target.transform.position + new Vector3(side, offset.y + Mathf.Sin(time * bobFrequency * Mathf.PI * 2f) * bobAmplitude, 0f);
            // ネムの絵は左右対称の正面向き（影は右の羽だけ）なので、反転しない
            transform.position = Vector3.SmoothDamp(transform.position, goal, ref velocity, smoothTime);

            if (flapFrames.Length > 0)
                spriteRenderer.sprite = flapFrames[(int)(time * flapFps) % flapFrames.Length];
        }
    }
}
