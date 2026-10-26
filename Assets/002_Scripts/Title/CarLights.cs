using System.Collections.Generic;
using UnityEngine;

namespace BlueNight.Title
{
    /// <summary>
    /// タイトルの高架ハイウェイを流れる車の光。前照灯は右から左、尾灯は左から右へ。
    /// 位置は 1 ドット単位にそろえる（ドットの大きさを混ぜない）。
    /// </summary>
    public class CarLights : MonoBehaviour
    {
        [SerializeField] Sprite headlight;
        [SerializeField] Sprite taillight;
        [SerializeField, Tooltip("道路の左端・右端（ワールド座標）。前照灯の車線")] Vector2 laneLeft = new Vector2(-15f, -1.5f);
        [SerializeField] Vector2 laneRight = new Vector2(15f, -2.6f);
        [SerializeField, Tooltip("尾灯の車線は前照灯の車線から下へ何ドットか")] int tailLaneOffsetPx = 3;
        [SerializeField] int cars = 6;
        [SerializeField] Vector2 speedRange = new Vector2(1.2f, 2.2f);
        [SerializeField] Material material;

        class Car { public Transform t; public float u; public float speed; public bool head; }
        readonly List<Car> list = new List<Car>();

        public void Configure(Sprite head, Sprite tail, Vector2 left, Vector2 right, Material spriteMaterial)
        {
            headlight = head;
            taillight = tail;
            laneLeft = left;
            laneRight = right;
            material = spriteMaterial;
        }

        void Start()
        {
            var random = new System.Random(4);
            for (int i = 0; i < cars; i++)
            {
                bool head = i % 2 == 0;
                var go = new GameObject(head ? "Headlight" : "Taillight");
                go.transform.SetParent(transform, false);
                var r = go.AddComponent<SpriteRenderer>();
                r.sprite = head ? headlight : taillight;
                r.sortingOrder = 5;
                if (material != null)
                    r.sharedMaterial = material;
                float length = Vector2.Distance(laneLeft, laneRight);
                list.Add(new Car
                {
                    t = go.transform,
                    u = (float)random.NextDouble(),
                    speed = Mathf.Lerp(speedRange.x, speedRange.y, (float)random.NextDouble()) / length,
                    head = head,
                });
            }
        }

        void Update()
        {
            foreach (var car in list)
            {
                car.u = Mathf.Repeat(car.u + (car.head ? -1f : 1f) * car.speed * Time.unscaledDeltaTime, 1f);
                Vector2 p = Vector2.Lerp(laneLeft, laneRight, car.u);
                if (!car.head)
                    p.y -= tailLaneOffsetPx / 16f;
                car.t.position = new Vector3(Mathf.Round(p.x * 16f) / 16f, Mathf.Round(p.y * 16f) / 16f, 0f);
            }
        }
    }
}
