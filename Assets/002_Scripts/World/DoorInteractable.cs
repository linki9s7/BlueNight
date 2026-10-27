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

        public void Configure(string area, string spawn, string flag = null, DialogueLine[] whenLocked = null)
        {
            targetArea = area;
            targetSpawn = spawn;
            requiredFlag = flag;
            lockedLines = whenLocked ?? new DialogueLine[0];
        }

        public override void Interact(PlayerInteractor who)
        {
            if (!string.IsNullOrEmpty(requiredFlag) && !GameFlags.Has(requiredFlag))
            {
                if (lockedLines.Length > 0 && DialogueRunner.Instance != null)
                    DialogueRunner.Instance.Play(lockedLines);
                return;
            }
            AreaManager.Instance?.Go(targetArea, targetSpawn);
        }
    }
}
