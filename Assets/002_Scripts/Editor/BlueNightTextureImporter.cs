using UnityEditor;
using UnityEngine;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// Assets/005_Textures 以下の画像を、ドット絵用の設定で自動的に取り込む。
    /// Point フィルタ・圧縮なし・PPU 16。タイルは中心、それ以外は足元をピボットにする。
    /// </summary>
    public class BlueNightTextureImporter : AssetPostprocessor
    {
        const string Root = "Assets/005_Textures/";
        const string TileFolder = "/Tiles/";
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
            settings.spriteAlignment = assetPath.Contains(TileFolder)
                ? (int)SpriteAlignment.Center
                : (int)SpriteAlignment.BottomCenter;
            importer.SetTextureSettings(settings);
        }
    }
}
