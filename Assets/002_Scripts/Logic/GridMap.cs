using System;
using System.Collections.Generic;

namespace BlueNight.Logic
{
    /// <summary>
    /// 文字で書いたマップ。1 文字 = 1 マス（16 px）。上の行ほど北（Y が大きい）。
    ///
    ///   #  壁・建物（光も人も通さない）     R  屋根の上（壁。第 1 章でルリの影が立つ所）
    ///   .  歩道（広場・床）  ,  路地（アスファルト）  =  車道  :  横断歩道
    ///   L  街灯（柱は通れない。光源）
    ///   H  路地のランタン掛け   h  広場・店の中のランタン掛け
    ///   V  自販機  A  室外機  T  ごみ箱  X  家具・バス停の壁（通れない。影を落とす）
    ///   B  ベンチ  M  ポスト  U  電柱  Q  バス停の標識（通れない）
    ///   G  おばあさん（ハル）  K  ランプ屋の主人  C  のら猫ゴマ（通れない）
    ///   N  軒先の古いランタン（ネムの住みか。通れる）  Y  調べる場所（通れる）
    ///   P  ルリの初期位置   S  逃げた影の初期位置   c  落とし影（ゴマの影）の初期位置
    ///   1〜9  ほかのエリアへの出入口（同じ数字どうしがつながる。通れる。Chapter1Maps.Links）
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

        public static bool IsWall(char c) => c == '#' || c == 'R';
        public static bool IsSolid(char c) => "LVGATXBMUQKC".IndexOf(c) >= 0;
        public static bool IsAlley(char c) => c == ',' || c == 'H' || c == 'S';
        public static bool IsLink(char c) => c >= '1' && c <= '9';
        public static bool IsWalkable(char c) => !IsWall(c) && !IsSolid(c);

        /// <summary>影を落とすモノの高さ（マス）。影を落とさないなら 0。</summary>
        public static float CasterHeight(char c)
        {
            switch (c)
            {
                case 'V': return 1.5f;   // 自販機（M1Map.VendingHeight と同じ）
                case 'X': return 1.2f;   // 棚・カウンター・バス停の壁
                case 'A': return 1f;     // 室外機
                case 'T': return 0.8f;   // ごみ箱
                default: return 0f;
            }
        }

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
