using System;
using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.LightShadow;
using BlueNight.Logic;
using BlueNight.Rendering;
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
        [SerializeField, Tooltip("その場でゆらゆらしているとき")] Sprite[] frames = Array.Empty<Sprite>();
        [SerializeField] float fps = 6f;
        [Header("動き（任意）")]
        [SerializeField] Sprite[] moveDown = Array.Empty<Sprite>();
        [SerializeField] Sprite[] moveUp = Array.Empty<Sprite>();
        [SerializeField] Sprite[] moveLeft = Array.Empty<Sprite>();
        [SerializeField] Sprite[] moveRight = Array.Empty<Sprite>();
        [SerializeField] float moveFps = 10f;
        [SerializeField, Tooltip("ルリが近づいたとき、びくっとする")] Sprite[] surprised = Array.Empty<Sprite>();
        [SerializeField] float surpriseDistance = 2.5f;
        [SerializeField] float surpriseCooldown = 5f;
        [SerializeField, Tooltip("捕まったとき、じたばたして光る")] Sprite[] caught = Array.Empty<Sprite>();
        [SerializeField] Sprite[] captureEffect = Array.Empty<Sprite>();
        [SerializeField] Sprite[] returnEffect = Array.Empty<Sprite>();
        [SerializeField] Material effectMaterial;
        [SerializeField] DialogueLine[] captureLines = Array.Empty<DialogueLine>();
        [SerializeField] string capturedFlag = "shadow_captured";
        [SerializeField] string returnedFlag = "shadow_returned";
        [SerializeField, Tooltip("触れると捕まらずに逃げていく（第 1 章の路地その 1：塀を越えて奥の路地へ）")] bool escapeOnTouch;

        SpriteRenderer spriteRenderer;
        ShadowWorld world;
        State state = State.Fleeing;
        Cell current;
        Cell target;
        float animTime;
        Vector3 followVelocity;
        Vector3 lastPosition;
        Vector2 moveDirection = Vector2.down;
        Sprite[] oneShot;
        float oneShotTime;
        float surpriseTimer;

        /// <summary>ルリが近づいて、びくっとしたとき（音を鳴らすのに使う）。</summary>
        public event Action Surprised;
        /// <summary>捕まったとき。</summary>
        public event Action Captured;
        /// <summary>触れたのに逃げられたとき（escapeOnTouch）。</summary>
        public event Action Escaped;

        /// <summary>触れると捕まらずに逃げていく影にする。逃げたら capturedFlag を立てる。</summary>
        public void SetEscapeOnTouch(bool escape) => escapeOnTouch = escape;

        public bool IsFleeing => state == State.Fleeing;
        public bool IsSpeaking => state == State.Speaking;
        public bool IsGone => state == State.Gone || state == State.Returning;

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

        /// <summary>動きと演出のコマ（無くても動く：その場合は frames だけで再生する）。</summary>
        public void ConfigureAnimations(Sprite[] down, Sprite[] up, Sprite[] left, Sprite[] right,
            Sprite[] surprisedFrames, Sprite[] caughtFrames, Sprite[] captureFx, Sprite[] returnFx, Material fxMaterial)
        {
            moveDown = down;
            moveUp = up;
            moveLeft = left;
            moveRight = right;
            surprised = surprisedFrames;
            caught = caughtFrames;
            captureEffect = captureFx;
            returnEffect = returnFx;
            effectMaterial = fxMaterial;
        }

        void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            lastPosition = transform.position;
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
            Vector3 delta = transform.position - lastPosition;
            lastPosition = transform.position;
            bool moving = delta.sqrMagnitude > 0.000001f;
            if (moving)
                moveDirection = delta;

            // びくっ・じたばた（1 回だけ）
            if (oneShot != null)
            {
                oneShotTime += Time.deltaTime;
                int frame = (int)(oneShotTime * 10f);
                if (frame < oneShot.Length)
                {
                    spriteRenderer.sprite = oneShot[frame];
                    return;
                }
                oneShot = null;
            }

            Sprite[] set = moving ? MoveFrames() : frames;
            if (set == null || set.Length == 0)
                set = frames;
            if (set.Length == 0)
                return;
            animTime += Time.deltaTime;
            spriteRenderer.sprite = set[(int)(animTime * (moving ? moveFps : fps)) % set.Length];
        }

        Sprite[] MoveFrames()
        {
            if (Mathf.Abs(moveDirection.x) > Mathf.Abs(moveDirection.y))
                return moveDirection.x < 0f ? moveLeft : moveRight;
            return moveDirection.y > 0f ? moveUp : moveDown;
        }

        void PlayOnce(Sprite[] shot)
        {
            if (shot == null || shot.Length == 0)
                return;
            oneShot = shot;
            oneShotTime = 0f;
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
                // 向きの絵が無いときだけ、左右を反転して向きを見せる（影には陰影が無いので反転してよい）
                if (target.X != current.X && moveLeft.Length == 0)
                    spriteRenderer.flipX = target.X < current.X;
            }

            float distance = Vector2.Distance(transform.position, player.position);
            surpriseTimer -= Time.deltaTime;
            if (distance <= surpriseDistance && surpriseTimer <= 0f)
            {
                PlayOnce(surprised);
                surpriseTimer = surpriseCooldown;
                Surprised?.Invoke();
            }

            if (distance <= touchDistance)
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
            if (escapeOnTouch)
            {
                Escape();
                return;
            }
            state = State.Speaking;
            transform.position = player.position + new Vector3(0.9f, 0f, 0f);
            lastPosition = transform.position;
            PlayOnce(caught);
            Captured?.Invoke();
            OneShotEffect.Spawn(captureEffect, transform.position + new Vector3(0f, 1f, 0f), 12f, effectMaterial);
            if (DialogueRunner.Instance != null)
                DialogueRunner.Instance.Play(captureLines, AfterCapture);
            else
                AfterCapture();
        }

        void AfterCapture()
        {
            state = State.Following;
            // エリアを移っても持ち主のところまでついてこられるよう、エリアの子から外す
            transform.SetParent(null, true);
            GameFlags.Set(capturedFlag);
        }

        Vector3 escapeDirection = Vector3.up;

        /// <summary>
        /// 触れたのに逃げられる：びくっとして、会話のあと近くの低い塀を越えて消える
        /// （低い塀の上は暗いので、影は越えられる。高い壁は越えられない）。
        /// </summary>
        void Escape()
        {
            state = State.Speaking;
            PlayOnce(surprised);
            Escaped?.Invoke();
            owner = null;
            escapeDirection = Vector3.up;
            if (world != null && world.Map != null)
            {
                foreach (var d in new[] { new Cell(0, 1), new Cell(1, 0), new Cell(-1, 0), new Cell(0, -1),
                                          new Cell(1, 1), new Cell(-1, 1), new Cell(1, -1), new Cell(-1, -1) })
                {
                    if (GridMap.IsLowFence(world.Map.At(current + d)))
                    {
                        escapeDirection = new Vector3(d.X, d.Y, 0f).normalized;
                        break;
                    }
                }
            }
            if (DialogueRunner.Instance != null)
                DialogueRunner.Instance.Play(captureLines, AfterEscape);
            else
                AfterEscape();
        }

        void AfterEscape()
        {
            state = State.Returning;
            GameFlags.Set(capturedFlag);
        }

        void UpdateFollowing()
        {
            if (player == null)
                return;
            // ルリの少し後ろを、ゆっくりついてくる。エリアを移ったら（遠く離れたら）すぐそばへ
            Vector3 goal = player.position + new Vector3(-0.9f, 0.1f, 0f);
            if ((goal - transform.position).sqrMagnitude > 36f)
            {
                transform.position = goal;
                followVelocity = Vector3.zero;
            }
            transform.position = Vector3.SmoothDamp(transform.position, goal, ref followVelocity, 0.4f);
        }

        void OnFlagChanged(string flag)
        {
            if (flag == returnedFlag && (state == State.Following || state == State.Speaking))
                state = State.Returning;
        }

        void UpdateReturning()
        {
            // 持ち主の足元へ帰る。持ち主がいない（逃げていく）ときは、塀を越えて上へ
            Vector3 goal = owner != null ? owner.position : transform.position + escapeDirection;
            transform.position = Vector3.MoveTowards(transform.position, goal, 2.5f * Time.deltaTime);

            var c = spriteRenderer.color;
            c.a = Mathf.MoveTowards(c.a, 0f, Time.deltaTime * 0.6f);
            spriteRenderer.color = c;

            if (c.a <= 0f)
            {
                if (owner != null)
                    OneShotEffect.Spawn(returnEffect, owner.position + new Vector3(0f, 1f, 0f), 8f, effectMaterial);
                state = State.Gone;
                gameObject.SetActive(false);
            }
        }
    }
}
