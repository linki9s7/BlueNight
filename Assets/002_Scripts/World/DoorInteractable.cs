using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.Interaction;
using BlueNight.Player;
using UnityEngine;

namespace BlueNight.World
{
    /// <summary>調べて入る戸（ランプ屋の戸など）。</summary>
    public class DoorInteractable : Interactable
    {
        [SerializeField] string targetArea;
        [SerializeField] string targetSpawn;
        [SerializeField] string requiredFlag;
        [SerializeField] DialogueLine[] lockedLines = new DialogueLine[0];
        [SerializeField, Tooltip("閉まっているときに調べたら立てるフラグ（演出のきっかけ。空なら立てない）")] string lockedSetsFlag;

        public void Configure(string area, string spawn, string flag = null, DialogueLine[] whenLocked = null, string setsWhenLocked = null)
        {
            targetArea = area;
            targetSpawn = spawn;
            requiredFlag = flag;
            lockedLines = whenLocked ?? new DialogueLine[0];
            lockedSetsFlag = setsWhenLocked;
        }

        public override void Interact(PlayerInteractor who)
        {
            if (!string.IsNullOrEmpty(requiredFlag) && !GameFlags.Has(requiredFlag))
            {
                if (lockedLines.Length > 0 && DialogueRunner.Instance != null)
                    DialogueRunner.Instance.Play(lockedLines, () => GameFlags.Set(lockedSetsFlag));
                else
                    GameFlags.Set(lockedSetsFlag);
                return;
            }
            AreaManager.Instance?.Go(targetArea, targetSpawn);
        }
    }
}
