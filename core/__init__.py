# -*- coding: utf-8 -*-

"""Core module of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from sys import exit
from core.mainwindow import MainWindow
from core.info import ARGUMENTS
from .QtModules import QApplication

__all__ = ['main']


def main():
    """Startup function."""
    if ARGUMENTS.test:
        print("All module loaded successfully.")
        exit(0)
    QApp = QApplication([])
    if ARGUMENTS.fusion:
        QApp.setStyle('fusion')
    run = MainWindow()
    run.show()
    exit(QApp.exec())
