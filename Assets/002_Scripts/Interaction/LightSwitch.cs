using BlueNight.Audio;
using BlueNight.LightShadow;
using BlueNight.Player;
using UnityEngine;

namespace BlueNight.Interaction
{
    /// <summary>
    /// 点け消しできる町の灯り（第 2 章の門灯など）。調べると点く・消える。
    /// やり直しのときは、最初の状態（InitialOn）に戻す。
    /// </summary>
    public class LightSwitch : Interactable
    {
        [SerializeField] GridLightSource target;
        [SerializeField, Tooltip("点いている・消えているで絵を替える（任意）")] SpriteRenderer picture;
        [SerializeField] Sprite onSprite;
        [SerializeField] Sprite offSprite;

        public bool InitialOn { get; private set; }

        public void Configure(GridLightSource light) => target = light;

        public void ConfigureSprites(SpriteRenderer renderer, Sprite on, Sprite off)
        {
            picture = renderer;
            onSprite = on;
            offSprite = off;
        }

        void SyncPicture()
        {
            if (picture != null && target != null)
                picture.sprite = target.On ? onSprite : offSprite;
        }

        void Awake()
        {
            if (target == null)
                target = GetComponent<GridLightSource>();
            InitialOn = target != null && target.On;
            SyncPicture();
        }

        public override bool CanInteract(PlayerInteractor who) => target != null;

        public override void Interact(PlayerInteractor who)
        {
            target.On = !target.On;
            SyncPicture();
            SoundEffects.Play(target.On ? "light_on" : "light_off");
        }

        public void ResetToInitial()
        {
            if (target != null)
                target.On = InitialOn;
            SyncPicture();
        }
    }
}
