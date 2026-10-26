using System.Collections.Generic;
using UnityEngine;

namespace BlueNight.Audio
{
    /// <summary>
    /// 場所ごとの音の決まり（四角い範囲）。足音の種類（石・木・濡れた路面）と、屋内かどうか。
    /// 範囲が重なったら、あとから置いたものが優先。
    /// </summary>
    public class AreaZone : MonoBehaviour
    {
        public static readonly List<AreaZone> All = new List<AreaZone>();

        [SerializeField] Rect area = new Rect(0f, 0f, 10f, 10f);
        [SerializeField, Tooltip("足音のグループ名（step_stone / step_wood / step_wet）")] string footsteps = "step_wood";
        [SerializeField] bool indoor = true;

        public string Footsteps => footsteps;
        public bool Indoor => indoor;

        public void Configure(Rect worldArea, string footstepGroup, bool isIndoor)
        {
            area = worldArea;
            footsteps = footstepGroup;
            indoor = isIndoor;
        }

        public bool Contains(Vector2 position) => area.Contains(position);

        void OnEnable() => All.Add(this);
        void OnDisable() => All.Remove(this);

        public static AreaZone At(Vector2 position)
        {
            for (int i = All.Count - 1; i >= 0; i--)
                if (All[i].Contains(position))
                    return All[i];
            return null;
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.color = new Color(1f, 0.8f, 0.4f, 0.6f);
            Gizmos.DrawWireCube(area.center, area.size);
        }
    }
}
