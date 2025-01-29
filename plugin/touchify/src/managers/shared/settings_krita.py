from krita import *
from touchify.src.datatypes.dataclass.KisColor import KisColor, KisAlphaColor
from touchify.src.extensions.parse_extensions import ParseExtensions
from touchify.src.managers.shared.events import GlobalEvents

class KritaSettings:
    def init():
        KritaSettings.notify_hooks = []

    def readSetting(group:str, name:str, defaultValue:str):
        return Krita.instance().readSetting(group, name, defaultValue)
    
    def readSettingInt(group:str, name:str, defaultValue:int):
        strVal = Krita.instance().readSetting(group, name, str(defaultValue))
        return ParseExtensions.parse_int(strVal, defaultValue)

    def readSettingFloat(group:str, name:str, defaultValue:float):
        strVal = Krita.instance().readSetting(group, name, str(defaultValue))
        return ParseExtensions.parse_float(strVal, defaultValue)


    def readSettingAlphaColor(group:str, name:str, defaultValue: KisAlphaColor):
        strVal = Krita.instance().readSetting(group, name, str(defaultValue))
        listVal = strVal.split(",")
        if len(listVal) == 4:
            r = ParseExtensions.parse_int(listVal[0], 0)
            g = ParseExtensions.parse_int(listVal[1], 0)
            b = ParseExtensions.parse_int(listVal[2], 0)
            a = ParseExtensions.parse_int(listVal[3], 0)
            return KisAlphaColor(r, g, b, a)
        
        return defaultValue 

    def readSettingColor(group:str, name:str, defaultValue: KisColor):
        strVal = Krita.instance().readSetting(group, name, str(defaultValue))
        listVal = strVal.split(",")
        if len(listVal) == 3:
            r = ParseExtensions.parse_int(listVal[0], 0)
            g = ParseExtensions.parse_int(listVal[1], 0)
            b = ParseExtensions.parse_int(listVal[2], 0)
            return KisColor(r, g, b)
        
        return defaultValue 

    def readSettingBool(group:str, name:str, defaultValue:bool):
        result = Krita.instance().readSetting(group, name, "true" if defaultValue == True else "false")
        if result == "true": return True
        elif result == "false": return False
        else: return None
        
        
    def writeSettingInt(group:str, name:str, value:int, notify: bool = True):
        return KritaSettings.writeSetting(group, name, str(value), notify)
    
    def writeSettingFloat(group:str, name:str, value:float, notify: bool = True):
        return KritaSettings.writeSetting(group, name, str(value), notify)
    
    def writeSettingColor(group:str, name:str, value:KisColor, notify: bool = True):
        return KritaSettings.writeSetting(group, name, str(value), notify)

    def writeSettingBool(group:str, name:str, value:bool, notify: bool = True):
        defaultVal = "true" if value == True else "false"
        return KritaSettings.writeSetting(group, name, defaultVal, notify)

    def writeSetting(group:str, name:str, value:str, notify: bool = True):
        result = Krita.instance().writeSetting(group, name, value)
        if notify: GlobalEvents.instance().EMIT_SIGNAL_KRITA_CONFIG_UPDATED()
        return result

    def showDockerTitlebars():
        settingStr = KritaSettings.readSetting("", "showDockerTitleBars", "false")
        result = True if settingStr == "true" else False
        return result

    def showRulers():
        settingStr: str = KritaSettings.readSetting("", "showrulers", "true")
        result = True if settingStr.lower() == "true" else False
        return result

    def hideScrollbars():
        settingStr: str = KritaSettings.readSetting("", "hideScrollbars", "false")
        result = True if settingStr.lower() == "true" else False
        return result
    
KritaSettings.init()