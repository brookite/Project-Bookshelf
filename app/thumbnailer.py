import os.path
import warnings
from typing import List
import threading
import random

from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QPixmap

from app.utils.path import SUPPORTED_THUMBNAIL_FORMATS
from app.widgets.books import BookWidget

try:
    import fitz
except ImportError:
    warnings.warn("pymupdf library wasn't found. Thumbnails for some file formats will be unavailable")
try:
    import djvu
except ImportError:
    warnings.warn("python-djvulibre library wasn't found. Thumbnails for some file formats will be unavailable")


class Thumbnailer:
    DEFAULT_THUMBNAIL_SIZE = (100, 126)

    def __init__(self, settings):
        self._dir = settings.thumbnail_dir
        self.settings = settings

    @staticmethod
    def _random_name(length=8):
        alpha = "qwertyuiopasdfghjklzxcvbnm1234567890"
        text = ""
        for i in range(length):
            text += random.choice(alpha)
        return text

    def load_thumbnails(self, books: List[BookWidget]):
        thread = threading.Thread(
            target=self._thread_loader,
            args=[books])
        thread.daemon = True
        thread.start()

    def _gen_thumbnail_mupdf(self, src: str) -> QImage:
        doc = fitz.open(src)
        pix = doc.load_page(0).get_pixmap()
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        qtimg = QImage(pix.samples, pix.width, pix.height, fmt)\
            .scaled(QSize(*self.DEFAULT_THUMBNAIL_SIZE))
        return qtimg

    def _gen_thumbnail_djvulibre(self, src: str):
        pass

    def _save(self, book: BookWidget, image):
        name = self._random_name() + ".png"
        image.save(os.path.join(self._dir, name), "PNG")
        book.metadata["thumbnail"] = f"$DEFAULT_THUMBNAIL_PATH/{name}"
        book.setThumbnail(QPixmap.fromImage(image))

    def _thread_loader(self, books: List[BookWidget]):
        for book in books:
            if book.metadata["thumbnail"]:
                if os.path.exists(book.metadata["thumbnail"]):
                    continue
            ext = os.path.splitext(book.metadata["src"])[-1]
            if ext not in SUPPORTED_THUMBNAIL_FORMATS:
                continue
            if ext in [".djv", ".djvu"]:
                image = self._gen_thumbnail_djvulibre(book.metadata["src"])
            else:
                image = self._gen_thumbnail_mupdf(book.metadata["src"])
                self._save(book, image)
        self.settings.config.save()

    @property
    def directory(self):
        return self._dir