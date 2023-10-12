import random

from PySide6.QtCore import QRect, QTimerEvent
from PySide6.QtGui import Qt, QKeyEvent, QCursor, QIcon, QCloseEvent, QResizeEvent
from PySide6.QtWidgets import QMainWindow, QFileDialog,  QInputDialog, \
    QWidget, QScrollArea, QVBoxLayout, QMenu, QMessageBox

from app.appinfo import VERSION_NAME
from app.settings import SettingsWindow, BookPathsSetupWindow
from app.storage import AppStorage
from app.thumbnailer import Thumbnailer
from app.ui.main import Ui_Bookshelf
from app.utils.applocale import tr
from app.utils.path import SUPPORTED_FORMATS_NAMES, SUPPORTED_FORMATS, resolve_path, BACKUP_FORMAT_NAME, BACKUP_FORMAT
from app.widgets.book import BookWidget
from app.widgets.shelf import ShelfWidget

import os


class BookshelfWindow(QMainWindow, Ui_Bookshelf):
    MAX_SHELFS_COUNT = 32

    def __init__(self, app):
        super().__init__()
        self._app = app
        self.settings = AppStorage()
        self.check_autorecover()
        self.check_book_paths()
        self._ctrl_pressed = False
        self._tab_revert_action = False
        self.setupUi(self)
        self.shelfs = []
        self.load_shelfs()
        # common selected shelf index (this tab)
        self.shelf_index = 0
        # selected shelf index for user selection (not only this tab)
        self._selected_shelf_index = -1
        self.scrollArea.setWidget(self.get_current_shelf())
        self.get_current_shelf().scrollbar = self.scrollArea.verticalScrollBar()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tabWidget.currentChanged.connect(self._tab_changed)
        self.tabWidget.tabBar().tabBarDoubleClicked.connect(self._tab_menu)
        self.tabWidget.tabBar().tabMoved.connect(self._tab_moved)

        self.actionOpen.triggered.connect(self.add_books)
        self.actionImport.triggered.connect(self.import_backup)
        self.actionExport.triggered.connect(self.export)
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionExit.triggered.connect(self.close)
        self.actionAdd_new_shelf.triggered.connect(self.add_shelf)
        self.actionRemoveShelf.triggered.connect(self.remove_shelf)
        self.actionOpenRandom.triggered.connect(self.open_random_book)
        self.actionAbout.triggered.connect(self.about)
        self.actionAbout_Qt.triggered.connect(self._app.aboutQt)

        self.setWindowIcon(QIcon(resolve_path("resources", "applogo.png")))

        self.settings_window = None
        self.__resize_timerid = 0

        self.thumbnailer = Thumbnailer(self.settings)
        self.load_books_widgets()
        self.get_current_shelf().set_background()
        self.get_current_shelf().scrollArea = self.scrollArea
        if self.settings.config["defaultShelf"] != 0:
            self.tabWidget.setCurrentIndex(self.settings.config["defaultShelf"])
        if self.settings.config["shelfs"][0]["name"] != "$DEFAULT_NAME":
            self.tabWidget.setTabText(0, self.settings.config["shelfs"][0]["name"])

        self.restore_geometry()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.store_geometry()
        self.settings.save()
        filename = self.settings.config["autobackupPath"]
        if os.path.exists(os.path.dirname(filename)) and filename.strip():
            if not filename.endswith(BACKUP_FORMAT):
                filename = filename + BACKUP_FORMAT
            self.settings.backup(filename, self.settings.config["storeThumbnails"])

    def resizeEvent(self, event: QResizeEvent) -> None:
        # This cooldown required for smooth rendering
        if self.__resize_timerid:
            self.killTimer(self.__resize_timerid)
            self.__resize_timerid = 0
        self.__resize_timerid = self.startTimer(ShelfWidget.RESIZE_COOLDOWN)

    def timerEvent(self, event: QTimerEvent) -> None:
        self.killTimer(self.__resize_timerid)
        self.__resize_timerid = 0
        if self.isVisible():
            for shelf in self.shelfs:
                shelf.row_capacity = self.size().width() // 128
            self.get_current_shelf().render_books()

    def store_geometry(self):
        self.settings.config["geometry"] = [self.x(), self.y(), self.width(), self.height()]

    def restore_geometry(self):
        if "geometry" in self.settings.config:
            self.setGeometry(*self.settings.config["geometry"])

    def check_autorecover(self):
        if self.settings.config["recoverAutobackup"]:
            path = self.settings.config["autobackupPath"]
            if os.path.exists(path) and path.strip():
                result = self.settings.restore(path, not self.settings.config["storeThumbnails"])
                if not result:
                    QMessageBox.critical(
                        self,
                        tr("Restore failed"),
                        tr("Backup wasn't restored. Check if your backup is valid"))
                print("Auto restore performed")

    def check_book_paths(self):
        if self.settings.config.uses_book_paths():
            is_all_unexists = True
            for path in self.settings.book_paths:
                is_all_unexists &= not os.path.exists(path)
            if is_all_unexists:
                self._tmp_bookpathdialog = BookPathsSetupWindow(self, self.settings)
                self._tmp_bookpathdialog.exec()
                return True
        return False

    def _tab_changed(self, index):
        self.shelf_index = index
        if not self.get_current_shelf().loaded:
            self.load_books_widgets()
            self.get_current_shelf().set_background()
        self.get_current_shelf().render_books()

    def open_settings(self):
        self.settings_window = SettingsWindow(self, self.shelf_index, self.settings)
        self.settings_window.show()

    def open_random_book(self):
        if len(self.get_current_shelf().books):
            book = random.choice(self.get_current_shelf().books)
            book.open()

    def rename_shelf(self):
        index = self._selected_shelf_index
        old_name = self.shelfs[index].metadata["name"]
        if old_name == "$DEFAULT_NAME":
            old_name = tr("My books")
        name, success = QInputDialog.getText(
            self,
            tr("Rename shelf"),
            tr("Input new name of your shelf"),
            text=old_name
        )
        if self.shelf_index == 0 and not name:
            name = "$DEFAULT_NAME"
        if success and name:
            self.shelfs[index].metadata["name"] = name
            display_name = name if name != "$DEFAULT_NAME" else tr("My books")
            self.tabWidget.tabBar().setTabText(self._selected_shelf_index, display_name)
            self.settings.config.save()
        self._selected_shelf_index = -1

    def remove_shelf(self):
        index = self._selected_shelf_index
        if index == -1:
            return
        elif index == 0:
            self.shelfs[0].clear_all()
        else:
            self.settings.config["shelfs"].pop(index)
            self.tabWidget.removeTab(index)
            self.shelfs.pop(index)
        self.settings.config.save()
        self._selected_shelf_index = -1

    def _tab_menu(self, index):
        self._selected_shelf_index = index
        menu = QMenu()
        renameAction = menu.addAction(tr("Rename shelf"))
        renameAction.triggered.connect(self.rename_shelf)
        removeAction = menu.addAction(tr("Remove shelf"))
        removeAction.triggered.connect(self.remove_shelf)
        menu.exec(QCursor.pos())

    def _tab_moved(self, from_, to):
        if self._tab_revert_action:
            self._tab_revert_action = False
            return
        if to == 0 or from_ == 0:
            self._tab_revert_action = True
            self.tabWidget.tabBar().moveTab(to, from_)
            return
        self.settings.config.move_shelfs(from_, to)
        self.settings.config.save()

    @property
    def ctrl_pressed(self):
        return self._ctrl_pressed

    def get_current_shelf(self):
        return self.shelfs[self.shelf_index]

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self._ctrl_pressed = True

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self._ctrl_pressed = False
        if not self.shelfs[self.shelf_index].selected_count:
            self.set_selection_mode(False)

    def is_selection_mode(self):
        return self.actionSelection_mode.isChecked()

    def set_selection_mode(self, value: bool) -> None:
        self.actionSelection_mode.setChecked(value)

    def load_books_widgets(self):
        for bookdata in self.settings.config.get_books(self.shelf_index):
            self.load_book_widget(bookdata)
        self.get_current_shelf().loaded = True
        self.thumbnailer.load_thumbnails(self.get_current_shelf().books)

    def load_book_widget(self, bookdata: dict) -> BookWidget:
        book = BookWidget(self.get_current_shelf(), self.thumbnailer)
        book.metadata = bookdata
        book.setToolTip(bookdata["name"])
        self.get_current_shelf().add_book(book)
        return book

    def _form_shelf(self, shelf):
        bookshelf = QWidget()
        vbox = QVBoxLayout(bookshelf)
        scrollArea = QScrollArea(bookshelf)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setWidgetResizable(True)
        shelf.setGeometry(QRect(0, 0, 386, 397))
        shelf.scrollbar = scrollArea.verticalScrollBar()
        scrollArea.setWidget(shelf)
        shelf.scrollArea = scrollArea
        vbox.addWidget(scrollArea)
        return bookshelf

    def rebuild_book_order(self):
        books = self.get_current_shelf().books
        self.settings.config["shelfs"][self.shelf_index]["books"] = []
        for book in books:
            self.settings.config["shelfs"][self.shelf_index]["books"].append(book.metadata)
        self.settings.config.save()

    def load_shelfs(self):
        for i, data in enumerate(self.settings.config["shelfs"]):
            shelf = ShelfWidget(self, data)
            self.shelfs.append(shelf)
            if i > 0:
                self.tabWidget.insertTab(i, self._form_shelf(shelf), data["name"])

    def add_shelf(self):
        if len(self.shelfs) >= self.MAX_SHELFS_COUNT:
            QMessageBox.warning(
                self, tr("Limit has reached"),
                tr("You may create only {} shelfs").format(self.MAX_SHELFS_COUNT))
            return
        name, success = QInputDialog.getText(
            self,
            tr("Adding new shelf"),
            tr("Input name of your new shelf")
        )
        if success:
            index, metadata = self.settings.config.add_shelf(name)
            shelf = ShelfWidget(self, metadata)
            self.shelfs.append(shelf)
            self.tabWidget.insertTab(index, self._form_shelf(shelf), name)

    def add_new_book_to_config(self, path: str):
        return self.settings.config.add_file(self.shelf_index, path)

    def export(self):
        filename = QFileDialog.getSaveFileName(
            self, tr("Export backup"), "",
            BACKUP_FORMAT_NAME
        )[0]
        if filename:
            if not filename.endswith(BACKUP_FORMAT):
                filename = filename + BACKUP_FORMAT
            self.settings.backup(filename, self.settings.config["storeThumbnails"])

    def import_backup(self):
        filename = QFileDialog.getOpenFileName(
            self, tr("Import backup"), "",
            BACKUP_FORMAT_NAME
        )[0]
        confirm = QMessageBox.question(self,
                             tr("Data erase warning"),
                             tr("Your books and all app information will be replaced "
                                     "by backup data. Are you sure?"))
        if confirm != QMessageBox.StandardButton.Yes:
            return
        result = self.settings.restore(filename, not self.settings.config["storeThumbnails"])
        self.check_book_paths()
        if not result:
            QMessageBox.critical(self,
                                 tr("Restore failed"),
                                 tr("Backup wasn't restored. Check if your backup is valid"))
        else:
            QMessageBox.information(self,
                                    tr("Restore finished"),
                                    tr("Backup has been restored successfully. "
                                            "Application will be closed, please open it again"))
            self.close()

    def add_books(self):
        default_dir = ""
        for directory in self.settings.book_paths:
            if os.path.isdir(directory):
                default_dir = directory
                break

        filenames = QFileDialog.getOpenFileNames(
            self, tr("Adding books"), default_dir,
            SUPPORTED_FORMATS_NAMES
        )
        books = []
        for file in filenames[0]:
            book = self.add_book(file)
            if book:
                books.append(book)
        self.thumbnailer.load_thumbnails(books)

    def add_book(self, file, thumbnailer_call=False) -> BookWidget:
        if os.path.splitext(file)[1].lower() in SUPPORTED_FORMATS:
            if (len(self.get_current_shelf().books) + 1) <= ShelfWidget.MAX_BOOKS_COUNT:
                metadata = self.add_new_book_to_config(file)
                if metadata:
                    book = self.load_book_widget(metadata)
                    if thumbnailer_call:
                        self.thumbnailer.load_thumbnails([book])
                    return book
            else:
                QMessageBox.warning(
                    self, tr("Limit has reached"),
                    tr("You may place in one shelf only {} books"
                                                          .format(ShelfWidget.MAX_BOOKS_COUNT)))

    def about(self):
        QMessageBox.about(self, tr("About Project Bookshelf"),
                                '<p><b>' + f'Project Bookshelf {VERSION_NAME}' + '</b></p>'
                                 + tr('Elegant bookshelf for your documents') + '<br>'
                                 + tr('Author: ') + "Brookit, 2023"
                                 + '<br><a href="https://github.com/brookite">GitHub</a>')

