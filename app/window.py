from PySide6.QtGui import QPalette, QPixmap, Qt, QMouseEvent, QDrag
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QSizePolicy
from app.ui.main import Ui_Bookshelf
from app.ui.shelf import Ui_Shelf
from app.utils.path import resolve_path

from typing import *


class BookWidget(QLabel):
    PIXMAP = None

    def __init__(self):
        super().__init__()
        self._booksrc = None
        if not BookWidget.PIXMAP:
            BookWidget.PIXMAP = QPixmap(resolve_path("resources", "dummybook.png"))
        self._thumbnail = BookWidget.PIXMAP
        self.setPixmap(BookWidget.PIXMAP)
        self.setFixedSize(100, 126)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

    @property
    def booksrc(self):
        return self._booksrc

    @property
    def thumbnail(self):
        return self._thumbnail


class ShelfWidget(QWidget, Ui_Shelf):
    BACKGROUND = None

    def __init__(self):
        super().__init__()
        self.capacity = 3
        self.books: List[BookWidget] = []
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.setupUi(self)
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.layout().setSpacing(1)

    def add_book(self, book: BookWidget) -> None:
        if len(self.books) < self.capacity:
            self.books.append(book)
            self.layout().addWidget(book, 1, len(self.books) - 1)

class BookshelfWindow(QMainWindow, Ui_Bookshelf):
    def __init__(self, app):
        super().__init__()
        self._app = app
        self.rendered_shelfs = []
        self.setupUi(self)
        self.shelfLayout = QVBoxLayout()
        self.set_shelf_background()
        self.scrollAreaWidgetContents.setLayout(self.shelfLayout)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.load_shelfs()

    def set_shelf_background(self):
        palette = QPalette()
        if not ShelfWidget.BACKGROUND:
            ShelfWidget.BACKGROUND = QPixmap(resolve_path("resources", "bg.png"))
        palette.setBrush(self.backgroundRole(), ShelfWidget.BACKGROUND)
        self.scrollAreaWidgetContents.setPalette(palette)

    def load_shelfs(self):
        for i in range(4):
            shelf = ShelfWidget()
            shelf.add_book(BookWidget())
            shelf.add_book(BookWidget())
            shelf.add_book(BookWidget())
            self.rendered_shelfs.append(shelf)
            self.shelfLayout.addWidget(shelf)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        for shelf in self.rendered_shelfs:
            for book in shelf.books:
                if event.button() == Qt.LeftButton and book.geometry().contains(event.pos()):
                    drag = QDrag(self)
                    drag.setPixmap(book.thumbnail)
                    drop_action = drag.exec()




