import inspect

class Extensions:
    def dictToObject(obj, dict):
        if dict is not None:
            for key, value in dict.items():
                setattr(obj, key, value)

    def getClassVariables(obj):
        return [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__")]
    
    def getVariable(obj, varName):
        return getattr(obj, varName)
    
    def default_assignment(args, attributeName, defaultValue):
        if attributeName in args:
            return args[attributeName]
        else:
            return defaultValue
        
    def list_assignment(array, classSrc, arraySrc):
        for i in array:
            arraySrc.append(classSrc.create(i))

class PyQtExtensions:
    def clearLayout(layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    PyQtExtensions.clearLayout(child.layout())