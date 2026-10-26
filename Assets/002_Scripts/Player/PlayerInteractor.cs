using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.Interaction;
using UnityEngine;

namespace BlueNight.Player
{
    /// <summary>
    /// 近くの調べられるものを選び、頭上にアイコンを出す。決定ボタンで調べ、ランタンボタンでランタン掛けを使う。
    /// 向いている方向にあるものを優先する。
    /// </summary>
    [RequireComponent(typeof(PlayerController))]
    public class PlayerInteractor : MonoBehaviour
    {
        [SerializeField] Lantern lantern;
        [SerializeField] SpriteRenderer promptMarker;
        [SerializeField, Range(0f, 1f)] float facingWeight = 0.4f;

        PlayerController controller;
        PlayerAnimator animator;
        Interactable current;

        public Lantern Lantern => lantern;
        public PlayerController Controller => controller;

        public void Configure(Lantern playerLantern, SpriteRenderer marker)
        {
            lantern = playerLantern;
            promptMarker = marker;
        }

        void Awake()
        {
            controller = GetComponent<PlayerController>();
            animator = GetComponentInChildren<PlayerAnimator>();
        }

        void Update()
        {
            if (DialogueRunner.IsBusy || DialogueRunner.ClosedThisFrame || !controller.InputEnabled)
            {
                SetMarker(null);
                return;
            }

            current = FindBest();
            SetMarker(current);
            if (current == null)
                return;

            if (GameInput.ConfirmPressed || (GameInput.LanternPressed && current is LanternHook))
            {
                // 動き：ランタン掛けは腕をのばして掛ける、人と話すときはそのまま、それ以外はのぞきこむ
                if (animator != null && current is LanternHook)
                    animator.PlayAction(PlayerAnimator.Action.Hang);
                else if (animator != null && !(current is TalkInteractable))
                    animator.PlayAction(PlayerAnimator.Action.Inspect);
                current.Interact(this);
            }
        }

        Interactable FindBest()
        {
            Vector2 facing = FacingVector(controller.Facing);
            Vector2 position = transform.position;
            Interactable best = null;
            float bestScore = float.MaxValue;

            foreach (var target in Interactable.All)
            {
                Vector2 toTarget = (Vector2)target.transform.position - position;
                float distance = toTarget.magnitude;
                if (distance > target.Range || !target.CanInteract(this))
                    continue;
                float alignment = distance > 0.01f ? Vector2.Dot(facing, toTarget / distance) : 1f;
                float score = distance - alignment * facingWeight;
                if (score < bestScore)
                {
                    best = target;
                    bestScore = score;
                }
            }
            return best;
        }

        void SetMarker(Interactable target)
        {
            if (promptMarker == null)
                return;
            promptMarker.enabled = target != null;
            if (target == null)
                return;
            float bob = Mathf.Round(Mathf.Sin(Time.time * 5f) * 1.5f) / 16f;
            promptMarker.transform.position = target.PromptPosition + new Vector3(0f, bob, 0f);
        }

        static Vector2 FacingVector(Facing facing)
        {
            switch (facing)
            {
                case Facing.Up: return Vector2.up;
                case Facing.Left: return Vector2.left;
                case Facing.Right: return Vector2.right;
                default: return Vector2.down;
            }
        }
    }
}
