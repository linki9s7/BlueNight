using System.Collections.Generic;
using System.Linq;
using BlueNight.Logic;
using NUnit.Framework;

namespace BlueNight.Tests
{
    /// <summary>第 1 章のマップ（Chapter1Maps）：形・出入口のつながり・追いつめの手ごたえ。</summary>
    public class Chapter1MapTests
    {
        // ------------------------------------------------------------------ 形とつながり

        [Test]
        public void EveryAreaIsClosedExceptItsLinks()
        {
            foreach (var id in Chapter1Maps.AreaIds)
            {
                var map = Chapter1Maps.Create(id);
                for (int y = 0; y < map.Height; y++)
                {
                    for (int x = 0; x < map.Width; x++)
                    {
                        if (x != 0 && y != 0 && x != map.Width - 1 && y != map.Height - 1)
                            continue;
                        char ch = map.At(new Cell(x, y));
                        Assert.IsTrue(GridMap.IsWall(ch) || GridMap.IsLink(ch), $"{id}: edge cell ({x}, {y}) is open: '{ch}'");
                    }
                }
            }
        }

        [Test]
        public void EveryLinkAppearsInExactlyItsTwoAreas()
        {
            foreach (var link in Chapter1Maps.Links)
            {
                foreach (var id in Chapter1Maps.AreaIds)
                {
                    bool has = Chapter1Maps.Create(id).Find(link.Symbol).Any();
                    bool expected = id == link.AreaA || id == link.AreaB;
                    Assert.AreEqual(expected, has, $"link {link.Symbol} in {id}");
                }
            }
            var declared = new HashSet<char>(Chapter1Maps.Links.Select(l => l.Symbol));
            foreach (var id in Chapter1Maps.AreaIds)
                foreach (var ch in Chapter1Maps.Rows(id).SelectMany(r => r).Where(GridMap.IsLink))
                    Assert.IsTrue(declared.Contains(ch), $"{id}: link {ch} is not declared in Chapter1Maps.Links");
        }

        [Test]
        public void EveryWalkableCellCanBeReachedFromEachLink()
        {
            foreach (var id in Chapter1Maps.AreaIds)
            {
                var map = Chapter1Maps.Create(id);
                var grid = map.CreateGrid();
                foreach (var link in Chapter1Maps.Links.Where(l => l.Other(id) != null))
                {
                    var start = Chapter1Maps.SpawnCell(map, link.Symbol);
                    var reach = grid.WalkDistancesFrom(start);
                    for (int y = 0; y < map.Height; y++)
                    {
                        for (int x = 0; x < map.Width; x++)
                        {
                            var c = new Cell(x, y);
                            if (GridMap.IsWalkable(map.At(c)))
                                Assert.AreNotEqual(ShadowGrid.Unreachable, grid.DistanceAt(reach, c), $"{id}: {c} unreachable from link {link.Symbol}");
                        }
                    }
                }
            }
        }

        [Test]
        public void EachAreaHasTheThingsTheScriptNeeds()
        {
            int Count(string id, char ch) => Chapter1Maps.Create(id).Find(ch).Count();
            Assert.AreEqual(1, Count(Chapter1Maps.Room, 'P'), "Ruri wakes up on her futon");
            Assert.AreEqual(0, Count(Chapter1Maps.Home, 'P'), "Ruri comes out of the apartment door, not from a start mark");
            Assert.AreEqual(1, Count(Chapter1Maps.Room, 'Y'), "the window that looks over the bay");
            Assert.AreEqual(1, Count(Chapter1Maps.Home, 'Q'), "bus stop timetable");
            Assert.AreEqual(1, Count(Chapter1Maps.Street, 'N'), "the old lantern at the lamp shop");
            Assert.AreEqual(1, Count(Chapter1Maps.Street, 'G'), "Haru");
            Assert.AreEqual(1, Count(Chapter1Maps.Street, 'C'), "Goma");
            Assert.AreEqual(1, Count(Chapter1Maps.Street, 'c'), "Goma's dropped shadow");
            Assert.AreEqual(1, Count(Chapter1Maps.Street, 'R'), "Ruri's shadow on the roof");
            Assert.AreEqual(1, Count(Chapter1Maps.LampShop, 'K'), "the keeper");
            Assert.AreEqual(1, Count(Chapter1Maps.LampShop, 'h'), "practice hook");
            Assert.AreEqual(1, Count(Chapter1Maps.Alley1, 'H'), "alley 1 has one hook");
            Assert.AreEqual(4, Count(Chapter1Maps.Alley2, 'H'), "alley 2 has a hook at each corner");
        }

        // ------------------------------------------------------------------ 光と影

