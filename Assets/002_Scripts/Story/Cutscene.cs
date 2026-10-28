using System.Collections;
using BlueNight.Audio;
using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.Player;
using BlueNight.Rendering;
using BlueNight.World;
using UnityEngine;

namespace BlueNight.Story
{
    /// <summary>
    /// 演出の台本（会話・歩かせる・待つ・フラグ・曲・暗転…を順に）。始まり方は CutsceneTrigger で決める。
    /// 演出のあいだはルリの操作を止める。一度きりの演出は doneFlag を立てて、二度と始まらないようにする。
    /// </summary>
    public class Cutscene : MonoBehaviour
    {
        /// <summary>演出中は true（調べる・メニューを止める）。</summary>
        public static bool IsPlaying { get; private set; }

        [SerializeField] CutsceneStep[] steps = new CutsceneStep[0];
        [SerializeField, Tooltip("終わったら立てるフラグ（空なら何度でも）")] string doneFlag;

        PlayerController player;

        public string DoneFlag => doneFlag;
        public bool IsDone => !string.IsNullOrEmpty(doneFlag) && GameFlags.Has(doneFlag);

        public void Configure(string flagWhenDone, params CutsceneStep[] script)
        {
            doneFlag = flagWhenDone;
            steps = script;
        }

        public void Play()
        {
            if (IsPlaying || IsDone)
                return;
            StartCoroutine(Run());
        }

        IEnumerator Run()
        {
            IsPlaying = true;
            if (player == null)
                player = FindObjectOfType<PlayerController>();
            if (player != null)
                player.InputEnabled = false;

            foreach (var step in steps)
                yield return RunStep(step);
            // カメラを別の場所に向けたまま終わらないように
            if (CameraFollow2D.Instance != null && CameraFollow2D.Instance.IsLookingAway)
                CameraFollow2D.Instance.LookBack(0.6f);

            if (player != null)
            {
                player.ScriptedMove = null;
                player.InputEnabled = true;
            }
            if (!string.IsNullOrEmpty(doneFlag))
                GameFlags.Set(doneFlag);
            IsPlaying = false;
        }

