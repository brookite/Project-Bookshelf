# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'shelf.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QSizePolicy, QWidget)

class Ui_Shelf(object):
    def setupUi(self, Shelf):
        if not Shelf.objectName():
            Shelf.setObjectName(u"Shelf")
        Shelf.resize(512, 167)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Shelf.sizePolicy().hasHeightForWidth())
        Shelf.setSizePolicy(sizePolicy)
        Shelf.setMinimumSize(QSize(256, 167))
        Shelf.setMaximumSize(QSize(16777215, 167))
        Shelf.setStyleSheet(u"")
        self.gridLayout_2 = QGridLayout(Shelf)
        self.gridLayout_2.setObjectName(u"gridLayout_2")

        self.retranslateUi(Shelf)

        QMetaObject.connectSlotsByName(Shelf)
    # setupUi

    def retranslateUi(self, Shelf):
        Shelf.setWindowTitle(QCoreApplication.translate("Shelf", u"Form", None))
    # retranslateUi

