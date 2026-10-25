using BlueNight.Player;
using UnityEngine;

namespace BlueNight.Interaction
{
    /// <summary>ランタン掛け。ランタンを掛けると、その場所に光が固定される。</summary>
    public class LanternHook : Interactable
    {
        [SerializeField, Tooltip("ランタンを吊るす位置（足元から）。ランタンは底がピボット")] Vector2 hangOffset = new Vector2(0.38f, 0.65f);

        public Vector3 HangPoint => transform.position + (Vector3)hangOffset;

        public override bool CanInteract(PlayerInteractor who) =>
            who.Lantern != null && (who.Lantern.IsCarried || who.Lantern.Hook == this);

        public override void Interact(PlayerInteractor who)
        {
            var lantern = who.Lantern;
            if (lantern == null)
                return;
            if (lantern.IsCarried)
                lantern.HangOn(this);
            else if (lantern.Hook == this)
                lantern.TakeBack();
        }
    }
}
