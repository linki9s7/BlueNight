using System.Collections.Generic;
using System.Linq;
using BlueNight.Logic;
using NUnit.Framework;
using static BlueNight.Tests.ShadowGridTests;

namespace BlueNight.Tests
{
    /// <summary>第 2 章の試作マップ：作戦が要ること（何もしない・全部点ける・ランタン無しでは捕まらない）。</summary>
    public class Chapter2ProtoMapTests
    {
        const int MaxTurns = 400;

        static GridMap Map => Chapter2ProtoMap.Create();

        /// <summary>いつも点いている街灯（L）＋点けた町の灯り（l）＋置いたランタンで計算したグリッド。</summary>
        static ShadowGrid Grid(IEnumerable<Cell> lampsOn, Cell? lantern)
        {
            var map = Map;
            var grid = map.CreateGrid();
            var lights = map.Find('L').Select(c => new GridLight { Position = c, Radius = Chapter2ProtoMap.StreetLampRadius }).ToList();
            lights.AddRange(lampsOn.Select(c => new GridLight
                { Position = c, Radius = Chapter2ProtoMap.SmallLampRadius, Height = Chapter2ProtoMap.SmallLampHeight }));
            if (lantern.HasValue)
                lights.Add(new GridLight { Position = lantern.Value, Radius = Chapter2ProtoMap.LanternRadius });
            var casters = new List<GridCaster>();
            for (int y = 0; y < map.Height; y++)
            {
                for (int x = 0; x < map.Width; x++)
                {
                    var c = new Cell(x, y);
                    float h = GridMap.CasterHeight(map.At(c));
                    if (h <= 0f) continue;
                    var caster = new GridCaster { Height = h };
                    caster.Cells.Add(c);
                    casters.Add(caster);
                }
            }
            grid.Compute(lights, casters);
            return grid;
        }

        static ChaseResult Play(IEnumerable<Cell> lampsOn, Cell? lantern) =>
            ChaseWithExits(Grid(lampsOn, lantern), Map.Find('P').Single(), Map.Find('S').Single(), MaxTurns);

        static IEnumerable<Cell[]> LampSubsets()
        {
            var lamps = Map.Find('l').ToArray();
            for (int mask = 0; mask < 1 << lamps.Length; mask++)
                yield return lamps.Where((_, i) => (mask & (1 << i)) != 0).ToArray();
        }

        [Test]
        public void NoLightsShadowEscapes()
        {
            Assert.AreEqual(ChaseResult.Escaped, Play(new Cell[0], null));
        }

        [Test]
        public void AllTownLampsOnStillFails()
        {
            Assert.AreNotEqual(ChaseResult.Caught, Play(Map.Find('l'), null));
        }

        [Test]
        public void PlannedSolutionCanBePlacedWithoutStartingTheChase()
        {
            var shadow = Map.Find('S').Single();
            Assert.Greater(Chapter2ProtoMap.SolutionLantern.DistanceTo(shadow), Chapter2ProtoMap.NoticeDistance);
        }

        [Test]
        public void PlannedSolutionCatches()
        {
            Assert.AreEqual(ChaseResult.Caught, Play(Chapter2ProtoMap.SolutionLamps, Chapter2ProtoMap.SolutionLantern));
        }

        [Test]
        public void EverySolutionNeedsTheLantern()
        {
            foreach (var lamps in LampSubsets())
                Assert.AreNotEqual(ChaseResult.Caught, Play(lamps, null), $"lamps {string.Join(" ", lamps)}");
        }

        [Test]
        public void ShadowOnlyReachesAlleyCells()
        {
            var map = Map;
            var grid = Grid(new Cell[0], null);
            var reach = grid.DistancesFrom(map.Find('S').Single(), grid.IsDark);
            for (int y = 0; y < map.Height; y++)
                for (int x = 0; x < map.Width; x++)
                {
                    var c = new Cell(x, y);
                    if (grid.DistanceAt(reach, c) != ShadowGrid.Unreachable)
                        Assert.IsTrue(GridMap.IsAlley(map.At(c)), $"shadow reaches {c} '{map.At(c)}'");
                }
        }

        /// <summary>設計用：どの点け方・どこに置けば捕まるかを全部書き出す（ふだんは走らせない）。</summary>
        [Test, Explicit]
        public void ExploreSolutions()
        {
            var map = Map;
            var spots = new List<Cell?> { null };
            for (int y = 0; y < map.Height; y++)
                for (int x = 0; x < map.Width; x++)
                    if (GridMap.IsWalkable(map.At(new Cell(x, y))) && map.At(new Cell(x, y)) != '.'
                        && new Cell(x, y).DistanceTo(map.Find('S').Single()) > Chapter2ProtoMap.NoticeDistance)
                        spots.Add(new Cell(x, y));
            foreach (var lamps in LampSubsets())
            {
                var caught = spots.Where(s => Play(lamps, s) == ChaseResult.Caught).ToList();
                TestContext.Progress.WriteLine($"lamps [{string.Join(" ", lamps)}] -> {Play(lamps, null)} without lantern; caught with lantern at: {string.Join(" ", caught)}");
            }
        }
    }
}
