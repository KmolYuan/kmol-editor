# -*- coding: utf-8 -*-

"""Main window of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2016-2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from core.QtModules import (
    pyqtSlot,
    Qt,
    QMainWindow,
    QTextCursor,
    QPoint,
    QTreeWidgetItem,
    QHeaderView,
)
from core.info import INFO
from core.text_editor import TextEditor
from core.context_menu import setmenu
from core.loggingHandler import XStream
from core.data_structure import DataDict
from .Ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    
    """
    Main window of kmol editor.
    """
    
    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.setupUi(self)
        
        #Text editor
        self.text_editor = TextEditor(self)
        self.h_splitter.insertWidget(1, self.text_editor)
        self.highlighter_option.currentIndexChanged.connect(
            self.text_editor.setHighlighter
        )
        self.h_splitter.setSizes([10, 100])
        
        #Tree widget
        setmenu(self)
        self.tree_main.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        #Console
        XStream.stdout().messageWritten.connect(self.__appendToConsole)
        XStream.stderr().messageWritten.connect(self.__appendToConsole)
        for info in INFO:
            print(info)
        print('-' * 7)
        
        #Data
        self.data = DataDict()
    
    @pyqtSlot(str)
    def __appendToConsole(self, log):
        """After inserted the text, move cursor to end."""
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(log)
        self.console.moveCursor(QTextCursor.End)
    
    @pyqtSlot(QPoint)
    def on_tree_widget_context_menu(self, point: QPoint):
        """TODO: Operations."""
        action = self.popMenu_tree.exec_(self.tree_widget.mapToGlobal(point))
        if action == self.tree_add:
            self.addNode()
    
    def addNode(self):
        """Add a node at current item."""
        current_item = self.tree_main.currentItem()
        item = QTreeWidgetItem(["New node", ""])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        if current_item and current_item.childCount():
            current_item.addChild(item)
        else:
            self.tree_main.addTopLevelItem(item)
