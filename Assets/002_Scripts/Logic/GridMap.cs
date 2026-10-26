using System;
using System.Collections.Generic;

namespace BlueNight.Logic
{
    /// <summary>
    /// 文字で書いたマップ。1 文字 = 1 マス（16 px）。上の行ほど北（Y が大きい）。
    ///
    ///   #  壁・建物（光も人も通さない）
    ///   .  歩道（広場）
    ///   ,  路地（アスファルト）
    ///   L  街灯（柱は通れない。光源）
    ///   H  路地のランタン掛け   h  広場のランタン掛け
    ///   V  自販機（通れない。影を落とす）
    ///   G  おばあさん
    ///   P  ルリの初期位置
    ///   S  逃げた影の初期位置
    /// </summary>
    public sealed class GridMap
    {
        public readonly string[] Rows;
        public int Width => Rows[0].Length;
        public int Height => Rows.Length;

        public GridMap(string[] rows)
        {
            if (rows == null || rows.Length == 0)
                throw new ArgumentException("map is empty");
            foreach (var row in rows)
                if (row.Length != rows[0].Length)
                    throw new ArgumentException($"row width mismatch: {row}");
            Rows = rows;
        }

        public char At(Cell c) => c.Y >= 0 && c.Y < Height && c.X >= 0 && c.X < Width ? Rows[Height - 1 - c.Y][c.X] : '#';

        public IEnumerable<Cell> Find(char symbol)
        {
            for (int y = 0; y < Height; y++)
                for (int x = 0; x < Width; x++)
                    if (At(new Cell(x, y)) == symbol)
                        yield return new Cell(x, y);
        }

        public static bool IsWall(char c) => c == '#';
        public static bool IsSolid(char c) => c == 'L' || c == 'V' || c == 'G';
        public static bool IsAlley(char c) => c == ',' || c == 'H' || c == 'S';

        /// <summary>壁と通れないモノを書き込んだ ShadowGrid を作る。</summary>
        public ShadowGrid CreateGrid()
        {
            var grid = new ShadowGrid(Width, Height);
            for (int y = 0; y < Height; y++)
            {
                for (int x = 0; x < Width; x++)
                {
                    var c = new Cell(x, y);
                    char ch = At(c);
                    if (IsWall(ch)) grid.SetWall(c);
                    else if (IsSolid(ch)) grid.SetSolid(c);
                }
            }
            return grid;
        }
    }

    /// <summary>
    /// M1 プロトタイプのマップ。
    /// 建物のまわりをぐるりと回る暗い路地（輪）に、おばあさんの影が逃げ込んでいる。
    /// 輪のままでは影は追いかけっこで逃げ続けるが、角のランタン掛けに光を置くと輪が切れ、
    /// 行き止まりに追いつめられるようになる。入口は街灯で照らされていて、影は広場へ出られない。
    /// </summary>
    public static class M1Map
    {
        public const float StreetLampRadius = 4.5f;
        public const float LanternRadius = 3f;
        public const float VendingHeight = 1.5f;

        public static readonly string[] Rows =
        {
            "################################",
            "#..............L...............#",
            "#..............................#",
            "#.......################.......#",
            "#..L....#H,,,,,,,,,,,,H#....L..#",
            "#.......#,,,,,,S,,,,,,,#.......#",
            "#.......#,,##########,,#.......#",
            "#.......#,,##########,,#..G....#",
            "#.......#,,##########,,#.......#",
            "#.......#,,##########,,#.......#",
            "#.......#,,##########,,#.......#",
            "#.......#,,##########,,#.......#",
            "#.......#,,,,,,,,,,,,,,#.......#",
            "#....V..#H,,,,,,,,,,,,H#.......#",
            "#.......#######,,#######.......#",
            "#..............................#",
            "#..L........h....P..........L..#",
            "#..............................#",
            "#..............L...............#",
            "################################",
        };

        public static GridMap Create() => new GridMap(Rows);
    }
}
