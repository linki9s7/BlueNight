using System;
using UnityEngine;

namespace BlueNight.Dialogue
{
    [Serializable]
    public class DialogueLine
    {
        public string speaker;
        [TextArea(2, 4)] public string text;
        [Tooltip("逃げた影の声（白抜き・揺れる表示）")] public bool shadowVoice;

        public DialogueLine() { }

        public DialogueLine(string speaker, string text, bool shadowVoice = false)
        {
            this.speaker = speaker;
            this.text = text;
            this.shadowVoice = shadowVoice;
        }
    }

    /// <summary>フラグの状態で出し分ける会話。上から順に、条件に合う最初のものが使われる。</summary>
    [Serializable]
    public class ConditionalDialogue
    {
        [Tooltip("このフラグが立っているときだけ（空なら条件なし）")] public string requiresFlag;
        [Tooltip("このフラグが立っていたら使わない（空なら条件なし）")] public string unlessFlag;
        [Tooltip("会話が終わったら立てるフラグ")] public string setsFlag;
        public DialogueLine[] lines = Array.Empty<DialogueLine>();
    }
}
