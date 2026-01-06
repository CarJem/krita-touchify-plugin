import copy


class PropertySystem:
    settings_clipboard_type: type = None
    settings_clipboard_data: any = None

    def getSettingsClipboard(requested_type: type):
        if PropertySystem.settings_clipboard_type == requested_type:
            return PropertySystem.settings_clipboard_data
        else: return None

    def setSettingsClipboard(item_type: type, item_data: any):
        PropertySystem.settings_clipboard_type = item_type
        PropertySystem.settings_clipboard_data = item_data

    def deepcopy(x):
        if hasattr(x, "deepcopy"):
            return x.deepcopy()
        else:
            #print(f"WARNING: DeepCopy is being used to clone this object: {str(x)}")
            return copy.deepcopy(x)
