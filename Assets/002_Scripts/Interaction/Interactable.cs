using System.Collections.Generic;
using BlueNight.Player;
using UnityEngine;

namespace BlueNight.Interaction
{
    /// <summary>調べられるもの（人・ランタン掛け・スイッチなど）の基底。</summary>
    public abstract class Interactable : MonoBehaviour
    {
        public static readonly List<Interactable> All = new List<Interactable>();

        [SerializeField] float range = 1.4f;
        [SerializeField, Tooltip("調べるアイコンを出す位置（足元から）")] Vector2 promptOffset = new Vector2(0f, 2.1f);

        public float Range => range;
        public Vector3 PromptPosition => transform.position + (Vector3)promptOffset;

        public void SetPromptOffset(Vector2 offset) => promptOffset = offset;
        public void SetRange(float distance) => range = distance;

        protected virtual void OnEnable() => All.Add(this);
        protected virtual void OnDisable() => All.Remove(this);

        public virtual bool CanInteract(PlayerInteractor who) => true;

        public abstract void Interact(PlayerInteractor who);
    }
}
