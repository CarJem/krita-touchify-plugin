from zipfile import ZipFile
import os

PARENT_DIR = os.path.dirname(os.path.dirname(__file__))
MATERIAL_ICONS = os.path.join(PARENT_DIR, 'plugin', 'touchify', 'resources', "builtin", 'material-icons.zip')
with ZipFile(MATERIAL_ICONS, 'r') as zip:
    for item in zip.filelist:
        if item.filename.startswith('MaterialDesign-master/svg/') and item.filename.endswith('.svg'):
            actualName = item.filename.removeprefix('MaterialDesign-master/svg/').removesuffix('.svg')
            print(actualName)
            #zip.read(item)