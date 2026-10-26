using System;
using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.Player;
using UnityEngine;

namespace BlueNight.Interaction
{
    /// <summary>話しかけると会話が始まる。フラグに応じて内容が変わる。</summary>
    public class TalkInteractable : Interactable
    {
        [SerializeField] ConditionalDialogue[] dialogues = Array.Empty<ConditionalDialogue>();

        public void Configure(params ConditionalDialogue[] entries) => dialogues = entries;

        public override bool CanInteract(PlayerInteractor who) => Pick() != null;

        public override void Interact(PlayerInteractor who)
        {
            var entry = Pick();
            if (entry == null || DialogueRunner.Instance == null)
                return;
            DialogueRunner.Instance.Play(entry.lines, () => GameFlags.Set(entry.setsFlag));
        }

        ConditionalDialogue Pick()
        {
            foreach (var entry in dialogues)
            {
                if (!string.IsNullOrEmpty(entry.requiresFlag) && !GameFlags.Has(entry.requiresFlag))
                    continue;
                if (!string.IsNullOrEmpty(entry.unlessFlag) && GameFlags.Has(entry.unlessFlag))
                    continue;
                return entry;
            }
            return null;
        }
    }
}
