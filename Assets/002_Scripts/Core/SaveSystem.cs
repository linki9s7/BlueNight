using System;
using System.IO;
using System.Linq;
using UnityEngine;

namespace BlueNight.Core
{
    /// <summary>セーブの中身。エリア・位置・フラグ・ことば帳。</summary>
    [Serializable]
    public class SaveData
    {
        public string scene;
        public string area;
        public float x;
        public float y;
        public string[] flags = new string[0];
        public string savedAt;
    }

    /// <summary>
    /// オートセーブ（エリアの移動・影を返したとき）。保存先は Application.persistentDataPath/save_auto.json。
    /// タイトルの「つづきから」で読み込むときは Pending に入れてシーンを開き、シーン側（AreaManager）が反映する。
    /// </summary>
    public static class SaveSystem
    {
        const string FileName = "save_auto.json";

        /// <summary>シーンを開いたあとで反映するセーブ（つづきから）。</summary>
        public static SaveData Pending { get; set; }

        static string PathOf(string name) => Path.Combine(Application.persistentDataPath, name);

        public static bool HasSave => File.Exists(PathOf(FileName));

        public static void Save(string scene, string area, Vector3 position)
        {
            var data = new SaveData
            {
                scene = scene,
                area = area,
                x = position.x,
                y = position.y,
                flags = GameFlags.All.ToArray(),
                savedAt = DateTime.Now.ToString("yyyy-MM-dd HH:mm"),
            };
            try
            {
                File.WriteAllText(PathOf(FileName), JsonUtility.ToJson(data, true));
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[BlueNight] セーブできませんでした: {e.Message}");
            }
        }

        public static SaveData Load()
        {
            try
            {
                return HasSave ? JsonUtility.FromJson<SaveData>(File.ReadAllText(PathOf(FileName))) : null;
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[BlueNight] セーブを読めませんでした: {e.Message}");
                return null;
            }
        }
    }
}
