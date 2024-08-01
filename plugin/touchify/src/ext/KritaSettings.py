from krita import *
from PyQt5.QtGui import QColor
from ..ext.extensions import Extensions





class KS_Color:
    def __init__(self, _r = 0, _g = 0, _b = 0):
        self.r = _r if  0 <= _r <= 255 else 0
        self.g =  _g if  0 <=  _g <= 255 else 0
        self.b = _b if  0 <= _b <= 255 else 0
        
        
    def setOpacityFloat(self, value: float):
        return KS_AlphaColor(self.r, self.g, self.b, int(value * 255))
    
    def fromQt(color: QColor):
        return KS_Color(color.red(), color.green(), color.blue())
        
    def toQt(self):
        return QColor(self.r, self.g, self.b, 255)

    def __str__(self) -> str:
        return f"{self.r},{self.g},{self.b}"

class KS_AlphaColor(KS_Color):
    def __init__(self, _r = 0, _g = 0, _b = 0, _a = 0):
        super().__init__(_r, _g, _b)
        self.a = _a if 0 <= _a <= 255 else 0
        
    def getOpacityFloat(self) -> float:
        return self.a / 255
    
    def noAlpha(self):
        return KS_Color(self.r, self.g, self.b)
    
    def fromQt(color: QColor):
        return KS_AlphaColor(color.red(), color.green(), color.blue(), color.alpha())
    
    def toQt(self):
        return QColor(self.r, self.g, self.b, self.a)
    
    def __str__(self) -> str:
        return f"{self.r},{self.g},{self.b},{self.a}"
    

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
    
    def readSettingInt(group:str, name:str, defaultValue:int):
        strVal = Krita.instance().readSetting(group, name, str(defaultValue))
        return Extensions.tryPraseInt(strVal, defaultValue)

    def readSettingFloat(group:str, name:str, defaultValue:float):
        strVal = Krita.instance().readSetting(group, name, str(defaultValue))
        return Extensions.tryPraseFloat(strVal, defaultValue)


    def readSettingAlphaColor(group:str, name:str, defaultValue: KS_AlphaColor):
        strVal = Krita.instance().readSetting(group, name, str(defaultValue))
        listVal = strVal.split(",")
        if len(listVal) == 4:
            r = Extensions.tryPraseInt(listVal[0], 0)
            g = Extensions.tryPraseInt(listVal[1], 0)
            b = Extensions.tryPraseInt(listVal[2], 0)
            a = Extensions.tryPraseInt(listVal[3], 0)
            return KS_AlphaColor(r, g, b, a)
        
        return defaultValue 

    def readSettingColor(group:str, name:str, defaultValue: KS_Color):
        strVal = Krita.instance().readSetting(group, name, str(defaultValue))
        listVal = strVal.split(",")
        if len(listVal) == 3:
            r = Extensions.tryPraseInt(listVal[0], 0)
            g = Extensions.tryPraseInt(listVal[1], 0)
            b = Extensions.tryPraseInt(listVal[2], 0)
            return KS_Color(r, g, b)
        
        return defaultValue 

    def readSettingBool(group:str, name:str, defaultValue:bool):
        result = Krita.instance().readSetting(group, name, "true" if defaultValue == True else "false")
        if result == "true": return True
        elif result == "false": return False
        else: return None
        
        
    def writeSettingInt(group:str, name:str, value:int):
        return KritaSettings.writeSetting(group, name, str(value))
    
    def writeSettingFloat(group:str, name:str, value:float):
        return KritaSettings.writeSetting(group, name, str(value))
    
    def writeSettingColor(group:str, name:str, value:KS_Color):
        return KritaSettings.writeSetting(group, name, str(value))

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