# -*- coding: utf-8 -*-

"""Core module of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2016-2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from .QtModules import QApplication
from core.mainwindow import MainWindow

__all__ = ['main']


def main():
    qApp = QApplication([])
    run = MainWindow()
    run.show()
    exit(qApp.exec())
