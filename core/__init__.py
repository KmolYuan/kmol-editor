# -*- coding: utf-8 -*-

"""Core module of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018-2019"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from sys import exit
import platform
from .main_window import MainWindow
from .info import ARGUMENTS
from .QtModules import QApplication

__all__ = ['main']


def main():
    """Startup function."""
    global app
    if ARGUMENTS.test:
        print("All module loaded successfully.")
        exit(0)
    app = QApplication([])
    if platform.system() == 'Darwin':
        ARGUMENTS.fusion = True
    if ARGUMENTS.fusion:
        app.setStyle('fusion')
    run = MainWindow()
    run.showMaximized()
    exit(app.exec())
