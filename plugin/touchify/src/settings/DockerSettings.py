from ..ext.KritaSettings import KritaSettings


class DockerSettings_BrushOptions:

    def __init__(self):
        self.ShowFlowSlider = KritaSettings.readSettingBool("BrushOptionsDocker", "ShowFlowSlider", True)
        self.ShowOpacitySlider = KritaSettings.readSettingBool("BrushOptionsDocker", "ShowOpacitySlider", True)
        self.ShowSizeSlider = KritaSettings.readSettingBool("BrushOptionsDocker", "ShowSizeSlider", True)
        self.ShowRotationSlider = KritaSettings.readSettingBool("BrushOptionsDocker", "ShowRotationSlider", True)

    def toggle(self, setting: str):
        if hasattr(self, setting):
            currentValue = getattr(self, setting)
            currentValue = not currentValue
            setattr(self, setting, currentValue)
            self.save()


    def save(self):
        KritaSettings.writeSettingBool("BrushOptionsDocker", "ShowFlowSlider", self.ShowFlowSlider)
        KritaSettings.writeSettingBool("BrushOptionsDocker", "ShowOpacitySlider", self.ShowOpacitySlider)
        KritaSettings.writeSettingBool("BrushOptionsDocker", "ShowSizeSlider", self.ShowSizeSlider)
        KritaSettings.writeSettingBool("BrushOptionsDocker", "ShowRotationSlider", self.ShowRotationSlider)