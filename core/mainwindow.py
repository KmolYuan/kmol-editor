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
    QShortcut,
    QKeySequence,
    QTextCursor,
    QPoint,
    QTreeItem,
    QTreeRoot,
    QTreeWidgetItem,
    QListWidgetItem,
    QHeaderView,
    QMessageBox,
    QDesktopServices,
    QUrl,
    QFileDialog,
    QStandardPaths,
    QFileInfo,
    QDir,
    QSCIHIGHLIGHTERS,
)
from core.info import INFO
from core.text_editor import TextEditor
from core.context_menu import setmenu
from core.loggingHandler import XStream
from core.data_structure import DataDict
from core.xml_parser import (
    tree_parse,
    saveFile,
)
from .Ui_mainwindow import Ui_MainWindow


def _get_root(node: QTreeWidgetItem) -> QTreeWidgetItem:
    """Return the top-level parent if exist."""
    parent = node.parent()
    return _get_root(parent) if parent else node


def _grand_parent(node: QTreeWidgetItem) -> QTreeWidgetItem:
    """Return the grand parent if exist."""
    parent = node.parent()
    return (parent.parent() if parent else node.treeWidget()) or node.treeWidget()


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
        self.text_editor.currtWordChanged.connect(self.search_bar.setPlaceholderText)
        
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
        
        #Searching function.
        find_next = QShortcut(QKeySequence("F3"), self)
        find_next.activated.connect(self.find_next_button.click)
        find_previous = QShortcut(QKeySequence("F4"), self)
        find_previous.activated.connect(self.find_previous_button.click)
        find_tab = QShortcut(QKeySequence("Ctrl+F"), self)
        find_tab.activated.connect(lambda: self.panel_widget.setCurrentIndex(1))
        find_project = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        find_project.activated.connect(self.find_project_button.click)
        
        #Replacing function.
        replace = QShortcut(QKeySequence("Ctrl+R"), self)
        replace.activated.connect(self.replace_node_button.click)
        replace_project = QShortcut(QKeySequence("Ctrl+Shift+R"), self)
        replace_project.activated.connect(self.replace_project_button.click)
        
        #Node edit function. (Ctrl + ArrowKey)
        #TODO: Undo redo for them.
        moveUpNode = QShortcut(QKeySequence("Ctrl+Up"), self)
        moveUpNode.activated.connect(self.__moveUpNode)
        moveDownNode = QShortcut(QKeySequence("Ctrl+Down"), self)
        moveDownNode.activated.connect(self.__moveDownNode)
        moveRightNode = QShortcut(QKeySequence("Ctrl+Right"), self)
        moveRightNode.activated.connect(self.__moveRightNode)
        moveLeftNode = QShortcut(QKeySequence("Ctrl+Left"), self)
        moveLeftNode.activated.connect(self.__moveLeftNode)
        
        #Run script button.
        run_sript = QShortcut(QKeySequence("F5"), self)
        run_sript.activated.connect(self.exec_button.click)
        
        #Data
        self.data = DataDict()
        self.data.codeAdded.connect(self.__addToPointers)
        self.data.codeChanged.connect(self.__editPointers)
        self.data.codeDeleted.connect(self.__removeFromPointers)
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
        self.__actionChanged()
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
        saveFile(item, self.data)
        self.data.saveAll()
    
    @pyqtSlot()
    def deleteNode(self):
        """Delete the current item."""
        current_item = self.tree_main.currentItem()
        parent = current_item.parent()
        self.tree_main.setCurrentItem(parent)
        parent.removeChild(current_item)
    
    @pyqtSlot(str, str)
    def __addToPointers(self, code: str, doc: str):
        """Add pointer content by code."""
        item = QListWidgetItem(code)
        item.setToolTip(doc[:50])
        self.pointer_list.addItem(item)
    
    @pyqtSlot(str, str)
    def __editPointers(self, code: str, doc: str):
        """Edit pointer content by code."""
        for row in range(self.pointer_list.count()):
            item = self.pointer_list.item(row)
            if code == item.text():
                item.setToolTip(doc[:50])
    
    @pyqtSlot(str)
    def __removeFromPointers(self, code: str):
        """Remove pointer by code."""
        for row in range(self.pointer_list.count()):
            if code == self.pointer_list.item(row).text():
                self.pointer_list.takeItem(row)
                return
    
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
    def __moveUpNode(self):
        """Move up current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        parent = node.parent()
        if parent:
            #Is sub-node.
            index = parent.indexOfChild(node)
            if index == 0:
                return
            parent.removeChild(node)
            parent.insertChild(index - 1, node)
        else:
            #Is root.
            index = self.tree_main.indexOfTopLevelItem(node)
            if index == 0:
                return
            self.tree_main.takeTopLevelItem(index)
            self.tree_main.insertTopLevelItem(index - 1, node)
        self.tree_main.setCurrentItem(node)
    
    @pyqtSlot()
    def __moveDownNode(self):
        """Move down current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        parent = node.parent()
        if parent:
            #Is sub-node.
            index = parent.indexOfChild(node)
            if index == parent.childCount() - 1:
                return
            parent.removeChild(node)
            parent.insertChild(index + 1, node)
        else:
            #Is root.
            index = self.tree_main.indexOfTopLevelItem(node)
            if index == self.tree_main.topLevelItemCount() - 1:
                return
            self.tree_main.takeTopLevelItem(index)
            self.tree_main.insertTopLevelItem(index + 1, node)
        self.tree_main.setCurrentItem(node)
    
    @pyqtSlot()
    def __moveRightNode(self):
        """Move right current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        parent = node.parent()
        if parent:
            #Is sub-node.
            index = parent.indexOfChild(node)
            if index == 0:
                return
            parent.removeChild(node)
            parent.child(index - 1).addChild(node)
        else:
            #Is root.
            index = self.tree_main.indexOfTopLevelItem(node)
            if index == 0:
                return
            self.tree_main.takeTopLevelItem(index)
            self.tree_main.topLevelItem(index - 1).addChild(node)
        self.tree_main.setCurrentItem(node)
    
    @pyqtSlot()
    def __moveLeftNode(self):
        """Move left current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        parent = node.parent()
        if not parent:
            return
        #Must be a sub-node.
        grand_parent = parent.parent()
        if not grand_parent:
            return
        index = grand_parent.indexOfChild(parent)
        parent.removeChild(node)
        grand_parent.insertChild(index + 1, node)
        self.tree_main.setCurrentItem(node)
    
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
        
        self.__actionChanged()
    
    def __actionChanged(self):
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
    
    def __findText(self, forward: bool) -> bool:
        """Find text by options."""
        if not self.search_bar.text():
            self.search_bar.setText(self.search_bar.placeholderText())
        pos = self.text_editor.positionFromLineIndex(
            *self.text_editor.getCursorPosition()
        )
        if not self.text_editor.findFirst(
            self.search_bar.text(),
            self.re_option.isChecked(),
            self.match_case_option.isChecked(),
            self.whole_word_option.isChecked(),
            self.wrap_around.isChecked(),
            forward,
            *self.text_editor.lineIndexFromPosition(pos if forward else pos - 1)
        ):
            QMessageBox.information(self,
                "Text not found.",
                "\"{}\" is not in current document".format(
                    self.search_bar.text()
                )
            )
    
    @pyqtSlot()
    def on_find_next_button_clicked(self):
        """Find to next."""
        self.__findText(True)
    
    @pyqtSlot()
    def on_find_previous_button_clicked(self):
        """Find to previous."""
        self.__findText(False)
    
    @pyqtSlot()
    def on_replace_node_button_clicked(self):
        """Replace current text by replace bar."""
        self.text_editor.replace(self.replace_bar.text())
