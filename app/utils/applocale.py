from PySide6.QtWidgets import QApplication


def tr(text):
    return QApplication.translate("", text)