using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.Interaction;
using BlueNight.Player;
using UnityEngine;

namespace BlueNight.World
{
    /// <summary>
    /// 歩いて入ると別のエリアへ移る所（道の続き・路地の入口）。requiredFlag が立つまでは通れず、ひとこと出して押し戻す。
    /// </summary>
    [RequireComponent(typeof(BoxCollider2D))]
    public class AreaExit : MonoBehaviour
    {
        [SerializeField] string targetArea;
        [SerializeField] string targetSpawn;
        [SerializeField] string requiredFlag;
        [SerializeField] DialogueLine[] blockedLines = new DialogueLine[0];
        [SerializeField, Tooltip("通れないとき、ルリを押し戻す向き")] Vector2 pushBack = Vector2.down;

        public void Configure(string area, string spawn, string flag = null, DialogueLine[] whenBlocked = null, Vector2? push = null)
        {
            targetArea = area;
            targetSpawn = spawn;
            requiredFlag = flag;
            blockedLines = whenBlocked ?? new DialogueLine[0];
            if (push.HasValue)
                pushBack = push.Value;
        }

        void Reset() => GetComponent<BoxCollider2D>().isTrigger = true;

        void OnTriggerEnter2D(Collider2D other)
        {
            var player = other.GetComponent<PlayerController>();
            if (player == null || AreaManager.Instance == null || AreaManager.Instance.IsMoving)
                return;

            if (!string.IsNullOrEmpty(requiredFlag) && !GameFlags.Has(requiredFlag))
            {
                player.transform.position += (Vector3)(pushBack.normalized * 0.5f);
                if (blockedLines.Length > 0 && DialogueRunner.Instance != null)
                    DialogueRunner.Instance.Play(blockedLines);
                return;
            }
            AreaManager.Instance.Go(targetArea, targetSpawn);
        }
    }
}
