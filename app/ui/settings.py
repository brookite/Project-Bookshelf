# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

class Ui_Settings(object):
    def setupUi(self, Settings):
        if not Settings.objectName():
            Settings.setObjectName(u"Settings")
        Settings.resize(520, 281)
        self.verticalLayout = QVBoxLayout(Settings)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(Settings)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.scrollArea_2 = QScrollArea(self.tab_2)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 478, 215))
        self.verticalLayout_5 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.shelfViewArea = QScrollArea(self.scrollAreaWidgetContents_2)
        self.shelfViewArea.setObjectName(u"shelfViewArea")
        self.shelfViewArea.setWidgetResizable(True)
        self.shelfViews = QWidget()
        self.shelfViews.setObjectName(u"shelfViews")
        self.shelfViews.setGeometry(QRect(0, 0, 347, 193))
        self.verticalLayout_7 = QVBoxLayout(self.shelfViews)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.shelfViewArea.setWidget(self.shelfViews)

        self.horizontalLayout_2.addWidget(self.shelfViewArea)


        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_4.addWidget(self.scrollArea_2)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_2 = QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea = QScrollArea(self.tab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 353, 161))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.bookShadows = QCheckBox(self.scrollAreaWidgetContents)
        self.bookShadows.setObjectName(u"bookShadows")

        self.verticalLayout_3.addWidget(self.bookShadows)

        self.denyBookPaths = QCheckBox(self.scrollAreaWidgetContents)
        self.denyBookPaths.setObjectName(u"denyBookPaths")

        self.verticalLayout_3.addWidget(self.denyBookPaths)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.setupBookPaths = QPushButton(self.scrollAreaWidgetContents)
        self.setupBookPaths.setObjectName(u"setupBookPaths")

        self.horizontalLayout.addWidget(self.setupBookPaths)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.pathBackup = QLineEdit(self.scrollAreaWidgetContents)
        self.pathBackup.setObjectName(u"pathBackup")

        self.horizontalLayout_3.addWidget(self.pathBackup)

        self.selectPath = QPushButton(self.scrollAreaWidgetContents)
        self.selectPath.setObjectName(u"selectPath")

        self.horizontalLayout_3.addWidget(self.selectPath)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.recoverBookshelf = QCheckBox(self.scrollAreaWidgetContents)
        self.recoverBookshelf.setObjectName(u"recoverBookshelf")

        self.verticalLayout_3.addWidget(self.recoverBookshelf)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.tabWidget.addTab(self.tab, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(Settings)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Settings)
    # setupUi

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QCoreApplication.translate("Settings", u"App Settings", None))
        self.label_2.setText(QCoreApplication.translate("Settings", u"Shelf background", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Settings", u"Shelf", None))
        self.bookShadows.setText(QCoreApplication.translate("Settings", u"Book shadows", None))
        self.denyBookPaths.setText(QCoreApplication.translate("Settings", u"Deny book paths usage", None))
        self.label.setText(QCoreApplication.translate("Settings", u"Book paths setup", None))
        self.setupBookPaths.setText(QCoreApplication.translate("Settings", u"Setup", None))
        self.label_3.setText(QCoreApplication.translate("Settings", u"Path for autobackup on exit", None))
        self.selectPath.setText(QCoreApplication.translate("Settings", u"Select", None))
        self.recoverBookshelf.setText(QCoreApplication.translate("Settings", u"Automatically recover bookshelf by autobackup path", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Settings", u"App", None))
    # retranslateUi

