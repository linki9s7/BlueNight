using System;
using UnityEngine;

namespace BlueNight.Rendering
{
    /// <summary>
    /// 演出で動かす人（回想の 8 歳のルリとミオ）のアニメーション。動いた向きで「走る（右・左）」、止まると「立つ」の絵にする。
    /// 足元の影（shadow）も同じコマで動かす。sit の絵があれば、最初に動き出すまでは座っている。
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class ActorAnimator : MonoBehaviour
    {
        [Serializable]
        public class Frames
        {
            public Sprite[] idle = Array.Empty<Sprite>();
            public Sprite[] runRight = Array.Empty<Sprite>();
            public Sprite[] runLeft = Array.Empty<Sprite>();
            public Sprite[] sit = Array.Empty<Sprite>();
        }

        [SerializeField] Frames body = new Frames();
        [SerializeField] Frames shadow = new Frames();
        [SerializeField] SpriteRenderer shadowRenderer;
        [SerializeField] float runFps = 10f;
        [SerializeField] float idleFps = 2f;

        SpriteRenderer spriteRenderer;
        Vector3 lastPosition;
        float time;
        bool sitting;
        bool facingLeft;
        float stillTime;

        public void Configure(Frames bodyFrames, Frames shadowFrames, SpriteRenderer shadowSprite)
        {
            body = bodyFrames;
            shadow = shadowFrames;
            shadowRenderer = shadowSprite;
        }

        void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            lastPosition = transform.position;
        }

        void OnEnable()
        {
            sitting = body.sit.Length > 0;
            lastPosition = transform.position;
        }

        void LateUpdate()
        {
            time += Time.deltaTime;
            Vector3 delta = transform.position - lastPosition;
            lastPosition = transform.position;
            bool moving = delta.sqrMagnitude > 0.000001f;
            if (moving)
            {
                sitting = false;
                stillTime = 0f;
                if (Mathf.Abs(delta.x) > 0.0001f)
                    facingLeft = delta.x < 0f;
            }
            else
            {
                stillTime += Time.deltaTime;
            }

            Sprite[] frames, shadowFrames;
            float fps;
            if (sitting)
            {
                frames = body.sit; shadowFrames = shadow.sit; fps = idleFps;
            }
            else if (moving || stillTime < 0.08f)   // 1 フレームだけ止まっても走る絵のまま（ちらつかない）
            {
                frames = facingLeft ? body.runLeft : body.runRight;
                shadowFrames = facingLeft ? shadow.runLeft : shadow.runRight;
                fps = runFps;
            }
            else
            {
                frames = body.idle; shadowFrames = shadow.idle; fps = idleFps;
            }
            if (frames.Length == 0)
                return;
            int i = (int)(time * fps) % frames.Length;
            spriteRenderer.sprite = frames[i];
            if (shadowRenderer != null)
            {
                shadowRenderer.enabled = shadowFrames.Length > 0;
                if (shadowFrames.Length > 0)
                    shadowRenderer.sprite = shadowFrames[i % shadowFrames.Length];
            }
        }
    }
}
