using BlueNight.Logic;
using NUnit.Framework;

namespace BlueNight.Tests
{
    /// <summary>第 2 章：抜け道（E）と、開いた抜け道を目指す逃げ方。</summary>
    public class EscapeExitTests
    {
        /// <summary>20×5 のグリッドに、y = 2 の x = 1..18 だけ通れる 1 本の通路。</summary>
        static ShadowGrid Corridor()
        {
            var grid = new ShadowGrid(20, 5);
            for (int y = 0; y < 5; y++)
                for (int x = 0; x < 20; x++)
                    if (y != 2 || x < 1 || x > 18)
                        grid.SetWall(new Cell(x, y));
            return grid;
        }

        static GridLight Light(int x, int y, float radius) => new GridLight { Position = new Cell(x, y), Radius = radius };

        static readonly GridLight[] NoLights = new GridLight[0];
        static readonly GridCaster[] NoCasters = new GridCaster[0];

        [Test]
        public void ShadowHeadsForOpenExit()
        {
            var grid = Corridor();
            grid.SetExit(new Cell(18, 2));
            grid.Compute(NoLights, NoCasters);
            var ruri = grid.WalkDistancesFrom(new Cell(2, 2));

            Assert.AreEqual(new Cell(11, 2), grid.ChaseStep(new Cell(10, 2), ruri));
        }

        [Test]
        public void ShadowPrefersExitOverFleeingFarther()
        {
            var grid = Corridor();
            grid.SetExit(new Cell(5, 2));
            grid.Compute(NoLights, NoCasters);
            var ruri = grid.WalkDistancesFrom(new Cell(1, 2));

            // ルリから遠ざかるだけなら (9, 2)。抜け道へはルリより先に着けるので、ルリのほうへ向かう
            Assert.AreEqual(new Cell(9, 2), grid.FleeStep(new Cell(8, 2), ruri));
            Assert.AreEqual(new Cell(7, 2), grid.ChaseStep(new Cell(8, 2), ruri));
        }

        [Test]
        public void LitExitIsClosed()
        {
            var grid = Corridor();
            grid.SetExit(new Cell(18, 2));
            grid.Compute(new[] { Light(18, 2, 1f) }, NoCasters);
            var ruri = grid.WalkDistancesFrom(new Cell(2, 2));

            Assert.IsFalse(grid.TryFindOpenExit(new Cell(10, 2), ruri, 1f, out _));
            Assert.AreEqual(grid.FleeStep(new Cell(10, 2), ruri), grid.ChaseStep(new Cell(10, 2), ruri));
        }

        [Test]
        public void ExitUnderRuriIsNotReachable()
        {
            var grid = Corridor();
            grid.SetExit(new Cell(18, 2));
            grid.Compute(NoLights, NoCasters);
            var ruri = grid.WalkDistancesFrom(new Cell(18, 2));

            Assert.IsFalse(grid.TryFindOpenExit(new Cell(10, 2), ruri, 1f, out _));
        }

        [Test]
        public void NearestExitTieIsDeterministic()
        {
            var grid = Corridor();
            grid.SetExit(new Cell(5, 2));
            grid.SetExit(new Cell(15, 2));
            grid.Compute(NoLights, NoCasters);
            var nobody = grid.DistancesFrom(new Cell(-1, -1), c => true); // ルリはどこにも届かない

            var first = grid.ChaseStep(new Cell(10, 2), nobody);
            Assert.IsTrue(first == new Cell(9, 2) || first == new Cell(11, 2), $"step {first}");
            for (int i = 0; i < 10; i++)
                Assert.AreEqual(first, grid.ChaseStep(new Cell(10, 2), nobody));
        }

        [Test]
        public void HasEscapedOnlyOnDarkExit()
        {
            var grid = Corridor();
            grid.SetExit(new Cell(18, 2));
            grid.SetExit(new Cell(3, 2));
            grid.Compute(new[] { Light(3, 2, 1f) }, NoCasters);

            Assert.IsTrue(grid.HasEscaped(new Cell(18, 2)));
            Assert.IsFalse(grid.HasEscaped(new Cell(3, 2)), "lit exit");
            Assert.IsFalse(grid.HasEscaped(new Cell(10, 2)), "not an exit");
        }

        [Test]
        public void GridMapLegendExitOnPuddle()
        {
            var grid = new GridMap(new[] { "#####", "#,e,#", "#####" }).CreateGrid();
            Assert.IsTrue(grid.IsExit(new Cell(2, 1)));
            Assert.IsTrue(grid.IsPuddle(new Cell(2, 1)));
            Assert.IsTrue(GridMap.IsAlley('e'));
        }

        [Test]
        public void GridMapLegendE()
        {
            var grid = new GridMap(new[] { "#####", "#,E,#", "#####" }).CreateGrid();
            Assert.IsTrue(grid.IsExit(new Cell(2, 1)));
            Assert.IsTrue(GridMap.IsAlley('E'));
            Assert.IsFalse(grid.IsBlocked(new Cell(2, 1)));
        }
    }
}
