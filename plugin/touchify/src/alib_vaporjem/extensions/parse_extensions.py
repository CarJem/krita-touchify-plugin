
class ParseExtensions:

    @staticmethod
    def parse_float(s: str, val: float):
        try: i = float(s); return i
        except ValueError: return val
        except Exception: return val
    
    @staticmethod
    def parse_int(s: str, val: int):
        try: i = int(s); return i
        except ValueError: return val
        except Exception: return val
    

    