        IEnumerator RunStep(CutsceneStep step)
        {
            switch (step.kind)
            {
                case CutsceneStep.Kind.Say:
                    if (DialogueRunner.Instance == null)
                        break;
                    bool done = false;
                    DialogueRunner.Instance.Play(step.lines, () => done = true);
                    while (!done)
                        yield return null;
                    if (player != null)
                        player.InputEnabled = false;  // 会話が閉じると操作が戻るので、演出中は止め直す
                    break;

                case CutsceneStep.Kind.Walk:
                    yield return Walk(step);
                    break;

                case CutsceneStep.Kind.Face:
                    if (player != null)
                        player.Face(step.facing);
                    break;

                case CutsceneStep.Kind.Wait:
                    yield return new WaitForSeconds(step.seconds);
                    break;

                case CutsceneStep.Kind.SetFlag:
                    GameFlags.Set(step.text);
                    break;

                case CutsceneStep.Kind.Music:
                    if (MusicDirector.Instance != null)
                    {
                        if (string.IsNullOrEmpty(step.text))
                            MusicDirector.Instance.Stop(step.seconds);
                        else
                            MusicDirector.Instance.CrossFade(step.text, step.seconds);
                    }
                    break;

                case CutsceneStep.Kind.Sound:
                    SoundEffects.Play(step.text);
                    break;

                case CutsceneStep.Kind.Show:
                case CutsceneStep.Kind.Hide:
                    if (step.actor != null)
                        step.actor.gameObject.SetActive(step.kind == CutsceneStep.Kind.Show);
                    break;

                case CutsceneStep.Kind.FadeOut:
                    yield return ScreenFader.Get().FadeOut(step.seconds);
                    break;

                case CutsceneStep.Kind.FadeIn:
                    yield return ScreenFader.Get().FadeIn(step.seconds);
                    break;

                case CutsceneStep.Kind.GoArea:
                    if (AreaManager.Instance != null)
                    {
                        var area = AreaManager.Instance.Find(step.text);
                        if (area != null)
                            yield return AreaManager.Instance.GoRoutine(area, step.area2);
                        if (player != null)
                            player.InputEnabled = false;
                    }
                    break;

                case CutsceneStep.Kind.Effect:
                    var at = step.actor != null ? step.actor : player != null ? player.transform : transform;
                    OneShotEffect.Spawn(step.frames, at.position + new Vector3(0f, 1f, 0f), 10f, null);
                    break;

                case CutsceneStep.Kind.AutoSave:
                    AreaManager.Instance?.AutoSave();
                    break;

                case CutsceneStep.Kind.Ambience:
                    AmbiencePlayer.Instance?.Set(step.text, step.volume, step.seconds);
                    break;

                case CutsceneStep.Kind.WalkAsync:
                    StartCoroutine(Walk(step));
                    break;

                case CutsceneStep.Kind.Memory:
                    MemoryEffect.Instance?.FadeTo(step.volume, step.seconds);
                    break;

                case CutsceneStep.Kind.Camera:
                    if (CameraFollow2D.Instance != null)
                    {
                        if (step.volume > 0f)
                            CameraFollow2D.Instance.LookAt(step.position, step.seconds);
                        else
                            CameraFollow2D.Instance.LookBack(step.seconds);
                    }
                    break;

                case CutsceneStep.Kind.Alpha:
                    if (step.actor != null && step.actor.TryGetComponent<SpriteRenderer>(out var sprite))
                        StartCoroutine(FadeSprite(sprite, step.volume, step.seconds));
                    break;

                case CutsceneStep.Kind.PlayerVisible:
                    if (player != null)
                    {
                        bool show = step.volume > 0f;
                        foreach (var r in player.GetComponentsInChildren<Renderer>(true))
                            r.enabled = show;
                        foreach (var l in player.GetComponentsInChildren<UnityEngine.Rendering.Universal.Light2D>(true))
                            l.enabled = show;
                    }
                    break;
            }
        }

        static IEnumerator FadeSprite(SpriteRenderer sprite, float alpha, float seconds)
        {
            float from = sprite.color.a;
            for (float t = 0f; t < seconds; t += Time.deltaTime)
            {
                var c = sprite.color;
                c.a = Mathf.Lerp(from, alpha, t / seconds);
                sprite.color = c;
                yield return null;
            }
            var end = sprite.color;
            end.a = alpha;
            sprite.color = end;
        }

        IEnumerator Walk(CutsceneStep step)
        {
            Vector3 goal = step.target != null ? step.target.position : (Vector3)step.position;
            bool isPlayer = step.actor == null || (player != null && step.actor == player.transform);
            var who = isPlayer && player != null ? player.transform : step.actor;
            if (who == null)
                yield break;

            float timeout = 10f;
            // 何かに引っかかって進めなくなったら（0.6 秒ほとんど近づかない）、そこで止める（ぶつかったまま歩き続けない）
            float best = ((Vector2)(goal - who.position)).magnitude;
            float stuck = 0f;
            while (((Vector2)(goal - who.position)).sqrMagnitude > 0.01f && timeout > 0f && stuck < 0.6f)
            {
                timeout -= Time.deltaTime;
                float now = ((Vector2)(goal - who.position)).magnitude;
                if (now < best - 0.02f)
                {
                    best = now;
                    stuck = 0f;
                }
                else
                {
                    stuck += Time.deltaTime;
                }
                Vector2 dir = ((Vector2)(goal - who.position)).normalized;
                if (isPlayer && player != null)
                {
                    // ルリは入力として歩かせる（歩きのアニメーション・足音がそのまま使える）
                    player.ScriptedMove = dir * Mathf.Clamp01(step.speed / 3.5f);
                }
                else
                {
                    who.position = Vector3.MoveTowards(who.position, goal, step.speed * Time.deltaTime);
                }
                yield return null;
            }
            if (isPlayer && player != null)
                player.ScriptedMove = null;
        }
    }
}
