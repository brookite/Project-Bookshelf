# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QScrollArea, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_Bookshelf(object):
    def setupUi(self, Bookshelf):
        if not Bookshelf.objectName():
            Bookshelf.setObjectName(u"Bookshelf")
        Bookshelf.resize(428, 483)
        Bookshelf.setStyleSheet(u"")
        self.actionOpen = QAction(Bookshelf)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionExport = QAction(Bookshelf)
        self.actionExport.setObjectName(u"actionExport")
        self.actionImport = QAction(Bookshelf)
        self.actionImport.setObjectName(u"actionImport")
        self.actionExit = QAction(Bookshelf)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAdd_new_shelf = QAction(Bookshelf)
        self.actionAdd_new_shelf.setObjectName(u"actionAdd_new_shelf")
        self.actionAbout_Qt = QAction(Bookshelf)
        self.actionAbout_Qt.setObjectName(u"actionAbout_Qt")
        self.actionAbout = QAction(Bookshelf)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionSettings = QAction(Bookshelf)
        self.actionSettings.setObjectName(u"actionSettings")
        self.actionSelection_mode = QAction(Bookshelf)
        self.actionSelection_mode.setObjectName(u"actionSelection_mode")
        self.actionSelection_mode.setCheckable(True)
        self.actionRemoveShelf = QAction(Bookshelf)
        self.actionRemoveShelf.setObjectName(u"actionRemoveShelf")
        self.central = QWidget(Bookshelf)
        self.central.setObjectName(u"central")
        self.verticalLayout = QVBoxLayout(self.central)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.central)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMinimumSize(QSize(410, 410))
        self.tabWidget.setTabsClosable(False)
        self.mainBookshelf = QWidget()
        self.mainBookshelf.setObjectName(u"mainBookshelf")
        self.verticalLayout_2 = QVBoxLayout(self.mainBookshelf)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea = QScrollArea(self.mainBookshelf)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 386, 397))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.tabWidget.addTab(self.mainBookshelf, "")

        self.verticalLayout.addWidget(self.tabWidget)

        Bookshelf.setCentralWidget(self.central)
        self.menubar = QMenuBar(Bookshelf)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 428, 20))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName(u"menuTools")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        Bookshelf.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addAction(self.actionExit)
        self.menuTools.addAction(self.actionAdd_new_shelf)
        self.menuTools.addAction(self.actionRemoveShelf)
        self.menuTools.addAction(self.actionSelection_mode)
        self.menuTools.addAction(self.actionSettings)
        self.menuHelp.addAction(self.actionAbout_Qt)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(Bookshelf)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Bookshelf)
    # setupUi

    def retranslateUi(self, Bookshelf):
        Bookshelf.setWindowTitle(QCoreApplication.translate("Bookshelf", u"Project Bookshelf", None))
        self.actionOpen.setText(QCoreApplication.translate("Bookshelf", u"Open", None))
        self.actionExport.setText(QCoreApplication.translate("Bookshelf", u"Export", None))
        self.actionImport.setText(QCoreApplication.translate("Bookshelf", u"Import", None))
        self.actionExit.setText(QCoreApplication.translate("Bookshelf", u"Exit", None))
        self.actionAdd_new_shelf.setText(QCoreApplication.translate("Bookshelf", u"Add new shelf", None))
        self.actionAbout_Qt.setText(QCoreApplication.translate("Bookshelf", u"About Qt", None))
        self.actionAbout.setText(QCoreApplication.translate("Bookshelf", u"About", None))
        self.actionSettings.setText(QCoreApplication.translate("Bookshelf", u"Settings", None))
        self.actionSelection_mode.setText(QCoreApplication.translate("Bookshelf", u"Selection mode", None))
        self.actionRemoveShelf.setText(QCoreApplication.translate("Bookshelf", u"Remove selected shelf", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mainBookshelf), QCoreApplication.translate("Bookshelf", u"My books", None))
        self.menuFile.setTitle(QCoreApplication.translate("Bookshelf", u"File", None))
        self.menuTools.setTitle(QCoreApplication.translate("Bookshelf", u"Tools", None))
        self.menuHelp.setTitle(QCoreApplication.translate("Bookshelf", u"Help", None))
    # retranslateUi

