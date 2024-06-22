from PyQt5.QtWidgets import QMessageBox


class PropertyUtils_Extensions:

    def tryGetVariable(obj, varName):
        if hasattr(obj, varName):
            return getattr(obj, varName)
        else: return None

    def getVariable(obj, varName):
        return getattr(obj, varName)

    def setVariable(obj, varName, data):
        return setattr(obj, varName, data)

    def getClassVariables(obj):
        return [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and
                not attr.startswith("__") and
                not attr.startswith("_"  + type(obj).__name__ + "__")]

    def getGroups(obj):
        if hasattr(obj, "propertygrid_groups"):
            return dict(obj.propertygrid_groups())
        else: return {}

    def getLabels(obj):
        if hasattr(obj, "propertygrid_labels"):
            return dict(obj.propertygrid_labels())
        else: return {}

    def isClassModel(obj):
        return hasattr(obj, "propertygrid_ismodel")


    def quickDialog(parent, text):
        dlg = QMessageBox(parent)
        dlg.setText(text)
        dlg.show()

    def clearLayout(layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    PropertyUtils_Extensions.clearLayout(child.layout())