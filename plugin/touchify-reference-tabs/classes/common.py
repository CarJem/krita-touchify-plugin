from PyQt5.QtCore import QMimeDatabase
from PyQt5.QtWidgets import QFileDialog, QWidget
from PyQt5.QtGui import QImageReader


def createFileDialog(parent: QWidget | None = None):
    result = QFileDialog(parent)
    result.setOptions(QFileDialog.Option.DontUseNativeDialog)
    return result

def getSupportedFiletypes():
    imgFormats = QImageReader.supportedImageFormats()

    formatList = []
    for formatBytes in imgFormats:
        # convert QByteArray to string and prepend "*."
        formatList.append(str(formatBytes, 'utf-8'))
    return formatList

# Generate the formats filter for the file dialog.
def generateFiletypeFilter():
    # Ask QImage what files it can load.
    # With Krita, this will return more formats than standard Qt.
    imgFormats = getSupportedFiletypes()

    formatList = []
    filterList = []
    db = QMimeDatabase()

    for formatName in imgFormats:
        # convert QByteArray to string and prepend "*."
        formatList.append(f"*.{formatName}")

    for format in formatList:
        formatDesc = db.mimeTypeForFile(format).comment()
        # Some formats (camera raw) don't have proper entries, so hide those.
        # They're still listed in "All supported formats".
        if formatDesc != "unknown":
            # "Krita document (*.kra)", etc
            filterList.append(f"{formatDesc} ({format})")

    formatAllString = " ".join(formatList)
    # Alphabetical by description,
    # then "All supported formats (*.bmp *.kra *.png ...)" first.
    filterList.sort()
    filterList.insert(0, f"All supported formats ({formatAllString})")

    return ";;".join(filterList)
