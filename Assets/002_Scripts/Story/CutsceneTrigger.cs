using BlueNight.Core;
using BlueNight.Interaction;
using BlueNight.Player;
using BlueNight.World;
using UnityEngine;

namespace BlueNight.Story
{
    /// <summary>
    /// 演出の始まり方：エリアに入ったとき／決まった場所に踏みこんだとき／フラグが立ったとき。
    /// requiredFlag が立っていて、blockedByFlag が立っていないときだけ始まる。
    /// </summary>
    [RequireComponent(typeof(Cutscene))]
    public class CutsceneTrigger : MonoBehaviour
    {
        public enum When { AreaEnter, Touch, Flag }

        [SerializeField] When when = When.AreaEnter;
        [SerializeField, Tooltip("AreaEnter：このエリアに入ったとき")] string areaId;
        [SerializeField, Tooltip("Touch：この範囲（ワールド座標）に入ったとき")] Rect touchArea;
        [SerializeField] string requiredFlag;
        [SerializeField] string blockedByFlag;
        [SerializeField, Tooltip("Flag：このフラグが立ったとき")] string watchFlag;

        Cutscene cutscene;
        PlayerController player;
        bool pending;   // 別の演出の最中に条件がそろった：その演出が終わってから始める

        public void Configure(When start, string area = null, Rect? touch = null, string required = null, string blocked = null, string watch = null)
        {
            when = start;
            areaId = area;
            if (touch.HasValue) touchArea = touch.Value;
            requiredFlag = required;
            blockedByFlag = blocked;
            watchFlag = watch;
        }

        void Awake() => cutscene = GetComponent<Cutscene>();

        void Start()
        {
            player = FindObjectOfType<PlayerController>();
            if (AreaManager.Instance != null)
                AreaManager.Instance.Entered += OnEntered;
            GameFlags.Changed += OnFlag;
            // エリアが先に決まっていた場合（最初のエリア）
            if (when == When.AreaEnter && AreaManager.Instance != null && AreaManager.Instance.Current != null)
                OnEntered(AreaManager.Instance.Current);
        }

        void OnDestroy()
        {
            if (AreaManager.Instance != null)
                AreaManager.Instance.Entered -= OnEntered;
            GameFlags.Changed -= OnFlag;
        }

        bool Allowed() =>
            (string.IsNullOrEmpty(requiredFlag) || GameFlags.Has(requiredFlag))
            && (string.IsNullOrEmpty(blockedByFlag) || !GameFlags.Has(blockedByFlag))
            && !cutscene.IsDone;

        void OnEntered(Area area)
        {
            if (when == When.AreaEnter && area.Id == areaId && Allowed())
                Begin();
        }

        void OnFlag(string flag)
        {
            if (when == When.Flag && flag == watchFlag && Allowed())
                Begin();
        }

        void Begin()
        {
            if (Cutscene.IsPlaying)
                pending = true;   // 例：演出の中でエリアを移り、移った先の演出が続く
            else
                cutscene.Play();
        }

        void Update()
        {
            if (pending && !Cutscene.IsPlaying)
            {
                pending = false;
                bool stillHere = when != When.AreaEnter || (AreaManager.Instance != null && AreaManager.Instance.Current != null
                    && AreaManager.Instance.Current.Id == areaId);
                if (stillHere && Allowed())
                    cutscene.Play();
            }

            if (when != When.Touch || player == null || Cutscene.IsPlaying || !player.InputEnabled)
                return;
            if (touchArea.Contains(player.transform.position) && Allowed())
                cutscene.Play();
        }
    }
}
