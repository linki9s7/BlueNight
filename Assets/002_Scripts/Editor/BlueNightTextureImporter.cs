using UnityEditor;
using UnityEngine;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// Assets/005_Textures 以下の画像を、ドット絵用の設定で自動的に取り込む。
    /// Point フィルタ・圧縮なし・PPU 16。タイル・顔グラフィック・UI・一枚絵は中心、それ以外（人物・建物・小物）は足元をピボットにする。
    /// </summary>
    public class BlueNightTextureImporter : AssetPostprocessor
    {
        const string Root = "Assets/005_Textures/";
        // 中心をピボットにするフォルダ（タイル・顔グラフィック・UI・タイトルなどの一枚絵）
        static readonly string[] CenterPivotFolders = { "/Tiles/", "/Faces/", "/UI/", "/Title/" };
        public const int PixelsPerUnit = 16;

        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(Root))
                return;

            var importer = (TextureImporter)assetImporter;
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = PixelsPerUnit;
            importer.filterMode = FilterMode.Point;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.mipmapEnabled = false;
            importer.alphaIsTransparency = true;
            importer.wrapMode = TextureWrapMode.Clamp;

            var settings = new TextureImporterSettings();
            importer.ReadTextureSettings(settings);
            settings.spriteMeshType = SpriteMeshType.FullRect;
            settings.spriteExtrude = 0;
            bool center = false;
            foreach (var folder in CenterPivotFolders)
                center |= assetPath.Contains(folder);
            settings.spriteAlignment = center ? (int)SpriteAlignment.Center : (int)SpriteAlignment.BottomCenter;
            importer.SetTextureSettings(settings);
        }
    }
}
