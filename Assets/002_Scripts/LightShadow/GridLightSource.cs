using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace BlueNight.LightShadow
{
    /// <summary>
    /// 影グリッドに参加する光源（街灯・窓・ランタン）。見た目の Light2D も一緒に切り替える。
    /// </summary>
    public class GridLightSource : MonoBehaviour
    {
        public static readonly List<GridLightSource> All = new List<GridLightSource>();

        [SerializeField, Tooltip("光が届く半径（マス）")] float radius = 4.5f;
        [SerializeField, Tooltip("光源の高さ（マス）。影の長さに影響する")] float height = 3f;
        [SerializeField] bool on = true;
        [SerializeField, Tooltip("見た目の光")] Light2D visual;
        [SerializeField] float visualPadding = 0.5f;
        [SerializeField, Tooltip("グリッド上の位置の基準。空ならこのオブジェクト自身")] Transform anchor;

        public float Radius => radius;
        public float Height => height;

        public bool On
        {
            get => on;
            set
            {
                on = value;
                SyncVisual();
            }
        }

        public Transform Anchor
        {
            get => anchor != null ? anchor : transform;
            set => anchor = value;
        }

        public void Configure(float lightRadius, Light2D light)
        {
            radius = lightRadius;
            visual = light;
            SyncVisual();
        }

        void OnEnable()
        {
            All.Add(this);
            SyncVisual();
        }

        void OnDisable()
        {
            All.Remove(this);
        }

        void SyncVisual()
        {
            if (visual == null)
                return;
            visual.enabled = on;
            visual.pointLightOuterRadius = radius + visualPadding;
        }
    }
}
