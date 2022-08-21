import hashlib
import os.path
import sys
import warnings
from typing import List, Optional
import threading
import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from app.storage import AppStorage
from app.utils.path import SUPPORTED_THUMBNAIL_FORMATS
from app.widgets.book import BookWidget

MUPDF_THUMBNAILES = False
DJVU_THUMBNAILES = False
try:
    import fitz
    MUPDF_THUMBNAILES = True
except ImportError:
    warnings.warn("pymupdf library wasn't found. Thumbnails for some file formats will be unavailable")
try:
    import djvu.decode
    DJVU_THUMBNAILES = True
except ImportError:
    warnings.warn("python-djvulibre library wasn't found. Thumbnails for some file formats will be unavailable")
try:
    from PIL import Image
except ImportError:
    MUPDF_THUMBNAILES = False
    DJVU_THUMBNAILES = False
    warnings.warn("pillow library wasn't found. All thumbnailes will be unavailable")


class Thumbnailer:
    DEFAULT_THUMBNAIL_SIZE = (100, 126)

    def __init__(self, settings: AppStorage):
        self._dir = settings.thumbnail_dir
        self._user_dir = settings.user_thumbnail_dir
        self.settings = settings
        self._tmp_ctx = None

    @staticmethod
    def _random_name(length=8):
        alpha = "qwertyuiopasdfghjklzxcvbnm1234567890"
        text = ""
        for i in range(length):
            text += random.choice(alpha)
        return text

    @staticmethod
    def _hashed_name(name):
        name = name.encode("utf-8")
        return hashlib.md5(name).hexdigest()

    def load_thumbnails(self, books: List[BookWidget]):
        thread = threading.Thread(
            target=self._thread_loader,
            args=[books])
        thread.daemon = True
        thread.start()

    def _pregen_checks(self, src):
        if "${{...}}" in src:
            return False
        return True

    def _gen_thumbnail_mupdf(self, src: str) -> Optional[QImage]:
        if not self._pregen_checks(src):
            return None
        doc = fitz.open(src)
        pix = doc.load_page(0).get_pixmap()
        stream = pix.pil_tobytes(format="PNG", optimize=True)
        img = QImage()
        img.loadFromData(stream)
        img = img.scaled(
            100, 126, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        return img

    def _gen_thumbnail_djvulibre(self, src: str) -> Optional[QImage]:
        if not self._pregen_checks(src):
            return None
        if not self._tmp_ctx:
            ctx = djvu.decode.Context()
            self._tmp_ctx = ctx
        else:
            ctx = self._tmp_ctx
        doc = ctx.new_document(djvu.decode.FileURI(src))
        doc.decoding_job.wait()
        page = doc.pages[0]
        page_job = page.decode(wait=True)
        width, height = page_job.size
        rect = (0, 0, width, height)

        djvu_pixel_format = djvu.decode.PixelFormatRgb()
        buf = page_job.render(djvu.decode.RENDER_COLOR, rect, rect, djvu_pixel_format)
        img = Image.frombuffer("RGB", (width, height), buf, "raw").resize((100, 126))
        img = img.toqimage()
        img.mirror()
        return img

    def load_external_thumbnail(self, book: BookWidget, image_path: str):
        image_path = os.path.abspath(image_path)
        image = QImage(image_path).scaled(100, 126)
        name = self._hashed_name(image_path) + ".png"
        image.save(os.path.join(self.user_directory, name), "PNG")
        book.metadata["thumbnail"] = f"$DEFAULT_USER_THUMBNAIL_PATH/{name}"
        book.set_thumbnail(QPixmap.fromImage(image))
        self.settings.config.save()

    def _save(self, book: BookWidget, image: QImage) -> None:
        name = self._hashed_name(book.metadata["src"]) + ".png"
        image.save(os.path.join(self._dir, name), "PNG")
        book.metadata["thumbnail"] = f"$DEFAULT_THUMBNAIL_PATH/{name}"
        book.set_thumbnail(QPixmap.fromImage(image))

    def resolve_path(self, path: str):
        clearpath = self.settings.resolve_env_variable(path)
        return os.path.abspath(clearpath)

    def reload_thumbnail(self, book: BookWidget):
        book.metadata["thumbnail"] = None
        thread = threading.Thread(
            target=self._thread_loader,
            args=[[book]])
        thread.daemon = True
        thread.start()

    def _thread_loader(self, books: List[BookWidget]):
        for book in books:
            try:
                if book.metadata["thumbnail"]:
                    if os.path.exists(self.resolve_path(book.metadata["thumbnail"])):
                        book.update_thumbnail()
                        continue
                ext = os.path.splitext(self.settings.config.booksrc(book.metadata))[-1]
                if ext.lower() not in SUPPORTED_THUMBNAIL_FORMATS:
                    continue
                if ext in [".djv", ".djvu"]:
                    if DJVU_THUMBNAILES:
                        image = self._gen_thumbnail_djvulibre(self.settings.config.booksrc(book.metadata))
                        if image:
                            self._save(book, image)
                else:
                    if MUPDF_THUMBNAILES:
                        image = self._gen_thumbnail_mupdf(self.settings.config.booksrc(book.metadata))
                        if image:
                            self._save(book, image)
            except Exception as e:
                print(type(e).__name__, ':', str(e), file=sys.stderr)
        self.settings.config.save()

    @property
    def directory(self) -> str:
        return self._dir

    @property
    def user_directory(self) -> str:
        return self._user_dir
