using System;
using System.Collections.Generic;

namespace BlueNight.Logic
{
    /// <summary>グリッドのマス座標（16 px = 1 マス）。</summary>
    public readonly struct Cell : IEquatable<Cell>
    {
        public readonly int X;
        public readonly int Y;

        public Cell(int x, int y)
        {
            X = x;
            Y = y;
        }

        public static readonly Cell[] Directions = { new Cell(0, 1), new Cell(1, 0), new Cell(0, -1), new Cell(-1, 0) };

        public static Cell operator +(Cell a, Cell b) => new Cell(a.X + b.X, a.Y + b.Y);
        public static Cell operator -(Cell a, Cell b) => new Cell(a.X - b.X, a.Y - b.Y);
        public static bool operator ==(Cell a, Cell b) => a.X == b.X && a.Y == b.Y;
        public static bool operator !=(Cell a, Cell b) => !(a == b);

        public bool Equals(Cell other) => this == other;
        public override bool Equals(object obj) => obj is Cell other && this == other;
        public override int GetHashCode() => (X * 73856093) ^ (Y * 19349663);
        public override string ToString() => $"({X}, {Y})";

        public float DistanceTo(Cell other)
        {
            float dx = X - other.X, dy = Y - other.Y;
            return (float)Math.Sqrt(dx * dx + dy * dy);
        }
    }

    public enum CellState
    {
        /// <summary>壁・モノ。誰も入れない。</summary>
        Blocked,
        /// <summary>どの光も届かない暗がり。逃げた影が動ける。</summary>
        Dark,
        /// <summary>光が当たっている。逃げた影は入れない。</summary>
        Lit,
        /// <summary>光の届く範囲にあるが、モノの影になっている。逃げた影が動ける。</summary>
        CastShadow,
    }

    public sealed class GridLight
    {
        public Cell Position;
        public float Radius;
        public bool On = true;
        /// <summary>光源の高さ（マス）。影の長さの計算に使う。</summary>
        public float Height = 3f;
    }

    public sealed class GridCaster
    {
        public readonly List<Cell> Cells = new List<Cell>();
        /// <summary>モノの高さ（マス）。高いほど影が長い。</summary>
        public float Height = 1f;
    }

    /// <summary>
    /// 光と影のグリッド。どのマスが明るく、どのマスが暗いかを計算し、
    /// 逃げた影の経路（暗いマスだけを通る）を求める。Unity に依存しない。
    /// </summary>
    public sealed class ShadowGrid
    {
        public const int MaxShadowLength = 8;
        public const int Unreachable = int.MaxValue / 4;

        public int Width { get; }
        public int Height { get; }

        readonly bool[] walls;   // 光も人も通さない（壁・建物）
        readonly bool[] solids;  // 人は通れないが光は越える（自販機・街灯の柱など）
        readonly CellState[] states;

        public ShadowGrid(int width, int height)
        {
            Width = width;
            Height = height;
            walls = new bool[width * height];
            solids = new bool[width * height];
            states = new CellState[width * height];
            for (int i = 0; i < states.Length; i++)
                states[i] = CellState.Dark;
        }

        public bool InBounds(Cell c) => c.X >= 0 && c.Y >= 0 && c.X < Width && c.Y < Height;
        int Index(Cell c) => c.Y * Width + c.X;

        public void SetWall(Cell c, bool value = true)
        {
            if (!InBounds(c)) return;
            walls[Index(c)] = value;
            RefreshBlocked(c);
        }

        public void SetSolid(Cell c, bool value = true)
        {
            if (!InBounds(c)) return;
            solids[Index(c)] = value;
            RefreshBlocked(c);
        }

        // Compute 前でも、壁が「暗いマス」に見えないようにする
        void RefreshBlocked(Cell c)
        {
            int i = Index(c);
            if (walls[i] || solids[i]) states[i] = CellState.Blocked;
            else if (states[i] == CellState.Blocked) states[i] = CellState.Dark;
        }

        public bool IsWall(Cell c) => !InBounds(c) || walls[Index(c)];

