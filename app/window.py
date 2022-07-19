from PySide6.QtGui import QPalette, QPixmap, Qt, QMouseEvent, QDrag
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QSizePolicy, QSpacerItem
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
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))

    @property
    def booksrc(self):
        return self._booksrc

    @property
    def thumbnail(self):
        return self._thumbnail


class ShelfWidget(QWidget, Ui_Shelf):
    BACKGROUND = None
    MAX_BOOKS_COUNT = 2048

    def __init__(self):
        super().__init__()
        self.row_capacity = 3
        self.current_row = 1
        self.previous_row = 0
        self.books: List[BookWidget] = []
        self.grid = None
        self._inititalSpacer = None
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self._inititalize_grid()
        self.setupUi(self)

    def _inititalize_grid(self):
        del self.grid
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self._inititalSpacer = QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.grid.addItem(self._inititalSpacer, 0, 0)
        self.grid.addItem(QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding),
                          ShelfWidget.MAX_BOOKS_COUNT, 0)
        self.setLayout(self.grid)

    def add_book(self, book: BookWidget) -> None:
        if len(self.books) >= ShelfWidget.MAX_BOOKS_COUNT:
            return
        row = len(self.books) // self.row_capacity
        if len(self.books) > 3 and self._inititalSpacer.maximumSize().height():
            self._inititalSpacer.changeSize(0, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)
        if self.previous_row != row:
            self.grid.addItem(QSpacerItem(0, 167, QSizePolicy.Fixed, QSizePolicy.Fixed), self.current_row, 0)
            self.grid.addItem(QSpacerItem(0, 167, QSizePolicy.Fixed, QSizePolicy.Fixed), self.current_row + 1, 0)
            self.current_row += 1
            self.previous_row = row
        column = len(self.books) % self.row_capacity
        self.books.append(book)
        self.grid.addWidget(book, self.current_row, column)


class BookshelfWindow(QMainWindow, Ui_Bookshelf):
    def __init__(self, app):
        super().__init__()
        self._app = app
        self.shelf = ShelfWidget()
        self.setupUi(self)
        self.set_shelf_background()
        self.scrollAreaWidgetContents.setLayout(self.shelf.grid)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.load_books()  # TODO: test

    def set_shelf_background(self):
        palette = QPalette()
        if not ShelfWidget.BACKGROUND:
            ShelfWidget.BACKGROUND = QPixmap(resolve_path("resources", "bg.png"))
        palette.setBrush(self.backgroundRole(), ShelfWidget.BACKGROUND)
        self.scrollAreaWidgetContents.setPalette(palette)

    def load_books(self):
        for i in range(3):
            self.shelf.add_book(BookWidget())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)
        for book in self.shelf.books:
            if event.button() == Qt.LeftButton and book.geometry().contains(event.pos()):
                drag = QDrag(self)
                drag.setPixmap(book.thumbnail)
                drop_action = drag.exec()
                print(drop_action)




