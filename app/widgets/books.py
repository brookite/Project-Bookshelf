import os.path

from PySide6.QtCore import QMimeData
from PySide6.QtGui import QPixmap, Qt, QMouseEvent, QDrag, QDragEnterEvent, QDropEvent, QResizeEvent
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy, QSpacerItem, \
    QApplication
from app.utils.path import resolve_path, open_file
from typing import *


class BookWidget(QLabel):
    metadata: dict
    thumbnail: QPixmap
    owner: "ShelfWidget"

    PIXMAP: QPixmap = None

    def __init__(self, owner):
        super().__init__()
        self._metadata = None
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
            self.hide()
            drag.exec(Qt.MoveAction)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        open_file(self.metadata["src"])

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict):
        self._metadata = value

    @property
    def thumbnail(self):
        return self._thumbnail

    def updateThumbnail(self, thumbnailer):
        if self.metadata["thumbnail"]:
            path = thumbnailer.resolve_path(self.metadata["thumbnail"])
            pixmap = QPixmap(path)
        else:
            pixmap = BookWidget.PIXMAP
        self._thumbnail = pixmap
        self.setPixmap(pixmap)

    def setThumbnail(self, thumbnail):
        self._thumbnail = thumbnail
        self.setPixmap(thumbnail)

    @property
    def owner(self):
        return self._owner


class ShelfWidget(QWidget):
    BACKGROUND = None
    MAX_BOOKS_COUNT = 256

    def __init__(self):
        super().__init__()
        self.row_capacity = 3
        self.current_row = 1
        self.previous_row = 0
        self.books: List[BookWidget] = []
        self.grid = None
        self._initialSpacer = None
        self._initialize_grid()
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

    def _initialize_grid(self):
        if self.grid:
            while (child := self.grid.takeAt(0)) is not None:
                if child.widget():
                    self.grid.removeWidget(child.widget())
                    child.widget().setParent(None)
                else:
                    self.grid.removeItem(child)
        else:
            self.grid = QGridLayout()
        self.current_row = 1
        self.previous_row = 0
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
        if len(self.books) > self.row_capacity \
                or len(self.books) % self.row_capacity == 1:
            self._initialSpacer.changeSize(0, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)
        else:
            self._initialSpacer.changeSize(0, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        if self.previous_row != row:
            self.grid.addItem(QSpacerItem(0, 167, QSizePolicy.Fixed, QSizePolicy.Fixed), self.current_row, 0)
            self.grid.addItem(QSpacerItem(0, 167, QSizePolicy.Fixed, QSizePolicy.Fixed), self.current_row + 1, 0)
            self.current_row += 1
            self.previous_row = row
        column = len(self.books) % self.row_capacity
        self.books.append(book)
        self.grid.addWidget(book, self.current_row, column)
        if len(self.books) % self.row_capacity == 1:
            self._initialSpacer.changeSize(0, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)

    def render_books(self):
        self._initialize_grid()
        books = self.books
        self.books = []
        for book in books:
            self.add_book(book)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        formats = event.mimeData().formats()
        if 'application/x-bookshelf-book' in formats:
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        new_index = self._find_book_by_pos(event.pos())
        old_index = self._book_index(*self._get_index_by_mime(event.mimeData()))
        self.books[old_index].show()
        self.replace_book(old_index, new_index)
        event.acceptProposedAction()

    def _find_book_by_pos(self, pos):
        found_row = False
        row = 1
        for row in range(1, self.current_row + 1):
            bookpos = self.get_book(row, 0).geometry()
            y_begin, y_end = bookpos.y() - 10, bookpos.y() + bookpos.height() + 10
            if y_begin <= pos.y() <= y_end:
                found_row = True
                break
        row = row if found_row else 1
        print("Found row:", row)
        if self.get_book(row, 0).geometry().topLeft().x() >= pos.x():
            return self._book_index(row, 0)
        else:
            min_length = [float("inf"), float("inf")]
            min_index = [-1, -1]
            for i in range(self.row_capacity):
                bookpos = self.get_book(row, i).geometry().center()
                length = abs(pos.x() - bookpos.x())
                if length < min_length[1]:
                    if min_index[0] != -1:
                        min_index[0] = min_index[1]
                        min_length[0] = min_length[1]
                    min_index[1] = i
                    min_length[1] = length
            if -1 not in min_index:
                return self._book_index(row, min(min_index)) + 1
            else:
                return self._book_index(row, min_index[1]) + 1

    def replace_book(self, old_index, new_index):
        print(old_index, new_index)  # TODO: check whether correct
        self.books.insert(new_index, self.books[old_index])
        if old_index <= new_index:
            self.books.pop(old_index)
        else:
            self.books.pop(old_index + 1)
        self.render_books()

    def find_book(self, book: BookWidget):
        if book in self.books:
            i = self.books.index(book)
            return self._find_by_index(i)
        else:
            return -1, -1

    def _find_by_index(self, i):
        return (i // self.row_capacity) + 1, i % self.row_capacity

    def get_book(self, row: int, column: int):
        return self.books[self._book_index(row, column)]

    def _book_index(self, row: int, column: int):
        row -= 1
        return row * self.row_capacity + column

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.isVisible():
            self.row_capacity = self.size().width() // 128
            self.render_books()

    @staticmethod
    def _get_index_by_mime(mime: QMimeData):
        formats = mime.formats()
        if 'application/x-bookshelf-book' in formats:
            return tuple(map(int, mime.data('application/x-bookshelf-book')
                             .data()
                             .decode("utf-8")
                             .split(",")))
        return -1, -1
