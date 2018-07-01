# -*- coding: utf-8 -*-

"""Main window of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import Optional
from core.QtModules import (
    pyqtSlot,
    QMainWindow,
    QTextCursor,
    QPoint,
    QTreeItem,
    QTreeRoot,
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
    QSCIHIGHLIGHTERS,
)
from core.info import INFO
from core.text_editor import TextEditor
from core.context_menu import setmenu
from core.loggingHandler import XStream
from core.data_structure import DataDict
from core.xml_parser import getpath, tree_parse, tree_write
from .Ui_mainwindow import Ui_MainWindow


def _get_root(node: QTreeWidgetItem) -> QTreeWidgetItem:
    """Return the parent if exist."""
    item = node.parent()
    return _get_root(item) if item else node


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
        self.h_splitter.setStretchFactor(0, 10)
        self.h_splitter.setStretchFactor(1, 20)
        
        #Highlighters
        self.highlighter_option.addItems(sorted(QSCIHIGHLIGHTERS))
        self.highlighter_option.setCurrentText("Markdown")
        self.highlighter_option.currentTextChanged.connect(
            self.text_editor.setHighlighter
        )
        
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
        self.__actionChange()
        self.popMenu_tree.exec_(self.tree_widget.mapToGlobal(point))
    
    @pyqtSlot()
    def newProj(self):
        """New file."""
        filename, suffix = QFileDialog.getSaveFileName(self,
            "New Project",
            self.env,
            "Kmol Project (*.kmol)"
        )
        if not filename:
            return
        if QFileInfo(filename).suffix() != 'kmol':
            filename += '.kmol'
        self.env = QFileInfo(filename).absolutePath()
        self.tree_main.addTopLevelItem(QTreeRoot(
            QFileInfo(filename).baseName(),
            filename,
            str(self.data.newNum())
        ))
    
    @pyqtSlot()
    def openProj(self):
        """Open file."""
        filenames, ok = QFileDialog.getOpenFileNames(self,
            "Open Projects",
            self.env,
            "Kmol Project (*.kmol)"
        )
        if not ok:
            return
        
        def in_widget(path: str) -> int:
            """Is name in tree widget."""
            for i in range(self.tree_main.topLevelItemCount()):
                if path == self.tree_main.topLevelItem(i).text(1):
                    return i
            return -1
        
        for filename in filenames:
            self.env = QFileInfo(filename).absolutePath()
            index = in_widget(filename)
            if index == -1:
                tree_parse(filename, self.tree_main, self.data)
            else:
                self.tree_main.setCurrentItem(self.tree_main.topLevelItem(index))
        
        self.text_editor.clear()
    
    @pyqtSlot()
    def addNode(self):
        """Add a node at current item."""
        self.tree_main.currentItem().addChild(QTreeItem(
            "New node",
            "",
            str(self.data.newNum())
        ))
    
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
                return
        else:
            filename, ok = QFileDialog.getOpenFileName(self,
                "Open File",
                self.env,
                ';;'.join([
                    "Markdown (*.md)",
                    "HTML (*.html)",
                    "Python script (*.py)",
                    "Text file (*.txt)",
                    "All files (*.*)",
                ])
            )
            if not ok:
                return
        self.env = QFileInfo(filename).absolutePath()
        project_path = QDir(_get_root(item).text(1))
        project_path.cdUp()
        item.setText(1, project_path.relativeFilePath(filename))
    
    @pyqtSlot()
    def saveProj(self, index: Optional[int] = None, *, all: bool = False):
        """Save project and files."""
        if all:
            for row in range(self.tree_main.topLevelItemCount()):
                self.saveProj(row)
            return
        if index is None:
            item = _get_root(self.tree_main.currentItem())
        else:
            item = self.tree_main.topLevelItem(index)
        self.data[int(self.tree_main.currentItem().text(2))] = self.text_editor.text()
        self.__saveFile(item)
        self.data.saveAll()
    
    def __saveFile(self, node: QTreeWidgetItem) -> str:
        """Recursive to all the contents of nodes."""
        data = []
        for i in range(node.childCount()):
            data.append(self.__saveFile(node.child(i)))
        my_content_list = self.data[int(node.text(2))].splitlines()
        for i in range(len(my_content_list)):
            text = my_content_list[i]
            if text.endswith("@others"):
                preffix = text[:-len("@others")]
                my_content_list[i] = '\n\n'.join(preffix + d for d in data)
        my_content_list = '\n'.join(my_content_list)
        path_text = QFileInfo(node.text(1)).fileName()
        if path_text:
            suffix = QFileInfo(path_text).suffix()
            if suffix in ('md', 'html', 'py', 'txt'):
                #Save text files.
                filepath = QDir(QFileInfo(getpath(node)).absolutePath())
                if not filepath.exists():
                    filepath.mkpath('.')
                    print("Create Folder: {}".format(filepath.absolutePath()))
                filename = filepath.filePath(path_text)
                with open(filename, 'w') as f:
                    f.write(my_content_list)
                print("Saved: {}".format(filename))
            elif suffix == 'kmol':
                #Save project.
                tree_write(node.text(1), node, self.data)
        return my_content_list
    
    @pyqtSlot()
    def deleteNode(self):
        """Delete the current item."""
        current_item = self.tree_main.currentItem()
        self.deprecated_list.addItem(QListWidgetItem(
            "{}@{}".format(current_item.text(0), current_item.text(2))
        ))
        item = current_item.parent()
        item.removeChild(current_item)
        self.text_editor.clear()
    
    @pyqtSlot()
    def closeFile(self):
        """Close project node."""
        if not self.data.is_all_saved():
            reply = QMessageBox.question(self,
                "Not saved",
                "Do you went to save the project?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if reply == QMessageBox.Save:
                self.saveProj()
            elif reply == QMessageBox.Cancel:
                return
        
        root = self.tree_main.currentItem()
        
        def clearData(node: QTreeWidgetItem):
            """Delete data from data structure."""
            del self.data[int(node.text(2))]
            for i in range(node.childCount()):
                clearData(node.child(i))
        
        clearData(root)
        self.tree_main.takeTopLevelItem(self.tree_main.indexOfTopLevelItem(root))
        self.text_editor.clear()
    
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
        """Run the script in a new thread."""
        from threading import Thread
        Thread(target=exec, args=(self.text_editor.text(),)).start()
    
    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def on_tree_main_currentItemChanged(self,
        current: QTreeWidgetItem,
        previous: QTreeWidgetItem
    ):
        """Switch node function.
        
        + Auto collapse and expand function.
        + Store the string data.
        """
        self.tree_main.expandItem(current)
        self.tree_main.scrollToItem(current)
        
        if previous:
            self.data[int(previous.text(2))] = self.text_editor.text()
        if current:
            self.text_editor.setText(self.data[int(current.text(2))])
        
        self.__actionChange()
    
    def __actionChange(self):
        item = self.tree_main.currentItem()
        has_item = bool(item)
        is_root = (not item.parent()) if has_item else False
        for action in (
            self.action_open,
            self.action_new_project,
        ):
            action.setVisible(is_root or not has_item)
        self.tree_close.setVisible(has_item and is_root)
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
