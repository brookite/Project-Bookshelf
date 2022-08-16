from PySide6 import QtWidgets
from PySide6.QtCore import QTranslator, QLocale, QLibraryInfo

from app.utils.path import resolve_path
from app.window import BookshelfWindow
import sys


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    language = QLocale().name()
    AppTranslator = QTranslator()
    AppTranslator.load('bookshelf_' + language,
                       resolve_path("resources", "i18n"))
    QtTranslator = QTranslator()
    translationsPath = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    QtTranslator.load("qtbase_" + language, translationsPath)
    app.installTranslator(AppTranslator)
    app.installTranslator(QtTranslator)

    window = BookshelfWindow(app)
    window.show()
    sys.exit(app.exec())