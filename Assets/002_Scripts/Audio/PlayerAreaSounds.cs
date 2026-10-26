using BlueNight.Player;
using UnityEngine;

namespace BlueNight.Audio
{
    /// <summary>
    /// ルリの足音（歩き・小走りの歩幅に合わせて）と、屋内に入ったときの環境音のこもり。
    /// 足音の種類は AreaZone で決まる（どこにも入っていなければ石畳）。
    /// </summary>
    [RequireComponent(typeof(PlayerController))]
    public class PlayerAreaSounds : MonoBehaviour
    {
        [SerializeField] string outdoorFootsteps = "step_stone";
        [SerializeField] float walkInterval = 0.36f;
        [SerializeField] float runInterval = 0.24f;
        [SerializeField, Range(0f, 1f)] float footstepVolume = 0.7f;

        PlayerController controller;
        float timer;
        bool wasIndoor;

        void Awake() => controller = GetComponent<PlayerController>();

        void Update()
        {
            var zone = AreaZone.At(transform.position);
            bool indoor = zone != null && zone.Indoor;
            if (indoor != wasIndoor && AmbiencePlayer.Instance != null)
                AmbiencePlayer.Instance.SetIndoor(indoor);
            wasIndoor = indoor;

            if (!controller.IsMoving)
            {
                timer = 0.12f;  // 歩き出しの 1 歩目はすぐに
                return;
            }
            timer -= Time.deltaTime;
            if (timer > 0f)
                return;
            timer = controller.IsRunning ? runInterval : walkInterval;
            SoundEffects.Play(zone != null ? zone.Footsteps : outdoorFootsteps, footstepVolume * (controller.IsRunning ? 1.1f : 1f), 0.05f);
        }
    }
}
