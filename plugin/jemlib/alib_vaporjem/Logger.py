ENABLE_DEBUG=False

def debug(namespace: str, name: str = None, value: str = None):
    if ENABLE_DEBUG: 
        if value: print(f'[{namespace}|{name}] :: {value}')
        elif name: print(f'[{namespace}] :: {name}')
        else: print(namespace)