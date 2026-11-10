using BlueNight.Logic;
using NUnit.Framework;

namespace BlueNight.Tests
{
    /// <summary>第 2 章：水たまりには、モノの影が光のほうへ逆さに映る。逆さの影の上は影が通れる（光より強い）。</summary>
    public class PuddleReflectionTests
    {
        static readonly Cell Thing = new Cell(10, 2);

        static ShadowGrid Grid(params Cell[] puddles)
        {
            var grid = new ShadowGrid(20, 5);
            grid.SetSolid(Thing);
            foreach (var p in puddles)
                grid.SetPuddle(p);
            return grid;
        }

        static GridCaster Caster()
        {
            var caster = new GridCaster { Height = 1.5f };
            caster.Cells.Add(Thing);
            return caster;
        }

        static GridLight Light(int x, bool on = true) => new GridLight { Position = new Cell(x, 2), Radius = 12f, On = on };

        static void Compute(ShadowGrid grid, GridLight light) => grid.Compute(new[] { light }, new[] { Caster() });

        [Test]
        public void ReflectionPointsTowardLight()
        {
            var grid = Grid(new Cell(8, 2), new Cell(9, 2));
            Compute(grid, Light(4));

            foreach (var c in new[] { new Cell(8, 2), new Cell(9, 2) })
            {
                Assert.AreEqual(CellState.CastShadow, grid.GetState(c), $"{c}");
                Assert.IsTrue(grid.IsReflection(c), $"{c}");
            }
            Assert.AreEqual(CellState.CastShadow, grid.GetState(new Cell(11, 2)));
            Assert.IsFalse(grid.IsReflection(new Cell(11, 2)));
        }

        [Test]
        public void NoPuddleNoReflection()
        {
            var grid = Grid();
            Compute(grid, Light(4));
            Assert.AreEqual(CellState.Lit, grid.GetState(new Cell(9, 2)));
            Assert.IsFalse(grid.IsReflection(new Cell(9, 2)));
        }

        [Test]
        public void PuddleAwayFromLightSideHasNoReflection()
        {
            var grid = Grid(new Cell(12, 2));
            Compute(grid, Light(4));
            Assert.AreEqual(CellState.CastShadow, grid.GetState(new Cell(12, 2)));
            Assert.IsFalse(grid.IsReflection(new Cell(12, 2)));
        }

        [Test]
        public void MovingLightChangesReflection()
        {
            var grid = Grid(new Cell(8, 2), new Cell(9, 2));
            Compute(grid, Light(16));
            Assert.IsFalse(grid.IsReflection(new Cell(8, 2)));
            Assert.IsFalse(grid.IsReflection(new Cell(9, 2)));
        }

        [Test]
        public void SwitchedOffLightMakesNoReflection()
        {
            var grid = Grid(new Cell(8, 2), new Cell(9, 2));
            Compute(grid, Light(4, on: false));
            Assert.IsFalse(grid.IsReflection(new Cell(8, 2)));
            Assert.IsFalse(grid.IsReflection(new Cell(9, 2)));
        }

        [Test]
        public void ReflectionLengthMatchesCastShadowLength()
        {
            var plain = Grid();
            Compute(plain, Light(4));
            int castLength = 0;
            for (int x = Thing.X + 1; x < 20 && plain.GetState(new Cell(x, 2)) == CellState.CastShadow; x++)
                castLength++;

            var puddles = new Cell[9];
            for (int x = 1; x <= 9; x++)
                puddles[x - 1] = new Cell(x, 2);
            var grid = Grid(puddles);
            Compute(grid, Light(4));
            int reflected = 0;
            foreach (var c in puddles)
                if (grid.IsReflection(c))
                    reflected++;

            Assert.Greater(castLength, 0);
            Assert.AreEqual(castLength, reflected);
        }

        // 頭の上の看板（n）：人も影も通れるマスにあるモノ。光が当たると、真下のマスも影になる。
        // 固い物（自販機など）の逆さの影は、まわりが照らされていて入口が無いが、看板なら真下から入れる。

        [Test]
        public void OverheadSignCellIsShadedWhenItCasts()
        {
            var grid = new ShadowGrid(20, 5);
            var sign = new GridCaster { Height = 2.5f };
            sign.Cells.Add(Thing);                       // SetSolid しない：通れる
            grid.Compute(new[] { Light(4) }, new[] { sign });
            Assert.AreEqual(CellState.CastShadow, grid.GetState(Thing));
        }

        [Test]
        public void SolidThingCellStaysBlocked()
        {
            var grid = Grid();
            Compute(grid, Light(4));
            Assert.AreEqual(CellState.Blocked, grid.GetState(Thing));
        }

        [Test]
        public void ShadowCanWalkFromUnderSignOntoReflection()
        {
            // 看板 (10, 2) の真下 → 光 (4, 2) のほうの水たまり (9, 2)・(8, 2) が、暗いまま続く
            var grid = new ShadowGrid(20, 5);
            grid.SetPuddle(new Cell(8, 2));
            grid.SetPuddle(new Cell(9, 2));
            var sign = new GridCaster { Height = 2.5f };
            sign.Cells.Add(Thing);
            grid.Compute(new[] { Light(4) }, new[] { sign });
            var reach = grid.DistancesFrom(new Cell(11, 2), grid.IsDark);
            Assert.AreNotEqual(ShadowGrid.Unreachable, grid.DistanceAt(reach, new Cell(8, 2)));
        }

        [Test]
        public void GridMapLegendSign()
        {
            Assert.IsTrue(GridMap.IsWalkable('n'));
            Assert.Greater(GridMap.CasterHeight('n'), 2f);
        }

        [Test]
        public void GridMapLegendPuddle()
        {
            var grid = new GridMap(new[] { "#####", "#,o,#", "#####" }).CreateGrid();
            Assert.IsTrue(grid.IsPuddle(new Cell(2, 1)));
            Assert.IsTrue(GridMap.IsAlley('o'));
        }
    }
}