        static ShadowGrid Lit(string id, params Cell[] hungLanterns)
        {
            var map = Chapter1Maps.Create(id);
            var grid = map.CreateGrid();
            var lights = map.Find('L').Select(c => new GridLight { Position = c, Radius = Chapter1Maps.StreetLampRadius }).ToList();
            lights.AddRange(hungLanterns.Select(c => new GridLight { Position = c, Radius = Chapter1Maps.LanternRadius }));
            var casters = new List<GridCaster>();
            for (int y = 0; y < map.Height; y++)
            {
                for (int x = 0; x < map.Width; x++)
                {
                    var c = new Cell(x, y);
                    float h = GridMap.CasterHeight(map.At(c));
                    if (h <= 0f)
                        continue;
                    var caster = new GridCaster { Height = h };
                    caster.Cells.Add(c);
                    casters.Add(caster);
                }
            }
            grid.Compute(lights, casters);
            return grid;
        }

        static Cell Entry(string id, char link) => Chapter1Maps.SpawnCell(Chapter1Maps.Create(id), link);
        static Cell Single(string id, char ch) => Chapter1Maps.Create(id).Find(ch).Single();

        [Test]
        public void HomeLampLightsTheSpotWhereRuriNoticesHerShadowIsGone()
        {
            var grid = Lit(Chapter1Maps.Home);
            var lamp = Chapter1Maps.Create(Chapter1Maps.Home).Find('L').OrderBy(c => c.X).First();
            Assert.AreEqual(CellState.Lit, grid.GetState(lamp + new Cell(0, 1)), "under the first street lamp");
        }

        [Test]
        public void GomasDroppedShadowHidesInTheDark()
        {
            Assert.IsTrue(Lit(Chapter1Maps.Street).IsDark(Single(Chapter1Maps.Street, 'c')));
        }

        [Test]
        public void LampShopPracticeHookMakesTheFurnitureCastShadows()
        {
            var grid = Lit(Chapter1Maps.LampShop, Single(Chapter1Maps.LampShop, 'h'));
            var map = Chapter1Maps.Create(Chapter1Maps.LampShop);
            int shadows = 0;
            for (int y = 0; y < map.Height; y++)
                for (int x = 0; x < map.Width; x++)
                    if (grid.GetState(new Cell(x, y)) == CellState.CastShadow)
                        shadows++;
            Assert.Greater(shadows, 0, "hanging the lantern should make the shelves and counter cast shadows");
        }

        static void AssertShadowStaysInAlley(string id, ShadowGrid grid)
        {
            var map = Chapter1Maps.Create(id);
            var reach = grid.DistancesFrom(Single(id, 'S'), grid.IsDark);
            for (int y = 0; y < map.Height; y++)
            {
                for (int x = 0; x < map.Width; x++)
                {
                    var c = new Cell(x, y);
                    if (grid.DistanceAt(reach, c) != ShadowGrid.Unreachable)
                        Assert.IsTrue(GridMap.IsAlley(map.At(c)) || map.At(c) == 'A' || map.At(c) == 'T', $"{id}: shadow can reach {c} '{map.At(c)}'");
                }
            }
        }

        [Test]
        public void Alley1ShadowCannotGetOutToTheStreet()
        {
            AssertShadowStaysInAlley(Chapter1Maps.Alley1, Lit(Chapter1Maps.Alley1));
        }

        [Test]
        public void Alley1ShadowCirclesTheShedWithoutALight()
        {
            Assert.IsFalse(ShadowGridTests.Chase(Lit(Chapter1Maps.Alley1), Entry(Chapter1Maps.Alley1, '3'), Single(Chapter1Maps.Alley1, 'S'), 600, true));
        }

        [Test]
        public void Alley1LanternOnTheCornerHookCornersTheShadow()
        {
            var grid = Lit(Chapter1Maps.Alley1, Single(Chapter1Maps.Alley1, 'H'));
            Assert.IsTrue(ShadowGridTests.Chase(grid, Entry(Chapter1Maps.Alley1, '3'), Single(Chapter1Maps.Alley1, 'S'), 200, true));
        }

        [Test]
        public void Alley2ShadowCannotGetOutToTheBackStreet()
        {
            AssertShadowStaysInAlley(Chapter1Maps.Alley2, Lit(Chapter1Maps.Alley2));
        }

        [Test]
        public void Alley2ShadowEscapesForeverWhenTheRingIsWhole()
        {
            Assert.IsFalse(ShadowGridTests.Chase(Lit(Chapter1Maps.Alley2), Entry(Chapter1Maps.Alley2, '4'), Single(Chapter1Maps.Alley2, 'S'), 600, true));
        }

        [Test]
        public void Alley2LanternOnACornerHookCornersTheShadow()
        {
            var results = Chapter1Maps.Create(Chapter1Maps.Alley2).Find('H')
                .ToDictionary(h => h, h => ShadowGridTests.Chase(Lit(Chapter1Maps.Alley2, h), Entry(Chapter1Maps.Alley2, '4'), Single(Chapter1Maps.Alley2, 'S'), 300, true));
            TestContext.WriteLine(string.Join(", ", results.Select(kv => $"{kv.Key}:{(kv.Value ? "caught" : "escaped")}")));
            Assert.IsTrue(results.Values.Any(v => v), "at least one corner hook must work");
        }
    }
}
