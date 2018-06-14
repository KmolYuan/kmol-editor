# -*- coding: utf-8 -*-

"""Right click menu of tree widget."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2016-2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from core.QtModules import (
    QMenu,
    QAction,
)


def setmenu(self):
    """Set context menu."""
    self.tree_widget.customContextMenuRequested.connect(
        self.on_tree_widget_context_menu
    )
    self.popMenu_tree = QMenu(self)
    self.tree_add = QAction("&Add", self)
    self.popMenu_tree.addAction(self.tree_add)
