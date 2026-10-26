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
