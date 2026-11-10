using System.Collections;
using BlueNight.Audio;
using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.Interaction;
using BlueNight.LightShadow;
using BlueNight.Logic;
using BlueNight.Player;
using BlueNight.Shadows;
using UnityEngine;

namespace BlueNight.Puzzle
{
    /// <summary>
    /// 第 2 章の追いかけっこ 1 つぶん。最初の状態を覚え、やり直し（R）と「逃げられた」演出をまとめる。
    /// 逃げられたとき：止まる・ゆっくり・カメラが抜け道へ → 影が消える → 抜け道に印・ネムの一言 → 暗転して最初に戻る。
    /// 自分でやり直すときは、暗転して戻るだけ（設計書 3.1）。
    /// </summary>
    public class ChasePuzzle : MonoBehaviour
    {
        /// <summary>演出中。やり直し・見渡すを受けつけない。</summary>
        public static bool IsBusy { get; private set; }

        [SerializeField] RunawayShadow shadow;
        [SerializeField] PlayerController player;
        [SerializeField] Lantern lantern;
        [SerializeField] LightSwitch[] switches = new LightSwitch[0];
        [SerializeField] ExitMarker[] exits = new ExitMarker[0];
        [SerializeField] DialogueLine[] escapeLines = new DialogueLine[0];
        [SerializeField] DialogueLine[] hintLines = new DialogueLine[0];
        [SerializeField, Tooltip("追いかけっこを始めてからこの秒数捕まえられずにいたら、ネムがやり直しをすすめる")] float hintAfterSeconds = 60f;
        [SerializeField, Tooltip("ネムの一言を出すのは、逃げられた最初の何回か")] int escapeLinesTimes = 2;

        public int EscapeCount { get; private set; }

        bool started;
        bool solved;
        Vector3 playerStart;
        Facing playerFacing;
        float chaseSeconds;
        bool hintShown;

        public void Configure(RunawayShadow chaseShadow, PlayerController ruri, Lantern ruriLantern, LightSwitch[] lights,
            ExitMarker[] exitMarkers, DialogueLine[] onEscape, DialogueLine[] hint)
        {
            shadow = chaseShadow;
            player = ruri;
            lantern = ruriLantern;
            switches = lights;
            exits = exitMarkers;
            escapeLines = onEscape;
            hintLines = hint;
        }

        void OnEnable()
        {
            if (shadow == null)
                return;
            shadow.ReachedExit += OnReachedExit;
            shadow.Captured += OnCaptured;
        }

        void OnDisable()
        {
            if (shadow != null)
            {
                shadow.ReachedExit -= OnReachedExit;
                shadow.Captured -= OnCaptured;
            }
            Time.timeScale = 1f;
            IsBusy = false;
        }

        void OnCaptured() => solved = true;

        void Update()
        {
            if (!started)
            {
                started = true;
                playerStart = player.transform.position;
                playerFacing = player.Facing;
            }
            if (!CanAct)
                return;

            if (GameInput.ResetPressed && TryReset())
                return;

            if (!shadow.IsWaiting)
                chaseSeconds += Time.deltaTime;
            if (!hintShown && chaseSeconds >= hintAfterSeconds && hintLines.Length > 0 && DialogueRunner.Instance != null)
            {
                hintShown = true;
                DialogueRunner.Instance.Play(hintLines);
            }
        }

        /// <summary>やり直し・ヒントを受けつけてよいか（捕まえたあと・演出中・会話中・見渡している間は受けつけない）。</summary>
        bool CanAct => !solved && !IsBusy && !DialogueRunner.IsBusy && !GamePause.IsPaused;

        /// <summary>やり直しボタン（R）。受けつけたら true。</summary>
        public bool TryReset()
        {
            if (!started || !CanAct)
                return false;
            StartCoroutine(ManualReset());
            return true;
        }

        void OnReachedExit(Cell cell)
        {
            if (!IsBusy)
                StartCoroutine(EscapeScene(cell));
        }

        IEnumerator ManualReset()
        {
            IsBusy = true;
            player.InputEnabled = false;
            yield return FadeAndRestore();
            IsBusy = false;
            player.InputEnabled = true;
        }

        IEnumerator EscapeScene(Cell cell)
        {
            IsBusy = true;
            player.InputEnabled = false;
            bool talk = EscapeCount < escapeLinesTimes;
            bool quick = EscapeCount > 0;
            EscapeCount++;

            var world = ShadowWorld.Instance;
            var camera = CameraFollow2D.Instance;
            if (camera != null && world != null)
                camera.LookAt(world.CellToWorld(cell), 0.35f);

            // 1. 止まる・少しゆっくり（決定ボタンで飛ばせる）
            bool skipped = false;
            Time.timeScale = 0.35f;
            float end = quick ? 0.3f : 0.6f;
            for (float t = 0f; t < end && !skipped; t += Time.unscaledDeltaTime)
            {
                yield return null;
                skipped = GameInput.ConfirmPressed;
            }
            Time.timeScale = 1f;

            // 2. 影が抜け道を越えて消えていく
            if (!skipped)
            {
                bool gone = false;
                SoundEffects.Play("shadow_escape");
                shadow.EscapeThroughExit(() => gone = true);
                while (!gone && !skipped)
                {
                    yield return null;
                    skipped = GameInput.ConfirmPressed;
                }
            }

            // 3. 逃げた抜け道に印・ネムの一言
            var marker = FindMarker(cell);
            if (marker != null)
                marker.ShowEscaped(6f);
            if (!skipped && talk && escapeLines.Length > 0 && DialogueRunner.Instance != null)
            {
                bool closed = false;
                DialogueRunner.Instance.Play(escapeLines, () => closed = true);
                while (!closed)
                    yield return null;
                player.InputEnabled = false; // 会話が閉じると操作が戻るので、演出中は止め直す
            }

            // 4. 暗転して最初に戻る
            yield return FadeAndRestore();
            if (camera != null)
                camera.LookBack(0.2f);
            IsBusy = false;
            player.InputEnabled = true;
        }

        IEnumerator FadeAndRestore()
        {
            var fader = ScreenFader.Get();
            yield return fader.FadeOut(0.35f);
            Restore();
            yield return new WaitForSecondsRealtime(0.1f);
            yield return fader.FadeIn(0.35f);
        }

        void Restore()
        {
            if (lantern != null && !lantern.IsCarried)
                lantern.TakeBack();
            foreach (var light in switches)
                if (light != null)
                    light.ResetToInitial();
            shadow.ResetTo(shadow.StartCell);

            player.transform.position = playerStart;
            if (player.TryGetComponent<Rigidbody2D>(out var body))
            {
                body.position = playerStart;
                body.velocity = Vector2.zero;
            }
            player.Face(playerFacing);
            foreach (var nemu in FindObjectsOfType<NemuFollower>())
                nemu.SnapToTarget();          // ネムもルリのそばへ（飛んで戻ってくると、戻ったことが分かりにくい）
            var camera = CameraFollow2D.Instance;
            if (camera != null)
            {
                camera.LookBack(-1f);
                camera.SnapToTarget();
            }

            chaseSeconds = 0f;
            hintShown = false;
        }

        ExitMarker FindMarker(Cell cell)
        {
            foreach (var marker in exits)
                if (marker != null && marker.Cell == cell)
                    return marker;
            return null;
        }
    }
}
