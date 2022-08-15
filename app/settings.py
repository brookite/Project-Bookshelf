import os.path

from PySide6.QtWidgets import QDialog, QFileDialog

from app.storage import AppStorage
from app.ui.settings import Ui_Settings
from app.ui.bookspath import Ui_BooksPath


class BookPathsSetupWindow(QDialog, Ui_BooksPath):
    def __init__(self, parent, storage: AppStorage):
        super().__init__(parent)
        self.storage = storage
        self.setupUi(self)
        self.addButton.clicked.connect(self.add_path)
        self.removeButton.clicked.connect(self.remove_path)
        self.cancelButton.clicked.connect(self.close)
        self.upButton.clicked.connect(self.up)
        self.downButton.clicked.connect(self.down)
        self.saveButton.clicked.connect(self.save)
        for bookpath in self.storage.book_paths:
            self.listWidget.addItem(bookpath)

    def _index(self):
        index = self.listWidget.selectedIndexes()
        if not len(index):
            index = 0
        else:
            index = index[0].row()
        return index

    def add_path(self):
        filename = QFileDialog.getExistingDirectory(
            self, self.tr("Select directory"), "")
        filename = os.path.abspath(filename)
        for bookpath in self.storage.book_paths:
            if os.path.samefile(bookpath, filename):
                return
        index = self._index() + 1
        self.listWidget.insertItem(index, filename)
        self.storage.book_paths.insert(index, filename)

    def remove_path(self):
        for item in self.listWidget.selectedItems():
            self.listWidget.takeItem(self.listWidget.row(item))

    def up(self):
        row = self._index()
        item = self.listWidget.takeItem(row)
        self.listWidget.insertItem(row - 1, item)
        path = self.storage.book_paths.pop(row)
        self.storage.book_paths.insert(row - 1, path)

    def down(self):
        row = self._index()
        item = self.listWidget.takeItem(row)
        self.listWidget.insertItem(row + 1, item)
        path = self.storage.book_paths.pop(row)
        self.storage.book_paths.insert(row + 1, path)

    def save(self):
        self.storage.save()
        self.close()


class SettingsWindow(QDialog, Ui_Settings):
    def __init__(self, parent, storage: AppStorage):
        super().__init__(parent)
        self.storage = storage
        self.setupUi(self)
        self.set_settings()
        self.bookPathsDialog = None
        self.setupBookPaths.clicked.connect(self.open_path_setup_window)

    def open_path_setup_window(self):
        self.bookPathsDialog = BookPathsSetupWindow(self, self.storage)
        self.bookPathsDialog.show()

    def poll_settings(self):
        self.storage.config["bookShadows"] = self.bookShadows.isChecked()
        if self.denyBookPaths.isChecked() != self.storage.config["denyBookPaths"]:
            self.storage.config["denyBookPaths"] = self.denyBookPaths.isChecked()
            if not self.storage.config["denyBookPaths"]:
                self.storage.config.convert_to_bookpaths()
            else:
                self.storage.config.convert_to_explicit_paths()
        self.storage.save()

    def set_settings(self):
        self.denyBookPaths.setChecked(self.storage.config["denyBookPaths"])
        self.bookShadows.setChecked(self.storage.config["bookShadows"])
        self.bookShadows.stateChanged.connect(self.poll_settings)
        self.denyBookPaths.stateChanged.connect(self.poll_settings)
