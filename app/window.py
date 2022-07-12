from PySide6.QtGui import QPalette, QPixmap, Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from app.ui.main import Ui_Bookshelf
from app.ui.shelf import Ui_Shelf
from app.utils.path import resolve_path


class ShelfWidget(QWidget, Ui_Shelf):
    BACKGROUND = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class BookshelfWindow(QMainWindow, Ui_Bookshelf):
    def __init__(self, app):
        super().__init__()
        self._app = app
        self._rendered_shelfs = []
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
            self._rendered_shelfs.append(shelf)
            self.shelfLayout.addWidget(shelf)


