using BlueNight.Interaction;
using BlueNight.LightShadow;
using UnityEngine;

namespace BlueNight.Player
{
    /// <summary>
    /// ルリのランタン。持っている間はルリの手元で光り、ランタン掛けに掛けるとその場に光を固定する。
    /// </summary>
    public class Lantern : MonoBehaviour
    {
        [SerializeField] PlayerController holder;
        [SerializeField] SpriteRenderer spriteRenderer;
        [SerializeField] GridLightSource lightSource;
        [SerializeField] Vector2 handOffsetDown = new Vector2(0.42f, 0.35f);
        [SerializeField] Vector2 handOffsetUp = new Vector2(-0.42f, 0.4f);
        [SerializeField] Vector2 handOffsetSide = new Vector2(0.4f, 0.35f);
        [SerializeField] float swingAmplitude = 0.04f;

        public LanternHook Hook { get; private set; }
        public bool IsCarried => Hook == null;

        float swingTime;

        public void Configure(PlayerController owner, SpriteRenderer sprite, GridLightSource source)
        {
            holder = owner;
            spriteRenderer = sprite;
            lightSource = source;
        }

        void Start()
        {
            if (lightSource != null && holder != null)
                lightSource.Anchor = holder.transform;
        }

        public void HangOn(LanternHook hook)
        {
            Hook = hook;
            // 掛けたランタンは、自分の足元の Y で前後が決まる（ルリの SortingGroup から出す）
            transform.SetParent(null, true);
            transform.position = hook.HangPoint;
            spriteRenderer.sortingOrder = 0;
            spriteRenderer.flipX = false;
            if (lightSource != null)
                lightSource.Anchor = hook.transform;
        }

        public void TakeBack()
        {
            Hook = null;
            // 持っている間はルリの子にして、ルリと一緒に前後を決める（下の sortingOrder はルリの中での前後）
            if (holder != null)
                transform.SetParent(holder.transform, true);
            if (lightSource != null && holder != null)
                lightSource.Anchor = holder.transform;
        }

        void LateUpdate()
        {
            if (!IsCarried || holder == null)
                return;

            Vector2 offset;
            switch (holder.Facing)
            {
                case Facing.Up: offset = handOffsetUp; break;
                case Facing.Left: offset = new Vector2(-handOffsetSide.x, handOffsetSide.y); break;
                case Facing.Right: offset = handOffsetSide; break;
                default: offset = handOffsetDown; break;
            }

            // 歩いているときだけ、手元で小さく揺れる
            if (holder.IsMoving)
                swingTime += Time.deltaTime * (holder.IsRunning ? 14f : 9f);
            offset.y += Mathf.Sin(swingTime) * swingAmplitude;

            transform.position = holder.transform.position + (Vector3)offset;
            // 背中を向けているときはランタンが体の向こう側になる
            spriteRenderer.sortingOrder = holder.Facing == Facing.Up ? -1 : 1;
        }
    }
}
