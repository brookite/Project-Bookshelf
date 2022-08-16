import os.path
from typing import List

from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QCloseEvent
from PySide6.QtWidgets import QDialog, QFileDialog, QRadioButton

from app.storage import AppStorage
from app.ui.settings import Ui_Settings
from app.ui.bookspath import Ui_BooksPath
from app.utils.path import BACKUP_FORMAT_NAME, BACKUP_FORMAT
from app.widgets.shelf import ShelfWidget


class BookPathsSetupWindow(QDialog, Ui_BooksPath):
    def __init__(self, parent, storage: AppStorage):
        super().__init__(parent)
        self.storage = storage
        self.setupUi(self)
        self.setModal(True)
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
    def __init__(self, parent, shelf_index, storage: AppStorage):
        super().__init__(parent)
        self.storage = storage
        self._shelf_index = shelf_index
        self._shelfviews_rb: List[QRadioButton] = []
        self.setupUi(self)
        self.set_settings()
        self.bookPathsDialog = None
        self.setupBookPaths.clicked.connect(self.open_path_setup_window)
        self.selectPath.clicked.connect(self.select_backuppath)
        self.form_shelf_views()

    def view_selected(self, checked):
        for rb in self._shelfviews_rb:
            if rb.isChecked():
                self.storage.config["shelfs"][self._shelf_index]["view"] = rb.objectName()
                self.parent().get_current_shelf().set_background()

    def form_shelf_views(self):
        default = QRadioButton()
        default.setChecked(True)
        default.setObjectName("default")
        default.setIcon(ShelfWidget.BACKGROUND)
        default.toggled.connect(self.view_selected)
        default.setIconSize(QSize(256, 84))
        self._shelfviews_rb.append(default)
        self.shelfViews.layout().addWidget(default)
        for view in self.storage.shelf_views():
            basename = os.path.basename(view)
            shelfview = QRadioButton()
            if self.storage.shelf_view_path(self._shelf_index) == view:
                shelfview.setChecked(True)
                default.setChecked(False)
            shelfview.setIcon(QPixmap(view))
            shelfview.toggled.connect(self.view_selected)
            shelfview.setIconSize(QSize(256, 84))
            shelfview.setObjectName(basename)
            self._shelfviews_rb.append(shelfview)
            self.shelfViews.layout().addWidget(shelfview)

    def open_path_setup_window(self):
        self.bookPathsDialog = BookPathsSetupWindow(self, self.storage)
        self.bookPathsDialog.show()

    def select_backuppath(self):
        filename = QFileDialog.getSaveFileName(
            self, self.tr("Select path for autobackup"), "",
            BACKUP_FORMAT_NAME
        )[0]
        if not filename.endswith(BACKUP_FORMAT):
            filename = filename + BACKUP_FORMAT
        if os.path.exists(os.path.dirname(filename)):
            self.pathBackup.setText(filename)
            self.storage.config["autobackupPath"] = filename

    def poll_settings(self):
        self.storage.config["bookShadows"] = self.bookShadows.isChecked()
        self.storage.config["recoverAutobackup"] = self.recoverBookshelf.isChecked()
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
        self.recoverBookshelf.setChecked(self.storage.config["recoverAutobackup"])
        self.bookShadows.stateChanged.connect(self.poll_settings)
        self.denyBookPaths.stateChanged.connect(self.poll_settings)
        self.recoverBookshelf.stateChanged.connect(self.poll_settings)
        self.pathBackup.setText(self.storage.config["autobackupPath"])

    def closeEvent(self, event: QCloseEvent) -> None:
        self.storage.save()
