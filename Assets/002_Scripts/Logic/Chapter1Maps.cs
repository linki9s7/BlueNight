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
    /// 序章と第 1 章「灯をひとつ」（バス停と商店街）のマップ（ルリの家＋5 エリア）（docs/M2_PLAN.md 3 章、台本は docs/STORY.md 8 節＝序章・9 節＝第 1 章）。
    /// M1 と同じく、シーンの作成・テスト・プレビューがすべてこの定義を読む。
    /// エリアはシーンの中で別々の場所に並べ、出入口（数字）で暗転してつなぐ。
    /// </summary>
    public static class Chapter1Maps
    {
        public const float StreetLampRadius = M1Map.StreetLampRadius;
        public const float LanternRadius = M1Map.LanternRadius;

        public const string Room = "room";
        public const string Home = "home";
        public const string Street = "street";
        public const string LampShop = "lamp_shop";
        public const string Alley1 = "alley1";
        public const string Alley2 = "alley2";

        /// <summary>
        /// ルリの家（18x10）。坂の上の古いアパートの一室。西からルリの部屋・台所・玄関（仕切りの壁に戸口）。
        /// 序章：ふとん（P）で目を覚ます → 机（X、スマホの未読）→ たんす（窓の右の X）でパジャマからワンピースに着がえる →
        /// 台所の冷蔵庫（書き置き）→ 玄関の椅子（青いマフラー）→ 戸（5）からアパートの前へ。
        /// 終章：机の引き出しの絵はがきに一行 → 玄関で母を迎える。Y は窓（湾の高架道路が見える）。
        /// docs/STORY.md 8 節（序章）・14 節（終章）、docs/M2_PLAN.md 3.1。
        /// </summary>
        public static readonly string[] RoomRows =
        {
            "##################",
            "##################",
            "##################",
            "#XX..Y.X#XX.X#.XX#",
            "#................#",
            "#................#",
            "#.......#.XX.#..X#",
            "#..P....#....#...#",
            "#.......#....#...#",
            "###############5##",
        };

        /// <summary>
        /// 家の前〜バス停（40x16）。坂の上の通り。北にルリのアパートと家並み、南の柵の向こうは坂の下の町。
        /// ルリはアパートの戸（5）から出て、街灯（すぐ東の L）の下で足元に影が無いことに気づく。
        /// 東のバス停（屋根 X・ベンチ B・時刻表 Q）、Y は商店街の明かりを見下ろす所。東の端（1）が商店街へ。
        /// バス停の西の街灯は歩道の奥（家並みの側）：回想 1 で 8 歳の二人が、その手前の歩道で影踏みをする（車道で遊ばない）。
        /// </summary>
        public static readonly string[] HomeRows =
        {
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "########################################",
            "####5###################################",
            "#..........................L..XXX......1",
            "#..............................B.......1",
            "#......L.........U................Q....1",
            "#===================:::================1",
            "#===================:::================1",
            "#===================:::================1",
            "#...................................Y..1",
            "#.............L........................1",
            "########################################",
        };

        /// <summary>
        /// 商店街（48x16）。北に店が並ぶ（x：家 1-4／シャッター 5-8／路地その 2 の口 9-10／ランプ屋 11-15・戸 14／
        /// 佐伯商店 16-20／シャッター 21-24・屋根にルリの影 R／ゴマのくぼみ 25／家 26-29／シャッター 30-33／
        /// 路地その 1 の口 34-35／家 36-39／シャッター 40-43／家 44-47）。南は車道と歩道。
        /// 路地その 1 は右（東）：ハルの話を聞いたあと、家の前から来た流れのまま右へ進むと入れる（ユーザーの指摘で入れ替えた）。
        /// 西の端（1）が家の前へ、戸（2）がランプ屋の中へ、路地の口（3・4）がそれぞれの路地へ。
        /// </summary>
        public static readonly string[] StreetRows =
        {
            "################################################",
            "################################################",
            "#######################R########################",
            "################################################",
            "#########44#######################33############",
            "#########,,##############c########,,############",
            "#########,,###2##########,########,,############",
            "1..............N..GC..M........V.T....B........#",
            "1..............................................#",
            "1.....L.....L................U............L....#",
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
        /// 路地その 1 は低いブロック塀（w）に囲まれた裏の路地：塀の上は暗いので、触れると影は塀を越えて逃げる。
        /// 路地その 2 の行き止まりは高い建物の壁なので越えられない（「なぜ 1 回目は逃げられたのか」の答え。ユーザーの決定）。
        /// 口は商店街の街灯（L）で照らされていて、影は外へ出られない。
        /// </summary>
        public static readonly string[] Alley1Rows =
        {
            "####################",
            "####wwwwwwwwwwwwww##",
            "####w,,,,,,,,,,,,w##",
            "####w,,,,,,,,,,,,w##",
            "####w,,wwwwwwww,,w##",
            "####w,,wwwwwwww,,www",
            "####w,,H,,,,,,,,,,,w",
            "####w,,,,,,T,,,S,,,w",
            "####w,,wwwwwwwwwwwww",
            "####w,,w############",
            "####w,,w############",
            "####L,,w############",
            "####w,,w############",
            "####w33w############",
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
        public static readonly string[] AreaIds = { Room, Home, Street, LampShop, Alley1, Alley2 };

        public static readonly AreaLink[] Links =
        {
            new AreaLink('1', Home, Street),
            new AreaLink('2', Street, LampShop, isDoor: true),
            new AreaLink('3', Street, Alley1),
            new AreaLink('4', Street, Alley2),
            new AreaLink('5', Room, Home, isDoor: true),
        };

        public static string[] Rows(string area)
        {
            switch (area)
            {
                case Room: return RoomRows;
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
            // 画面の端の出入口（何マスもある）は、車道ではなく歩道の側に立つ
            var sidewalk = cells.FindAll(c => Array.Exists(Cell.Directions, d => map.At(c + d) == '.'));
            if (sidewalk.Count > 0)
                cells = sidewalk;
            cells.Sort((a, b) => a.X != b.X ? a.X.CompareTo(b.X) : a.Y.CompareTo(b.Y));
            var middle = cells[cells.Count / 2];
            foreach (var d in Cell.Directions)
            {
                var n = middle + d;
                char ch = map.At(n);
                if (GridMap.IsWalkable(ch) && !GridMap.IsLink(ch) && (ch == '.' || sidewalk.Count == 0))
                    return n;
            }
            throw new ArgumentException($"link {link} at {middle} has no walkable neighbour");
        }
    }
}
