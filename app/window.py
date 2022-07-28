from PySide6.QtGui import QPalette, QPixmap, Qt
from PySide6.QtWidgets import QMainWindow
from app.ui.main import Ui_Bookshelf
from app.utils.path import resolve_path

from app.widgets.books import ShelfWidget, BookWidget


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
        for i in range(30):
            book = BookWidget(self.shelf)
            book.setToolTip(str(i))
            self.shelf.add_book(book)







