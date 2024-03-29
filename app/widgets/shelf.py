import math
import os
from typing import List

from PySide6.QtCore import QMimeData, QTimerEvent
from PySide6.QtGui import QPixmap, QPalette, QDragEnterEvent, QDropEvent, QResizeEvent, QDragMoveEvent, QCursor
from PySide6.QtWidgets import QWidget, QSizePolicy, QGridLayout, QSpacerItem

from app.storage import BooksConfig
from app.utils.path import resolve_path


class ShelfWidget(QWidget):
    BACKGROUND = None
    BACKGROUND_DEFAULT_SIZE = (512, 167)
    MAX_BOOKS_COUNT = 512  # it may cause lags on big values
    RESIZE_COOLDOWN = 120  # milliseconds

    def __init__(self, owner: "BookshelfWindow", metadata: dict):
        super().__init__(owner)
        self.row_capacity = 3
        self.loaded = False
        self._owner = owner
        self.current_row = 1
        self.drag_state = False
        self.scrollArea = None
        self.metadata = metadata
        self.previous_row = 0
        self.selected_count = 0
        self.books: List["BookWidget"] = []
        self.grid = None
        self._initialSpacer = None
        self._initialize_grid()
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

    def set_background(self):
        palette = QPalette()
        if not ShelfWidget.BACKGROUND:
            ShelfWidget.BACKGROUND = QPixmap(resolve_path("resources", "bg.png"))
        pixmap = ShelfWidget.BACKGROUND
        if self in self.owner.shelfs:
            i = self.owner.shelfs.index(self)
            path = self.owner.settings.shelf_view_path(i)
            if path and os.path.exists(path):
                pixmap = QPixmap(path)
                if pixmap.width() != self.BACKGROUND_DEFAULT_SIZE[0] \
                        or pixmap.height() != self.BACKGROUND_DEFAULT_SIZE[1]:
                    pixmap = pixmap.scaled(self.BACKGROUND_DEFAULT_SIZE)
        palette.setBrush(self.owner.backgroundRole(), pixmap)
        self.setPalette(palette)

    @property
    def owner(self) -> "BookshelfWindow":
        return self._owner

    @property
    def config(self) -> BooksConfig:
        return self._owner.settings.config

    def _initialize_grid(self):
        print("Grid updated")
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

    def add_book(self, book: "BookWidget") -> None:
        if len(self.books) >= ShelfWidget.MAX_BOOKS_COUNT:
            return
        row = len(self.books) // self.row_capacity
        if len(self.books) > self.row_capacity:
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
        if len(self.books) % self.row_capacity == 1 and len(self.books) > self.row_capacity:
            self._initialSpacer.changeSize(0, 0, QSizePolicy.Fixed, QSizePolicy.Fixed)

    def render_books(self):
        print("Rendering {} books".format(len(self.books)))
        self._initialize_grid()
        books = self.books
        self.books = []
        for book in books:
            self.add_book(book)

    def open_selected_books(self):
        for book in self.books:
            if book.is_selected():
                book.open()
        self.clear_selection()

    def clear_selection(self):
        for book in self.books:
            if book.is_selected():
                book.select()
        self.owner.set_selection_mode(False)

    def clear_all(self):
        # removes books on UI side and in config
        to_deletion = self.books.copy()
        for book in to_deletion:
            book.remove(update_ui=False)
        # UI Updating
        for book in to_deletion:
            self.pop_book(book, False)
        self.render_books()

    def remove_selected_books(self):
        # removes books on UI side and in config
        to_deletion = []
        for book in self.books:
            if book.is_selected():
                to_deletion.append(book)
        for book in to_deletion:
            book.remove(update_ui=False)
        # UI Updating
        for book in to_deletion:
            self.pop_book(book, False)
        self.render_books()
        self.clear_selection()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mimedata = event.mimeData()
        formats = mimedata.formats()
        if 'application/x-bookshelf-book' in formats or mimedata.hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if self.drag_state:
            pos = self.scrollArea.mapFromGlobal(QCursor.pos())
            scroll_max_y = self.scrollArea.size().height()
            max_y = self.size().height()
            bar = self.scrollArea.verticalScrollBar()
            if scroll_max_y != max_y:
                step = 0
                if abs(pos.y() - scroll_max_y) <= 15:
                    step = 25
                elif abs(pos.y() - scroll_max_y) <= 45:
                    step = 15

                if bar.value() > 0 and pos.y() <= 30:
                    step = -15

                bar.setValue(bar.value() + step)

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    self.owner.add_book(url.toLocalFile(), True)
                    self.replace_book(len(self.books) - 1, self._find_book_by_pos(event.pos()))
        else:
            new_index = self._find_book_by_pos(event.pos())
            old_index = self._book_index(*self._get_index_by_mime(event.mimeData()))
            self.books[old_index].show()
            self.replace_book(old_index, new_index)
            event.acceptProposedAction()

    def _find_book_by_pos(self, pos):
        '''
        Finds book internal index by position. Initially, method will find destination row number,
        and then will find column for book placement
        '''
        found_row = False
        row = 1
        for row in range(1, self.current_row + 1):
            bookpos = self.get_book(row, 0).geometry()
            y_begin, y_end = bookpos.y() - 10, bookpos.y() + bookpos.height() + 10
            if y_begin <= pos.y() <= y_end:
                found_row = True
                break
        row = row if found_row else 1
        if self.get_book(row, 0).geometry().topLeft().x() >= pos.x():
            return self._book_index(row, 0)
        else:
            min_length = [float("inf"), float("inf")]
            min_index = [-1, -1]
            if math.ceil(len(self.books) / self.row_capacity) == row and len(self.books) % self.row_capacity != 0:
                places = len(self.books) % self.row_capacity
            else:
                places = self.row_capacity
            for i in range(places):
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
        self.books.insert(new_index, self.books[old_index])
        if old_index <= new_index:
            self.books.pop(old_index)
        else:
            self.books.pop(old_index + 1)
        self.render_books()
        self.owner.rebuild_book_order()

    def pop_book(self, book, update_ui=True):
        '''
        Removes book only on shelf (not in config)
        '''
        if book in self.books:
            self.books.remove(book)
        if update_ui:
            self.render_books()

    def find_book(self, book: "BookWidget"):
        '''
        Finds book row, column by book widget
        '''
        if book in self.books:
            i = self.books.index(book)
            return self._find_by_index(i)
        else:
            return -1, -1

    def _find_by_index(self, i):
        '''
        Returns row, column by internal index (in 'self.books' list)
        '''
        return (i // self.row_capacity) + 1, i % self.row_capacity

    def get_book(self, row: int, column: int):
        return self.books[self._book_index(row, column)]

    def _book_index(self, row: int, column: int):
        '''
        Returns book internal index by row and column
        '''
        row -= 1
        return row * self.row_capacity + column

    @staticmethod
    def _get_index_by_mime(mime: QMimeData):
        formats = mime.formats()
        if 'application/x-bookshelf-book' in formats:
            return tuple(map(int, mime.data('application/x-bookshelf-book')
                             .data()
                             .decode("utf-8")
                             .split(",")))
        return -1, -1
