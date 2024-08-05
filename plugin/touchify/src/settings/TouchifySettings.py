from ..ext.KritaSettings import KritaSettings
import json
from ..cfg.CfgCanvasPreset import CfgCanvasPreset

class TouchifySettings:

    def instance():
        try:
            return TouchifySettings.__instance
        except AttributeError:
            TouchifySettings.__instance = TouchifySettings()
            return TouchifySettings.__instance

    def __init__(self) -> None:
        self.__has_preloaded = False

        self.Styles_BorderlessToolbar = False
        self.Styles_ThinDocumentTabs = False
        self.Styles_PrivacyMode = False

        self.CanvasWidgets_EnableToolbox = False
        self.CanvasWidgets_EnableToolshelf = False
        self.CanvasWidgets_EnableAltToolshelf = False
        self.CanvasWidgets_ToolboxOnRight = False
        self.CanvasWidgets_AlternativeToolboxPosition = False
        self.CanvasWidgets_ToolboxDirection = ""

        self.DockerUtils_HiddenDockersLeft: str = ""
        self.DockerUtils_HiddenDockersRight: str = ""
        self.DockerUtils_HiddenDockersUp: str = ""
        self.DockerUtils_HiddenDockersDown: str = ""
        
        self.CanvasPresets_Items: dict[int, CfgCanvasPreset] = dict()

        self.loadSettings()
        
    def private_readCanvasPresets(self, name: str):
        result = dict()
        
        try:
            json_data = KritaSettings.readSetting("Touchify", name, "[]")
            json_object = json.loads(json_data)
            
            index = 0

            if isinstance(json_object, list):
                json_list: list = json_object
                for dict_item in json_list:
                    if isinstance(dict_item, dict):
                        presetItem = CfgCanvasPreset()
                        presetItem.loads(dict_item)
                        result[str(index)] = presetItem
                        index += 1
        except:
            pass
        
        return result
    
    def private_writeCanvasPresets(self, name: str, values: dict):
        output = json.dumps(list(values.values()), default=vars)
        self.private_writeSetting(name, output, "[]")

    def private_readSetting(self, name: str, defaultValue: str) -> str:
        return KritaSettings.readSetting("Touchify", name, defaultValue)

    def private_writeSetting(self, name: str, value: str, defaultValue: str) -> None:
        if self.private_readSetting(name, defaultValue) != value:
            KritaSettings.writeSetting("Touchify", name, value)

    def private_readSettingBool(self, name: str, defaultValue: bool) -> bool:
        return KritaSettings.readSettingBool("Touchify", name, defaultValue)

    def private_writeSettingBool(self, name: str, value: bool, defaultValue: bool) -> None:
        if self.private_readSettingBool(name, defaultValue) != value:
            KritaSettings.writeSettingBool("Touchify", name, value)

    def loadSettings(self):
        self.Styles_FlatTheme = False

        self.Styles_BorderlessToolbar = self.private_readSettingBool("usesBorderlessToolbar", False)
        self.Styles_ThinDocumentTabs = self.private_readSettingBool("usesThinDocumentTabs", False)
        self.Styles_PrivacyMode = self.private_readSettingBool("Styles_PrivacyMode", False)
        
        self.CanvasWidgets_EnableToolbox = self.private_readSettingBool("usesNuToolbox", False)
        self.CanvasWidgets_EnableToolshelf = self.private_readSettingBool("usesNuToolOptions", False)
        self.CanvasWidgets_EnableAltToolshelf = self.private_readSettingBool("usesNuToolOptionsAlt", False)
        self.CanvasWidgets_ToolboxDirection = self.private_readSetting("CanvasWidgets_ToolboxDirection", "")

        self.CanvasWidgets_ToolboxOnRight = self.private_readSettingBool("nuOptions_ToolboxOnRight", False)
        self.CanvasWidgets_AlternativeToolboxPosition = self.private_readSettingBool("nuOptions_alternativeToolboxPosition", False)

        self.DockerUtils_HiddenDockersLeft = self.private_readSetting("DockerUtils_HiddenLeft", "")
        self.DockerUtils_HiddenDockersRight = self.private_readSetting("DockerUtils_HiddenRight", "")
        self.DockerUtils_HiddenDockersUp = self.private_readSetting("DockerUtils_HiddenUp", "")
        self.DockerUtils_HiddenDockersDown = self.private_readSetting("DockerUtils_HiddenDown", "")
        
        self.CanvasPresets_Items = self.private_readCanvasPresets("CanvasPresets_Items")

    def saveSettings(self):
        self.private_writeSettingBool("usesBorderlessToolbar", self.Styles_BorderlessToolbar, False)
        self.private_writeSettingBool("usesThinDocumentTabs", self.Styles_ThinDocumentTabs, False)
        self.private_writeSettingBool("Styles_PrivacyMode", self.Styles_PrivacyMode, False)
        
        self.private_writeSettingBool("usesNuToolbox", self.CanvasWidgets_EnableToolbox, False)
        self.private_writeSettingBool("usesNuToolOptions", self.CanvasWidgets_EnableToolshelf, False)
        self.private_writeSettingBool("usesNuToolOptionsAlt", self.CanvasWidgets_EnableAltToolshelf, False)
        self.private_writeSetting("CanvasWidgets_ToolboxDirection", self.CanvasWidgets_ToolboxDirection, "")


        self.private_writeSettingBool("nuOptions_ToolboxOnRight", self.CanvasWidgets_ToolboxOnRight, False)
        self.private_writeSettingBool("nuOptions_alternativeToolboxPosition", self.CanvasWidgets_AlternativeToolboxPosition, False)

        self.private_writeSetting("DockerUtils_HiddenLeft", self.DockerUtils_HiddenDockersLeft, "")
        self.private_writeSetting("DockerUtils_HiddenRight", self.DockerUtils_HiddenDockersRight, "")
        self.private_writeSetting("DockerUtils_HiddenUp", self.DockerUtils_HiddenDockersUp, "")
        self.private_writeSetting("DockerUtils_HiddenDown", self.DockerUtils_HiddenDockersDown, "")
        
        self.private_writeCanvasPresets("CanvasPresets_Items", self.CanvasPresets_Items)