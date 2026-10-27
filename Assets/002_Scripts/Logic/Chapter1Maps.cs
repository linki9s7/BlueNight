using System;
using System.Collections.Generic;

namespace BlueNight.Logic
{
    /// <summary>エリアどうしの出入口。マップの中の同じ数字のマスどうしがつながる。</summary>
    public sealed class AreaLink
    {
        /// <summary>マップの中の数字（'1'〜'9'）。</summary>
        public readonly char Symbol;
        public readonly string AreaA;
        public readonly string AreaB;
        /// <summary>true：調べて入る戸（ランプ屋の戸）。false：歩いて入る（道の続き・路地の口）。</summary>
        public readonly bool IsDoor;

        public AreaLink(char symbol, string areaA, string areaB, bool isDoor = false)
        {
            Symbol = symbol;
            AreaA = areaA;
            AreaB = areaB;
            IsDoor = isDoor;
        }

        /// <summary>この出入口の、もう片方のエリア。</summary>
        public string Other(string area) => area == AreaA ? AreaB : area == AreaB ? AreaA : null;
    }

    /// <summary>
    /// 第 1 章「灯をひとつ」（バス停と商店街）のマップ（docs/M2_PLAN.md 3 章、台本は docs/STORY.md 7・8 節）。
    /// M1 と同じく、シーンの作成・テスト・プレビューがすべてこの定義を読む。
    /// エリアはシーンの中で別々の場所に並べ、出入口（数字）で暗転してつなぐ。
    /// </summary>
    public static class Chapter1Maps
    {
        public const float StreetLampRadius = M1Map.StreetLampRadius;
        public const float LanternRadius = M1Map.LanternRadius;

        public const string Home = "home";
        public const string Street = "street";
        public const string LampShop = "lamp_shop";
        public const string Alley1 = "alley1";
        public const string Alley2 = "alley2";

        /// <summary>
        /// 家の前〜バス停（40x16）。坂の上の通り。北にルリのアパートと家並み、南の柵の向こうは坂の下の町。
        /// ルリはアパートの前（P）から出て、街灯（すぐ東の L）の下で足元に影が無いことに気づく。
        /// 東のバス停（屋根 X・ベンチ B・時刻表 Q）、Y は商店街の明かりを見下ろす所。東の端（1）が商店街へ。
        /// </summary>
        public static readonly string[] HomeRows =
        {
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "#.............................XXX......1",
            "#...P..........................B.......1",
            "#......L.........U.........L......Q....1",
            "#===================:::================1",
            "#===================:::================1",
            "#===================:::================1",
            "#...................................Y..1",
            "#.............L........................1",
            "########################################",
        };

        /// <summary>
        /// 商店街（48x16）。北に店が並ぶ（x：家 1-4／シャッター 5-8／路地その 1 の口 9-10／ランプ屋 11-15・戸 14／
        /// 佐伯商店 16-20／シャッター 21-24・屋根にルリの影 R／ゴマのくぼみ 25／家 26-29／シャッター 30-33／
        /// 路地その 2 の口 34-35／家 36-39／シャッター 40-43／家 44-47）。南は車道と歩道。
        /// 西の端（1）が家の前へ、戸（2）がランプ屋の中へ、路地の口（3・4）がそれぞれの路地へ。
        /// </summary>
        public static readonly string[] StreetRows =
        {
            "################################################",
            "################################################",
            "#######################R########################",
            "################################################",
            "#########33#######################44############",
            "#########,,##############c########,,############",
            "#########,,###2##########,########,,############",
            "1..............N..GC..M........V.T....B........#",
            "1..............................................#",
            "1.....L............L.........U............L....#",
            "1==============================================#",
            "1==============================================#",
            "1==============================================#",
            "1...........L.................L................#",
            "1..............................................#",
            "################################################",
        };

        /// <summary>
        /// ランプ屋「ともしび堂」の中（15x10）。北の壁ぎわに棚（X）と柱時計、西に作業台、東にカウンター（主人 K）、
        /// 床の真ん中にランプを並べた台（X）。小さなランタン掛け（h）で「掛ける」を練習する：
        /// 掛けると台の影が床に落ちる（ネム「灯りを動かすと、影も動くんだよ」）。南の戸（2）が商店街へ。
        /// </summary>
        public static readonly string[] LampShopRows =
        {
            "###############",
            "###############",
            "###############",
            "#.XX.XX...XXX.#",
            "#.............#",
            "#.XX...X..K...#",
            "#........XXX..#",
            "#......h......#",
            "#.............#",
            "#######2#######",
        };

