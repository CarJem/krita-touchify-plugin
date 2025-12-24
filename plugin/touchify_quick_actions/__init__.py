from krita import Krita, Extension  # type: ignore
from touchify_quick_actions.QuickActionsDocker import PresetGroupsDockerFactory


class QuickAccessManagerExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.docker_factory = None

    def setup(self):
        self.docker_factory = PresetGroupsDockerFactory()
        Krita.instance().addDockWidgetFactory(self.docker_factory)

    def createActions(self, window):
        pass


Krita.instance().addExtension(QuickAccessManagerExtension(Krita.instance()))
