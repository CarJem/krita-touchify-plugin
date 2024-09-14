from krita import *
from PyQt5.QtGui import QColor
from ..ext.extensions import Extensions





class KS_Color:
    def __init__(self, r = 0, g = 0, b = 0):
        self.r = r if  0 <= r <= 255 else 0
        self.g =  g if  0 <=  g <= 255 else 0
        self.b = b if  0 <= b <= 255 else 0
        
        
    def setOpacityFloat(self, value: float):
        return KS_AlphaColor(self.r, self.g, self.b, int(value * 255))
    
    def fromQt(color: QColor):
        return KS_Color(color.red(), color.green(), color.blue())
        
    def toQt(self):
        return QColor(self.r, self.g, self.b, 255)

    def __str__(self) -> str:
        return f"{self.r},{self.g},{self.b}"

class KS_AlphaColor(KS_Color):
    def __init__(self, r = 0, g = 0, b = 0, a = 0):
        super().__init__(r, g, b)
        self.a = a if 0 <= a <= 255 else 0
        
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
        
        
    def writeSettingInt(group:str, name:str, value:int, notify: bool = True):
        return KritaSettings.writeSetting(group, name, str(value), notify)
    
    def writeSettingFloat(group:str, name:str, value:float, notify: bool = True):
        return KritaSettings.writeSetting(group, name, str(value), notify)
    
    def writeSettingColor(group:str, name:str, value:KS_Color, notify: bool = True):
        return KritaSettings.writeSetting(group, name, str(value), notify)

    def writeSettingBool(group:str, name:str, value:bool, notify: bool = True):
        defaultVal = "true" if value == True else "false"
        return KritaSettings.writeSetting(group, name, defaultVal, notify)

    def writeSetting(group:str, name:str, value:str, notify: bool = True):
        result = Krita.instance().writeSetting(group, name, value)
        if notify: KritaSettings.notifyUpdate()
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