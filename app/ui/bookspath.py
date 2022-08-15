# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bookspath.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_BooksPath(object):
    def setupUi(self, BooksPath):
        if not BooksPath.objectName():
            BooksPath.setObjectName(u"BooksPath")
        BooksPath.resize(538, 427)
        self.verticalLayout = QVBoxLayout(BooksPath)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(BooksPath)
        self.label.setObjectName(u"label")
        self.label.setWordWrap(True)

        self.verticalLayout.addWidget(self.label)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.addButton = QPushButton(BooksPath)
        self.addButton.setObjectName(u"addButton")

        self.horizontalLayout_2.addWidget(self.addButton)

        self.removeButton = QPushButton(BooksPath)
        self.removeButton.setObjectName(u"removeButton")

        self.horizontalLayout_2.addWidget(self.removeButton)

        self.upButton = QPushButton(BooksPath)
        self.upButton.setObjectName(u"upButton")

        self.horizontalLayout_2.addWidget(self.upButton)

        self.downButton = QPushButton(BooksPath)
        self.downButton.setObjectName(u"downButton")

        self.horizontalLayout_2.addWidget(self.downButton)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.scrollArea = QScrollArea(BooksPath)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 518, 324))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidget = QListWidget(self.scrollAreaWidgetContents)
        self.listWidget.setObjectName(u"listWidget")
        self.listWidget.setWordWrap(True)
        self.listWidget.setSelectionRectVisible(True)

        self.verticalLayout_2.addWidget(self.listWidget)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.saveButton = QPushButton(BooksPath)
        self.saveButton.setObjectName(u"saveButton")

        self.horizontalLayout.addWidget(self.saveButton)

        self.cancelButton = QPushButton(BooksPath)
        self.cancelButton.setObjectName(u"cancelButton")

        self.horizontalLayout.addWidget(self.cancelButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(BooksPath)

        QMetaObject.connectSlotsByName(BooksPath)
    # setupUi

    def retranslateUi(self, BooksPath):
        BooksPath.setWindowTitle(QCoreApplication.translate("BooksPath", u"Setup books path", None))
        self.label.setText(QCoreApplication.translate("BooksPath", u"Select paths where app will find your books", None))
        self.addButton.setText(QCoreApplication.translate("BooksPath", u"Add path", None))
        self.removeButton.setText(QCoreApplication.translate("BooksPath", u"Remove", None))
        self.upButton.setText(QCoreApplication.translate("BooksPath", u"Up", None))
        self.downButton.setText(QCoreApplication.translate("BooksPath", u"Down", None))
        self.saveButton.setText(QCoreApplication.translate("BooksPath", u"Save", None))
        self.cancelButton.setText(QCoreApplication.translate("BooksPath", u"Cancel", None))
    # retranslateUi

