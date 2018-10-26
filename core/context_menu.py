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
    self.popMenu_tree.addAction(self.action_new_project)
    self.popMenu_tree.addAction(self.action_open)
    self.popMenu_tree.addAction(self.action_open_from_dir)
    self.tree_add = QAction("&Add Node", self)
    self.tree_add.triggered.connect(self.add_node)
    self.tree_add.setShortcut("Ctrl+I")
    self.tree_add.setShortcutContext(Qt.WindowShortcut)
    self.popMenu_tree.addAction(self.tree_add)

    self.popMenu_tree.addSeparator()

    self.tree_path = QAction("Set &Path", self)
    self.tree_path.triggered.connect(self.set_path)
    self.popMenu_tree.addAction(self.tree_path)
    self.tree_refresh = QAction("&Refresh from Path", self)
    self.tree_refresh.triggered.connect(self.refresh_proj)
    self.popMenu_tree.addAction(self.tree_refresh)
    self.tree_openurl = QAction("&Open from Path", self)
    self.tree_openurl.triggered.connect(self.open_path)
    self.popMenu_tree.addAction(self.tree_openurl)
    self.action_save.triggered.connect(self.save_proj)
    self.popMenu_tree.addAction(self.action_save)
    self.tree_copy = QAction("Co&py", self)
    self.tree_copy.triggered.connect(self.copy_node)
    self.popMenu_tree.addAction(self.tree_copy)
    self.tree_clone = QAction("C&lone", self)
    self.tree_clone.triggered.connect(self.clone_node)
    self.popMenu_tree.addAction(self.tree_clone)
    self.tree_copy_tree = QAction("Recursive Copy", self)
    self.tree_copy_tree.triggered.connect(self.copy_node_recursive)
    self.popMenu_tree.addAction(self.tree_copy_tree)
    self.tree_clone_tree = QAction("Recursive Clone", self)
    self.tree_clone_tree.triggered.connect(self.clone_node_recursive)
    self.popMenu_tree.addAction(self.tree_clone_tree)

    self.popMenu_tree.addSeparator()

    self.tree_delete = QAction("&Delete", self)
    self.tree_delete.triggered.connect(self.delete_node)
    self.popMenu_tree.addAction(self.tree_delete)
    self.tree_close = QAction("&Close", self)
    self.tree_close.triggered.connect(self.close_file)
    self.popMenu_tree.addAction(self.tree_close)
