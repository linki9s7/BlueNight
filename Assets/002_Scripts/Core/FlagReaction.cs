using System;
using BlueNight.Rendering;
using UnityEngine;

namespace BlueNight.Core
{
    /// <summary>
    /// フラグが立ったら、ものを出す・消す・アニメーションを差し替える。
    /// 例：影が戻ったおばあさんの足元に影を出し、居眠りのアニメーションにする。
    /// </summary>
    public class FlagReaction : MonoBehaviour
    {
        [SerializeField] string flag;
        [SerializeField, Tooltip("このフラグが立っていたら何もしない（空なら条件なし）")] string unlessFlag;
        [SerializeField] GameObject[] activate = Array.Empty<GameObject>();
        [SerializeField] GameObject[] deactivate = Array.Empty<GameObject>();
        [SerializeField] SimpleSpriteAnimator animator;
        [SerializeField] Sprite[] newFrames = Array.Empty<Sprite>();
        [SerializeField] float newFps = 1f;

        public void Configure(string flagName, GameObject[] show, GameObject[] hide, SimpleSpriteAnimator target, Sprite[] frames, float fps,
            string unless = null)
        {
            flag = flagName;
            unlessFlag = unless;
            activate = show ?? Array.Empty<GameObject>();
            deactivate = hide ?? Array.Empty<GameObject>();
            animator = target;
            newFrames = frames ?? Array.Empty<Sprite>();
            newFps = fps;
        }

        void Start()
        {
            GameFlags.Changed += OnChanged;
            if (GameFlags.Has(flag))
                Apply();
        }

        void OnDestroy()
        {
            GameFlags.Changed -= OnChanged;
        }

        void OnChanged(string changed)
        {
            if (changed == flag)
                Apply();
        }

        void Apply()
        {
            if (!string.IsNullOrEmpty(unlessFlag) && GameFlags.Has(unlessFlag))
                return;
            foreach (var go in activate)
                if (go != null) go.SetActive(true);
            foreach (var go in deactivate)
                if (go != null) go.SetActive(false);
            if (animator != null && newFrames.Length > 0)
                animator.Configure(newFrames, newFps);
        }
    }
}
