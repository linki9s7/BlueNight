using System.Collections.Generic;

namespace BlueNight.Logic
{
    /// <summary>
    /// 第 2 章 追いかけっこの試作マップ（30x20）。建物のまわりの輪の路地。ルリは南の広場から入る（入口は街灯 L で照らされている）。
    /// 影（S）は北の路地で待っている。抜け道は 2 つ：
    /// - 東の抜け道（E）：奥の門灯（l）を点ければふさがる。
    /// - 北の抜け道（e、水たまりの上）：奥の門灯（l）を点けても、路地の上の看板（n）の逆さの影が水たまりに映って、開いたまま。
    ///   ランタンを抜け道の手前（西側）に置いて照らすとふさがり、同じ光で北の路地も切れる。
    /// 答え：東の門灯を点け、ランタンを (12,14)・(13,14)・(14,14)・(13,15)・(14,16) のどれかに置く（北の門灯は点けても点けなくてもよい）。
    /// 全部点けただけでは、北の抜け道から逃げられる。ランタンが要る。影から 4 マス以内に置くと、影が気づいて逃げ出す。
    /// </summary>
    public static class Chapter2ProtoMap
    {
        /// <summary>いつも点いている街灯（L）。</summary>
        public const float StreetLampRadius = 4.5f;
        /// <summary>点け消しできる小さな門灯（l）。低い所にあるので、そばの物の影が長く伸びる。</summary>
        public const float SmallLampRadius = 3f;
        public const float SmallLampHeight = 1f;
        public const float LanternRadius = 3f;
        /// <summary>ルリがこれより近づくと、待っている影が気づいて逃げ出す（RunawayShadow.noticeDistance と同じ）。</summary>
        public const float NoticeDistance = 4f;

        public static readonly string[] Rows =
        {
            "##############################",
            "##############l###############",
            "##############e###############",
            "##############o###############",
            "######,,,,,,,,n,,,S,,,,,######",
            "######,,,,,,,,,,,,,,,,,,######",
            "######,,##############,,######",
            "######,,##############,,######",
            "######,,##############,,######",
            "######,,##############,,######",
            "######,,##############,,######",
            "######,,##############,,,El###",
            "######,,##############,,######",
            "######,,,,,,,,,,,,,,,,,,######",
            "######,,,,,,,,,,,,,,,,,,######",
            "##############,,##############",
            "##############,,##############",
            "#............................#",
            "#.............L.P............#",
            "##############################",
        };

        /// <summary>答え：点ける町の灯り（l）。</summary>
        public static readonly Cell[] SolutionLamps = { new Cell(5, 8), new Cell(26, 9) };

        /// <summary>答え：ランタンを置くマス。</summary>
        public static readonly Cell SolutionLantern = new Cell(13, 14);

        public static GridMap Create() => new GridMap(Rows);
    }
}
