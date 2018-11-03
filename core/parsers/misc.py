# -*- coding: utf-8 -*-

"""Misc functions."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from core.QtModules import (
    QTreeWidgetItem,
    QFileInfo,
    QDir,
)


def file_suffix(filename: str) -> str:
    """Return suffix of file name."""
    return QFileInfo(filename).suffix()


def node_getpath(node: QTreeWidgetItem) -> str:
    """Recursive return the path of the node."""
    path = node.text(1)
    parent = node.parent()
    if not parent:
        if file_suffix(path) == 'kmol':
            return QFileInfo(path).absolutePath()
        else:
            return path
    return QDir(node_getpath(parent)).filePath(path)


def getpath(node: QTreeWidgetItem) -> str:
    """Get the path of current node."""
    parent = node.parent()
    filename = node.text(1)
    if parent:
        return QFileInfo(QDir(node_getpath(parent)).filePath(filename)).absoluteFilePath()
    return filename
