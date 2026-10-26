using UnityEngine;

namespace BlueNight.World
{
    /// <summary>
    /// 1 つのエリア（商店街・ランプ屋の中・路地など）。エリアはワールドの別々の場所に並べ、いま居るエリアだけを動かす。
    /// 入口の位置は子の「Spawn: 名前」で決める。
    /// </summary>
    public class Area : MonoBehaviour
    {
        [SerializeField] string id;
        [SerializeField, Tooltip("カメラが映してよい範囲（ワールド座標）")] Rect cameraBounds;
        [SerializeField, Tooltip("このエリアの曲（空なら今の曲のまま）")] string musicTrack;

        public string Id => id;
        public Rect CameraBounds => cameraBounds;
        public string MusicTrack => musicTrack;

        public void Configure(string areaId, Rect bounds, string music)
        {
            id = areaId;
            cameraBounds = bounds;
            musicTrack = music;
        }

        /// <summary>入口の位置。見つからなければエリアの中心。</summary>
        public Vector3 SpawnPoint(string spawn)
        {
            var t = transform.Find($"Spawn: {spawn}");
            return t != null ? t.position : (Vector3)cameraBounds.center;
        }

        public Transform AddSpawn(string spawn, Vector3 position)
        {
            var go = new GameObject($"Spawn: {spawn}");
            go.transform.SetParent(transform, false);
            go.transform.position = position;
            return go.transform;
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.color = new Color(0.4f, 0.8f, 1f, 0.6f);
            Gizmos.DrawWireCube(cameraBounds.center, cameraBounds.size);
        }
    }
}