        /// <summary>
        /// 路地その 1（20x14）。南の口（3）から北へのびて、角で東へ折れる L 字。東の奥は短い行き止まり。
        /// 角の北には小屋があり、その裏を回る道で輪になっている：灯りが無いと、影は輪を回って逃げ続ける
        /// （行き止まりを長くすると、影は自分から奥へ逃げ込んで捕まってしまうので短くしてある）。
        /// 角のランタン掛け（H）に掛けると輪が切れ、影は奥へ追いつめられる（練習）。
        /// 口は商店街の街灯（L）で照らされていて、影は外へ出られない。
        /// </summary>
        public static readonly string[] Alley1Rows =
        {
            "####################",
            "####################",
            "#####,,,,,,,,,,,,###",
            "#####,,,,,,,,,,,,###",
            "#####,,########,,###",
            "#####,,########,,###",
            "#####,,H,,,,,,,,,,,#",
            "#####,,,,,,T,,,S,,,#",
            "#####,,#############",
            "#####,,#############",
            "#####,,#############",
            "####L,,#############",
            "#####,,#############",
            "#####33#############",
        };

        /// <summary>
        /// 路地その 2・裏通りの輪（32x20）。M1 と同じく、建物の裏をぐるりと回る輪。南の裏通りから細い道で入る。
        /// 入口は両わきの街灯（L）で照らされている（光の 1 か所目）。輪の 4 つの角にランタン掛け（H）：
        /// どこかに掛けて輪をもう 1 か所切ると、影は行き止まりへ（ネムのヒント「二つの光で、輪を二か所で切る」）。
        /// 室外機（A）・ごみ箱（T）は灯りの影を落とす。南の端（4）が商店街の路地の口へ。
        /// </summary>
        public static readonly string[] Alley2Rows =
        {
            "################################",
            "################################",
            "#######,,,,,,,,,,,,,,,,,,#######",
            "#######H,,,,,,,,,,,,,,,,H#######",
            "#######,,,,A,,,S,,,,,,,,,#######",
            "#######,,##############,,#######",
            "#######,,##############,,#######",
            "#######,,##############,,#######",
            "#######,,##############,,#######",
            "#######,,##############,,#######",
            "#######,,##############,,#######",
            "#######,,##############T,#######",
            "#######,,,,,,,,,,,,,,,,,,#######",
            "#######H,,,,,,,,,,,,,,,,H#######",
            "#######,,,,,,,,,,,,,,,,,,#######",
            "##############,,################",
            "##############,,################",
            "#..............................#",
            "#...........L....L.............#",
            "##############44################",
        };

        /// <summary>エリアの並び（シーンでの並べ方・テストで使う）。</summary>
        public static readonly string[] AreaIds = { Home, Street, LampShop, Alley1, Alley2 };

        public static readonly AreaLink[] Links =
        {
            new AreaLink('1', Home, Street),
            new AreaLink('2', Street, LampShop, isDoor: true),
            new AreaLink('3', Street, Alley1),
            new AreaLink('4', Street, Alley2),
        };

        public static string[] Rows(string area)
        {
            switch (area)
            {
                case Home: return HomeRows;
                case Street: return StreetRows;
                case LampShop: return LampShopRows;
                case Alley1: return Alley1Rows;
                case Alley2: return Alley2Rows;
                default: throw new ArgumentException($"unknown area: {area}");
            }
        }

        public static GridMap Create(string area) => new GridMap(Rows(area));

        /// <summary>
        /// 出入口から入ったときに立つマス：出入口のマスのとなりで、出入口ではない歩けるマス（出入口が何マスかあるなら、その真ん中のとなり）。
        /// </summary>
        public static Cell SpawnCell(GridMap map, char link)
        {
            var cells = new List<Cell>(map.Find(link));
            if (cells.Count == 0)
                throw new ArgumentException($"link {link} not in map");
            cells.Sort((a, b) => a.X != b.X ? a.X.CompareTo(b.X) : a.Y.CompareTo(b.Y));
            var middle = cells[cells.Count / 2];
            foreach (var d in Cell.Directions)
            {
                var n = middle + d;
                char ch = map.At(n);
                if (GridMap.IsWalkable(ch) && !GridMap.IsLink(ch))
                    return n;
            }
            throw new ArgumentException($"link {link} at {middle} has no walkable neighbour");
        }
    }
}