        /// <summary>人（ルリ・影）が入れないマス。</summary>
        public bool IsBlocked(Cell c) => !InBounds(c) || walls[Index(c)] || solids[Index(c)];

        public CellState GetState(Cell c) => InBounds(c) ? states[Index(c)] : CellState.Blocked;

        public bool IsDark(Cell c)
        {
            var s = GetState(c);
            return s == CellState.Dark || s == CellState.CastShadow;
        }

        // ------------------------------------------------------------------ 明暗の計算

        public void Compute(IEnumerable<GridLight> lights, IEnumerable<GridCaster> casters)
        {
            var lit = new bool[states.Length];
            var shaded = new bool[states.Length];
            var casterList = new List<GridCaster>(casters);
            var shadowCells = new HashSet<Cell>();

            foreach (var light in lights)
            {
                if (!light.On || light.Radius <= 0f)
                    continue;

                shadowCells.Clear();
                foreach (var caster in casterList)
                    foreach (var cell in caster.Cells)
                        AddCastShadow(light, cell, caster.Height, shadowCells);

                int r = (int)Math.Ceiling(light.Radius);
                for (int y = light.Position.Y - r; y <= light.Position.Y + r; y++)
                {
                    for (int x = light.Position.X - r; x <= light.Position.X + r; x++)
                    {
                        var c = new Cell(x, y);
                        if (!InBounds(c) || IsWall(c) || light.Position.DistanceTo(c) > light.Radius)
                            continue;
                        if (!HasLineOfSight(light.Position, c))
                            continue;
                        if (shadowCells.Contains(c))
                            shaded[Index(c)] = true;
                        else
                            lit[Index(c)] = true;
                    }
                }
            }

            for (int y = 0; y < Height; y++)
            {
                for (int x = 0; x < Width; x++)
                {
                    var c = new Cell(x, y);
                    int i = Index(c);
                    if (IsBlocked(c)) states[i] = CellState.Blocked;
                    else if (lit[i]) states[i] = CellState.Lit;
                    else if (shaded[i]) states[i] = CellState.CastShadow;
                    else states[i] = CellState.Dark;
                }
            }
        }

        /// <summary>光源から見てモノの向こう側へ、距離に応じた長さの影を伸ばす（遠いほど長い）。</summary>
        void AddCastShadow(GridLight light, Cell caster, float casterHeight, HashSet<Cell> result)
        {
            float distance = light.Position.DistanceTo(caster);
            if (distance <= 0f || distance > light.Radius || !HasLineOfSight(light.Position, caster))
                return;

            int length = light.Height <= casterHeight
                ? MaxShadowLength
                : Math.Max(1, Math.Min(MaxShadowLength, (int)Math.Round(distance * casterHeight / (light.Height - casterHeight))));

            double dx = (caster.X - light.Position.X) / distance;
            double dy = (caster.Y - light.Position.Y) / distance;
            for (int k = 1; k <= length * 2; k++)
            {
                double t = k * 0.5;
                if (t > length) break;
                var c = new Cell((int)Math.Round(caster.X + dx * t), (int)Math.Round(caster.Y + dy * t));
                if (c == caster) continue;
                if (IsWall(c)) break;
                result.Add(c);
            }
        }

        /// <summary>2 マスの間に壁が無いか（ブレゼンハムの直線）。両端は調べない。</summary>
        public bool HasLineOfSight(Cell from, Cell to)
        {
            int x0 = from.X, y0 = from.Y, x1 = to.X, y1 = to.Y;
            int dx = Math.Abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
            int dy = -Math.Abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
            int err = dx + dy;
            while (true)
            {
                if (x0 == x1 && y0 == y1) return true;
                int e2 = 2 * err;
                if (e2 >= dy) { err += dy; x0 += sx; }
                if (e2 <= dx) { err += dx; y0 += sy; }
                if ((x0 != x1 || y0 != y1) && IsWall(new Cell(x0, y0)))
                    return false;
            }
        }

        // ------------------------------------------------------------------ 経路

