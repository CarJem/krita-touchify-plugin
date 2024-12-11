from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions


class TouchifyRegistryHotkeys:


    def __init__(self, **args) -> None:
        self.hotkey1: str = "none"
        self.hotkey2: str = "none"
        self.hotkey3: str = "none"
        self.hotkey4: str = "none"
        self.hotkey5: str = "none"
        self.hotkey6: str = "none"
        self.hotkey7: str = "none"
        self.hotkey8: str = "none"
        self.hotkey9: str = "none"
        self.hotkey10: str = "none"
        Extensions.dictToObject(self, args)

    def forceLoad(self):
        pass
    
    def propertygrid_sorted(self):
        return [
            "hotkey1",
            "hotkey2",
            "hotkey3",
            "hotkey4",
            "hotkey5",
            "hotkey6",
            "hotkey7",
            "hotkey8",
            "hotkey9",
            "hotkey10"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["hotkey1"] =  "Hotkey 1"
        labels["hotkey2"] =  "Hotkey 2"
        labels["hotkey3"] =  "Hotkey 3"
        labels["hotkey4"] =  "Hotkey 4"
        labels["hotkey5"] =  "Hotkey 5"
        labels["hotkey6"] =  "Hotkey 6"
        labels["hotkey7"] =  "Hotkey 7"
        labels["hotkey8"] =  "Hotkey 8"
        labels["hotkey9"] =  "Hotkey 9"
        labels["hotkey10"] = "Hotkey 10"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["hotkey1"]  =  {"type": "hotkey_selection"}
        restrictions["hotkey2"]  =  {"type": "hotkey_selection"}
        restrictions["hotkey3"]  =  {"type": "hotkey_selection"}
        restrictions["hotkey4"]  =  {"type": "hotkey_selection"}
        restrictions["hotkey5"]  =  {"type": "hotkey_selection"}
        restrictions["hotkey6"]  =  {"type": "hotkey_selection"}
        restrictions["hotkey7"]  =  {"type": "hotkey_selection"}
        restrictions["hotkey8"]  =  {"type": "hotkey_selection"}
        restrictions["hotkey9"]  =  {"type": "hotkey_selection"}
        restrictions["hotkey10"] =  {"type": "hotkey_selection"}
        return restrictions