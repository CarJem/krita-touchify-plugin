from .PropertyGridHost import PropertyGridHost
from .PropertyGrid import PropertyGrid

class PropertyGridFactory:
    def __init__(self):
        self.gridHost = PropertyGridHost()
        self.propertyGrid = PropertyGrid(self.gridHost)
        self.gridHost.setGrid(self.propertyGrid)
    
    def updateDataObject(self, data: any):
        self.propertyGrid.updateDataObject(data)


