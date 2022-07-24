from PySide6.QtCore import QMimeData, QRect, QPoint
from PySide6.QtGui import QPalette, QPixmap, Qt, QMouseEvent, QDrag, QDragEnterEvent, QDropEvent, QResizeEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QSizePolicy, QSpacerItem, \
    QApplication
from app.ui.main import Ui_Bookshelf
from app.utils.path import resolve_path

from typing import *


class BookWidget(QLabel):
    booksrc: str
    thumbnail: QPixmap
    owner: "ShelfWidget"

    PIXMAP: QPixmap = None

    def __init__(self, owner):
        super().__init__()
        self._booksrc = None
        self._owner = owner
        if not BookWidget.PIXMAP:
            BookWidget.PIXMAP = QPixmap(resolve_path("resources", "dummybook.png"))
        self._thumbnail = BookWidget.PIXMAP
        self.setPixmap(BookWidget.PIXMAP)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._drag_start = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._drag_start = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (event.buttons() == Qt.LeftButton) and \
                (QApplication.startDragDistance() <= (event.pos() - self._drag_start).manhattanLength()):
            drag = QDrag(self)
            mime = QMimeData()
            row, column = self.owner.find_book(self)
            mime.setData("application/x-bookshelf-book", f"{row},{column}".encode("utf-8"))
            drag.setMimeData(mime)
            drag.setPixmap(self.thumbnail)
            self.owner.hide_book(self)
            result = drag.exec(Qt.MoveAction)
            if result == Qt.MoveAction:
                pass

    @property
    def booksrc(self):
        return self._booksrc

    @property
    def thumbnail(self):
        return self._thumbnail

    @property
    def owner(self):
        return self._owner


class ShelfWidget(QWidget):
    BACKGROUND = None
    MAX_BOOKS_COUNT = 2048

    def __init__(self):
        super().__init__()
        self.row_capacity = 3
        self.current_row = 1
        self.previous_row = 0
        self.books: List[BookWidget] = []
        self.grid = None
        self._initialSpacer = None
        self._inititalize_grid()
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

    def _inititalize_grid(self):
        del self.grid
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self._initialSpacer = QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.grid.addItem(self._initialSpacer, 0, 0)
        self.grid.addItem(QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding),
                          ShelfWidget.MAX_BOOKS_COUNT, 0)
        self.setLayout(self.grid)

    def add_book(self, book: BookWidget) -> None:
        if len(self.books) >= ShelfWidget.MAX_BOOKS_COUNT:
            return
        row = len(self.books) // self.row_capacity
        if len(self.books) > 3 and self._initialSpacer.maximumSize().height():
            self._initialSpacer.changeSize(0, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)
        if self.previous_row != row:
            self.grid.addItem(QSpacerItem(0, 167, QSizePolicy.Fixed, QSizePolicy.Fixed), self.current_row, 0)
            self.grid.addItem(QSpacerItem(0, 167, QSizePolicy.Fixed, QSizePolicy.Fixed), self.current_row + 1, 0)
            self.current_row += 1
            self.previous_row = row
        column = len(self.books) % self.row_capacity
        self.books.append(book)
        self.grid.addWidget(book, self.current_row, column)

    def render_books(self):
        self._inititalize_grid()
        for book in self.books:
            self.add_book(book)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        formats = event.mimeData().formats()
        if 'application/x-bookshelf-book' in formats:
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        min_length = float("inf")
        min_book = self
        for book in self.books:
            point = event.pos() - book.geometry().topRight()
            if (length := point.manhattanLength()) < min_length:
                min_length = length
                min_book = book
        old_row, old_column = self._get_index_by_mime(event.mimeData())
        self.get_book(old_row, old_column).show()
        self.replace_book(old_row, old_column, *self.find_book(min_book))
        event.acceptProposedAction()

    def hide_book(self, book: BookWidget):
        self.grid.removeWidget(book)
        book.hide()

    def replace_book(self, old_row: int, old_column: int, row: int, column: int):
        old_index = self._book_index(old_row, old_column)
        new_index = self._book_index(row, column)

        print(old_index, new_index)  # TODO: check whether correct
        self.books.insert(new_index, self.books[old_index])
        if old_index <= new_index:
            self.books.pop(old_index)
        else:
            self.books.pop(old_index + 1)
        print(self.books)

        self.render_books()

    def find_book(self, book: BookWidget):
        if book in self.books:
            i = self.books.index(book)
            return i // self.row_capacity, i % self.row_capacity
        else:
            return -1, -1

    def get_book(self, row: int, column: int):
        return self.books[self._book_index(row, column)]

    def _book_index(self, row: int, column: int):
        return row * self.row_capacity + column

    def resizeEvent(self, event: QResizeEvent) -> None:
        # TODO: add resize
        pass

    @staticmethod
    def _get_index_by_mime(mime: QMimeData):
        formats = mime.formats()
        if 'application/x-bookshelf-book' in formats:
            return tuple(map(int, mime.data('application/x-bookshelf-book')
                             .data()
                             .decode("utf-8")
                             .split(",")))
        return -1, -1


class BookshelfWindow(QMainWindow, Ui_Bookshelf):
    def __init__(self, app):
        super().__init__()
        self._app = app
        self.shelf = ShelfWidget()
        self.setupUi(self)
        self.scrollArea.setWidget(self.shelf)
        self.set_shelf_background()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.load_books()  # TODO: test

    def set_shelf_background(self):
        palette = QPalette()
        if not ShelfWidget.BACKGROUND:
            ShelfWidget.BACKGROUND = QPixmap(resolve_path("resources", "bg.png"))
        palette.setBrush(self.backgroundRole(), ShelfWidget.BACKGROUND)
        self.shelf.setPalette(palette)

    def load_books(self):
        for i in range(10):
            self.shelf.add_book(BookWidget(self.shelf))






