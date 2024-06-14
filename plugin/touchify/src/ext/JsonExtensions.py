class JsonExtensions:

    def tryGetEntry(jsonData, key, type, defaultValue):
        if not jsonData:
            return defaultValue
        if key in jsonData:
            result: type = jsonData[key]
            return result
        else:
            return defaultValue