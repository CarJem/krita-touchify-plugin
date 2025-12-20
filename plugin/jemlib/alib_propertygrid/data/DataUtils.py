from jemlib.alib_datatypes.TypedList import TypedList

class DataUtils:

    @staticmethod
    def getListType(variable: any):
        varType = type(variable)
        if varType == TypedList:
            list: TypedList = variable
            listType = list.allowedTypes()
            if listType != None and listType != tuple:
                return listType
        return None