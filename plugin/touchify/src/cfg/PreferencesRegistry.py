from touchify.src.ext.KritaSettings import KritaSettings

class PreferencesRegistry:

    class IO:
        def readStr(name: str, defaultValue: str) -> str:
            return KritaSettings.readSetting("Touchify", name, defaultValue)

        def writeStr(name: str, value: str, defaultValue: str) -> None:
            if PreferencesRegistry.IO.readStr(name, defaultValue) != value:
                KritaSettings.writeSetting("Touchify", name, value)

        def readBool(name: str, defaultValue: bool) -> bool:
            return KritaSettings.readSettingBool("Touchify", name, defaultValue)

        def writeBool(name: str, value: bool, defaultValue: bool) -> None:
            if PreferencesRegistry.IO.readBool(name, defaultValue) != value:
                KritaSettings.writeSettingBool("Touchify", name, value)

        def readFloat(name: str, defaultValue: float) -> float:
            return KritaSettings.readSettingFloat("Touchify", name, defaultValue)

        def writeFloat(name: str, value: float, defaultValue: float) -> None:
            if PreferencesRegistry.IO.readFloat(name, defaultValue) != value:
                KritaSettings.writeSettingFloat("Touchify", name, value)

    def __init__(self) -> None:
        self.Styles_BorderlessToolbar = False
        self.Styles_ThinDocumentTabs = False
        self.Styles_PrivacyMode = False

        self.CanvasWidgets_EnableToolbox = False
        self.CanvasWidgets_EnableToolshelf = False
        self.CanvasWidgets_EnableAltToolshelf = False
        self.CanvasWidgets_ToolboxOnRight = False
        self.CanvasWidgets_AlternativeToolboxPosition = False

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

            "CanvasWidgets_EnableToolbox",
            "CanvasWidgets_EnableToolshelf",
            "CanvasWidgets_EnableAltToolshelf",
            "CanvasWidgets_ToolboxOnRight",
            "CanvasWidgets_AlternativeToolboxPosition",

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
        

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["Interface_CanvasToggleScale"] = {"type": "range", "min": 1}
        restrictions["Interface_ToolboxIconScale"] = {"type": "range", "min": 1}
        restrictions["Interface_ToolshelfActionBarScale"] = {"type": "range", "min": 1}
        restrictions["Interface_ToolshelfTabBarScale"] = {"type": "range", "min": 1}
        restrictions["Interface_ToolshelfHeaderScale"] = {"type": "range", "min": 1}
        restrictions["Interface_ToolshelfActionSectionScale"] = {"type": "range", "min": 1}
        restrictions["Interface_ColorOptionsDockerScale"] = {"type": "range", "min": 1}
        restrictions["Canvas_RightClickAction"] = {"type": "action_selection"}
        restrictions["Canvas_LeftClickAction"] = {"type": "action_selection"}
        restrictions["Canvas_MiddleClickAction"] = {"type": "action_selection"}
        return restrictions

    def load(self):
        self.Styles_BorderlessToolbar = PreferencesRegistry.IO.readBool("usesBorderlessToolbar", False)
        self.Styles_ThinDocumentTabs = PreferencesRegistry.IO.readBool("usesThinDocumentTabs", False)
        self.Styles_PrivacyMode = PreferencesRegistry.IO.readBool("Styles_PrivacyMode", False)
        
        self.CanvasWidgets_EnableToolbox = PreferencesRegistry.IO.readBool("usesNuToolbox", False)
        self.CanvasWidgets_EnableToolshelf = PreferencesRegistry.IO.readBool("usesNuToolOptions", False)
        self.CanvasWidgets_EnableAltToolshelf = PreferencesRegistry.IO.readBool("usesNuToolOptionsAlt", False)

        self.CanvasWidgets_ToolboxOnRight = PreferencesRegistry.IO.readBool("nuOptions_ToolboxOnRight", False)
        self.CanvasWidgets_AlternativeToolboxPosition = PreferencesRegistry.IO.readBool("nuOptions_alternativeToolboxPosition", False)

        self.DockerUtils_HiddenDockersLeft = PreferencesRegistry.IO.readStr("DockerUtils_HiddenLeft", "")
        self.DockerUtils_HiddenDockersRight = PreferencesRegistry.IO.readStr("DockerUtils_HiddenRight", "")
        self.DockerUtils_HiddenDockersUp = PreferencesRegistry.IO.readStr("DockerUtils_HiddenUp", "")
        self.DockerUtils_HiddenDockersDown = PreferencesRegistry.IO.readStr("DockerUtils_HiddenDown", "")

        self.Interface_CanvasToggleScale = PreferencesRegistry.IO.readFloat("Interface_CanvasToggleScale", 1.0)
        self.Interface_ToolboxIconScale = PreferencesRegistry.IO.readFloat("Interface_ToolboxIconScale", 1.0)
        self.Interface_ToolshelfActionBarScale = PreferencesRegistry.IO.readFloat("Interface_ToolshelfActionBarScale", 1.0)
        self.Interface_ToolshelfTabBarScale = PreferencesRegistry.IO.readFloat("Interface_ToolshelfTabBarScale", 1.0)
        self.Interface_ToolshelfHeaderScale = PreferencesRegistry.IO.readFloat("Interface_ToolshelfHeaderScale", 1.0)
        self.Interface_ToolshelfActionSectionScale = PreferencesRegistry.IO.readFloat("Interface_ToolshelfActionSectionScale", 1.0)
        self.Interface_ColorOptionsDockerScale = PreferencesRegistry.IO.readFloat("Interface_ColorOptionsDockerScale", 1.0)

        self.Canvas_RightClickAction = PreferencesRegistry.IO.readStr("Canvas_RightClickAction", "")
        self.Canvas_LeftClickAction = PreferencesRegistry.IO.readStr("Canvas_LeftClickAction", "")
        self.Canvas_MiddleClickAction = PreferencesRegistry.IO.readStr("Canvas_MiddleClickAction", "")

    def save(self):
        PreferencesRegistry.IO.writeBool("usesBorderlessToolbar", self.Styles_BorderlessToolbar, False)
        PreferencesRegistry.IO.writeBool("usesThinDocumentTabs", self.Styles_ThinDocumentTabs, False)
        PreferencesRegistry.IO.writeBool("Styles_PrivacyMode", self.Styles_PrivacyMode, False)
        
        PreferencesRegistry.IO.writeBool("usesNuToolbox", self.CanvasWidgets_EnableToolbox, False)
        PreferencesRegistry.IO.writeBool("usesNuToolOptions", self.CanvasWidgets_EnableToolshelf, False)
        PreferencesRegistry.IO.writeBool("usesNuToolOptionsAlt", self.CanvasWidgets_EnableAltToolshelf, False)

        PreferencesRegistry.IO.writeBool("nuOptions_ToolboxOnRight", self.CanvasWidgets_ToolboxOnRight, False)
        PreferencesRegistry.IO.writeBool("nuOptions_alternativeToolboxPosition", self.CanvasWidgets_AlternativeToolboxPosition, False)

        PreferencesRegistry.IO.writeStr("DockerUtils_HiddenLeft", self.DockerUtils_HiddenDockersLeft, "")
        PreferencesRegistry.IO.writeStr("DockerUtils_HiddenRight", self.DockerUtils_HiddenDockersRight, "")
        PreferencesRegistry.IO.writeStr("DockerUtils_HiddenUp", self.DockerUtils_HiddenDockersUp, "")
        PreferencesRegistry.IO.writeStr("DockerUtils_HiddenDown", self.DockerUtils_HiddenDockersDown, "")

        PreferencesRegistry.IO.writeFloat("Interface_CanvasToggleScale", self.Interface_CanvasToggleScale, 1.0)
        PreferencesRegistry.IO.writeFloat("Interface_ToolboxIconScale", self.Interface_ToolboxIconScale, 1.0)
        PreferencesRegistry.IO.writeFloat("Interface_ToolshelfActionBarScale", self.Interface_ToolshelfActionBarScale, 1.0)
        PreferencesRegistry.IO.writeFloat("Interface_ToolshelfTabBarScale", self.Interface_ToolshelfTabBarScale, 1.0)
        PreferencesRegistry.IO.writeFloat("Interface_ToolshelfHeaderScale", self.Interface_ToolshelfHeaderScale, 1.0)
        PreferencesRegistry.IO.writeFloat("Interface_ToolshelfActionSectionScale", self.Interface_ToolshelfActionSectionScale, 1.0)
        PreferencesRegistry.IO.writeFloat("Interface_ColorOptionsDockerScale", self.Interface_ColorOptionsDockerScale, 1.0)

        PreferencesRegistry.IO.writeStr("Canvas_RightClickAction", self.Canvas_RightClickAction, "")
        PreferencesRegistry.IO.writeStr("Canvas_LeftClickAction", self.Canvas_LeftClickAction, "")
        PreferencesRegistry.IO.writeStr("Canvas_MiddleClickAction", self.Canvas_MiddleClickAction, "")

        
