# -*- coding: utf-8 -*-

"""Main window of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import Optional
from core.QtModules import (
    pyqtSlot,
    Qt,
    QMainWindow,
    QTextCursor,
    QPoint,
    QTreeWidgetItem,
    QHeaderView,
    QMessageBox,
    QDesktopServices,
    QUrl,
    QFileDialog,
    QStandardPaths,
    QFileInfo,
    QListWidgetItem,
    QDir,
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
        
        #Start new window.
        @pyqtSlot()
        def newMainWindow():
            XStream.back()
            run = self.__class__()
            run.show()
        
        self.action_New_Window.triggered.connect(newMainWindow)
        
        #Text editor
        self.text_editor = TextEditor(self)
        self.h_splitter.insertWidget(1, self.text_editor)
        self.highlighter_option.currentIndexChanged.connect(
            self.text_editor.setHighlighter
        )
        self.h_splitter.setStretchFactor(0, 10)
        self.h_splitter.setStretchFactor(1, 20)
        
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
        self.env = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
    
    @pyqtSlot(str)
    def __appendToConsole(self, log):
        """After inserted the text, move cursor to end."""
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(log)
        self.console.moveCursor(QTextCursor.End)
    
    @pyqtSlot(QPoint)
    def on_tree_widget_context_menu(self, point: QPoint):
        """Operations."""
        item = self.tree_main.currentItem()
        has_item = bool(item)
        is_root = (not item.parent()) if has_item else False
        for action in (
            self.action_open,
            self.action_new_project,
        ):
            action.setVisible(is_root or not has_item)
        self.tree_close.setVisible(has_item and is_root)
        self.action_save.setVisible(is_root)
        for action in (
            self.tree_add,
            self.tree_path,
        ):
            action.setVisible(has_item)
        for action in (
            self.tree_copy,
            self.tree_clone,
            self.tree_delete,
        ):
            action.setVisible(has_item and not is_root)
        action = self.popMenu_tree.exec_(self.tree_widget.mapToGlobal(point))
    
    @pyqtSlot()
    def newFile(self):
        """New file."""
        filename, suffix = QFileDialog.getSaveFileName(self,
            "New Project",
            self.env,
            "Kmol Project (*.kmol)"
        )
        if not filename:
            return
        self.__addFile(filename + '.kmol')
    
    @pyqtSlot()
    def openFile(self):
        """Open file."""
        filenames, ok = QFileDialog.getOpenFileNames(self,
            "Open Projects",
            self.env,
            "Kmol Project (*.kmol)"
        )
        if not ok:
            return
        for name in filenames:
            self.__addFile(name)
    
    def __addFile(self, path: str):
        """Add a file."""
        self.env = QFileInfo(path).absolutePath()
        item = QTreeWidgetItem([QFileInfo(path).baseName(), path])
        item.setFlags(
            Qt.ItemIsSelectable |
            Qt.ItemIsUserCheckable |
            Qt.ItemIsEnabled
        )
        self.tree_main.addTopLevelItem(item)
    
    @pyqtSlot()
    def addNode(self):
        """Add a node at current item."""
        current_item = self.tree_main.currentItem()
        item = QTreeWidgetItem(["New node", ""])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        current_item.addChild(item)
    
    @pyqtSlot()
    def setPath(self):
        """Set file directory."""
        item = self.tree_main.currentItem()
        if ((not item.parent()) if bool(item) else False):
            filename, suffix = QFileDialog.getSaveFileName(self,
                "Set Project",
                self.env,
                "Kmol Project (*.kmol)"
            )
            if filename:
                filename += '.kmol'
        else:
            filename, ok = QFileDialog.getOpenFileName(self,
                "Open File",
                self.env,
                ';;'.join([
                    "Markdown (*.md)",
                    "HTML (*.html)",
                    "Python script (*.py)",
                    "All files (*.*)",
                ])
            )
        if filename and ok:
            item.setText(1, filename)
    
    @pyqtSlot()
    def saveFile(self, index: Optional[int] = None, *, all: bool = False):
        """Save project and files."""
        if all:
            for row in range(self.tree_main.topLevelItemCount()):
                self.saveFile(row)
            return
        elif index is None:
            item = self.tree_main.currentItem()
        else:
            item = self.tree_main.topLevelItem(index)
        self.__saveFile(item)
    
    def __saveFile(self, node: QTreeWidgetItem) -> Optional[str]:
        """Recursive to all the contents of nodes."""
        data = []
        for i in range(node.childCount()):
            data.append(self.__saveFile(node.child(i)))
        my_content_list = self.data[node.text(0)].splitlines()
        for i in range(len(my_content_list)):
            text = my_content_list[i]
            if text.endswith("@others"):
                preffix = text[:len("@others")]
                my_content_list[i] = ''.join(preffix + d for d in data)
        my_content_list = '\n'.join(my_content_list)
        path_text = node.text(1)
        if path_text:
            
            def getpath(node: QTreeWidgetItem) -> str:
                """Get the path from parent."""
                parent = node.parent()
                if parent:
                    return QFileInfo(QDir(getpath(parent)), node.text(1) + '/').absolutePath()
                else:
                    return QFileInfo(node.text(1)).absoluteFilePath()
            
            current_path = QFileInfo(getpath(node))
            suffix = QFileInfo(path_text).suffix()
            if suffix in ('md', 'html', 'py'):
                #TODO: Save text files.
                print(my_content_list)
                print(current_path.absoluteFilePath())
            elif suffix == 'kmol':
                #TODO: Save project.
                return None
        return my_content_list
    
    @pyqtSlot()
    def deleteNode(self):
        """Delete the current item."""
        current_item = self.tree_main.currentItem()
        self.deprecated_list.addItem(QListWidgetItem(current_item.text(0)))
        item = current_item.parent()
        item.removeChild(current_item)
    
    @pyqtSlot()
    def closeFile(self):
        """Close project node."""
        #TODO: Check is all saved.
        index = self.tree_main.indexOfTopLevelItem(self.tree_main.currentItem())
        self.tree_main.takeTopLevelItem(index)
    
    @pyqtSlot()
    def on_action_about_qt_triggered(self):
        """Qt about."""
        QMessageBox.aboutQt(self)
    
    @pyqtSlot()
    def on_action_about_triggered(self):
        """Kmol editor about."""
        QMessageBox.about(self, "About Kmol Editor", '\n'.join(INFO + ('',
            "Author: " + __author__,
            "Email: " + __email__,
            __copyright__,
            "License: " + __license__,
        )))
    
    @pyqtSlot()
    def on_action_mde_tw_triggered(self):
        """Mde website."""
        QDesktopServices.openUrl(QUrl("http://mde.tw"))
    
    @pyqtSlot()
    def on_exec_button_clicked(self):
        """Execute the script."""
        script = self.text_editor.toPlainText()
        
        def func():
            try:
                exec(script)
            except Exception as e:
                print(e)
        
        func()
    
    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def on_tree_main_currentItemChanged(self,
        current: QTreeWidgetItem,
        previous: QTreeWidgetItem
    ):
        """Switch node function.
        
        + Auto collapse and expand function.
        + TODO: Store the string data.
        """
        self.tree_main.collapseItem(previous)
        self.tree_main.expandItem(current)
        self.tree_main.scrollToItem(current)