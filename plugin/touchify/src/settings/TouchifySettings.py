from ..ext.KritaSettings import KritaSettings


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

        self.loadSettings()

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