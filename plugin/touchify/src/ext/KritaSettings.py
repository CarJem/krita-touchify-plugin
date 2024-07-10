from krita import *


class KritaSettings:

    def init():
        KritaSettings.notify_hooks = []

    def notifyConnect(event):
        KritaSettings.notify_hooks.append(event)

    def notifyUpdate():
        for hook in KritaSettings.notify_hooks:
            hook()

    def readSetting(group:str, name:str, defaultValue:str):
        return Krita.instance().readSetting(group, name, defaultValue)

    def readSettingBool(group:str, name:str, defaultValue:bool):
        defaultVal = "true" if defaultValue == True else "false"

        result = KritaSettings.readSetting(group, name, defaultVal)
        if result == "true": return True
        elif result == "false": return False
        else: return None

    def writeSettingBool(group:str, name:str, value:bool):
        defaultVal = "true" if value == True else "false"
        return KritaSettings.writeSetting(group, name, defaultVal)

    def writeSetting(group:str, name:str, value:str):
        result = Krita.instance().writeSetting(group, name, value)
        KritaSettings.notifyUpdate()
        return result

    def showDockerTitlebars():
        settingStr = KritaSettings.readSetting("", "showDockerTitleBars", "false")
        result = True if settingStr == "true" else False
        return result

    def showRulers():
        settingStr = KritaSettings.readSetting("", "showrulers", "true")
        result = True if settingStr == "true" else False
        return result

    def hideScrollbars():
        settingStr = KritaSettings.readSetting("", "hideScrollbars", "false")
        result = True if settingStr == "true" else False
        return result
    
KritaSettings.init()