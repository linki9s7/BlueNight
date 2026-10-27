using System.Collections.Generic;
using System.Linq;
using BlueNight.Logic;
using NUnit.Framework;

namespace BlueNight.Tests
{
    public class ShadowGridTests
    {
        static ShadowGrid OpenGrid(int w = 20, int h = 20) => new ShadowGrid(w, h);

        static GridLight Light(int x, int y, float radius) => new GridLight { Position = new Cell(x, y), Radius = radius };

        static readonly GridCaster[] NoCasters = new GridCaster[0];

        [Test]
        public void LightReachesOnlyWithinRadius()
        {
            var grid = OpenGrid();
            grid.Compute(new[] { Light(10, 10, 3f) }, NoCasters);

            Assert.AreEqual(CellState.Lit, grid.GetState(new Cell(10, 10)));
            Assert.AreEqual(CellState.Lit, grid.GetState(new Cell(13, 10)));
            Assert.AreEqual(CellState.Dark, grid.GetState(new Cell(14, 10)));
            Assert.AreEqual(CellState.Dark, grid.GetState(new Cell(13, 13)));
        }

        [Test]
        public void WallBlocksLight()
        {
            var grid = OpenGrid();
            for (int y = 0; y < 20; y++)
                grid.SetWall(new Cell(12, y));
            grid.Compute(new[] { Light(10, 10, 5f) }, NoCasters);

            Assert.AreEqual(CellState.Lit, grid.GetState(new Cell(11, 10)));
            Assert.AreEqual(CellState.Blocked, grid.GetState(new Cell(12, 10)));
            Assert.AreEqual(CellState.Dark, grid.GetState(new Cell(13, 10)));
        }

        [Test]
        public void SwitchedOffLightDoesNothing()
        {
            var grid = OpenGrid();
            var light = Light(10, 10, 3f);
            light.On = false;
            grid.Compute(new[] { light }, NoCasters);
            Assert.AreEqual(CellState.Dark, grid.GetState(new Cell(10, 10)));
        }

        static int CastShadowLength(int casterX)
        {
            var grid = OpenGrid(40, 5);
            var caster = new GridCaster { Height = 1.5f };
            caster.Cells.Add(new Cell(casterX, 2));
            grid.SetSolid(new Cell(casterX, 2));
            grid.Compute(new[] { Light(2, 2, 30f) }, new[] { caster });

            int length = 0;
            for (int x = casterX + 1; x < 40 && grid.GetState(new Cell(x, 2)) == CellState.CastShadow; x++)
                length++;
            return length;
        }

        [Test]
        public void CastShadowGetsLongerFartherFromLight()
        {
            int near = CastShadowLength(4);
            int far = CastShadowLength(8);
            Assert.Greater(near, 0);
            Assert.Greater(far, near);
        }

        [Test]
        public void CastShadowPointsAwayFromLight()
        {
            var grid = OpenGrid();
            var caster = new GridCaster { Height = 1.5f };
            caster.Cells.Add(new Cell(10, 12));
            grid.SetSolid(new Cell(10, 12));
            grid.Compute(new[] { Light(10, 9, 8f) }, new[] { caster });

            Assert.AreEqual(CellState.CastShadow, grid.GetState(new Cell(10, 13)));
            Assert.AreEqual(CellState.Lit, grid.GetState(new Cell(10, 11)));
        }

        [Test]
        public void LitShadowStepsTowardNearestDark()
        {
            var grid = OpenGrid();
            grid.Compute(new[] { Light(10, 10, 2f) }, NoCasters);
            var start = new Cell(11, 10);
            var step = grid.StepTowardNearestDark(start);
            Assert.AreEqual(1, System.Math.Abs(step.X - start.X) + System.Math.Abs(step.Y - start.Y));
            Assert.IsTrue(grid.IsDark(grid.StepTowardNearestDark(step)), "dark cell is two steps away");
        }

        // ------------------------------------------------------------------ M1 マップ

        static List<GridLight> StreetLamps(GridMap map) =>
            map.Find('L').Select(c => new GridLight { Position = c, Radius = M1Map.StreetLampRadius }).ToList();

        static List<GridCaster> Casters(GridMap map) =>
            map.Find('V').Select(c =>
            {
                var caster = new GridCaster { Height = M1Map.VendingHeight };
                caster.Cells.Add(c);
                return caster;
            }).ToList();

