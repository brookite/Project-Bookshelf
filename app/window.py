from PySide6.QtGui import QPalette, QPixmap, Qt
from PySide6.QtWidgets import QMainWindow, QFileDialog

from app.settings import AppStorage
from app.thumbnailer import Thumbnailer
from app.ui.main import Ui_Bookshelf
from app.utils.path import resolve_path, SUPPORTED_FORMATS_NAMES, SUPPORTED_FORMATS
from app.widgets.books import ShelfWidget, BookWidget

import os


class BookshelfWindow(QMainWindow, Ui_Bookshelf):
    def __init__(self, app):
        super().__init__()
        self._app = app
        self.settings = AppStorage()
        self.shelfs = [ShelfWidget(self)]
        self.shelf_index = 0
        self.setupUi(self)
        self.scrollArea.setWidget(self.get_current_shelf())
        self.set_shelf_background()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.actionOpen.triggered.connect(self.add_books)
        self.thumbnailer = Thumbnailer(self.settings)
        self.load_books()

    def get_current_shelf(self):
        return self.shelfs[self.shelf_index]

    def set_shelf_background(self):
        palette = QPalette()
        if not ShelfWidget.BACKGROUND:
            ShelfWidget.BACKGROUND = QPixmap(resolve_path("resources", "bg.png"))
        palette.setBrush(self.backgroundRole(), ShelfWidget.BACKGROUND)
        self.get_current_shelf().setPalette(palette)

    def load_books(self):
        for bookdata in self.settings.config.get_books(self.shelf_index):
            self.load_book(bookdata)
        self.thumbnailer.load_thumbnails(self.shelfs[self.shelf_index].books)

    def load_book(self, bookdata: dict):
        book = BookWidget(self.get_current_shelf())
        book.metadata = bookdata
        book.setToolTip(bookdata["name"])
        self.get_current_shelf().add_book(book)

    def add_book(self, path: str):
        return self.settings.config.add_file(self.shelf_index, path)

    def add_books(self):
        filenames = QFileDialog.getOpenFileNames(
            self, self.tr("Open books"), "",
            SUPPORTED_FORMATS_NAMES
        )
        for file in filenames[0]:
            if os.path.splitext(file)[1] in SUPPORTED_FORMATS:
                metadata = self.add_book(file)
                if metadata:
                    self.load_book(metadata)
        self.thumbnailer.load_thumbnails(self.shelfs[self.shelf_index].books)
