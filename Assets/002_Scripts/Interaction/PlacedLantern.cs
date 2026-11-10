using BlueNight.Audio;
using BlueNight.Player;
using UnityEngine;

namespace BlueNight.Interaction
{
    /// <summary>地面に置いたランタン。調べるかランタンボタンで、手に戻す。ランタンと同じ物に付ける。</summary>
    [RequireComponent(typeof(Lantern))]
    public class PlacedLantern : Interactable
    {
        Lantern lantern;

        void Awake() => lantern = GetComponent<Lantern>();

        public override bool CanInteract(PlayerInteractor who) =>
            lantern != null && lantern.State == LanternState.Placed && who.Lantern == lantern;

        public override void Interact(PlayerInteractor who)
        {
            lantern.TakeBack();
            SoundEffects.Play("lantern_take");
        }
    }
}
