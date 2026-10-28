using UnityEngine;

namespace BlueNight.Core
{
    /// <summary>
    /// ターゲットをなめらかに追うカメラ。部屋の範囲（bounds）の外は映さない。
    /// 位置は 1 px 単位にそろえ、ドット絵がガタつかないようにする。
    /// 演出では LookAt で別の場所を映し、LookBack でルリに戻す（カメラワーク）。
    /// </summary>
    public class CameraFollow2D : MonoBehaviour
    {
        public static CameraFollow2D Instance { get; private set; }

        [SerializeField] Transform target;
        [SerializeField] Vector2 targetOffset = new Vector2(0f, 1f);
        [SerializeField] float smoothTime = 0.15f;
        [SerializeField] Rect bounds = new Rect(-20f, -12f, 40f, 24f);
        [SerializeField] Vector2 viewSize = new Vector2(30f, 16.875f); // 480x270 px / 16 PPU
        [SerializeField] int pixelsPerUnit = 16;

        Vector3 velocity;
        Vector3 unsnappedPosition;
        bool looking;
        Vector2 lookPoint;
        float currentSmooth = -1f;

        public bool IsLookingAway => looking;

        /// <summary>演出：ターゲットの代わりに point を映す（smooth 秒くらいでゆっくり動く）。</summary>
        public void LookAt(Vector2 point, float smooth)
        {
            looking = true;
            lookPoint = point;
            currentSmooth = smooth;
        }

        /// <summary>演出のあと：ターゲット（ルリ）に戻す。</summary>
        public void LookBack(float smooth)
        {
            looking = false;
            currentSmooth = smooth;
        }

        void Awake() => Instance = this;

        void OnDestroy()
        {
            if (Instance == this)
                Instance = null;
        }

        public void Configure(Transform follow, Rect roomBounds)
        {
            target = follow;
            bounds = roomBounds;
        }

        /// <summary>エリアを移動したとき：範囲を変えて、すぐにその位置へ（なめらかに追わない）。</summary>
        public void SetBounds(Rect roomBounds)
        {
            bounds = roomBounds;
            velocity = Vector3.zero;
            if (target == null)
                return;
            unsnappedPosition = Clamp(Goal());
            transform.position = Snap(unsnappedPosition);
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

            Vector3 goal = Clamp(Goal());
            unsnappedPosition = Vector3.SmoothDamp(unsnappedPosition, goal, ref velocity, currentSmooth > 0f ? currentSmooth : smoothTime);
            transform.position = Snap(unsnappedPosition);
            // ルリに戻り終えたら、ふだんの追い方に戻す
            if (!looking && currentSmooth > 0f && (goal - unsnappedPosition).sqrMagnitude < 0.0025f)
                currentSmooth = -1f;
        }

        Vector3 Goal()
        {
            if (looking)
                return new Vector3(lookPoint.x, lookPoint.y, transform.position.z);
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
