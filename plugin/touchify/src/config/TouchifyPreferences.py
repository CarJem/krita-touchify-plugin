from jemlib.api_touchify.env import TouchifyEnv
from jemlib.managers.KritaSettings import KritaSettings
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints

class TouchifyPreferences:

    class IO:
        def readStr(name: str, defaultValue: str) -> str:
            return KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOUCHIFY, name, defaultValue)

        def writeStr(name: str, value: str, defaultValue: str) -> None:
            if TouchifyPreferences.IO.readStr(name, defaultValue) != value:
                KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOUCHIFY, name, value, False)

        def readBool(name: str, defaultValue: bool) -> bool:
            return KritaSettings.readSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY, name, defaultValue)

        def writeBool(name: str, value: bool, defaultValue: bool) -> None:
            if TouchifyPreferences.IO.readBool(name, defaultValue) != value:
                KritaSettings.writeSettingBool(TouchifyEnv.SettingsPath.TOUCHIFY, name, value, False)

        def readFloat(name: str, defaultValue: float) -> float:
            return KritaSettings.readSettingFloat(TouchifyEnv.SettingsPath.TOUCHIFY, name, defaultValue)

        def writeFloat(name: str, value: float, defaultValue: float) -> None:
            if TouchifyPreferences.IO.readFloat(name, defaultValue) != value:
                KritaSettings.writeSettingFloat(TouchifyEnv.SettingsPath.TOUCHIFY, name, value, False)

    def __init__(self) -> None:
        self.Styles_BorderlessToolbar = False
        self.Styles_ThinDocumentTabs = False
        self.Styles_PrivacyMode = False
        self.Styles_DockedBrushEditor = False
        self.Styles_BrushEditorZoomFix = False

        self.DockerUtils_HiddenDockersLeft: str = ""
        self.DockerUtils_HiddenDockersRight: str = ""
        self.DockerUtils_HiddenDockersUp: str = ""
        self.DockerUtils_HiddenDockersDown: str = ""

        self.Canvas_RightClickAction: str = ""
        self.Canvas_LeftClickAction: str = ""
        self.Canvas_MiddleClickAction: str = ""

        self.Application_EnableMenuIcons: bool = False
        self.Application_EnableScalingWorkarounds: bool = False
        
        self.Scaling_UseFakeHighDpiScaling: bool = False
        self.Scaling_UseHighDpiPixmaps: bool = False
        self.Scaling_Use96Dpi: bool = False
        self.Scaling_UseAdjustedFontScale: bool = False
        self.Scaling_AdjustedFontScale: float = 0.0

    def propertygrid_view_type(self):
        return "form"
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}

        row["canvas_triggers"] = { 
            "items": [
                "Canvas_LeftClickAction", 
                "Canvas_RightClickAction", 
                "Canvas_MiddleClickAction"
            ], 
            "use_labels": True, 
            "flip_labels": True
        }

        row["application_overrides"] = { 
            "items": [
                "Application_EnableMenuIcons",
                "Application_EnableScalingWorkarounds", 

                "Scaling_UseFakeHighDpiScaling", 
                "Scaling_UseHighDpiPixmaps",
                "Scaling_Use96Dpi",
                "Scaling_UseAdjustedFontScale",
                "Scaling_AdjustedFontScale",
            ], 
            "use_labels": True, 
            "flip_labels": False
        }

        return row
    
    def propertygrid_hidden(self):
        result = [
            "Styles_BorderlessToolbar",
            "Styles_ThinDocumentTabs",
            "Styles_PrivacyMode",
            "Styles_DockedBrushEditor",
            "Styles_BrushEditorZoomFix",

            "DockerUtils_HiddenDockersLeft",
            "DockerUtils_HiddenDockersRight",
            "DockerUtils_HiddenDockersUp",
            "DockerUtils_HiddenDockersDown"
        ]

        if not self.Application_EnableScalingWorkarounds:
            result.append("Scaling_UseFakeHighDpiScaling")
            result.append("Scaling_UseHighDpiPixmaps")
            result.append("Scaling_Use96Dpi")
            result.append("Scaling_UseAdjustedFontScale")

        if not self.Application_EnableScalingWorkarounds or not self.Scaling_UseAdjustedFontScale:
            result.append("Scaling_AdjustedFontScale")
            

        return result
    
    def propertygrid_sorted(self):
        return [
            "canvas_triggers",
            "application_overrides"
        ]
    
    def propertygrid_labels(self):
        return {
            "canvas_triggers": "Canvas Click Event Actions",
            "Canvas_RightClickAction": "Right Click",
            "Canvas_LeftClickAction": "Left Click",
            "Canvas_MiddleClickAction": "Middle Click",

            "application_overrides": "Application Overrides",
            "Application_EnableMenuIcons": "Enable Menu Icons",
            "Application_EnableScalingWorkarounds": "Enable Scaling Workarounds",

            "Scaling_UseFakeHighDpiScaling": "Enable Fake High Dpi Scaling", 
            "Scaling_UseHighDpiPixmaps": "Enable High Dpi Pixmaps",
            "Scaling_Use96Dpi": "Enable 96Dpi Mode",
            "Scaling_UseAdjustedFontScale": "Adjust Font Scale",
            "Scaling_AdjustedFontScale": ""
        }

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["Canvas_RightClickAction"] = DataConstraints.strMod(DataConstraints.StrMod.ActionSelection)
        restrictions["Canvas_LeftClickAction"] = DataConstraints.strMod(DataConstraints.StrMod.ActionSelection)
        restrictions["Canvas_MiddleClickAction"] = DataConstraints.strMod(DataConstraints.StrMod.ActionSelection)

        restrictions["Scaling_AdjustedFontScale"] = DataConstraints.range(-10, 10)
        return restrictions

    def load(self):
        self.Styles_BorderlessToolbar = TouchifyPreferences.IO.readBool("usesBorderlessToolbar", False)
        self.Styles_ThinDocumentTabs = TouchifyPreferences.IO.readBool("usesThinDocumentTabs", False)
        self.Styles_PrivacyMode = TouchifyPreferences.IO.readBool("Styles_PrivacyMode", False)
        self.Styles_DockedBrushEditor = TouchifyPreferences.IO.readBool("Styles_DockedBrushEditor", False)
        self.Styles_BrushEditorZoomFix = TouchifyPreferences.IO.readBool("Styles_BrushEditorZoomFix", False)

        self.DockerUtils_HiddenDockersLeft = TouchifyPreferences.IO.readStr("DockerUtils_HiddenLeft", "")
        self.DockerUtils_HiddenDockersRight = TouchifyPreferences.IO.readStr("DockerUtils_HiddenRight", "")
        self.DockerUtils_HiddenDockersUp = TouchifyPreferences.IO.readStr("DockerUtils_HiddenUp", "")
        self.DockerUtils_HiddenDockersDown = TouchifyPreferences.IO.readStr("DockerUtils_HiddenDown", "")

        self.Canvas_RightClickAction = TouchifyPreferences.IO.readStr("Canvas_RightClickAction", "")
        self.Canvas_LeftClickAction = TouchifyPreferences.IO.readStr("Canvas_LeftClickAction", "")
        self.Canvas_MiddleClickAction = TouchifyPreferences.IO.readStr("Canvas_MiddleClickAction", "")

        self.Application_EnableMenuIcons = TouchifyPreferences.IO.readBool("Application_EnableMenuIcons", False)
        self.Application_EnableScalingWorkarounds = TouchifyPreferences.IO.readBool("Application_EnableScalingWorkarounds", False)

        self.Scaling_UseFakeHighDpiScaling = TouchifyPreferences.IO.readBool("Scaling_UseFakeHighDpiScaling", False)
        self.Scaling_UseHighDpiPixmaps = TouchifyPreferences.IO.readBool("Scaling_UseHighDpiPixmaps", False)
        self.Scaling_Use96Dpi = TouchifyPreferences.IO.readBool("Scaling_Use96Dpi", False)
        self.Scaling_UseAdjustedFontScale = TouchifyPreferences.IO.readBool("Scaling_UseAdjustedFontScale", False)
        self.Scaling_AdjustedFontScale = TouchifyPreferences.IO.readFloat("Scaling_AdjustedFontScale", 0.0)

    def save(self):
        TouchifyPreferences.IO.writeBool("usesBorderlessToolbar", self.Styles_BorderlessToolbar, False)
        TouchifyPreferences.IO.writeBool("usesThinDocumentTabs", self.Styles_ThinDocumentTabs, False)
        TouchifyPreferences.IO.writeBool("Styles_PrivacyMode", self.Styles_PrivacyMode, False)
        TouchifyPreferences.IO.writeBool("Styles_DockedBrushEditor", self.Styles_DockedBrushEditor, False)
        TouchifyPreferences.IO.writeBool("Styles_BrushEditorZoomFix", self.Styles_BrushEditorZoomFix, False)
        
        TouchifyPreferences.IO.writeStr("DockerUtils_HiddenLeft", self.DockerUtils_HiddenDockersLeft, "")
        TouchifyPreferences.IO.writeStr("DockerUtils_HiddenRight", self.DockerUtils_HiddenDockersRight, "")
        TouchifyPreferences.IO.writeStr("DockerUtils_HiddenUp", self.DockerUtils_HiddenDockersUp, "")
        TouchifyPreferences.IO.writeStr("DockerUtils_HiddenDown", self.DockerUtils_HiddenDockersDown, "")

        TouchifyPreferences.IO.writeStr("Canvas_RightClickAction", self.Canvas_RightClickAction, "")
        TouchifyPreferences.IO.writeStr("Canvas_LeftClickAction", self.Canvas_LeftClickAction, "")
        TouchifyPreferences.IO.writeStr("Canvas_MiddleClickAction", self.Canvas_MiddleClickAction, "")

        TouchifyPreferences.IO.writeBool("Application_EnableMenuIcons", self.Application_EnableMenuIcons, False)
        TouchifyPreferences.IO.writeBool("Application_EnableScalingWorkarounds", self.Application_EnableScalingWorkarounds, False)

        TouchifyPreferences.IO.writeBool("Scaling_UseFakeHighDpiScaling", self.Scaling_UseFakeHighDpiScaling, False)
        TouchifyPreferences.IO.writeBool("Scaling_Use96Dpi", self.Scaling_Use96Dpi, False)
        TouchifyPreferences.IO.writeBool("Scaling_UseHighDpiPixmaps", self.Scaling_UseHighDpiPixmaps, False)
        TouchifyPreferences.IO.writeBool("Scaling_UseAdjustedFontScale", self.Scaling_UseAdjustedFontScale, False)
        TouchifyPreferences.IO.writeFloat("Scaling_AdjustedFontScale", self.Scaling_AdjustedFontScale, 0.0)

        
