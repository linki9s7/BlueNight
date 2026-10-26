using System;
using System.Collections;
using System.Collections.Generic;
using BlueNight.Audio;
using BlueNight.Core;
using BlueNight.Player;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace BlueNight.World
{
    /// <summary>
    /// エリアの切り替え。暗転 → 前のエリアを止める → 次のエリアを動かす → ルリ・ネム・カメラを移す → 明転。
    /// 掛けたままのランタンは、エリアを出るときにルリが持っていく。エリアを移るたびにオートセーブする。
    /// </summary>
    public class AreaManager : MonoBehaviour
    {
        public static AreaManager Instance { get; private set; }

        [SerializeField] Area[] areas = new Area[0];
        [SerializeField] string startArea;
        [SerializeField] string startSpawn = "start";
        [SerializeField] PlayerController player;
        [SerializeField] CameraFollow2D cameraFollow;
        [SerializeField] float fadeSeconds = 0.4f;

        public Area Current { get; private set; }
        public bool IsMoving { get; private set; }

        /// <summary>エリアに入ったとき（演出の始まりなどに使う）。</summary>
        public event Action<Area> Entered;

        public void Configure(Area[] allAreas, string firstArea, string firstSpawn, PlayerController ruri, CameraFollow2D follow)
        {
            areas = allAreas;
            startArea = firstArea;
            startSpawn = firstSpawn;
            player = ruri;
            cameraFollow = follow;
        }

        void Awake()
        {
            Instance = this;
            foreach (var area in areas)
                area.gameObject.SetActive(false);
        }

        void OnDestroy()
        {
            if (Instance == this)
                Instance = null;
        }

        void Start()
        {
            // つづきから：セーブのエリアと位置から始める
            var save = SaveSystem.Pending;
            SaveSystem.Pending = null;
            if (save != null && Find(save.area) != null)
            {
                GameFlags.Load(save.flags);
                Enter(Find(save.area), new Vector3(save.x, save.y, 0f));
            }
            else
            {
                var first = Find(startArea) ?? (areas.Length > 0 ? areas[0] : null);
                if (first != null)
                    Enter(first, first.SpawnPoint(startSpawn));
            }
        }

        public Area Find(string id)
        {
            foreach (var area in areas)
                if (area.Id == id)
                    return area;
            return null;
        }

        /// <summary>別のエリアへ移る（暗転つき）。</summary>
        public void Go(string areaId, string spawn)
        {
            var area = Find(areaId);
            if (area == null)
            {
                Debug.LogWarning($"[BlueNight] エリアが見つかりません: {areaId}");
                return;
            }
            if (!IsMoving)
                StartCoroutine(GoRoutine(area, spawn));
        }

        public IEnumerator GoRoutine(Area area, string spawn)
        {
            IsMoving = true;
            bool hadInput = player.InputEnabled;
            player.InputEnabled = false;
            var fader = ScreenFader.Get();
            yield return fader.FadeOut(fadeSeconds);

            var lantern = player.GetComponent<PlayerInteractor>()?.Lantern;
            if (lantern != null && !lantern.IsCarried)
                lantern.TakeBack();

            Enter(area, area.SpawnPoint(spawn));
            SaveSystem.Save(SceneManager.GetActiveScene().name, area.Id, player.transform.position);

            yield return new WaitForSecondsRealtime(0.15f);
            yield return fader.FadeIn(fadeSeconds);
            player.InputEnabled = hadInput;
            IsMoving = false;
        }

        void Enter(Area area, Vector3 position)
        {
            if (Current != null && Current != area)
                Current.gameObject.SetActive(false);
            Current = area;
            area.gameObject.SetActive(true);

            var body = player.GetComponent<Rigidbody2D>();
            if (body != null)
            {
                body.position = position;
                body.velocity = Vector2.zero;
            }
            player.transform.position = position;
            foreach (var nemu in FindObjectsOfType<NemuFollower>())
                nemu.SnapToTarget();
            if (cameraFollow != null)
                cameraFollow.SetBounds(area.CameraBounds);
            if (!string.IsNullOrEmpty(area.MusicTrack) && MusicDirector.Instance != null)
                MusicDirector.Instance.Play(area.MusicTrack);

            Entered?.Invoke(area);
        }

        /// <summary>いまの場所でオートセーブ（影を返したときなど）。</summary>
        public void AutoSave()
        {
            if (Current != null)
                SaveSystem.Save(SceneManager.GetActiveScene().name, Current.Id, player.transform.position);
        }
    }
}
