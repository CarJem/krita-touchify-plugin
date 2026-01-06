ENABLE_DEBUG = False

ALLOWED_NAMESPACES = [
    "JemLib",
    "Touchify",
]

ALLOWED_FILENAMES = [
    #"TouchifyWindow",
    #"TouchifyManagers",
    #"PropertyViewport",
    #"PropertyGrid_Window",
    #"PropertyGrid",
    #"DockerManager",
    #"DockerContainer",
    #"ActionManager",
]

def logDebug(namespace: str, filename: str, function: str, value: str):
    if not ENABLE_DEBUG: return

    if namespace not in ALLOWED_NAMESPACES and len(ALLOWED_NAMESPACES) > 0: return
    if filename not in ALLOWED_FILENAMES and len(ALLOWED_FILENAMES) > 0: return


    print(f'[DEBUG][{namespace} : {filename} : {function}] {value}')

def logError(namespace: str, filename: str, function: str, value: str):
    print(f'[ERROR][{namespace} : {filename} : {function}] {value}')