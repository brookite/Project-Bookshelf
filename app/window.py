from PySide6.QtCore import QRect
from PySide6.QtGui import QPalette, QPixmap, Qt, QKeyEvent
from PySide6.QtWidgets import QMainWindow, QFileDialog, QDialog, QInputDialog, QWidget, QScrollArea, QVBoxLayout

from app.settings import AppStorage
from app.thumbnailer import Thumbnailer
from app.ui.main import Ui_Bookshelf
from app.utils.path import resolve_path, SUPPORTED_FORMATS_NAMES, SUPPORTED_FORMATS
from app.widgets.books import ShelfWidget, BookWidget

import os


class BookshelfWindow(QMainWindow, Ui_Bookshelf):
    MAX_SHELFS_COUNT = 32

    def __init__(self, app):
        super().__init__()
        self._app = app
        self.settings = AppStorage()
        self._ctrl_pressed = False
        self.setupUi(self)
        self.shelfs = []
        self.load_shelfs()
        self.shelf_index = 0
        self.scrollArea.setWidget(self.get_current_shelf())
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tabWidget.currentChanged.connect(self._tab_changed)
        self.actionOpen.triggered.connect(self.add_books)
        self.actionAdd_new_shelf.triggered.connect(self.add_shelf)
        self.thumbnailer = Thumbnailer(self.settings)
        self.load_books()

    def _tab_changed(self, index):
        self.shelf_index = index
        if not self.get_current_shelf().loaded:
            self.load_books()

    @property
    def ctrl_pressed(self):
        return self._ctrl_pressed

    def get_current_shelf(self):
        return self.shelfs[self.shelf_index]

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self._ctrl_pressed = True

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self._ctrl_pressed = False
        if not self.shelfs[self.shelf_index].selected_count:
            self.set_selection_mode(False)

    def is_selection_mode(self):
        return self.actionSelection_mode.isChecked()

    def set_selection_mode(self, value: bool) -> None:
        self.actionSelection_mode.setChecked(value)

    def load_books(self):
        for bookdata in self.settings.config.get_books(self.shelf_index):
            self.load_book(bookdata)
        self.get_current_shelf().loaded = True
        self.thumbnailer.load_thumbnails(self.get_current_shelf().books)

    def load_book(self, bookdata: dict):
        book = BookWidget(self.get_current_shelf(), self.thumbnailer)
        book.metadata = bookdata
        book.setToolTip(bookdata["name"])
        self.get_current_shelf().add_book(book)

    def _form_shelf(self, shelf):
        bookshelf = QWidget()
        vbox = QVBoxLayout(bookshelf)
        scrollArea = QScrollArea(bookshelf)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setWidgetResizable(True)
        shelf.setGeometry(QRect(0, 0, 386, 397))
        scrollArea.setWidget(shelf)
        vbox.addWidget(scrollArea)
        return bookshelf

    def load_shelfs(self):
        for i, data in enumerate(self.settings.config["shelfs"]):
            shelf = ShelfWidget(self, data)
            self.shelfs.append(shelf)
            if i > 0:
                self.tabWidget.insertTab(i, self._form_shelf(shelf), data["name"])

    def add_shelf(self):
        name, success = QInputDialog.getText(
            self,
            self.tr("Adding new shelf"),
            self.tr("Input name of your new shelf")
        )
        if success:
            index, metadata = self.settings.config.add_shelf(name)
            shelf = ShelfWidget(self, metadata)
            self.shelfs.append(shelf)
            self.tabWidget.insertTab(index, self._form_shelf(shelf), name)

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
