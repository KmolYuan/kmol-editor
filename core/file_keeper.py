# -*- coding: utf-8 -*-

"""The file keeper used to watch the file changes."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from os import stat
from os.path import isfile
from core.QtModules import (
    Slot,
    Signal,
    QWidget,
    QThread,
)


class FileKeeper(QThread):

    """File keeper thread for each file."""

    file_changed = Signal(str)

    def __init__(self, file_name: str, parent: QWidget):
        super(FileKeeper, self).__init__(parent)
        self.finished.connect(self.deleteLater)
        self.file_name = file_name
        self.stopped = False

    def run(self):
        """Watch the file."""
        if not isfile(self.file_name):
            return
        stemp_old = stat(self.file_name).st_mtime
        while not self.stopped:
            stemp = stat(self.file_name).st_mtime
            if stemp_old != stemp:
                self.file_changed.emit(self.file_name)
                stemp_old = stemp
            self.msleep(1)

    @Slot()
    def stop(self):
        self.stopped = True
