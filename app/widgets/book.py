from PySide6.QtCore import QMimeData
from PySide6.QtGui import QPixmap, Qt, QMouseEvent, QDrag
from PySide6.QtWidgets import QLabel, QSizePolicy, QApplication, \
    QMenu, QFileDialog, QGraphicsDropShadowEffect

from app.utils.path import resolve_path, open_file, SUPPORTED_IMAGES_NAMES


class BookWidget(QLabel):
    metadata: dict
    thumbnail: QPixmap
    owner: "ShelfWidget"

    PIXMAP: QPixmap = None

    def __init__(self, owner, thumbnailer):
        super().__init__(owner)
        self._metadata = None
        self._thumbnailer: "Thumbnailer" = thumbnailer
        self._settings = thumbnailer.settings
        self._owner = owner
        if not BookWidget.PIXMAP:
            BookWidget.PIXMAP = QPixmap(resolve_path("resources", "dummybook.png"))
        self._thumbnail = BookWidget.PIXMAP
        self.setPixmap(BookWidget.PIXMAP)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self._drag_start = None
        self.set_shadow()

    def set_shadow(self):
        if self._settings.config["bookShadows"]:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setOffset(3)
            shadow.setBlurRadius(10)
            self.setGraphicsEffect(shadow)

    def _book_menu(self) -> QMenu:
        menu = QMenu(self)
        thumbnailAction = menu.addAction(QApplication.instance().translate("", "Set thumbnail"))
        thumbnailAction.triggered.connect(self.set_external_thumbnail)
        thumbnailAction = menu.addAction(QApplication.instance().translate("", "Reset thumbnail"))
        thumbnailAction.triggered.connect(self.reset_thumbnail)
        removeAction = menu.addAction(QApplication.instance().translate("", "Remove book"))
        removeAction.triggered.connect(self.remove)
        return menu

    def _selection_menu(self) -> QMenu:
        menu = QMenu(self)
        thumbnailAction = menu.addAction(QApplication.instance().translate("", "Open selected books"))
        thumbnailAction.triggered.connect(self.owner.open_selected_books)
        thumbnailAction = menu.addAction(QApplication.instance().translate("", "Remove selected books"))
        thumbnailAction.triggered.connect(self.owner.remove_selected_books)
        return menu

    def reset_thumbnail(self):
        self._thumbnailer.reload_thumbnail(self)

    def set_external_thumbnail(self):
        filename = QFileDialog.getOpenFileName(
            self, QApplication.instance().translate("", "Set external thumbnails"), "",
            SUPPORTED_IMAGES_NAMES
        )[0]
        self._thumbnailer.load_external_thumbnail(self, filename)

    def remove(self, checked=False, update_ui=True):
        # 'checked' parameter is unused
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
                self._drag_start = None
                self.show()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_start = None
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
                    self.open()

    def open(self):
        src = self._settings.config.booksrc(self.metadata)
        if "${{...}}" in src:
            self.owner.owner.check_book_paths()
        else:
            open_file(src)
            self.metadata["openCount"] += 1

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
