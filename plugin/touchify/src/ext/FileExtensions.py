import string
import tempfile
import itertools as IT
import os

class FileExtensions:
   
    def fileStringify(input: str):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in input if c in valid_chars)
        filename = filename.replace(' ','_') # I don't like spaces in filenames.
        return filename.lower()    

    def uniquify(path: str, sep = ''):
        def name_sequence():
            count = IT.count()
            yield ''
            while True:
                yield '{s}{n:d}'.format(s = sep, n = next(count))

        orig = tempfile._name_sequence 
        with tempfile._once_lock:
            tempfile._name_sequence = name_sequence()
            path = os.path.normpath(path)
            dirname, basename = os.path.split(path)
            filename, ext = os.path.splitext(basename)
            fd, filename = tempfile.mkstemp(dir = dirname, prefix = filename, suffix = ext)
            tempfile._name_sequence = orig
        return filename

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
    
    def extend(class_to_extend):
        def decorator(extending_class):
            class_to_extend.__dict__.update(extending_class.__dict__)
            return class_to_extend
        return decorator
    

    

