using System;
using System.Collections.Generic;
using UnityEngine;

namespace BlueNight.Core
{
    /// <summary>進行フラグ（謎の解決状況・会話の分岐など）。</summary>
    public static class GameFlags
    {
        static readonly HashSet<string> flags = new HashSet<string>();

        public static event Action<string> Changed;

        public static bool Has(string flag) => !string.IsNullOrEmpty(flag) && flags.Contains(flag);

        /// <summary>いま立っているフラグ（セーブに使う）。</summary>
        public static IEnumerable<string> All => flags;

        /// <summary>セーブから読み込む（Changed は呼ばない）。</summary>
        public static void Load(IEnumerable<string> saved)
        {
            flags.Clear();
            if (saved != null)
                foreach (var flag in saved)
                    if (!string.IsNullOrEmpty(flag))
                        flags.Add(flag);
        }

        public static void Set(string flag)
        {
            if (string.IsNullOrEmpty(flag) || !flags.Add(flag))
                return;
            Changed?.Invoke(flag);
        }

        // ドメインリロードを切っていても、再生のたびに空から始める
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void ResetOnPlay()
        {
            flags.Clear();
            Changed = null;
        }
    }
}
