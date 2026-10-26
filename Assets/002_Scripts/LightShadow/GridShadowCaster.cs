using System.Collections.Generic;
using UnityEngine;

namespace BlueNight.LightShadow
{
    /// <summary>光を受けて地面に影を落とすモノ（自販機・ベンチなど）。</summary>
    public class GridShadowCaster : MonoBehaviour
    {
        public static readonly List<GridShadowCaster> All = new List<GridShadowCaster>();

        [SerializeField, Tooltip("高さ（マス）。高いほど影が長い")] float height = 1f;
        [SerializeField, Tooltip("占めるマス数（足元から右・上へ）")] Vector2Int size = Vector2Int.one;

        public float Height => height;
        public Vector2Int Size => size;

        public void Configure(float casterHeight, Vector2Int footprint)
        {
            height = casterHeight;
            size = footprint;
        }

        void OnEnable() => All.Add(this);
        void OnDisable() => All.Remove(this);
    }
}
