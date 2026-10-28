using BlueNight.Audio;
using BlueNight.Player;
using UnityEngine;

namespace BlueNight.Interaction
{
    /// <summary>ランタン掛け。ランタンを掛けると、その場所に光が固定される。</summary>
    public class LanternHook : Interactable
    {
        [SerializeField, Tooltip("ランタンを吊るす位置（足元から）。ランタンは底がピボット")] Vector2 hangOffset = new Vector2(0.38f, 0.65f);
        [SerializeField, Tooltip("掛けたときに立てるフラグ（掛ける練習など）")] string setsFlagOnHang;

        public void SetFlagOnHang(string flag) => setsFlagOnHang = flag;

        public Vector3 HangPoint => transform.position + (Vector3)hangOffset;

        public override bool CanInteract(PlayerInteractor who) =>
            who.Lantern != null && who.Lantern.isActiveAndEnabled && (who.Lantern.IsCarried || who.Lantern.Hook == this);

        public override void Interact(PlayerInteractor who)
        {
            var lantern = who.Lantern;
            if (lantern == null)
                return;
            if (lantern.IsCarried)
            {
                lantern.HangOn(this);
                SoundEffects.Play("lantern_hang");
                if (!string.IsNullOrEmpty(setsFlagOnHang))
                    BlueNight.Core.GameFlags.Set(setsFlagOnHang);
            }
            else if (lantern.Hook == this)
            {
                lantern.TakeBack();
                SoundEffects.Play("lantern_take");
            }
        }
    }
}