        static ShadowGrid M1Grid(params Cell[] lanternHooks)
        {
            var map = M1Map.Create();
            var grid = map.CreateGrid();
            var lights = StreetLamps(map);
            lights.AddRange(lanternHooks.Select(h => new GridLight { Position = h, Radius = M1Map.LanternRadius }));
            grid.Compute(lights, Casters(map));
            return grid;
        }

        [Test]
        public void M1EntranceIsLitAndAlleyLoopIsDark()
        {
            var map = M1Map.Create();
            var grid = M1Grid();

            var entrance = new[] { new Cell(15, 5), new Cell(16, 5) };
            foreach (var c in entrance)
                Assert.AreEqual(CellState.Lit, grid.GetState(c), $"entrance {c}");

            foreach (var c in map.Find(',').Concat(map.Find('H')).Concat(map.Find('S')).Except(entrance))
                Assert.IsTrue(grid.IsDark(c), $"alley cell {c} should be dark");
        }

        [Test]
        public void M1ShadowCannotLeaveTheAlley()
        {
            var map = M1Map.Create();
            var grid = M1Grid();
            var start = map.Find('S').Single();

            var reachable = grid.DistancesFrom(start, grid.IsDark);
            for (int y = 0; y < map.Height; y++)
            {
                for (int x = 0; x < map.Width; x++)
                {
                    var c = new Cell(x, y);
                    if (grid.DistanceAt(reachable, c) != ShadowGrid.Unreachable)
                        Assert.IsTrue(GridMap.IsAlley(map.At(c)), $"shadow can reach non-alley cell {c}");
                }
            }
        }

        /// <summary>
        /// ルリ（灯りなし）が最短経路で影を追い、影は逃げる。1 手ずつ交互に同じ速さで動く。
        /// 実際のゲームでは影のほうが速いので、ここで逃げ切れるなら本番でも逃げ切れる。
        /// </summary>
        internal static bool Chase(ShadowGrid grid, Cell player, Cell shadow, int maxTurns, bool captureWhenAdjacent)
        {
            bool Caught() => player == shadow || (captureWhenAdjacent && System.Math.Abs(player.X - shadow.X) + System.Math.Abs(player.Y - shadow.Y) <= 1);

            var recent = new Queue<Cell>();
            for (int turn = 0; turn < maxTurns; turn++)
            {
                if (Caught()) return true;

                // 最短経路で近づく。ただし最近通ったマスへは引き返さず、決めた向きに押し続ける
                // （実際のプレイヤーと同じく、輪の片側から影を行き止まりへ追い込む）
                var toShadow = grid.WalkDistancesFrom(shadow);
                var next = player;
                for (int pass = 0; pass < 2 && next == player; pass++)
                {
                    foreach (var d in Cell.Directions)
                    {
                        var n = player + d;
                        if (grid.IsBlocked(n) || (pass == 0 && recent.Contains(n)))
                            continue;
                        if (next == player || grid.DistanceAt(toShadow, n) < grid.DistanceAt(toShadow, next))
                            next = n;
                    }
                }
                recent.Enqueue(player);
                if (recent.Count > 12)
                    recent.Dequeue();
                player = next;
                if (Caught()) return true;

                if (!grid.IsDark(shadow))
                {
                    shadow = grid.StepTowardNearestDark(shadow);
                }
                else
                {
                    shadow = grid.FleeStep(shadow, grid.WalkDistancesFrom(player));
                }
            }
            return Caught();
        }

        static Cell PlayerStart => M1Map.Create().Find('P').Single();
        static Cell ShadowStart => M1Map.Create().Find('S').Single();

        [Test]
        public void M1ShadowEscapesForeverWhenAlleyIsALoop()
        {
            Assert.IsFalse(Chase(M1Grid(), PlayerStart, ShadowStart, 600, captureWhenAdjacent: true));
        }

        [Test]
        public void M1LanternOnPlazaHookDoesNotHelp()
        {
            var plazaHook = M1Map.Create().Find('h').Single();
            Assert.IsFalse(Chase(M1Grid(plazaHook), PlayerStart, ShadowStart, 600, captureWhenAdjacent: true));
        }

        [Test]
        public void M1LanternOnAnyCornerHookLetsRuriCornerTheShadow()
        {
            foreach (var hook in M1Map.Create().Find('H'))
                Assert.IsTrue(Chase(M1Grid(hook), PlayerStart, ShadowStart, 200, captureWhenAdjacent: true), $"hook {hook}");
        }
    }
}
