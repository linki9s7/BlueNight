using System;
using BlueNight.Dialogue;
using BlueNight.Player;
using UnityEngine;

namespace BlueNight.Story
{
    /// <summary>演出の台本の 1 行。種類（kind）によって使う欄が変わる。</summary>
    [Serializable]
    public class CutsceneStep
    {
        public enum Kind
        {
            Say,        // lines を会話で出す
            Walk,       // actor（空ならルリ）を target / position まで歩かせる
            Face,       // ルリの向きを facing にする
            Wait,       // seconds 秒待つ
            SetFlag,    // text のフラグを立てる
            Music,      // text の曲へ seconds 秒でクロスフェード（空なら止める）
            Sound,      // text の効果音
            Show,       // actor を出す
            Hide,       // actor を消す
            FadeOut,    // 暗転（seconds 秒）
            FadeIn,     // 明転（seconds 秒）
            GoArea,     // text のエリアの area2 の入口へ（暗転つき）
            Effect,     // frames を actor（空ならルリ）の位置に 1 回出す
            AutoSave,   // いまの場所でオートセーブ
            Ambience,   // 環境音 text を volume まで seconds 秒で（雨の降り出しなど）
        }

        public Kind kind;
        public DialogueLine[] lines = new DialogueLine[0];
        public Transform actor;
        public Transform target;
        public Vector2 position;
        public float speed = 3f;
        public Facing facing;
        public float seconds = 1f;
        public string text;
        public string area2;
        public float volume;
        public Sprite[] frames = new Sprite[0];

        // ---- 台本を書くための短い作り方（エディタのシーン作成で使う）
        public static CutsceneStep Say(params DialogueLine[] l) => new CutsceneStep { kind = Kind.Say, lines = l };
        public static CutsceneStep WalkTo(Vector2 p, float s = 3f, Transform who = null) => new CutsceneStep { kind = Kind.Walk, position = p, speed = s, actor = who };
        public static CutsceneStep WalkTo(Transform t, float s = 3f, Transform who = null) => new CutsceneStep { kind = Kind.Walk, target = t, speed = s, actor = who };
        public static CutsceneStep FaceTo(Facing f) => new CutsceneStep { kind = Kind.Face, facing = f };
        public static CutsceneStep WaitFor(float s) => new CutsceneStep { kind = Kind.Wait, seconds = s };
        public static CutsceneStep Flag(string flag) => new CutsceneStep { kind = Kind.SetFlag, text = flag };
        public static CutsceneStep MusicTo(string track, float s = 3f) => new CutsceneStep { kind = Kind.Music, text = track, seconds = s };
        public static CutsceneStep Sfx(string name) => new CutsceneStep { kind = Kind.Sound, text = name };
        public static CutsceneStep ShowActor(Transform t) => new CutsceneStep { kind = Kind.Show, actor = t };
        public static CutsceneStep HideActor(Transform t) => new CutsceneStep { kind = Kind.Hide, actor = t };
        public static CutsceneStep Fade(bool toDark, float s = 0.6f) => new CutsceneStep { kind = toDark ? Kind.FadeOut : Kind.FadeIn, seconds = s };
        public static CutsceneStep Go(string area, string spawn) => new CutsceneStep { kind = Kind.GoArea, text = area, area2 = spawn };
        public static CutsceneStep Fx(Sprite[] f, Transform at = null) => new CutsceneStep { kind = Kind.Effect, frames = f, actor = at };
        public static CutsceneStep Save() => new CutsceneStep { kind = Kind.AutoSave };
        public static CutsceneStep Amb(string name, float vol, float s = 3f) => new CutsceneStep { kind = Kind.Ambience, text = name, volume = vol, seconds = s };
    }
}
