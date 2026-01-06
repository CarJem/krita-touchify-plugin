ENABLE_DEBUG = True

ALLOWED_NAMESPACES = [
    "JemLib",
    "Touchify",
]

ALLOWED_FILENAMES = [
    #"TouchifyWindow",
    #"TouchifyManagers",
    "PropertyGrid_Window",
    #"DockerManager",
    #"DockerContainer",
    #"ActionManager",
]

def logDebug(namespace: str, filename: str, function: str, value: str):
    if not ENABLE_DEBUG: return

    if namespace not in ALLOWED_NAMESPACES and len(ALLOWED_NAMESPACES) > 0: return
    if filename not in ALLOWED_FILENAMES and len(ALLOWED_FILENAMES) > 0: return


    print(f'[DEBUG][{namespace} : {filename} : {function}] {value}')