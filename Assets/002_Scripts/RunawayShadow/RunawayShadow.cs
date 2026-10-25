using System;
using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.LightShadow;
using BlueNight.Logic;
using UnityEngine;

namespace BlueNight.Shadows
{
    /// <summary>
    /// 持ち主から逃げ出した影。暗いマスだけを通ってルリから逃げる。
    /// 追いつめて触れると捕まえられ、持ち主の「言えなかった言葉」を話す。
    /// 返却フラグが立つと、持ち主のもとへ帰っていく。
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class RunawayShadow : MonoBehaviour
    {
        enum State { Fleeing, Speaking, Following, Returning, Gone }

        [SerializeField] Transform player;
        [SerializeField] Transform owner;
        [SerializeField, Tooltip("移動の速さ（マス/秒）。ルリの小走りより速くして、輪の路地では逃げ切れるようにする")] float speed = 6.5f;
        [SerializeField, Tooltip("逃げ方を考えるときに想定するルリの速さ（マス/秒）")] float assumedPlayerSpeed = 6f;
        [SerializeField] float touchDistance = 1.05f;
        [SerializeField] Sprite[] frames = Array.Empty<Sprite>();
        [SerializeField] float fps = 6f;
        [SerializeField] DialogueLine[] captureLines = Array.Empty<DialogueLine>();
        [SerializeField] string capturedFlag = "shadow_captured";
        [SerializeField] string returnedFlag = "shadow_returned";

        SpriteRenderer spriteRenderer;
        ShadowWorld world;
        State state = State.Fleeing;
        Cell current;
        Cell target;
        float animTime;
        Vector3 followVelocity;

        static readonly Vector3 FootOffset = new Vector3(0f, -0.45f, 0f); // マスの中心 → 足元

        public void Configure(Transform playerTransform, Transform ownerTransform, Sprite[] animationFrames,
            DialogueLine[] linesOnCapture, string flagOnCapture, string flagOnReturn)
        {
            player = playerTransform;
            owner = ownerTransform;
            frames = animationFrames;
            captureLines = linesOnCapture;
            capturedFlag = flagOnCapture;
            returnedFlag = flagOnReturn;
        }

        void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
        }

        void Start()
        {
            world = ShadowWorld.Instance;
            current = world.WorldToCell(transform.position);
            target = current;
            transform.position = world.CellToWorld(current) + FootOffset;
            GameFlags.Changed += OnFlagChanged;
        }

        void OnDestroy()
        {
            GameFlags.Changed -= OnFlagChanged;
        }

        void Update()
        {
            Animate();
            switch (state)
            {
                case State.Fleeing: UpdateFleeing(); break;
                case State.Following: UpdateFollowing(); break;
                case State.Returning: UpdateReturning(); break;
            }
        }

        void Animate()
        {
            if (frames.Length == 0)
                return;
            animTime += Time.deltaTime;
            spriteRenderer.sprite = frames[(int)(animTime * fps) % frames.Length];
        }

        // ------------------------------------------------------------------ 逃げる

        void UpdateFleeing()
        {
            if (DialogueRunner.IsBusy || player == null || !world.IsReady)
                return;

            Vector3 goal = world.CellToWorld(target) + FootOffset;
            transform.position = Vector3.MoveTowards(transform.position, goal, speed * Time.deltaTime);
            if ((transform.position - goal).sqrMagnitude < 0.0001f)
            {
                current = target;
                target = ChooseNext();
                if (target.X != current.X)
                    spriteRenderer.flipX = target.X < current.X;
            }

            if (Vector2.Distance(transform.position, player.position) <= touchDistance)
                Capture();
        }

        Cell ChooseNext()
        {
            var grid = world.Grid;
            if (!grid.IsDark(current))
                return grid.StepTowardNearestDark(current); // 光に照らされたら、いちばん近い暗がりへ

            var playerDistances = grid.WalkDistancesFrom(world.WorldToCell(player.position));
            return grid.FleeStep(current, playerDistances, speed / assumedPlayerSpeed);
        }

        // ------------------------------------------------------------------ 捕まる・ついてくる・帰る

        void Capture()
        {
            state = State.Speaking;
            transform.position = player.position + new Vector3(0.9f, 0f, 0f);
            if (DialogueRunner.Instance != null)
                DialogueRunner.Instance.Play(captureLines, AfterCapture);
            else
                AfterCapture();
        }

        void AfterCapture()
        {
            state = State.Following;
            GameFlags.Set(capturedFlag);
        }

        void UpdateFollowing()
        {
            if (player == null)
                return;
            // ルリの少し後ろを、ゆっくりついてくる
            Vector3 goal = player.position + new Vector3(-0.9f, 0.1f, 0f);
            transform.position = Vector3.SmoothDamp(transform.position, goal, ref followVelocity, 0.4f);
        }

        void OnFlagChanged(string flag)
        {
            if (flag == returnedFlag && (state == State.Following || state == State.Speaking))
                state = State.Returning;
        }

        void UpdateReturning()
        {
            Vector3 goal = owner != null ? owner.position : transform.position;
            transform.position = Vector3.MoveTowards(transform.position, goal, 2.5f * Time.deltaTime);

            var c = spriteRenderer.color;
            c.a = Mathf.MoveTowards(c.a, 0f, Time.deltaTime * 0.6f);
            spriteRenderer.color = c;

            if (c.a <= 0f)
            {
                state = State.Gone;
                gameObject.SetActive(false);
            }
        }
    }
}
