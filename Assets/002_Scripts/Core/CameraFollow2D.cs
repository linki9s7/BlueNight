using UnityEngine;

namespace BlueNight.Core
{
    /// <summary>
    /// ターゲットをなめらかに追うカメラ。部屋の範囲（bounds）の外は映さない。
    /// 位置は 1 px 単位にそろえ、ドット絵がガタつかないようにする。
    /// </summary>
    public class CameraFollow2D : MonoBehaviour
    {
        [SerializeField] Transform target;
        [SerializeField] Vector2 targetOffset = new Vector2(0f, 1f);
        [SerializeField] float smoothTime = 0.15f;
        [SerializeField] Rect bounds = new Rect(-20f, -12f, 40f, 24f);
        [SerializeField] Vector2 viewSize = new Vector2(30f, 16.875f); // 480x270 px / 16 PPU
        [SerializeField] int pixelsPerUnit = 16;

        Vector3 velocity;
        Vector3 unsnappedPosition;

        public void Configure(Transform follow, Rect roomBounds)
        {
            target = follow;
            bounds = roomBounds;
        }

        void Start()
        {
            unsnappedPosition = transform.position;
            if (target != null)
                unsnappedPosition = Clamp(Goal());
            transform.position = Snap(unsnappedPosition);
        }

        void LateUpdate()
        {
            if (target == null)
                return;

            unsnappedPosition = Vector3.SmoothDamp(unsnappedPosition, Clamp(Goal()), ref velocity, smoothTime);
            transform.position = Snap(unsnappedPosition);
        }

        Vector3 Goal()
        {
            Vector3 p = target.position;
            return new Vector3(p.x + targetOffset.x, p.y + targetOffset.y, transform.position.z);
        }

        Vector3 Clamp(Vector3 p)
        {
            float halfW = viewSize.x * 0.5f;
            float halfH = viewSize.y * 0.5f;
            p.x = bounds.width <= viewSize.x ? bounds.center.x : Mathf.Clamp(p.x, bounds.xMin + halfW, bounds.xMax - halfW);
            p.y = bounds.height <= viewSize.y ? bounds.center.y : Mathf.Clamp(p.y, bounds.yMin + halfH, bounds.yMax - halfH);
            return p;
        }

        Vector3 Snap(Vector3 p)
        {
            return new Vector3(Mathf.Round(p.x * pixelsPerUnit) / pixelsPerUnit, Mathf.Round(p.y * pixelsPerUnit) / pixelsPerUnit, p.z);
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.cyan;
            Gizmos.DrawWireCube(bounds.center, bounds.size);
        }
    }
}
