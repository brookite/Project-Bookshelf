from PySide6 import QtWidgets
from app.window import BookshelfWindow
import sys


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = BookshelfWindow(app)
    window.show()
    sys.exit(app.exec())