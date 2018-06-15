# -*- coding: utf-8 -*-

"""Right click menu of tree widget."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from core.QtModules import (
    Qt,
    QMenu,
    QAction,
)


def setmenu(self):
    """Set context menu."""
    self.tree_widget.customContextMenuRequested.connect(
        self.on_tree_widget_context_menu
    )
    self.popMenu_tree = QMenu(self)
    self.popMenu_tree.setSeparatorsCollapsible(True)
    self.action_new_project.triggered.connect(self.newFile)
    self.popMenu_tree.addAction(self.action_new_project)
    self.action_open.triggered.connect(self.openFile)
    self.popMenu_tree.addAction(self.action_open)
    self.tree_add = QAction("&Add", self)
    self.tree_add.triggered.connect(self.addNode)
    self.tree_add.setShortcut("Ctrl+I")
    self.tree_add.setShortcutContext(Qt.WindowShortcut)
    self.popMenu_tree.addAction(self.tree_add)
    
    self.popMenu_tree.addSeparator()
    
    self.tree_path = QAction("Set &Path", self)
    self.tree_path.triggered.connect(self.setPath)
    self.popMenu_tree.addAction(self.tree_path)
    self.action_save.triggered.connect(self.saveFile)
    self.popMenu_tree.addAction(self.action_save)
    self.tree_copy = QAction("Co&py", self)
    self.popMenu_tree.addAction(self.tree_copy)
    self.tree_clone = QAction("C&lone", self)
    self.popMenu_tree.addAction(self.tree_clone)
    
    self.popMenu_tree.addSeparator()
    
    self.tree_delete = QAction("&Delete", self)
    self.tree_delete.triggered.connect(self.deleteNode)
    self.popMenu_tree.addAction(self.tree_delete)
    self.tree_close = QAction("&Close", self)
    self.tree_close.triggered.connect(self.closeFile)
    self.popMenu_tree.addAction(self.tree_close)