        /// <summary>origin から各マスまでの歩数（上下左右）。届かないマスは Unreachable。</summary>
        public int[] DistancesFrom(Cell origin, Func<Cell, bool> passable)
        {
            var dist = new int[states.Length];
            for (int i = 0; i < dist.Length; i++) dist[i] = Unreachable;
            if (!InBounds(origin)) return dist;

            var queue = new Queue<Cell>();
            dist[Index(origin)] = 0;
            queue.Enqueue(origin);
            while (queue.Count > 0)
            {
                var c = queue.Dequeue();
                foreach (var d in Cell.Directions)
                {
                    var n = c + d;
                    if (!InBounds(n) || dist[Index(n)] != Unreachable || !passable(n))
                        continue;
                    dist[Index(n)] = dist[Index(c)] + 1;
                    queue.Enqueue(n);
                }
            }
            return dist;
        }

        /// <summary>ルリ（人）が歩ける範囲での歩数。</summary>
        public int[] WalkDistancesFrom(Cell origin) => DistancesFrom(origin, c => !IsBlocked(c));

        public int DistanceAt(int[] field, Cell c) => InBounds(c) ? field[Index(c)] : Unreachable;

        /// <summary>
        /// 逃げた影の次の 1 歩。
        /// 「ルリより先にたどり着ける暗いマス」だけを通って行ける範囲で、ルリからいちばん遠いマスを目指す。
        /// 輪になった路地なら反対側へ回り込み続け、行き止まりなら奥へ逃げ込む（そこで捕まる）。
        /// </summary>
        /// <param name="speedRatio">影の速さ ÷ ルリの速さ。</param>
        public Cell FleeStep(Cell shadow, int[] playerDistances, float speedRatio = 1f)
        {
            var steps = new Dictionary<Cell, int> { [shadow] = 0 };
            var parent = new Dictionary<Cell, Cell> { [shadow] = shadow };
            var queue = new Queue<Cell>();
            queue.Enqueue(shadow);

            Cell best = shadow;
            int bestScore = DistanceAt(playerDistances, shadow);
            int bestSteps = 0;

            while (queue.Count > 0)
            {
                var c = queue.Dequeue();
                foreach (var d in Cell.Directions)
                {
                    var n = c + d;
                    if (!IsDark(n) || steps.ContainsKey(n))
                        continue;
                    int k = steps[c] + 1;
                    int player = DistanceAt(playerDistances, n);
                    if (player != Unreachable && k >= player * speedRatio)
                        continue; // ルリのほうが先に着く：通れない
                    steps[n] = k;
                    parent[n] = c;
                    queue.Enqueue(n);

                    if (player > bestScore || (player == bestScore && k < bestSteps))
                    {
                        best = n;
                        bestScore = player;
                        bestSteps = k;
                    }
                }
            }

            if (best == shadow)
                return shadow;
            var step = best;
            while (parent[step] != shadow)
                step = parent[step];
            return step;
        }

        /// <summary>どの暗いマスへ動いても、今より遠ざかれない（追いつめられた）。</summary>
        public bool IsCornered(Cell shadow, int[] playerDistances)
        {
            int here = DistanceAt(playerDistances, shadow);
            foreach (var d in Cell.Directions)
            {
                var n = shadow + d;
                if (IsDark(n) && DistanceAt(playerDistances, n) > here)
                    return false;
            }
            return true;
        }

        /// <summary>光に照らされてしまったとき、いちばん近い暗いマスへ向かう 1 歩。無ければ自分自身。</summary>
        public Cell StepTowardNearestDark(Cell from)
        {
            if (!InBounds(from)) return from;
            var parent = new Dictionary<Cell, Cell>();
            var queue = new Queue<Cell>();
            queue.Enqueue(from);
            parent[from] = from;
            while (queue.Count > 0)
            {
                var c = queue.Dequeue();
                if (c != from && IsDark(c))
                {
                    var step = c;
                    while (parent[step] != from) step = parent[step];
                    return step;
                }
                foreach (var d in Cell.Directions)
                {
                    var n = c + d;
                    if (IsBlocked(n) || parent.ContainsKey(n)) continue;
                    parent[n] = c;
                    queue.Enqueue(n);
                }
            }
            return from;
        }
    }
}
