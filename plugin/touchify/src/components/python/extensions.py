
class Extensions:
    def tryPraseFloat(s: str, defaultValue: float):
        try:
            i = float(s)
            return i
        except ValueError as verr:
            return defaultValue
        except Exception as ex:
            return defaultValue
    
    def tryPraseInt(s: str, defaultValue: int):
        try:
            i = int(s)
            return i
        except ValueError as verr:
            return defaultValue
        except Exception as ex:
            return defaultValue
    

    

