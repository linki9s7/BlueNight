// 型の確認だけに使う代用品（URP・Input System・UI パッケージ）。Tools/CodeCheck でだけ使い、Unity には入れない。
using System.Collections.Generic;

namespace UnityEngine.Rendering
{
    public class VolumeParameter<T> { public T value; public void Override(T v) { value = v; } }
    public class VolumeComponent : ScriptableObject { }
    public class VolumeProfile : ScriptableObject
    {
        public List<VolumeComponent> components = new List<VolumeComponent>();
        public T Add<T>(bool overrides = false) where T : VolumeComponent => CreateInstance<T>();
    }
    public class Volume : MonoBehaviour { public bool isGlobal; public VolumeProfile sharedProfile; }
}

namespace UnityEngine.Rendering.Universal
{
    using UnityEngine.Rendering;
    public class Light2D : MonoBehaviour
    {
        public enum LightType { Parametric, Freeform, Sprite, Point, Global }
        public LightType lightType; public Color color; public float intensity;
        public float pointLightInnerRadius, pointLightOuterRadius, falloffIntensity;
    }
    public class Renderer2DData : ScriptableObject { }
    public class PostProcessData : ScriptableObject { }
    public class UniversalRenderPipelineAsset : ScriptableObject { }
    public enum TonemappingMode { None, Neutral, ACES }
    public enum FilmGrainLookup { Thin1, Thin2, Medium1 }
    public enum AntialiasingMode { None, FastApproximateAntialiasing, SubpixelMorphologicalAntiAliasing }
    public class Bloom : VolumeComponent { public VolumeParameter<float> threshold = new(), intensity = new(), scatter = new(); public VolumeParameter<Color> tint = new(); }
    public class Tonemapping : VolumeComponent { public VolumeParameter<TonemappingMode> mode = new(); }
    public class ColorAdjustments : VolumeComponent { public VolumeParameter<float> postExposure = new(), contrast = new(), saturation = new(); }
    public class SplitToning : VolumeComponent { public VolumeParameter<Color> shadows = new(), highlights = new(); public VolumeParameter<float> balance = new(); }
    public class WhiteBalance : VolumeComponent { public VolumeParameter<float> temperature = new(); }
    public class Vignette : VolumeComponent { public VolumeParameter<Color> color = new(); public VolumeParameter<float> intensity = new(), smoothness = new(); }
    public class FilmGrain : VolumeComponent { public VolumeParameter<FilmGrainLookup> type = new(); public VolumeParameter<float> intensity = new(), response = new(); }
    public class ChromaticAberration : VolumeComponent { public VolumeParameter<float> intensity = new(); }
    public class UniversalAdditionalCameraData : MonoBehaviour { public bool renderPostProcessing; public AntialiasingMode antialiasing; }
    public static class CameraExtensions { public static UniversalAdditionalCameraData GetUniversalAdditionalCameraData(this Camera c) => null; }
}

namespace UnityEngine.Experimental.Rendering.Universal
{
    public class PixelPerfectCamera : MonoBehaviour
    {
        public enum GridSnapping { None, PixelSnapping, UpscaleRenderTexture }
        public enum CropFrame { None, Pillarbox, Letterbox, Windowbox, StretchFill }
        public int assetsPPU, refResolutionX, refResolutionY; public GridSnapping gridSnapping; public CropFrame cropFrame;
    }
}

namespace UnityEngine.UI
{
    public class Graphic : MonoBehaviour { public Color color; public bool raycastTarget; }
    public class Text : Graphic
    {
        public Font font; public int fontSize; public float lineSpacing; public string text; public TextAnchor alignment;
        public HorizontalWrapMode horizontalOverflow; public VerticalWrapMode verticalOverflow;
    }
    public class Image : Graphic { public Sprite sprite; }
    public class Outline : MonoBehaviour { public Color effectColor; public Vector2 effectDistance; }
    public class CanvasScaler : MonoBehaviour
    {
        public enum ScaleMode { ConstantPixelSize, ScaleWithScreenSize, ConstantPhysicalSize }
        public enum ScreenMatchMode { MatchWidthOrHeight, Expand, Shrink }
        public ScaleMode uiScaleMode; public float scaleFactor; public Vector2 referenceResolution;
        public ScreenMatchMode screenMatchMode; public float matchWidthOrHeight;
    }
}

namespace UnityEngine.InputSystem
{
    namespace Controls
    {
        public class ButtonControl { public bool isPressed, wasPressedThisFrame; }
        public class KeyControl : ButtonControl { }
        public class StickControl { public Vector2 ReadValue() => default; }
    }
    public class Keyboard
    {
        public static Keyboard current;
        public Controls.KeyControl aKey, dKey, sKey, wKey, eKey, fKey, xKey, zKey, spaceKey, enterKey, numpadEnterKey,
            leftArrowKey, rightArrowKey, upArrowKey, downArrowKey, leftShiftKey, rightShiftKey;
    }
    public class Gamepad
    {
        public static Gamepad current;
        public Controls.StickControl leftStick, dpad;
        public Controls.ButtonControl buttonSouth, buttonWest, rightTrigger;
    }
}
