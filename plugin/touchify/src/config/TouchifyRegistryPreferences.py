from touchify.src.managers.shared.settings_krita import KritaSettings
from touchify.src.components.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class TouchifyRegistryPreferences:

    class IO:
        def readStr(name: str, defaultValue: str) -> str:
            return KritaSettings.readSetting("Touchify", name, defaultValue)

        def writeStr(name: str, value: str, defaultValue: str) -> None:
            if TouchifyRegistryPreferences.IO.readStr(name, defaultValue) != value:
                KritaSettings.writeSetting("Touchify", name, value)

        def readBool(name: str, defaultValue: bool) -> bool:
            return KritaSettings.readSettingBool("Touchify", name, defaultValue)

        def writeBool(name: str, value: bool, defaultValue: bool) -> None:
            if TouchifyRegistryPreferences.IO.readBool(name, defaultValue) != value:
                KritaSettings.writeSettingBool("Touchify", name, value)

        def readFloat(name: str, defaultValue: float) -> float:
            return KritaSettings.readSettingFloat("Touchify", name, defaultValue)

        def writeFloat(name: str, value: float, defaultValue: float) -> None:
            if TouchifyRegistryPreferences.IO.readFloat(name, defaultValue) != value:
                KritaSettings.writeSettingFloat("Touchify", name, value)

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

        self.Interface_CanvasToggleScale: float = 1.0
        self.Interface_ToolboxIconScale: float = 1.0
        self.Interface_ToolshelfActionBarScale: float = 1.0
        self.Interface_ToolshelfTabBarScale: float = 1.0
        self.Interface_ToolshelfHeaderScale: float = 1.0
        self.Interface_ToolshelfActionSectionScale: float = 1.0
        self.Interface_ColorOptionsDockerScale: float = 1.0

        self.Canvas_RightClickAction: str = ""
        self.Canvas_LeftClickAction: str = ""
        self.Canvas_MiddleClickAction: str = ""

        self.load()

    def propertygrid_hidden(self):
        return [
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
    
    def propertygrid_labels(self):
        return {
            "Interface_CanvasToggleScale": "Canvas Widget Toggle Scale",
            "Interface_ToolboxIconScale": "Toolbox Icon Scale",
            "Interface_ToolshelfTabBarScale": "Toolshelf Tab Bar Scale",
            "Interface_ToolshelfActionBarScale": "Toolshelf Action Bar Scale",
            "Interface_ToolshelfHeaderScale": "Toolshelf Header Scale",
            "Interface_ToolshelfActionSectionScale": "Toolshelf Action Section Scale",
            "Interface_ColorOptionsDockerScale": "Color Options Docker Scale",
            "Canvas_RightClickAction": "Canvas Right Click Action",
            "Canvas_LeftClickAction": "Canvas Left Click Action",
            "Canvas_MiddleClickAction": "Canvas Middle Click Action"
        }

    def propertygrid_sorted(self):
        return [
            "Canvas_LeftClickAction",
            "Canvas_RightClickAction",
            "Canvas_MiddleClickAction",
            "#NEW_COLUMN",
            "Interface_CanvasToggleScale",
            "Interface_ToolboxIconScale",
            "Interface_ToolshelfActionBarScale",
            "Interface_ToolshelfTabBarScale",
            "Interface_ToolshelfHeaderScale",
            "Interface_ToolshelfActionSectionScale",
            "Interface_ColorOptionsDockerScale"
        ]

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["Interface_CanvasToggleScale"] = PropertyGrid_Restrictions.range(min=1)
        restrictions["Interface_ToolboxIconScale"] = PropertyGrid_Restrictions.range(min=1)
        restrictions["Interface_ToolshelfActionBarScale"] = PropertyGrid_Restrictions.range(min=1)
        restrictions["Interface_ToolshelfTabBarScale"] = PropertyGrid_Restrictions.range(min=1)
        restrictions["Interface_ToolshelfHeaderScale"] = PropertyGrid_Restrictions.range(min=1)
        restrictions["Interface_ToolshelfActionSectionScale"] = PropertyGrid_Restrictions.range(min=1)
        restrictions["Interface_ColorOptionsDockerScale"] = PropertyGrid_Restrictions.range(min=1)
        restrictions["Canvas_RightClickAction"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.ActionSelection)
        restrictions["Canvas_LeftClickAction"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.ActionSelection)
        restrictions["Canvas_MiddleClickAction"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.ActionSelection)
        return restrictions

    def load(self):
        self.Styles_BorderlessToolbar = TouchifyRegistryPreferences.IO.readBool("usesBorderlessToolbar", False)
        self.Styles_ThinDocumentTabs = TouchifyRegistryPreferences.IO.readBool("usesThinDocumentTabs", False)
        self.Styles_PrivacyMode = TouchifyRegistryPreferences.IO.readBool("Styles_PrivacyMode", False)
        self.Styles_DockedBrushEditor = TouchifyRegistryPreferences.IO.readBool("Styles_DockedBrushEditor", False)
        self.Styles_BrushEditorZoomFix = TouchifyRegistryPreferences.IO.readBool("Styles_BrushEditorZoomFix", False)

        self.DockerUtils_HiddenDockersLeft = TouchifyRegistryPreferences.IO.readStr("DockerUtils_HiddenLeft", "")
        self.DockerUtils_HiddenDockersRight = TouchifyRegistryPreferences.IO.readStr("DockerUtils_HiddenRight", "")
        self.DockerUtils_HiddenDockersUp = TouchifyRegistryPreferences.IO.readStr("DockerUtils_HiddenUp", "")
        self.DockerUtils_HiddenDockersDown = TouchifyRegistryPreferences.IO.readStr("DockerUtils_HiddenDown", "")

        self.Interface_CanvasToggleScale = TouchifyRegistryPreferences.IO.readFloat("Interface_CanvasToggleScale", 1.0)
        self.Interface_ToolboxIconScale = TouchifyRegistryPreferences.IO.readFloat("Interface_ToolboxIconScale", 1.0)
        self.Interface_ToolshelfActionBarScale = TouchifyRegistryPreferences.IO.readFloat("Interface_ToolshelfActionBarScale", 1.0)
        self.Interface_ToolshelfTabBarScale = TouchifyRegistryPreferences.IO.readFloat("Interface_ToolshelfTabBarScale", 1.0)
        self.Interface_ToolshelfHeaderScale = TouchifyRegistryPreferences.IO.readFloat("Interface_ToolshelfHeaderScale", 1.0)
        self.Interface_ToolshelfActionSectionScale = TouchifyRegistryPreferences.IO.readFloat("Interface_ToolshelfActionSectionScale", 1.0)
        self.Interface_ColorOptionsDockerScale = TouchifyRegistryPreferences.IO.readFloat("Interface_ColorOptionsDockerScale", 1.0)

        self.Canvas_RightClickAction = TouchifyRegistryPreferences.IO.readStr("Canvas_RightClickAction", "")
        self.Canvas_LeftClickAction = TouchifyRegistryPreferences.IO.readStr("Canvas_LeftClickAction", "")
        self.Canvas_MiddleClickAction = TouchifyRegistryPreferences.IO.readStr("Canvas_MiddleClickAction", "")

    def save(self):
        TouchifyRegistryPreferences.IO.writeBool("usesBorderlessToolbar", self.Styles_BorderlessToolbar, False)
        TouchifyRegistryPreferences.IO.writeBool("usesThinDocumentTabs", self.Styles_ThinDocumentTabs, False)
        TouchifyRegistryPreferences.IO.writeBool("Styles_PrivacyMode", self.Styles_PrivacyMode, False)
        TouchifyRegistryPreferences.IO.writeBool("Styles_DockedBrushEditor", self.Styles_DockedBrushEditor, False)
        TouchifyRegistryPreferences.IO.writeBool("Styles_BrushEditorZoomFix", self.Styles_BrushEditorZoomFix, False)
        

        TouchifyRegistryPreferences.IO.writeStr("DockerUtils_HiddenLeft", self.DockerUtils_HiddenDockersLeft, "")
        TouchifyRegistryPreferences.IO.writeStr("DockerUtils_HiddenRight", self.DockerUtils_HiddenDockersRight, "")
        TouchifyRegistryPreferences.IO.writeStr("DockerUtils_HiddenUp", self.DockerUtils_HiddenDockersUp, "")
        TouchifyRegistryPreferences.IO.writeStr("DockerUtils_HiddenDown", self.DockerUtils_HiddenDockersDown, "")

        TouchifyRegistryPreferences.IO.writeFloat("Interface_CanvasToggleScale", self.Interface_CanvasToggleScale, 1.0)
        TouchifyRegistryPreferences.IO.writeFloat("Interface_ToolboxIconScale", self.Interface_ToolboxIconScale, 1.0)
        TouchifyRegistryPreferences.IO.writeFloat("Interface_ToolshelfActionBarScale", self.Interface_ToolshelfActionBarScale, 1.0)
        TouchifyRegistryPreferences.IO.writeFloat("Interface_ToolshelfTabBarScale", self.Interface_ToolshelfTabBarScale, 1.0)
        TouchifyRegistryPreferences.IO.writeFloat("Interface_ToolshelfHeaderScale", self.Interface_ToolshelfHeaderScale, 1.0)
        TouchifyRegistryPreferences.IO.writeFloat("Interface_ToolshelfActionSectionScale", self.Interface_ToolshelfActionSectionScale, 1.0)
        TouchifyRegistryPreferences.IO.writeFloat("Interface_ColorOptionsDockerScale", self.Interface_ColorOptionsDockerScale, 1.0)

        TouchifyRegistryPreferences.IO.writeStr("Canvas_RightClickAction", self.Canvas_RightClickAction, "")
        TouchifyRegistryPreferences.IO.writeStr("Canvas_LeftClickAction", self.Canvas_LeftClickAction, "")
        TouchifyRegistryPreferences.IO.writeStr("Canvas_MiddleClickAction", self.Canvas_MiddleClickAction, "")

        
