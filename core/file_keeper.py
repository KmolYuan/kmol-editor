# -*- coding: utf-8 -*-

"""The file keeper used to watch the file changes."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018-2019"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import Sequence
from os import stat
from os.path import isfile
from core.QtModules import (
    Slot,
    Signal,
    QWidget,
    QThread,
    QTreeWidgetItem,
)
from core.parsers import getpath


class FileKeeper(QThread):

    """File keeper thread for each file."""

    file_changed = Signal(str, QTreeWidgetItem)

    def __init__(self, nodes: Sequence[QTreeWidgetItem], parent: QWidget):
        super(FileKeeper, self).__init__(parent)
        self.finished.connect(self.deleteLater)
        self.nodes = {}
        self.files = {}
        for node in nodes:
            path = getpath(node)
            self.nodes[path] = node
            self.files[path] = stat(path).st_mtime
        self.stopped = False
        self.passed = False

    def run(self):
        """Watch the files."""
        while not self.stopped:
            for f in self.files:
                if self.passed or not isfile(f):
                    continue
                stemp = stat(f).st_mtime
                if self.files[f] != stemp:
                    self.file_changed.emit(f, self.nodes[f])
                    self.files[f] = stemp
            self.msleep(1)

    @Slot()
    def stop(self):
        self.stopped = True

    def set_passed(self, passed: bool):
        """Skip checking."""
        if not passed:
            for f in self.files:
                self.files[f] = stat(f).st_mtime
        self.passed = passed
