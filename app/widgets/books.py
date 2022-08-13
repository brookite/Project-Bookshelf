from PySide6.QtCore import QMimeData, QTimerEvent
from PySide6.QtGui import QPixmap, Qt, QMouseEvent, QDrag, QDragEnterEvent, QDropEvent, QResizeEvent, \
    QPalette
from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy, QSpacerItem, \
    QApplication, QMenu, QFileDialog, QGraphicsDropShadowEffect

from app.settings import BooksConfig
from app.utils.path import resolve_path, open_file, SUPPORTED_IMAGES
from typing import *


class BookWidget(QLabel):
    metadata: dict
    thumbnail: QPixmap
    owner: "ShelfWidget"

    PIXMAP: QPixmap = None

    def __init__(self, owner, thumbnailer):
        super().__init__()
        self._metadata = None
        self._thumbnailer: "Thumbnailer" = thumbnailer
        self._owner = owner
        if not BookWidget.PIXMAP:
            BookWidget.PIXMAP = QPixmap(resolve_path("resources", "dummybook.png"))
        self._thumbnail = BookWidget.PIXMAP
        self.setPixmap(BookWidget.PIXMAP)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._drag_start = None
        self.set_shadow()

    def set_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(3)
        shadow.setBlurRadius(10)
        self.setGraphicsEffect(shadow)

    def _book_menu(self) -> QMenu:
        menu = QMenu()
        thumbnailAction = menu.addAction(self.tr("Set thumbnail"))
        thumbnailAction.triggered.connect(self.set_external_thumbnail)
        thumbnailAction = menu.addAction(self.tr("Reset thumbnail"))
        thumbnailAction.triggered.connect(self.reset_thumbnail)
        removeAction = menu.addAction(self.tr("Remove book"))
        removeAction.triggered.connect(self.remove)
        return menu

    def _selection_menu(self) -> QMenu:
        menu = QMenu()
        thumbnailAction = menu.addAction(self.tr("Open selected books"))
        thumbnailAction.triggered.connect(self.owner.open_selected_books)
        thumbnailAction = menu.addAction(self.tr("Remove selected books"))
        thumbnailAction.triggered.connect(self.owner.remove_selected_books)
        return menu

    def reset_thumbnail(self):
        self._thumbnailer.reload_thumbnail(self)

    def set_external_thumbnail(self):
        filename = QFileDialog.getOpenFileName(
            self, self.tr("Set external thumbnails"), "",
            SUPPORTED_IMAGES
        )[0]
        self._thumbnailer.load_external_thumbnail(self, filename)

    def remove(self, update_ui=True):
        self.owner.owner.settings.config.remove_book(
            self.metadata, self.owner.owner.shelf_index)
        self.owner.owner.settings.config.save()
        if update_ui:
            self.owner.pop_book(self)

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
            action = drag.exec(Qt.MoveAction)
            if action == Qt.IgnoreAction:
                self.show()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.RightButton:
            if self.owner.owner.is_selection_mode():
                self._selection_menu().exec(event.globalPos())
            else:
                self._book_menu().exec(event.globalPos())
        else:
            if self.owner.owner.is_selection_mode():
                self.select()
            else:
                if self.owner.owner.ctrl_pressed:
                    self.owner.owner.set_selection_mode(True)
                    self.select()
                else:
                    open_file(self.metadata["src"])

    def select(self):
        if not self.is_selected():
            self.setStyleSheet("border: 3px solid #677ff4")
            self.owner.selected_count += 1
        else:
            self.setStyleSheet("")
            self.owner.selected_count -= 1

    def is_selected(self):
        return self.styleSheet().startswith("border")

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict):
        self._metadata = value

    @property
    def thumbnail(self):
        return self._thumbnail

    def update_thumbnail(self):
        if self.metadata["thumbnail"]:
            path = self._thumbnailer.resolve_path(self.metadata["thumbnail"])
            pixmap = QPixmap(path)
        else:
            pixmap = BookWidget.PIXMAP
        self._thumbnail = pixmap
        self.setPixmap(pixmap)

    def set_thumbnail(self, thumbnail):
        self._thumbnail = thumbnail
        self.setPixmap(thumbnail)

    @property
    def owner(self):
        return self._owner


class ShelfWidget(QWidget):
    BACKGROUND = None
    MAX_BOOKS_COUNT = 512
    RESIZE_COOLDOWN = 180  # milliseconds

    def __init__(self, owner: "BookshelfWindow", metadata: dict):
        super().__init__()
        self.row_capacity = 3
        self.loaded = False
        self._owner = owner
        self.current_row = 1
        self.metadata = metadata
        self.previous_row = 0
        self.selected_count = 0
        self.books: List[BookWidget] = []
        self.grid = None
        self._initialSpacer = None
        self.__resize_timerid = 0
        self._initialize_grid()
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.set_background()

    def set_background(self):
        palette = QPalette()
        if not ShelfWidget.BACKGROUND:
            ShelfWidget.BACKGROUND = QPixmap(resolve_path("resources", "bg.png"))
        palette.setBrush(self.owner.backgroundRole(), ShelfWidget.BACKGROUND)
        self.setPalette(palette)

    @property
    def owner(self) -> "BookshelfWindow":
        return self._owner

    @property
    def config(self) -> BooksConfig:
        return self._owner.settings.config

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

    def open_selected_books(self):
        for book in self.books:
            if book.is_selected():
                open_file(book.metadata["src"])
        self.clear_selection()

    def clear_selection(self):
        for book in self.books:
            if book.is_selected():
                book.select()
        self.owner.set_selection_mode(False)

    def clear_all(self):
        to_deletion = self.books.copy()
        for book in to_deletion:
            book.remove(update_ui=False)
        # UI Updating
        for book in to_deletion:
            self.pop_book(book, False)
        self.render_books()

    def remove_selected_books(self):
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
        #FIXME: incorrect replace to end of shelf
        print(old_index, new_index)
        self.books.insert(new_index, self.books[old_index])
        if old_index <= new_index:
            self.books.pop(old_index)
        else:
            self.books.pop(old_index + 1)
        self.render_books()

    def pop_book(self, book, update_ui=True):
        if book in self.books:
            self.books.remove(book)
        if update_ui:
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
        if self.__resize_timerid:
            self.killTimer(self.__resize_timerid)
            self.__resize_timerid = 0
        self.__resize_timerid = self.startTimer(self.RESIZE_COOLDOWN)

    def timerEvent(self, event: QTimerEvent) -> None:
        self.killTimer(self.__resize_timerid)
        self.__resize_timerid = 0
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
