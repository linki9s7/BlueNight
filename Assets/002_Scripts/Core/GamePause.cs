namespace BlueNight.Core
{
    /// <summary>
    /// 遊びを止めている間（第 2 章の「見渡す」など）。逃げた影は動かず、捕まる判定もしない。
    /// 会話（DialogueRunner.IsBusy）とは別：会話は会話で止まる。
    /// </summary>
    public static class GamePause
    {
        public static bool IsPaused { get; set; }
    }
}
