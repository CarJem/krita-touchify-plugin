from touchify.__env__ import Env
from touchify.src.settings.KritaSettings import KritaSettings
from jemlib.alib_propertygrid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class TouchifyRegistryPreferences:

    class IO:
        def readStr(name: str, defaultValue: str) -> str:
            return KritaSettings.readSetting(Env.SettingsPath.TOUCHIFY, name, defaultValue)

        def writeStr(name: str, value: str, defaultValue: str) -> None:
            if TouchifyRegistryPreferences.IO.readStr(name, defaultValue) != value:
                KritaSettings.writeSetting(Env.SettingsPath.TOUCHIFY, name, value)

        def readBool(name: str, defaultValue: bool) -> bool:
            return KritaSettings.readSettingBool(Env.SettingsPath.TOUCHIFY, name, defaultValue)

        def writeBool(name: str, value: bool, defaultValue: bool) -> None:
            if TouchifyRegistryPreferences.IO.readBool(name, defaultValue) != value:
                KritaSettings.writeSettingBool(Env.SettingsPath.TOUCHIFY, name, value)

        def readFloat(name: str, defaultValue: float) -> float:
            return KritaSettings.readSettingFloat(Env.SettingsPath.TOUCHIFY, name, defaultValue)

        def writeFloat(name: str, value: float, defaultValue: float) -> None:
            if TouchifyRegistryPreferences.IO.readFloat(name, defaultValue) != value:
                KritaSettings.writeSettingFloat(Env.SettingsPath.TOUCHIFY, name, value)

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
            "Canvas_RightClickAction": "Canvas Right Click Action",
            "Canvas_LeftClickAction": "Canvas Left Click Action",
            "Canvas_MiddleClickAction": "Canvas Middle Click Action"
        }

    def propertygrid_sorted(self):
        return [
            "Canvas_LeftClickAction",
            "Canvas_RightClickAction",
            "Canvas_MiddleClickAction"
        ]

    def propertygrid_restrictions(self):
        restrictions = {}
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


        TouchifyRegistryPreferences.IO.writeStr("Canvas_RightClickAction", self.Canvas_RightClickAction, "")
        TouchifyRegistryPreferences.IO.writeStr("Canvas_LeftClickAction", self.Canvas_LeftClickAction, "")
        TouchifyRegistryPreferences.IO.writeStr("Canvas_MiddleClickAction", self.Canvas_MiddleClickAction, "")

        
