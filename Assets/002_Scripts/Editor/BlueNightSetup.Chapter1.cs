using System.Collections.Generic;
using System.Linq;
using BlueNight.Audio;
using BlueNight.Core;
using BlueNight.Dialogue;
using BlueNight.LightShadow;
using BlueNight.Logic;
using BlueNight.Player;
using BlueNight.Rendering;
using BlueNight.Shadows;
using BlueNight.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Tilemaps;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// 第 1 章「灯をひとつ」のシーン（M2）。マップは BlueNight.Logic.Chapter1Maps（テストと同じ定義）から組み立てる。
    /// 5 つのエリア（家の前〜バス停・商店街・ランプ屋の中・路地その 1・路地その 2）を横に並べ、出入口（数字）で暗転してつなぐ。
    /// 会話・演出（docs/STORY.md 8 節＝序章・9 節＝第 1 章）は BlueNightSetup.Chapter1Story で入れる。
    /// </summary>
    public static partial class BlueNightSetup
    {
        const string Chapter1ScenePath = "Assets/001_Scenes/Chapter1.unity";
        const float AreaSpacing = 64f;

        // 北の店の並び（左端の x と絵）。足元は「歩道のいちばん北の行」の上のふち
        static readonly (int x, string sprite)[] StreetBuildings =
        {
            (1, "house"), (5, "shutter_shop_0"), (11, "lamp_shop"), (16, "grandma_shop"), (21, "shutter_shop_1"),
            (26, "house"), (30, "shutter_shop_0"), (36, "house"), (40, "shutter_shop_1"), (44, "house"),
        };

        static readonly (int x, string sprite)[] HomeBuildings =
        {
            (2, "house"), (9, "house"), (22, "house"),
        };

        [MenuItem("BlueNight/7. 第 1 章のシーンを作成", priority = 26)]
        public static void BuildChapter1Scene()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
                return;

            EnsureProjectConfigured();

            EnsureFolder("Assets/001_Scenes");
            EnsureFolder(TileAssetFolder);
            EnsureFolder("Assets/009_Rendering");
            AssetDatabase.ImportAsset(TexturesRoot, ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceUpdate);

            var lit = AssetDatabase.LoadAssetAtPath<Material>(SpriteLitMaterialPath);
            var unlit = AssetDatabase.LoadAssetAtPath<Material>(SpriteUnlitMaterialPath);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            Camera camera = CreateCamera();
            CreateMoonlight();
            CreateVolume();

            var areas = new List<Area>();
            var areaObjects = new Dictionary<string, Area>();
            for (int i = 0; i < Chapter1Maps.AreaIds.Length; i++)
            {
                string id = Chapter1Maps.AreaIds[i];
                var area = BuildArea(id, new Vector2(i * AreaSpacing, 0f), lit, unlit);
                areas.Add(area);
                areaObjects[id] = area;
            }

            // 序章：ルリの部屋のふとんで目を覚ます
            var roomMap = Chapter1Maps.Create(Chapter1Maps.Room);
            var start = AreaCellFoot(areaObjects[Chapter1Maps.Room], roomMap.Find('P').Single());
            areaObjects[Chapter1Maps.Room].AddSpawn("start", start);

            PlayerController player = CreateRuri(lit, start, withLanternLight: false);
            CreateLanternAndInteractor(player, unlit);
            CreateNemu(lit, player);
            player.gameObject.AddComponent<PlayerAreaSounds>();

            // 序章は曲なし（虫の声と遠くのハイウェイ）。曲は街灯の下の演出のあとから
            CreateAudio("", Ambience("crickets", 0.55f), Ambience("highway", 0.35f));
            var dialogue = new GameObject("Dialogue").AddComponent<DialogueRunner>();
            dialogue.Configure(AssetDatabase.LoadAssetAtPath<Font>(DialogueFontPath));

            BuildChapter1Story(areaObjects, player, lit, unlit);

            var follow = camera.gameObject.AddComponent<CameraFollow2D>();
            follow.Configure(player.transform, areaObjects[Chapter1Maps.Room].CameraBounds);
            new GameObject("Area Manager").AddComponent<AreaManager>()
                .Configure(areas.ToArray(), Chapter1Maps.Room, "start", player, follow);

            EditorSceneManager.SaveScene(scene, Chapter1ScenePath);
            AddSceneToBuildSettings(Chapter1ScenePath);
            Debug.Log($"[BlueNight] {Chapter1ScenePath} を作成しました。再生すると、ルリの部屋（序章）から第 1 章の終わりまで遊べます。");
        }

        static Vector3 AreaCellFoot(Area area, Cell cell) => area.transform.position + CellFoot(cell);

        // ------------------------------------------------------------------ エリア

        static Area BuildArea(string id, Vector2 origin, Material lit, Material unlit)
        {
            var map = Chapter1Maps.Create(id);
            var go = new GameObject($"Area: {id}");
            go.transform.position = origin;
            var area = go.AddComponent<Area>();
            // 序章の場所（ルリの家・家の前）は曲を変えない（序章は曲なし。第 1 章が始まると町の曲のまま）
            bool prologue = id == Chapter1Maps.Room || id == Chapter1Maps.Home;
            area.Configure(id, new Rect(origin.x, origin.y, map.Width, map.Height), prologue ? "" : "ch1_shopping_street");

            bool indoor = id == Chapter1Maps.LampShop || id == Chapter1Maps.Room;
            bool alley = id == Chapter1Maps.Alley1 || id == Chapter1Maps.Alley2;
            Tilemap overlay = BuildAreaTiles(go, map, lit, unlit, indoor, alley, id == Chapter1Maps.Room);

            // 光と影の計算：影が動く所（路地）と、掛ける練習をする店の中だけ
            if (alley || id == Chapter1Maps.LampShop)
            {
                var world = new GameObject("Shadow World").AddComponent<ShadowWorld>();
                world.transform.SetParent(go.transform, false);
                world.Configure(map.Rows, overlay, LoadTile("overlay_dark"), LoadTile("overlay_cast_shadow"), origin);
            }
            if (indoor)
                new GameObject("Area Zone").AddComponent<AreaZone>().Configure(new Rect(origin.x, origin.y, map.Width, map.Height), "step_wood", true);

            BuildAreaProps(go, map, lit, unlit, indoor);
            if (id == Chapter1Maps.Street)
                PlaceBuildings(go, StreetBuildings, 9f, lit);
            else if (id == Chapter1Maps.Home)
            {
                PlaceBuildings(go, HomeBuildings, 9f, lit);
                var shelter = CreateSpriteObject(go, "Bus Shelter", "Buildings/bus_shelter", origin + new Vector2(31.5f, 7f), lit);
                shelter.GetComponent<SpriteRenderer>().sortingOrder = 0;
            }
            else if (id == Chapter1Maps.LampShop)
                FurnishLampShop(go, lit);
            else if (id == Chapter1Maps.Room)
                FurnishRoom(go, lit);

            BuildLinks(go, area, map);
            return area;
        }

        /// <summary>地面・壁（当たり判定つき）・暗がりの重ね絵。マスの文字から決める。</summary>
        static Tilemap BuildAreaTiles(GameObject area, GridMap map, Material lit, Material unlit, bool indoor, bool alley, bool home)
        {
            var grid = new GameObject("Grid").AddComponent<Grid>();
            grid.transform.SetParent(area.transform, false);
            Tilemap ground = CreateTilemap(grid, "Ground", -100, lit);
            Tilemap walls = CreateTilemap(grid, "Walls", -80, lit);
            Tilemap overlay = CreateTilemap(grid, "Darkness", -90, unlit);

            Tile road0 = LoadTile("road_0"), road1 = LoadTile("road_1"), line = LoadTile("road_line");
            Tile side0 = LoadTile("sidewalk_0"), side1 = LoadTile("sidewalk_1"), curb = LoadTile("curb");
            Tile cross0 = LoadTile("crosswalk_0"), cross1 = LoadTile("crosswalk_1");
            Tile wallTop = LoadTile("wall_top"), block = LoadTile("block_wall");
            Tile floor0 = LoadTileFrom("Interior/Tiles/floor_wood_0", "floor_wood_0");
            Tile floor1 = LoadTileFrom("Interior/Tiles/floor_wood_1", "floor_wood_1");
            Tile innerTop = LoadTileFrom("Interior/Tiles/wall_top_inner", "wall_top_inner");
            Tile plaster0 = LoadTileFrom("Interior/Tiles/wall_plaster_0", "wall_plaster_0");
            Tile plaster1 = LoadTileFrom("Interior/Tiles/wall_plaster_1", "wall_plaster_1");
            Tile wainscot = LoadTileFrom("Interior/Tiles/wall_wainscot", "wall_wainscot");
            // ルリの家（Tools/Art/room.py）
            Tile homeWall0 = LoadTileFrom("Home/Tiles/home_wall_0", "home_wall_0");
            Tile homeWall1 = LoadTileFrom("Home/Tiles/home_wall_1", "home_wall_1");
            Tile homeWallBase = LoadTileFrom("Home/Tiles/home_wall_base", "home_wall_base");
            var homeFloors = new[] { "tatami_0", "tatami_1", "floor_vinyl", "tataki" }
                .ToDictionary(n => n, n => LoadTileFrom($"Home/Tiles/{n}", n));
            foreach (var t in new[] { wallTop, block, innerTop, plaster0, plaster1, wainscot, homeWall0, homeWall1, homeWallBase })
            {
                t.colliderType = Tile.ColliderType.Grid;
                EditorUtility.SetDirty(t);
            }

            var doors = new HashSet<char>(Chapter1Maps.Links.Where(l => l.IsDoor).Select(l => l.Symbol));
            var random = new System.Random(map.Width * 31 + map.Height);
            for (int y = 0; y < map.Height; y++)
            {
                int row = map.Height - 1 - y;   // 上からの行
                for (int x = 0; x < map.Width; x++)
                {
                    var cell = new Cell(x, y);
                    char ch = map.At(cell);
                    var p = new Vector3Int(x, y, 0);
                    if (GridMap.IsLink(ch) && !doors.Contains(ch))
                        ch = map.At(Chapter1Maps.SpawnCell(map, ch));   // 出入口の地面は、となりの地面と同じに
                    if (GridMap.IsWall(ch) || doors.Contains(ch))
                    {
                        Tile wall;
                        bool openBelow = GridMap.IsWalkable(map.At(cell + new Cell(0, -1)));
                        if (home)
                            wall = row == 0 || x == 0 || x == map.Width - 1 || y == 0 ? innerTop
                                : row == 1 ? (x % 6 == 3 ? homeWall1 : homeWall0) : row == 2 || openBelow ? homeWallBase : innerTop;
                        else if (indoor)
                            wall = row == 0 || x == 0 || x == map.Width - 1 || y == 0 ? innerTop
                                : row == 1 ? (x % 5 == 2 ? plaster1 : plaster0) : row == 2 ? wainscot : innerTop;
                        else
                            wall = !GridMap.IsWall(map.At(cell + new Cell(0, 1))) ? block : wallTop;   // 北が開けている壁は、正面の塀として見せる
                        walls.SetTile(p, wall);
                        if (!doors.Contains(ch))
                            continue;
                    }

                    Tile floor;
                    char below = map.At(cell + new Cell(0, -1));
                    char above = map.At(cell + new Cell(0, 1));
                    if (home)
                        floor = homeFloors[RoomFloor(x, row)];
                    else if (indoor)
                        floor = (x * 3 + y) % 5 == 0 ? floor1 : floor0;
                    else if (ch == ':')
                        floor = (x + y) % 3 == 0 ? cross1 : cross0;
                    else if (ch == '=')
                        floor = above == '=' && below == '=' && (x & 1) == 0 ? line : random.NextDouble() < 0.15 ? road1 : road0;
                    else if (ch == ',' || alley && "HSATL".IndexOf(ch) >= 0)
                        floor = random.NextDouble() < 0.15 ? road1 : road0;
                    else if (below == '=' || below == ':')
                        floor = curb;
                    else
                        floor = random.NextDouble() < 0.2 ? side1 : side0;
                    ground.SetTile(p, floor);
                }
            }

            var body = walls.gameObject.AddComponent<Rigidbody2D>();
            body.bodyType = RigidbodyType2D.Static;
            var tilemapCollider = walls.gameObject.AddComponent<TilemapCollider2D>();
            var composite = walls.gameObject.AddComponent<CompositeCollider2D>();
            composite.geometryType = CompositeCollider2D.GeometryType.Polygons;
            tilemapCollider.usedByComposite = true;
            return overlay;
        }

        /// <summary>マスの文字から小物・人・灯りを置く。通れないマスには当たり判定。</summary>
        static void BuildAreaProps(GameObject area, GridMap map, Material lit, Material unlit, bool indoor)
        {
            var props = new GameObject("Props");
            props.transform.SetParent(area.transform, false);
            var people = new GameObject("Characters");
            people.transform.SetParent(area.transform, false);
            Vector3 origin = area.transform.position;

            for (int y = 0; y < map.Height; y++)
            {
                for (int x = 0; x < map.Width; x++)
                {
                    var cell = new Cell(x, y);
                    char ch = map.At(cell);
                    Vector3 foot = origin + CellFoot(cell);
                    switch (ch)
                    {
                        case 'L':
                            CreateStreetLamp(props, cell, lit, flicker: false);
                            MoveLast(props, foot);
                            break;
                        case 'V':
                            CreateVendingMachine(props, cell, lit);
                            MoveLast(props, foot);
                            break;
                        case 'H':
                        case 'h':
                            CreateLanternHook(props, cell, lit);
                            MoveLast(props, foot);
                            break;
                        case 'A':
                            Caster(CreateSpriteObject(props, "AC Unit (仮)", "Props/beer_crates", foot, lit), ch);
                            break;
                        case 'T':
                            Caster(CreateSpriteObject(props, "Trash Bin", "Props/trash_bin", foot, lit), ch);
                            break;
                        case 'B':
                            CreateSpriteObject(props, "Bench", "Props/bench", foot, lit);
                            break;
                        case 'M':
                            CreateSpriteObject(props, "Mailbox", "Props/mailbox", foot, lit);
                            break;
                        case 'U':
                            CreateSpriteObject(props, "Power Pole", "Props/power_pole", foot, lit);
                            break;
                        case 'Q':
                            CreateSpriteObject(props, "Bus Stop Sign", "Props/bus_sign", foot, lit);
                            break;
                        case 'X':
                            Caster(new GameObject("Furniture (shadow)"), ch, props, foot);
                            break;
                        case 'G':
                            var haru = CreateLoopWithFootShadow(people, "Haru", "Characters/Grandma/grandma_idle_", foot, lit, 1.2f);
                            haru.transform.Find("Foot Shadow").gameObject.SetActive(false); // 影はまだ無い（返すと戻る）
                            CreatePointLight(haru, "Shop Light", new Vector3(0f, 2f, 0f), Hex("#ffb866"), 0.9f, 3.5f);
                            break;
                        case 'K':
                            CreateLoopWithFootShadow(people, "Keeper", "Characters/Keeper/keeper_idle_", foot, lit, 0.8f);
                            break;
                        case 'C':
                            CreateLoopWithFootShadow(people, "Goma", "Characters/Cat/cat_idle_", foot, lit, 1.5f)
                                .transform.Find("Foot Shadow").gameObject.SetActive(false);
                            break;
                        case 'N':
                            var lantern = CreateSpriteObject(props, "Old Lantern (Nemu's home)", "Props/lantern", foot + new Vector3(-0.1f, 1.6f, 0f), unlit);
                            CreatePointLight(lantern, "Light", new Vector3(0f, 0.3f, 0f), Hex("#ffb866"), 0.7f, 2.5f);
                            break;
                    }

                    // 通れないマスの当たり判定（絵の大きさに関係なく、マップのとおり）。
                    // 街灯・自販機・人は、作るときに足元の当たり判定が付いている
                    if (GridMap.IsSolid(ch) && "LVGKC".IndexOf(ch) < 0)
                        AddCellCollider(props, foot);
                }
            }
        }

        static void MoveLast(GameObject parent, Vector3 foot)
        {
            var last = parent.transform.GetChild(parent.transform.childCount - 1);
            last.position = foot;
        }

        /// <summary>影を落とすモノにする（ShadowWorld は足元の位置からマスを決める）。</summary>
        static void Caster(GameObject go, char ch, GameObject parent = null, Vector3? foot = null)
        {
            if (parent != null)
                go.transform.SetParent(parent.transform, false);
            if (foot.HasValue)
                go.transform.position = foot.Value;
            go.AddComponent<GridShadowCaster>().Configure(GridMap.CasterHeight(ch), Vector2Int.one);
        }

        static void AddCellCollider(GameObject parent, Vector3 foot)
        {
            var go = new GameObject("Solid");
            go.transform.SetParent(parent.transform, false);
            go.transform.position = foot;
            var box = go.AddComponent<BoxCollider2D>();
            box.size = new Vector2(0.9f, 0.6f);
            box.offset = new Vector2(0f, 0.3f);
        }

        static void PlaceBuildings(GameObject area, (int x, string sprite)[] list, float baseY, Material lit)
        {
            var root = new GameObject("Buildings");
            root.transform.SetParent(area.transform, false);
            Vector3 origin = area.transform.position;
            foreach (var (x, name) in list)
            {
                var sprite = LoadSprite($"{TexturesRoot}/Buildings/{name}.png");
                if (sprite == null)
                    continue;
                float width = sprite.rect.width / PixelsPerUnit;
                CreateSpriteObject(root, name, $"Buildings/{name}", origin + new Vector3(x + width / 2f, baseY, 0f), lit);
            }
        }

        /// <summary>ランプ屋の中の家具（マップの X のマスに合わせて置く）。</summary>
        static void FurnishLampShop(GameObject area, Material lit)
        {
            var root = new GameObject("Furniture");
            root.transform.SetParent(area.transform, false);
            Vector3 o = area.transform.position;
            Vector3 P(float x, float y) => o + new Vector3(x, y, 0f);
            // y は下から：北の棚の行 = 6、作業台・台の行 = 4、カウンターの行 = 3
            CreateSpriteObject(root, "Window", "Interior/window_inner", P(7.5f, 7.6f), lit);
            CreateSpriteObject(root, "Shelf 1", "Interior/shelf_lamps", P(3f, 6.05f), lit);
            CreateSpriteObject(root, "Shelf 2", "Interior/shelf_lamps", P(6f, 6.05f), lit);
            CreateSpriteObject(root, "Shelf 3", "Interior/shelf_lamps", P(11f, 6.05f), lit);
            CreateSpriteObject(root, "Clock (3:12)", "Interior/grandfather_clock", P(12.5f, 6.05f), lit);
            CreateSpriteObject(root, "Workbench", "Interior/workbench", P(3f, 4.05f), lit);
            CreateSpriteObject(root, "Stool", "Interior/stool", P(3f, 3.1f), lit);
            CreateSpriteObject(root, "Lamp Table (仮)", "Interior/crate", P(7.5f, 4.05f), lit);
            CreateSpriteObject(root, "Counter", "Interior/counter", P(10.5f, 3.05f), lit);
            var rug = CreateSpriteObject(root, "Rug", "Interior/rug", P(7.5f, 1.2f), lit);
            rug.GetComponent<SpriteRenderer>().sortingOrder = -60;
            var mat = CreateSpriteObject(root, "Doormat", "Interior/doormat", P(7.5f, 0.6f), lit);
            mat.GetComponent<SpriteRenderer>().sortingOrder = -60;
            CreateSpriteObject(root, "Hanging Lamp (off)", "Interior/hanging_lamp_off", P(4.5f, 7.3f), lit);
            var lamp = CreateSpriteObject(root, "Hanging Lamp (on)", "Interior/hanging_lamp_on", P(10.5f, 7.3f), lit);
            CreatePointLight(lamp, "Light", new Vector3(0f, 0.3f, 0f), Hex("#ffc98a"), 0.9f, 5f);
        }

        /// <summary>ルリの家の床（Tools/Art/room.py の floor_tile と同じ決め方）。row は上からの行。</summary>
        static string RoomFloor(int x, int row)
        {
            if (x <= 7)
                return row % 2 == 1 ? "tatami_1" : "tatami_0";   // 部屋は畳（2 行で 1 枚、上の行にへり）
            if (x >= 14 && row >= 7)
                return "tataki";                                  // 玄関の戸の前は土間
            return "floor_vinyl";                                 // 台所と上がり口
        }

        /// <summary>
        /// ルリの家の中の家具（Tools/Art/room.py。置き場所はマップの X のマスと、build.py の ROOM_FURNITURE に合わせる）。
        /// 窓から月明かりが入る。机の上のスマホは伏せてある（序章で光るのは演出で足す）。
        /// </summary>
        static void FurnishRoom(GameObject area, Material lit)
        {
            var root = new GameObject("Furniture");
            root.transform.SetParent(area.transform, false);
            Vector3 o = area.transform.position;
            Vector3 P(float x, float y) => o + new Vector3(x, y, 0f);
            // y は下から：北の壁ぎわの行の足元 = 6、テーブル・椅子の行の足元 = 3
            var window = CreateSpriteObject(root, "Window (bay)", "Home/window_bay", P(5.5f, 7.375f), lit);
            CreatePointLight(window, "Moonlight", new Vector3(0f, -1.5f, 0f), Hex("#9fc4ff"), 0.6f, 4f);
            CreateSpriteObject(root, "Desk", "Home/desk", P(2f, 6.05f), lit);
            var futon = CreateSpriteObject(root, "Futon", "Home/futon", P(2.5f, 2.5f), lit);
            futon.GetComponent<SpriteRenderer>().sortingOrder = -60;
            CreateSpriteObject(root, "Sink", "Home/sink", P(10f, 6.05f), lit);
            CreateSpriteObject(root, "Fridge (note from Mom)", "Home/fridge", P(12.5f, 6.05f), lit);
            CreateSpriteObject(root, "Kitchen Table", "Home/kitchen_table", P(11f, 3.05f), lit);
            CreateSpriteObject(root, "Shoe Cabinet", "Home/shoe_cabinet", P(16f, 6.05f), lit);
            CreateSpriteObject(root, "Chair with the Blue Scarf", "Home/chair_scarf", P(16.5f, 3.05f), lit);
            CreateSpriteObject(root, "Chair", "Home/chair", P(16.5f, 3.05f), lit);          // マフラーを取ったあと
            var glow = new GameObject("Phone Glow");                                          // 序章：ミオからの通知で光る
            glow.transform.SetParent(root.transform, false);
            glow.transform.position = P(1.9f, 6.9f);
            CreatePointLight(glow, "Light", Vector3.zero, Hex("#cfe8ff"), 0.9f, 2.2f);
            glow.SetActive(false);
            var mat = CreateSpriteObject(root, "Doormat", "Interior/doormat", P(15.5f, 0.6f), lit);
            mat.GetComponent<SpriteRenderer>().sortingOrder = -60;
        }

        /// <summary>出入口：歩いて入る所は AreaExit（当たり判定はトリガー）、戸は DoorInteractable。入ったときに立つ所は Spawn。</summary>
        static void BuildLinks(GameObject areaGo, Area area, GridMap map)
        {
            var root = new GameObject("Exits");
            root.transform.SetParent(areaGo.transform, false);
            Vector3 origin = areaGo.transform.position;
            foreach (var link in Chapter1Maps.Links)
            {
                string other = link.Other(area.Id);
                if (other == null)
                    continue;
                string spawn = link.Symbol.ToString();
                area.AddSpawn(spawn, origin + CellFoot(Chapter1Maps.SpawnCell(map, link.Symbol)));

                var cells = map.Find(link.Symbol).ToList();
                LinkGates.TryGetValue((area.Id, link.Symbol), out var gate);
                if (link.IsDoor)
                {
                    var door = new GameObject($"Door → {other}").AddComponent<DoorInteractable>();
                    door.transform.SetParent(root.transform, false);
                    door.transform.position = origin + CellFoot(cells[0]);
                    door.SetPromptOffset(new Vector2(0f, 1.6f));
                    door.Configure(other, spawn, gate.flag, gate.lines);
                    continue;
                }

                int minX = cells.Min(c => c.X), maxX = cells.Max(c => c.X), minY = cells.Min(c => c.Y), maxY = cells.Max(c => c.Y);
                var exit = new GameObject($"Exit → {other}");
                exit.transform.SetParent(root.transform, false);
                exit.transform.position = origin + new Vector3((minX + maxX + 1) / 2f, (minY + maxY + 1) / 2f, 0f);
                var box = exit.AddComponent<BoxCollider2D>();
                box.isTrigger = true;
                box.size = new Vector2(maxX - minX + 1, maxY - minY + 1) * 0.8f;
                exit.AddComponent<AreaExit>().Configure(other, spawn, gate.flag, gate.lines);
            }
        }
    }
}
