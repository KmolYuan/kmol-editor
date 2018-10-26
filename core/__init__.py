# -*- coding: utf-8 -*-

"""Core module of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from sys import exit
import platform
from .mainwindow import MainWindow
from .info import ARGUMENTS
from .QtModules import QApplication

__all__ = ['main']


def main():
    """Startup function."""
    if ARGUMENTS.test:
        print("All module loaded successfully.")
        exit(0)
    qapp = QApplication([])
    if platform.system() == 'Darwin':
        ARGUMENTS.fusion = True
    if ARGUMENTS.fusion:
        qapp.setStyle('fusion')
    run = MainWindow()
    run.show()
    exit(qapp.exec())
