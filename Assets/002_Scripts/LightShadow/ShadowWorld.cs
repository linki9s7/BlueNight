using System;
using System.Collections.Generic;
using BlueNight.Logic;
using UnityEngine;
using UnityEngine.Tilemaps;

namespace BlueNight.LightShadow
{
    /// <summary>
    /// 部屋の影グリッドを持ち、光源やモノが動いたら明暗を計算し直して、暗がりのタイルを塗り替える。
    /// マス (0, 0) の左下がワールド座標の origin。
    /// </summary>
    public class ShadowWorld : MonoBehaviour
    {
        public static ShadowWorld Instance { get; private set; }

        [SerializeField, TextArea] string[] mapRows = Array.Empty<string>();
        [SerializeField] Vector2 origin = Vector2.zero;
        [SerializeField] Tilemap overlay;
        [SerializeField] TileBase darkTile;
        [SerializeField] TileBase castShadowTile;

        public GridMap Map { get; private set; }
        public ShadowGrid Grid { get; private set; }

        /// <summary>一度でも明暗を計算したか。</summary>
        public bool IsReady => computed;

        /// <summary>明暗を計算し直したとき。</summary>
        public event Action Recomputed;

        readonly List<GridLight> lights = new List<GridLight>();
        readonly List<GridCaster> casters = new List<GridCaster>();
        int lastSignature;
        bool computed;

        public void Configure(string[] rows, Tilemap overlayTilemap, TileBase dark, TileBase castShadow) =>
            Configure(rows, overlayTilemap, dark, castShadow, Vector2.zero);

        /// <summary>origin：マス (0, 0) の左下のワールド座標（エリアごとに場所をずらすとき）。</summary>
        public void Configure(string[] rows, Tilemap overlayTilemap, TileBase dark, TileBase castShadow, Vector2 worldOrigin)
        {
            origin = worldOrigin;
            mapRows = rows;
            overlay = overlayTilemap;
            darkTile = dark;
            castShadowTile = castShadow;
        }

        void Awake()
        {
            Map = new GridMap(mapRows);
            Grid = Map.CreateGrid();
        }

        // エリアが切り替わると、表示中のエリアの影グリッドが「いまの影グリッド」になる
        void OnEnable()
        {
            Instance = this;
            computed = false;
        }

        void OnDisable()
        {
            if (Instance == this)
                Instance = null;
        }

        void OnDestroy()
        {
            if (Instance == this)
                Instance = null;
        }

        void LateUpdate()
        {
            int signature = Signature();
            if (computed && signature == lastSignature)
                return;
            lastSignature = signature;
            Recompute();
        }

        public Cell WorldToCell(Vector3 position) =>
            new Cell(Mathf.FloorToInt(position.x - origin.x), Mathf.FloorToInt(position.y - origin.y));

        public Vector3 CellToWorld(Cell cell) =>
            new Vector3(origin.x + cell.X + 0.5f, origin.y + cell.Y + 0.5f, 0f);

        public bool IsDarkAt(Vector3 position) => Grid != null && Grid.IsDark(WorldToCell(position));

        /// <summary>光源の位置・点灯状態とモノの位置が変わったときだけ計算し直す。</summary>
        int Signature()
        {
            unchecked
            {
                int hash = 17;
                foreach (var light in GridLightSource.All)
                {
                    var c = WorldToCell(light.Anchor.position);
                    hash = hash * 31 + c.GetHashCode();
                    hash = hash * 31 + (light.On ? 1 : 0);
                    hash = hash * 31 + light.Radius.GetHashCode();
                }
                foreach (var caster in GridShadowCaster.All)
                    hash = hash * 31 + WorldToCell(caster.transform.position).GetHashCode();
                return hash;
            }
        }

        public void Recompute()
        {
            lights.Clear();
            foreach (var source in GridLightSource.All)
            {
                lights.Add(new GridLight
                {
                    Position = WorldToCell(source.Anchor.position),
                    Radius = source.Radius,
                    Height = source.Height,
                    On = source.On && source.isActiveAndEnabled,
                });
            }

            casters.Clear();
            foreach (var source in GridShadowCaster.All)
            {
                var caster = new GridCaster { Height = source.Height };
                var anchor = WorldToCell(source.transform.position);
                for (int y = 0; y < source.Size.y; y++)
                    for (int x = 0; x < source.Size.x; x++)
                        caster.Cells.Add(new Cell(anchor.X + x, anchor.Y + y));
                casters.Add(caster);
            }

            Grid.Compute(lights, casters);
            computed = true;
            UpdateOverlay();
            Recomputed?.Invoke();
        }

        void UpdateOverlay()
        {
            if (overlay == null)
                return;

            var tiles = new TileBase[Grid.Width * Grid.Height];
            for (int y = 0; y < Grid.Height; y++)
            {
                for (int x = 0; x < Grid.Width; x++)
                {
                    var state = Grid.GetState(new Cell(x, y));
                    tiles[y * Grid.Width + x] = state == CellState.Dark ? darkTile
                        : state == CellState.CastShadow ? castShadowTile
                        : null;
                }
            }
            overlay.SetTilesBlock(new BoundsInt(0, 0, 0, Grid.Width, Grid.Height, 1), tiles);
        }

        void OnDrawGizmos()
        {
            if (Grid == null)
                return;
            for (int y = 0; y < Grid.Height; y++)
            {
                for (int x = 0; x < Grid.Width; x++)
                {
                    var state = Grid.GetState(new Cell(x, y));
                    Gizmos.color = state == CellState.Lit ? new Color(1f, 0.8f, 0.3f, 0.25f)
                        : state == CellState.CastShadow ? new Color(0.3f, 0.5f, 1f, 0.35f)
                        : state == CellState.Dark ? new Color(0f, 0f, 0.2f, 0.25f)
                        : new Color(1f, 0f, 0f, 0.15f);
                    Gizmos.DrawCube(CellToWorld(new Cell(x, y)), new Vector3(0.95f, 0.95f, 0f));
                }
            }
        }
    }
}
