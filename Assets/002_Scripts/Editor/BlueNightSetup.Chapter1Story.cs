using System.Collections.Generic;
using System.Linq;
using BlueNight.Audio;
using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.Interaction;
using BlueNight.Logic;
using BlueNight.Player;
using BlueNight.Rendering;
using BlueNight.Shadows;
using BlueNight.Story;
using BlueNight.World;
using UnityEngine;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// 序章と第 1 章の会話・演出（台本は docs/STORY.md 8 節＝序章・9 節＝第 1 章。セリフはそのまま使う。「／」はウィンドウの中の改行）。
    /// 台本に無いのは、操作の案内・通れないときの一言・回想の入りの一言だけ（どれも 1 行 22 字・2 行まで）。
    /// 流れはフラグでつなぐ（Flags）。会話は TalkInteractable / InspectInteractable、演出は Cutscene + CutsceneTrigger。
    /// </summary>
    public static partial class BlueNightSetup
    {
        /// <summary>序章・第 1 章のフラグ（並びは物語の順）。</summary>
        static class Flags
        {
            public const string Woke = "pro_woke";               // 部屋で目を覚ました
            public const string Scarf = "pro_scarf";             // マフラーを巻いた（玄関から出られる）
            public const string NoShadow = "pro_no_shadow";      // 街灯の下で影が無いことに気づいた（序章の終わり）
            public const string BenchMemory = "c1_bench_memory";
            public const string LanternTouched = "c1_lantern_touched";
            public const string MetNemu = "c1_met_nemu";
            public const string KeeperOpen = "c1_keeper_open";   // 主人が戸を開けた（ランプ屋に入れる）
            public const string GotLantern = "c1_got_lantern";
            public const string PracticeHung = "c1_practice_hung";
            public const string PracticeDone = "c1_practice_done";
            public const string KeeperBye = "c1_keeper_bye";
            public const string TalkedHaru = "c1_talked_haru";   // 路地その 1 に入れる
            public const string Alley1Intro = "c1_alley1_intro";
            public const string Alley1Escaped = "c1_alley1_escaped"; // 路地その 2 に入れる
            public const string Alley2Intro = "c1_alley2_intro";
            public const string Captured = "c1_captured";
            public const string Words = "c1_words";              // 影の言葉を聞いた（ことば帳：佐伯ハル「ありがとう」）
            public const string Delivered = "c1_delivered";
            public const string Returned = "c1_returned";        // 影がハルの足元へ戻った
            public const string GotStand = "c1_got_lantern_stand";
            public const string HaruSleep = "c1_haru_sleep";
            public const string Done = "c1_done";
        }

        // ------------------------------------------------------------------ 出入口の条件

        /// <summary>出入口（エリア・数字）ごとの「通れる条件」と、まだ通れないときの一言。BuildLinks が使う。</summary>
        static readonly Dictionary<(string area, char link), (string flag, DialogueLine[] lines)> LinkGates =
            new Dictionary<(string, char), (string, DialogueLine[])>
            {
                [(Chapter1Maps.Room, '5')] = (Flags.Scarf, new[] { N("椅子に、青いマフラーが／かかっている。") }),
                [(Chapter1Maps.Street, '2')] = (Flags.KeeperOpen, new[] { N("戸は閉まっている。") }),
                [(Chapter1Maps.LampShop, '2')] = (Flags.PracticeDone, new[] { N("ランタン掛けに、ランタンを／掛けてみよう。") }),
                [(Chapter1Maps.Street, '3')] = (Flags.TalkedHaru, new[] { N("路地の奥は、真っ暗だ。") }),
                [(Chapter1Maps.Street, '4')] = (Flags.Alley1Escaped, new[] { N("路地の奥は、真っ暗だ。") }),
            };

        // ------------------------------------------------------------------ 書き方の道具

        static DialogueLine L(string speaker, string text) => new DialogueLine(speaker, text.Replace("／", "\n"));
        static DialogueLine N(string text) => L("", text);                         // ト書き・画面の文字
        static DialogueLine Ru(string text) => L("ルリ", text);
        static DialogueLine Ne(string text) => L("ネム", text);
        static DialogueLine Ke(string text) => L("主人", text);
        static DialogueLine Ha(string text) => L("ハル", text);
        static DialogueLine ShadowVoice(string text) => new DialogueLine("", text.Replace("／", "\n"), shadowVoice: true);

        static ConditionalDialogue When(string requires, string unless, string sets, params DialogueLine[] lines) =>
            new ConditionalDialogue { requiresFlag = requires, unlessFlag = unless, setsFlag = sets, lines = lines };

        static ConditionalDialogue Always(params DialogueLine[] lines) => When(null, null, null, lines);

        static InspectInteractable Inspect(GameObject parent, string name, Vector3 position, params ConditionalDialogue[] entries)
        {
            var go = new GameObject($"Inspect: {name}");
            go.transform.SetParent(parent.transform, false);
            go.transform.position = position;
            var inspect = go.AddComponent<InspectInteractable>();
            inspect.SetPromptOffset(new Vector2(0f, 1.6f));
            inspect.Configure(entries);
            return inspect;
        }

        static Cutscene Scene(GameObject root, string name, string doneFlag, CutsceneTrigger.When when, string area = null, Rect? touch = null,
            string required = null, string blocked = null, string watch = null, params CutsceneStep[] steps)
        {
            var go = new GameObject($"Cutscene: {name}");
            go.transform.SetParent(root.transform, false);
            var cutscene = go.AddComponent<Cutscene>();
            cutscene.Configure(doneFlag, steps);
            go.AddComponent<CutsceneTrigger>().Configure(when, area, touch, required, blocked, watch);
            return cutscene;
        }

        static void React(GameObject root, string flag, GameObject[] show = null, GameObject[] hide = null,
            SimpleSpriteAnimator animator = null, Sprite[] frames = null, float fps = 1f)
        {
            var go = new GameObject($"On {flag}");
            go.transform.SetParent(root.transform, false);
            go.AddComponent<FlagReaction>().Configure(flag, show, hide, animator, frames, fps);
        }

        static CutsceneStep Say(params DialogueLine[] lines) => CutsceneStep.Say(lines);

        // ------------------------------------------------------------------ 序章と第 1 章

        static void BuildChapter1Story(Dictionary<string, Area> areas, PlayerController player, Material lit, Material unlit)
        {
            var story = new GameObject("Story (Prologue & Chapter 1)");
            Vector3 At(string area, int x, int y, float dx = 0f, float dy = 0f) =>
                areas[area].transform.position + CellFoot(new Cell(x, y)) + new Vector3(dx, dy, 0f);
            Cell One(string area, char ch) => Chapter1Maps.Create(area).Find(ch).Single();
            Rect Box(string area, float x, float y, float w, float h) =>
                new Rect(areas[area].transform.position.x + x, areas[area].transform.position.y + y, w, h);

            var nemu = player.transform.Find("Nemu").gameObject;
            var lantern = player.transform.Find("Lantern").gameObject;
            nemu.SetActive(false);       // ネムはランプ屋の前で出会う
            lantern.SetActive(false);    // ランタンは主人からもらう
            React(story, Flags.MetNemu, show: new[] { nemu });
            var eaves = areas[Chapter1Maps.Street].transform.Find("Props/Old Lantern (Nemu's home)").gameObject;
            React(story, Flags.GotLantern, show: new[] { lantern }, hide: new[] { eaves });

            BuildPrologue(story, areas, At, Box);
            BuildChapter1Street(story, areas, player, At, One, unlit);
            BuildChapter1LampShop(story, areas, At, Box);
            BuildChapter1Alleys(story, areas, player, At, One, Box, unlit);
        }

        // ---- 序章「眠れない夜」（8 節）：部屋 → 台所 → 玄関 → アパートの前の街灯
        static void BuildPrologue(GameObject story, Dictionary<string, Area> areas,
            System.Func<string, int, int, float, float, Vector3> At, System.Func<string, float, float, float, float, Rect> Box)
        {
            string room = Chapter1Maps.Room, home = Chapter1Maps.Home;
            var roomGo = areas[room].gameObject;
            var phoneGlow = roomGo.transform.Find("Furniture/Phone Glow");

            Scene(story, "目を覚ます", Flags.Woke, CutsceneTrigger.When.AreaEnter, area: room, steps: new[]
            {
                CutsceneStep.Fade(true, 0.01f),
                CutsceneStep.MusicTo("", 0.1f),               // 序章は曲なし（時計の音・遠くのハイウェイ・虫）
                CutsceneStep.WaitFor(1.6f),
                CutsceneStep.Fade(false, 2.2f),
                CutsceneStep.WaitFor(0.6f),
                Say(Ru("……まだ、夜だ")),
                CutsceneStep.WalkTo((Vector2)At(room, 2, 5, 0f, 0f), 2f),
                CutsceneStep.FaceTo(Facing.Up),
                CutsceneStep.ShowActor(phoneGlow),
                CutsceneStep.Sfx("cursor"),
                CutsceneStep.WaitFor(0.9f),
                Say(N("ミオ　新着メッセージ 2 件")),
                CutsceneStep.HideActor(phoneGlow),
                CutsceneStep.WaitFor(0.5f),
                Say(Ru("……見ない")),
                Say(N("移動 WASD・矢印キー／調べる Space・E・Z")),
            });

            Inspect(roomGo, "Desk (phone)", At(room, 2, 6, 0f, 0f),
                When(Flags.Woke, null, null, Ru("……見ない")));
            Inspect(roomGo, "Fridge (note from Mom)", At(room, 12, 6, 0f, 0f),
                Always(N("おかず、冷蔵庫。／先に寝ててね。　母"), N("その下に、ルリの字で／小さく『了解』。")));
            Inspect(roomGo, "Window (bay)", At(room, 5, 6, 0f, 0f),
                Always(N("湾の上を、高架道路の車の／光が流れていく。")));
            var chairScarf = roomGo.transform.Find("Furniture/Chair with the Blue Scarf").gameObject;
            var chairPlain = roomGo.transform.Find("Furniture/Chair").gameObject;
            chairPlain.SetActive(false);
            Inspect(roomGo, "Chair (blue scarf)", At(room, 16, 3, 0f, 0f),
                When(null, Flags.Scarf, Flags.Scarf, N("椅子にかけた、青いマフラー。"), Ru("……暑い")));
            React(story, Flags.Scarf, show: new[] { chairPlain }, hide: new[] { chairScarf });

            // 外。坂の上の街灯の下で、足元に影が無いことに気づく（何も言わない）
            var lamp = Chapter1Maps.Create(home).Find('L').OrderBy(c => c.X).First();
            Scene(story, "影が無い", Flags.NoShadow, CutsceneTrigger.When.Touch,
                touch: Box(home, lamp.X - 1.5f, lamp.Y - 1f, 4f, 3.5f), steps: new[]
                {
                    CutsceneStep.WalkTo((Vector2)At(home, lamp.X + 1, lamp.Y, 0f, 0f), 2f),
                    CutsceneStep.WaitFor(0.6f),
                    CutsceneStep.FaceTo(Facing.Up),
                    CutsceneStep.WaitFor(1.4f),
                    CutsceneStep.FaceTo(Facing.Down),
                    CutsceneStep.WaitFor(1.8f),
                    Say(Ru("…………")),
                    CutsceneStep.WaitFor(0.8f),
                    CutsceneStep.MusicTo("ch1_shopping_street", 5f),   // ここから第 1 章
                    Say(N("小走り Shift")),
                    CutsceneStep.Save(),
                });
        }

        // ---- 第 1 章：バス停（9.1）・ランプ屋の前（9.2）・佐伯商店（9.4）・届ける（9.8）・屋根の上（9.9）・章の終わり（9.10）
        static void BuildChapter1Street(GameObject story, Dictionary<string, Area> areas, PlayerController player,
            System.Func<string, int, int, float, float, Vector3> At, System.Func<string, char, Cell> One, Material unlit)
        {
            string home = Chapter1Maps.Home, street = Chapter1Maps.Street;
            var homeGo = areas[home].gameObject;
            var streetGo = areas[street].gameObject;

            // バス停
            var q = One(home, 'Q');
            Inspect(homeGo, "Timetable", At(home, q.X, q.Y, 0f, 0f),
                Always(Ru("最終、22 時 48 分。／……とっくに行っちゃった")));
            var bench = One(home, 'B');
            Inspect(homeGo, "Bench", At(home, bench.X, bench.Y, 0f, 0f),
                When(null, Flags.BenchMemory, Flags.BenchMemory, N("——8 歳の夜。／このベンチで、母のバスを待っていた。")),
                Always(Ru("……")));
            Scene(story, "回想 1（ベンチ）", null, CutsceneTrigger.When.Flag, watch: Flags.BenchMemory, steps: new[]
            {
                CutsceneStep.Fade(true, 0.8f),
                Say(L("ミオ", "ひとり？"), Ru("……"), L("ミオ", "わたしも。／影踏みしよ。街灯の下なら、影あるよ")),
                CutsceneStep.Fade(false, 0.8f),
                Say(Ru("……今は、無いけど")),
            });
            var view = One(home, 'Y');
            Inspect(homeGo, "Lights of the shopping street", At(home, view.X, view.Y, 0f, 0f),
                Always(Ru("明かりのついてる窓、／数えてた。昔から"), Ru("起きてる人がいると、／ひとりじゃない気がして"),
                    Ru("あそこの窓は、いつも／最後まで明るかった"), Ru("……ランプ屋さん")));

            // ランプ屋の前：看板・軒先のランタン（ネムと出会う）
            Inspect(streetGo, "Sign of the lamp shop", At(street, 12, 9, 0f, 0f),
                Always(Ru("『闇を嘆くより　灯をひとつ』")));
            var n = One(street, 'N');
            Inspect(streetGo, "Old lantern", At(street, n.X, n.Y, 0f, 0f),
                When(null, Flags.LanternTouched, Flags.LanternTouched, N("軒先の古いランタンだけが、／ぼんやり灯っている。")));
            Scene(story, "ネムと出会う", Flags.MetNemu, CutsceneTrigger.When.Flag, watch: Flags.LanternTouched, steps: new[]
            {
                CutsceneStep.Sfx("light_on"),
                CutsceneStep.Flag(Flags.MetNemu),
                CutsceneStep.WaitFor(0.6f),
                Say(Ne("わっ！ ……びっくりした"), Ne("人間だ。こんな時間に"), Ru("……蛾が、しゃべった"),
                    Ne("蛾じゃない。オオミズアオ"), Ne("ネム。……って、きみ、影は？"), Ru("……"), Ne("やっぱり。きみもか"),
                    Ne("今夜ね、町じゅうの影が／逃げちゃったんだ"), Ne("影がないと、人は眠れない"), Ne("眠れないと、朝が来ない"),
                    Ne("だから今夜はずっと夜"), Ru("……べつに困らない"), Ne("困るよ！ ……えっと"),
                    Ne("ぼくは困らないけど。／いや、困るんだって"), Ne("影を連れ戻せば、朝は来る"), Ne("ねえ、手伝ってくれない？"),
                    Ne("ぼく、暗いところ、苦手で"), Ru("……夜の虫なのに？"), Ne("夜の虫だからだよ"), Ne("ぼくらは灯りが好きなの"),
                    Ne("暗いのは灯りがない／ところでしょ")),
                CutsceneStep.WaitFor(0.8f),
                Say(Ru("……虫なのに、しゃべるんだ"), Ne("でしょ？ しかもぼく"), Ne("口、ないんだよ"), Ne("ものも、食べない"),
                    Ne("しゃべるのは、ないしょの特技"), Ru("…………"), Ne("いま、ちょっと笑った？"), Ru("……べつに")),
                CutsceneStep.Sfx("lantern_take"),             // 店の戸が開く
                CutsceneStep.WaitFor(0.5f),
                Say(Ke("……こんな夜ふけに、なんだ"), Ne("青柳さん！ この子も／影がないんだ"), Ne("手伝ってもらおうと思って"),
                    Ke("……そうか")),
                CutsceneStep.WaitFor(1.2f),
                Say(Ke("入んな。夜風は、体に毒だ")),
                CutsceneStep.Flag(Flags.KeeperOpen),
                CutsceneStep.Go(Chapter1Maps.LampShop, "2"),
            });

            // 佐伯商店：ハル・日よけ・ゴマ
            var haruTransform = streetGo.transform.Find("Characters/Haru");
            var haru = haruTransform.gameObject;
            haru.AddComponent<TalkInteractable>().Configure(
                When(Flags.HaruSleep, null, null, N("……すう……すう……")),
                When(Flags.Captured, Flags.Delivered, Flags.Delivered,
                    Ru("……あの"), Ru("影が言ってました"), Ru("『ありがとう』って"), Ru("『あの朝、言えなかった』"),
                    Ru("『帽子のことなんか、／どうでもよかったのに』って"), Ha("…………"), Ha("……ああ。そうだよ"), Ha("そうだった"),
                    Ha("じいさんが入院した朝ね"), Ha("あたしが言ったのは"), Ha("『ほら、帽子かぶってきな』"), Ha("それが、最後さ"),
                    Ha("ありがとうなんて／安い言葉なのにさ"), Ha("とうとう、言えなかった"),
                    Ha("この日よけもね"), Ha("あの人が、つくろったんだよ"), Ha("毎年、春に何も言わずに"),
                    Ha("……ありがとね、あんた"), Ha("帽子、似合ってたよ")),
                When(Flags.TalkedHaru, Flags.Captured, null, Ha("無理するんじゃないよ"), Ha("……ほら、気をつけて")),
                When(Flags.GotLantern, null, Flags.TalkedHaru,
                    Ha("おや……ルリちゃんじゃないか"), Ha("こんな時間に、どうしたんだい"), Ru("……眠れなくて"), Ha("あたしもだよ"),
                    Ha("年寄りは眠れないもんだけど"), Ha("今夜はまた、特別でね"), Ha("あたしの影がいなくなった"),
                    Ha("あっちの路地へ、すうっと"), Ne("ほらね"), Ha("なんだい、その虫。／……まあ、いいや"),
                    Ha("最近の子は変わったもん／連れてるね"), Ha("ミオちゃんは？"), Ha("あんたたち、いつも二人／だったじゃないか"),
                    Ha("ラムネ、二本ずつ"), Ru("…………"), Ha("ああ、そうか。明日だったね"), Ha("……ごめんよ"),
                    Ha("年寄りは余計なこと／ばっかり言う"), Ha("青い夜が明けないのはね"), Ha("だれかが朝をこわがって／るんだってさ"),
                    Ha("むかし、うちのばあさんが／言ってた"), Ru("……影、さがしてきます"), Ha("無理するんじゃないよ"),
                    Ha("……ほら、気をつけて")),
                Always(N("おばあさんが、店先で／ぼんやり座っている。")));
            Inspect(streetGo, "Awning", At(street, 17, 9, 0f, 0f),
                Always(N("しま模様の日よけ。／ていねいにつくろってある")));
            var goma = One(street, 'C');
            Inspect(streetGo, "Goma", At(street, goma.X, goma.Y, 0f, 0f),
                When(Flags.MetNemu, null, null, Ne("この猫、ゴマっていうんだ"), Ne("おばあさんの煮干しを狙ってる"), Ne("……あれ、この子も影がない")),
                Always(N("のら猫が寝ている。")));

            // 影が戻る → ハルが眠くなる・ランタン立て（9.8）→ 屋根の上のルリの影（9.9）→ 章の終わり（9.10）
            var footShadow = haruTransform.Find("Foot Shadow").gameObject;
            React(story, Flags.Returned, show: new[] { footShadow });
            React(story, Flags.HaruSleep, animator: haru.GetComponent<SimpleSpriteAnimator>(),
                frames: LoadFrames($"{TexturesRoot}/Characters/Grandma/grandma_doze_"), fps: 0.8f);

            var r = One(street, 'R');
            var roofShadow = CreateLoop(streetGo, "Ruri's Shadow (roof)", "Characters/Shadows/shadow_ruri_idle_down_",
                At(street, r.X, r.Y, 0f, 0.8f), unlit, 4f);
            roofShadow.SetActive(false);

            Scene(story, "届ける・屋根の上・章の終わり", Flags.Done, CutsceneTrigger.When.Flag, watch: Flags.Delivered, steps: new[]
            {
                CutsceneStep.Flag(Flags.Returned),             // 影がハルの足元へ戻る（光のつぶ）
                CutsceneStep.WaitFor(3f),
                Say(Ha("……おや"), Ha("なんだか、急に眠くなってきた"), Ha("ルリちゃん"), Ha("言えるときに言わないと"),
                    Ha("言えなくなるんだねえ"), Ha("……年寄りのつまらない話")),
                CutsceneStep.WaitFor(0.6f),
                Say(Ha("そうだ、これ、持っておいき"), Ha("じいさんが作った／ランタン立て"), Ha("地面に置いても倒れない"),
                    Ha("あたしが持ってても／しょうがないからね")),
                CutsceneStep.Sfx("journal_add"),
                Say(N("ランタン立てを、もらった。")),
                CutsceneStep.Flag(Flags.GotStand),
                CutsceneStep.Flag(Flags.HaruSleep),
                CutsceneStep.WaitFor(2f),
                Say(Ne("……ねえ、ルリ。屋根の上")),
                CutsceneStep.FaceTo(Facing.Up),
                CutsceneStep.ShowActor(roofShadow.transform),
                CutsceneStep.Sfx("shadow_presence"),
                CutsceneStep.WaitFor(1.2f),
                Say(Ru("……わたしの、影"), L("ルリの影", "やっと気づいた")),
                CutsceneStep.WaitFor(0.6f),
                Say(L("ルリの影", "おばあちゃん、よかったね"), L("ルリの影", "ありがとうって言えて"), L("ルリの影", "ルリはさ"),
                    L("ルリの影", "ミオに言えなかったこと、／あるでしょ"), Ru("……"), L("ルリの影", "……あるよね？"),
                    L("ルリの影", "つかまえてごらん"), L("ルリの影", "つかまえられたら／教えてあげる")),
                CutsceneStep.Sfx("shadow_escape"),
                CutsceneStep.HideActor(roofShadow.transform),
                CutsceneStep.Amb("rain", 0.45f, 6f),          // ぽつり、と雨が降り出す
                CutsceneStep.WaitFor(1.5f),
                Say(Ne("ルリ……今の、知り合い？"), Ru("……べつに"), Ne("べつにって顔じゃないよ"), Ru("…………行く"), Ru("追いかける")),
                CutsceneStep.WaitFor(0.8f),
                CutsceneStep.Fade(true, 2f),
                CutsceneStep.WaitFor(1f),
                Say(N("第 1 章　灯をひとつ")),
                CutsceneStep.Save(),
                CutsceneStep.Fade(false, 2f),
            });
        }

        // ---- ランプ屋の中（9.3）：影のきまり・ランタンをもらう・掛ける練習・出口の一言
        static void BuildChapter1LampShop(GameObject story, Dictionary<string, Area> areas,
            System.Func<string, int, int, float, float, Vector3> At, System.Func<string, float, float, float, float, Rect> Box)
        {
            string shop = Chapter1Maps.LampShop;
            var shopGo = areas[shop].gameObject;
            Scene(story, "影のきまり・ランタン", Flags.GotLantern, CutsceneTrigger.When.AreaEnter, area: shop,
                required: Flags.KeeperOpen, steps: new[]
                {
                    CutsceneStep.WaitFor(0.6f),
                    CutsceneStep.WalkTo((Vector2)At(shop, 8, 3, 0f, 0f), 2f),
                    CutsceneStep.FaceTo(Facing.Up),
                    Say(Ke("影はな、光の向こうにできる"), Ke("影があるってことは"), Ke("どこかに灯りがある／ってことだ"),
                        Ke("今夜の影どもは／それを忘れて逃げとる"), Ke("やつらは暗いところしか／通れん"), Ke("光の中には入れん"),
                        Ke("だから、灯りで道をふさげ"), Ke("町のあちこちに／ランタン掛けがある"), Ke("掛けりゃ、そこは／ずっと明るいままだ")),
                    CutsceneStep.WaitFor(0.6f),
                    Say(Ke("持っていけ")),
                    CutsceneStep.Flag(Flags.GotLantern),
                    CutsceneStep.Sfx("lantern_take"),
                    Say(Ne("えっ、それ、ぼくの家……"), Ke("おまえも行くんだ"), Ne("……ですよね"), Ru("……いいんですか"),
                        Ru("大事なものじゃ"), Ke("灯りは、暗いところでしか／役に立たん"), Ke("しまっておいても／しょうがない")),
                    Say(N("ランタン掛けの前で F（X）／ランタンを掛ける・外す")),
                });
            foreach (var h in shopGo.GetComponentsInChildren<LanternHook>(true))
                h.SetFlagOnHang(Flags.PracticeHung);
            Scene(story, "影が動く", Flags.PracticeDone, CutsceneTrigger.When.Flag, watch: Flags.PracticeHung, steps: new[]
            {
                CutsceneStep.WaitFor(0.8f),
                Say(Ne("ほら、影の向きが変わった"), Ne("灯りを動かすと、影も動く"), Ke("……長い夜には、わけがある"), Ru("……わけ？"),
                    Ke("そのうち、わかる")),
            });
            Scene(story, "出口の一言", Flags.KeeperBye, CutsceneTrigger.When.Touch, touch: Box(shop, 5.5f, 0f, 4f, 1.6f),
                required: Flags.PracticeDone, steps: new[]
                {
                    Say(Ke("おまえさん"), Ke("……ひとりで、平気か"), Ru("……大丈夫。慣れてるから"), Ke("……そうか")),
                });
            Inspect(shopGo, "Grandfather clock", At(shop, 12, 6, 0f, 0f), Always(Ru("……3 時 12 分"), Ru("うちの時計と同じ")));
            Inspect(shopGo, "Shelves", At(shop, 5, 6, 0f, 0f),
                When(Flags.MetNemu, null, null, Ne("ここのランプ、ぜんぶ／青柳さんが直したんだ"), Ne("ぼくの評価？ 全部、三ツ星")));
            Inspect(shopGo, "Workbench", At(shop, 2, 4, 0f, 0f), Always(N("分解されたランプ。／ガラスのほやが並んでいる")));
        }

        // ---- 路地その 1（9.5）・その 2（9.6）・影の言葉（9.7）
        static void BuildChapter1Alleys(GameObject story, Dictionary<string, Area> areas, PlayerController player,
            System.Func<string, int, int, float, float, Vector3> At, System.Func<string, char, Cell> One,
            System.Func<string, float, float, float, float, Rect> Box, Material unlit)
        {
            string alley1 = Chapter1Maps.Alley1, alley2 = Chapter1Maps.Alley2;
            var haru = areas[Chapter1Maps.Street].transform.Find("Characters/Haru");

            // 路地その 1：近づくと逃げる。角に掛けて追いつめると、触れた瞬間に塀を越えて奥の路地へ
            Scene(story, "逃げた！", Flags.Alley1Intro, CutsceneTrigger.When.Touch, touch: Box(alley1, 4.8f, 4.5f, 2.6f, 3.5f), steps: new[]
            {
                Say(Ne("逃げた！"), Ne("光で道をふさがなきゃ"), Ne("あそこにランタン掛け"), Ne("あの角を明るくすれば"), Ne("影は奥に閉じこめられる")),
            });
            var s1 = One(alley1, 'S');
            var shadow1 = CreateGrandmaShadow(s1, player.transform, haru, unlit);
            shadow1.transform.SetParent(areas[alley1].transform, false);
            shadow1.transform.position = At(alley1, s1.X, s1.Y, 0f, 0f);
            shadow1.SetEscapeOnTouch(true);
            shadow1.Configure(player.transform, haru, LoadFrames($"{TexturesRoot}/Characters/Shadows/shadow_grandma_"),
                new[] { Ne("惜しい！"), Ne("でも、わかったでしょ"), Ne("灯りの置き方しだいなんだ") },
                Flags.Alley1Escaped, "c1_unused_returned");
            shadow1.gameObject.AddComponent<ChaseMusic>().Configure(shadow1, player.transform, "ch1_shopping_street");

            // 路地その 2：輪の路地。ネムのヒント（3 段階）
            Scene(story, "輪の路地", Flags.Alley2Intro, CutsceneTrigger.When.AreaEnter, area: alley2, steps: new[]
            {
                CutsceneStep.WaitFor(0.8f),
                Say(Ne("ぐるぐる回られると／追いつけないね"), Ne("輪の角にランタン掛けがある"), Ne("光で輪を切っちゃえばいい"),
                    Ne("街灯とランタン、二つの光で"), Ne("輪を二か所で切るんだ"), Ne("そしたら、影は行き止まり")),
            });
            var s2 = One(alley2, 'S');
            var shadow2 = CreateGrandmaShadow(s2, player.transform, haru, unlit);
            shadow2.transform.SetParent(areas[alley2].transform, false);
            shadow2.transform.position = At(alley2, s2.X, s2.Y, 0f, 0f);
            shadow2.Configure(player.transform, haru, LoadFrames($"{TexturesRoot}/Characters/Shadows/shadow_grandma_"),
                new[] { ShadowVoice("……ありがとう、って"), ShadowVoice("あの朝、言えなかった"), ShadowVoice("帽子のことなんか、／どうでもよかったのに") },
                Flags.Captured, Flags.Returned);
            shadow2.gameObject.AddComponent<ChaseMusic>().Configure(shadow2, player.transform, "ch1_shopping_street");

            // 捕まえた会話のすぐあとに続ける（間をあけると「影の言葉」の曲が町の曲へ戻ってしまう）
            Scene(story, "影の言葉", Flags.Words, CutsceneTrigger.When.Flag, watch: Flags.Captured, steps: new[]
            {
                Say(Ne("……これが、影の言葉"), Ne("持ち主が言えなかった言葉"), Ru("…………"), Ne("ルリ？"), Ru("……届けよう")),
                CutsceneStep.Sfx("journal_add"),
                Say(N("ことば帳に書いた。／佐伯ハル『ありがとう』")),
            });
        }
    }
}
