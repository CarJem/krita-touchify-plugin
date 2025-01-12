from krita import *

class GridNativeActions(QObject):

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

    def addImageLayer(self, photoPath: str):
        pass

    def openNewDocument(self, path: str):
        if not self.checkPath(path):
            return 

        document = Krita.instance().openDocument(path)
        Krita.instance().activeWindow().addView(document)

    def dragToDocument(self, source: QObject, path: str, qimage: QImage, pixmap: QPixmap, export_scale: int, fit_canvas: bool):
        # MimeData
        mimedata = QMimeData()
        url = QUrl().fromLocalFile(path)
        mimedata.setUrls([url])

        # create appropriate res image that will placed
        doc = Krita.instance().activeDocument()

        # Saving a non-existent document causes crashes, so lets check for that first.
        if doc is None:
            return 

        scale = export_scale / 100

        # only scale to document if it exists
        if fit_canvas and not doc is None:
            fullImage = QImage(path).scaled(int(doc.width() * scale), int(doc.height() * scale), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        else:
            fullImage = QImage(path)
            # scale image, now knowing the bounds
            fullImage = fullImage.scaled(int(fullImage.width() * scale), int(fullImage.height() * scale), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        fullPixmap = QPixmap(50, 50).fromImage(fullImage)
        mimedata.setImageData(fullPixmap)

        # Clipboard
        QApplication.clipboard().setImage(qimage)

        # drag, using information about the smaller version of the image
        drag = QDrag(source)
        drag.setMimeData(mimedata)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(int(qimage.width() / 2), int(qimage.height() / 2)))
        drag.exec_(Qt.CopyAction)

    def placeReference(self, path: str):
        if not self.checkPath(path):
            self.updateImages()
            return

        # MimeData
        mimedata = QMimeData()
        url = QUrl().fromLocalFile(path)
        mimedata.setUrls([url])
        image = QImage(path)
        mimedata.setImageData(image)

        QApplication.clipboard().setImage(image)
        Krita.instance().action('paste_as_reference').trigger()
