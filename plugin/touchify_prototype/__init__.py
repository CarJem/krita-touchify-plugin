
try:
    from krita import *
    KRITA_LOADED = True
except:
    KRITA_LOADED = False


if KRITA_LOADED:
    import sys
    import os.path as path
    PLUGIN_PYTHON_DIR = path.dirname(path.abspath(__file__))

    sys.path.insert(0, path.join(PLUGIN_PYTHON_DIR, 'third_deps'))


    from touchify_prototype.src.api_krita import KritaAPI
    from touchify_prototype.src.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI
    from touchify_prototype.src.components.PrototypeDockWidget import PrototypeDockWidget


    KritaAPI.add_dock_widget_factory("TouchifyPrototype", DockWidgetFactoryAPI.DockPosition.DockLeft, PrototypeDockWidget)
else:
    import sys
    from pathlib import Path # if you haven't already done so
    file = Path(__file__).resolve()
    parent, root = file.parent, file.parents[1]
    sys.path.append(str(root))

    # Additionally remove the current file's directory from sys.path
    try:
        sys.path.remove(str(parent))
    except ValueError: # Already removed
        pass


    from PyQt5.QtWidgets import QApplication, QMainWindow
    from touchify_prototype.src.components.PrototypeDockWidgetContainer import PrototypeDockWidgetContainer

    class MainWindow(QMainWindow):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.text_edit = PrototypeDockWidgetContainer(self)
            self.setCentralWidget(self.text_edit)
            self.show()


    if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = MainWindow()
        sys.exit(app.exec())    



    


