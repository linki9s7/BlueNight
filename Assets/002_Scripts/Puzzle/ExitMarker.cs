using System.Collections;
using BlueNight.LightShadow;
using BlueNight.Logic;
using UnityEngine;

namespace BlueNight.Puzzle
{
    /// <summary>
    /// 抜け道（E・e）の印。開いている（暗い）ときはうっすら見え、ふさがっている（明るい）ときは薄くなる。
    /// 影に逃げられたら、しばらくぼんやり光る（どこから逃げたかの手がかり）。
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class ExitMarker : MonoBehaviour
    {
        [SerializeField] Sprite open;
        [SerializeField] Sprite closed;
        [SerializeField] Sprite escaped;
        [SerializeField] Vector2Int cell;

        SpriteRenderer spriteRenderer;
        SpriteRenderer glow;
        ShadowWorld world;
        Coroutine glowing;

        public Cell Cell => new Cell(cell.x, cell.y);

        public void Configure(Cell exitCell, Sprite openSprite, Sprite closedSprite, Sprite escapedSprite)
        {
            cell = new Vector2Int(exitCell.X, exitCell.Y);
            open = openSprite;
            closed = closedSprite;
            escaped = escapedSprite;
        }

        void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            var child = new GameObject("Escaped Glow");
            child.transform.SetParent(transform, false);
            glow = child.AddComponent<SpriteRenderer>();
            glow.sprite = escaped;
            glow.sharedMaterial = spriteRenderer.sharedMaterial;
            glow.sortingOrder = spriteRenderer.sortingOrder + 1;
            glow.enabled = false;
        }

        void OnEnable()
        {
            world = ShadowWorld.Instance;
            if (world != null)
                world.Recomputed += Refresh;
            Refresh();
        }

        void OnDisable()
        {
            if (world != null)
                world.Recomputed -= Refresh;
        }

        void Refresh()
        {
            if (spriteRenderer == null || world == null || world.Grid == null)
                return;
            bool isOpen = world.Grid.IsDark(Cell);
            spriteRenderer.sprite = isOpen ? open : closed;
            spriteRenderer.color = isOpen ? Color.white : new Color(1f, 1f, 1f, 0.35f); // ふさがっていると薄く
        }

        /// <summary>逃げた印：ぼんやり光らせて、seconds 秒かけて消す（やり直しのあとも残る）。</summary>
        public void ShowEscaped(float seconds)
        {
            if (glowing != null)
                StopCoroutine(glowing);
            glowing = StartCoroutine(Glow(seconds));
        }

        IEnumerator Glow(float seconds)
        {
            glow.enabled = true;
            for (float t = 0f; t < seconds; t += Time.unscaledDeltaTime)
            {
                float pulse = 0.75f + 0.25f * Mathf.Sin(t * 5f);
                glow.color = new Color(1f, 1f, 1f, pulse * (1f - t / seconds));
                yield return null;
            }
            glow.enabled = false;
            glowing = null;
        }
    }
}
