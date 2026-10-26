using UnityEditor;
using UnityEngine;

namespace BlueNight.EditorTools
{
    /// <summary>
    /// Assets/008_Fonts のフォントを、ドット絵に合うくっきりした描画（Hinted Raster）で取り込む。
    /// </summary>
    public class BlueNightFontImporter : AssetPostprocessor
    {
        const string Root = "Assets/008_Fonts/";

        void OnPreprocessAsset()
        {
            if (!assetPath.StartsWith(Root) || !(assetImporter is TrueTypeFontImporter importer))
                return;
            importer.fontRenderingMode = FontRenderingMode.HintedRaster;
            importer.fontTextureCase = FontTextureCase.Dynamic;
        }
    }
}
