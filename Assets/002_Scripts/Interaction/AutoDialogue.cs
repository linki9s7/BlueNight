using System.Collections;
using System;
using BlueNight.Core;
using BlueNight.Dialogue;
using UnityEngine;

namespace BlueNight.Interaction
{
    /// <summary>シーンが始まって少ししたら、一度だけ会話を流す（導入・チュートリアル用）。</summary>
    public class AutoDialogue : MonoBehaviour
    {
        [SerializeField] float delay = 0.8f;
        [SerializeField] string setsFlag;
        [SerializeField] DialogueLine[] lines = Array.Empty<DialogueLine>();

        public void Configure(string flag, params DialogueLine[] dialogue)
        {
            setsFlag = flag;
            lines = dialogue;
        }

        IEnumerator Start()
        {
            if (GameFlags.Has(setsFlag))
                yield break;
            yield return new WaitForSeconds(delay);
            while (DialogueRunner.IsBusy)
                yield return null;
            if (DialogueRunner.Instance != null)
                DialogueRunner.Instance.Play(lines, () => GameFlags.Set(setsFlag));
        }
    }
}
