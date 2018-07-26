# -*- coding: utf-8 -*-

"""Main window of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import Optional, Union
import re
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
    QUrl,
    QFileDialog,
    QStandardPaths,
    QFileInfo,
    QDir,
    QDesktopServices,
    QSCIHIGHLIGHTERS,
    HIGHLIGHTER_SUFFIX,
    HIGHLIGHTER_FILENAME,
)
from core.info import INFO, ARGUMENTS
from core.text_editor import TextEditor
from core.context_menu import setmenu
from core.loggingHandler import XStream
from core.data_structure import DataDict
from core.parser import (
    getpath,
    parse,
    save_file,
    SUPPORT_FILE_FORMATS,
)
from .Ui_mainwindow import Ui_MainWindow
__veriables__ = {}


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
        self.text_editor.currentWordChanged.connect(self.search_bar.setPlaceholderText)
        self.edge_line_option.toggled.connect(self.text_editor.setEdgeMode)
        
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
        self.console.setFont(self.text_editor.font)
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
        
        #Splitter
        self.h_splitter.setStretchFactor(0, 10)
        self.h_splitter.setStretchFactor(1, 60)
        self.v_splitter.setStretchFactor(0, 30)
        self.v_splitter.setStretchFactor(1, 10)
        
        #Data
        self.data = DataDict()
        self.env = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        
        for filename in ARGUMENTS.r:
            filename = QFileInfo(filename).canonicalFilePath()
            if not filename:
                return
            root_node = QTreeRoot(QFileInfo(filename).baseName(), filename, '')
            self.tree_main.addTopLevelItem(root_node)
            parse(root_node, self.data)
        self.__add_macros()
    
    def dragEnterEvent(self, event):
        """Drag file in to our window."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Drop file in to our window."""
        filename = event.mimeData().urls()[-1].toLocalFile()
        root_node = QTreeRoot(QFileInfo(filename).baseName(), filename, '')
        self.tree_main.addTopLevelItem(root_node)
        parse(root_node, self.data)
        self.__add_macros()
        event.acceptProposedAction()
    
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
            SUPPORT_FILE_FORMATS
        )
        if not filename:
            return
        if suffix != "All files (*.*)":
            suffix = suffix.split('.')[-1][:-1]
            if QFileInfo(filename).suffix() != suffix:
                filename += '.' + suffix
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
            SUPPORT_FILE_FORMATS
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
                root_node = QTreeRoot(QFileInfo(filename).baseName(), filename, '')
                self.tree_main.addTopLevelItem(root_node)
                parse(root_node, self.data)
                self.__add_macros()
            else:
                self.tree_main.setCurrentItem(self.tree_main.topLevelItem(index))
        
        self.text_editor.clear()
    
    @pyqtSlot()
    def refreshProj(self):
        """Re-parse the file node."""
        node = self.tree_main.currentItem()
        if not node.text(1):
            QMessageBox.warning(self,
                "No path",
                "Can only refresh from valid path."
            )
        parse(node, self.data)
        self.text_editor.setText(self.data[int(node.text(2))])
    
    @pyqtSlot()
    def openPath(self):
        """Open path of current node."""
        node = self.tree_main.currentItem()
        filename = getpath(node)
        QDesktopServices.openUrl(QUrl(filename))
        print("Open: {}".format(filename))
    
    @pyqtSlot()
    def addNode(self):
        """Add a node at current item."""
        node = self.tree_main.currentItem()
        new_node = QTreeItem(
            "New node",
            "",
            str(self.data.newNum())
        )
        if node.childCount() or node.text(1):
            node.addChild(new_node)
            return
        parent = node.parent()
        if parent:
            parent.insertChild(parent.indexOfChild(node) + 1, new_node)
            return
        self.tree_main.indexOfTopLevelItem(
            self.tree_main.indexOfTopLevelItem(node) + 1,
            new_node
        )
    
    @pyqtSlot()
    def setPath(self):
        """Set file directory."""
        node = self.tree_main.currentItem()
        filename, ok = QFileDialog.getOpenFileName(self,
            "Open File",
            self.env,
            SUPPORT_FILE_FORMATS
        )
        if not ok:
            return
        self.env = QFileInfo(filename).absolutePath()
        project_path = QDir(_get_root(node).text(1))
        project_path.cdUp()
        node.setText(1, project_path.relativeFilePath(filename))
    
    @pyqtSlot()
    def copyNode(self):
        """Copy current node."""
        node_origin = self.tree_main.currentItem()
        parent = node_origin.parent()
        node = node_origin.clone()
        node.takeChildren()
        code = self.data.newNum()
        self.data[code] = self.data[int(node.text(2))]
        node.setText(2, str(code))
        parent.insertChild(parent.indexOfChild(node_origin) + 1, node)
    
    @pyqtSlot()
    def cloneNode(self):
        """Copy current node with same pointer."""
        node_origin = self.tree_main.currentItem()
        parent = node_origin.parent()
        node = node_origin.clone()
        node.takeChildren()
        parent.insertChild(parent.indexOfChild(node_origin) + 1, node)
    
    @pyqtSlot()
    def copyNodeRecursive(self):
        """Copy current node and its subnodes."""
        node_origin = self.tree_main.currentItem()
        parent = node_origin.parent()
        node = node_origin.clone()
        
        def new_pointer(node: QTreeWidgetItem):
            """Give a new pointer code for node."""
            code = self.data.newNum()
            self.data[code] = self.data[int(node.text(2))]
            node.setText(2, str(code))
            for i in range(node.childCount()):
                new_pointer(node.child(i))
        
        new_pointer(node)
        parent.insertChild(parent.indexOfChild(node_origin) + 1, node)
    
    @pyqtSlot()
    def cloneNodeRecursive(self):
        """Copy current node and its subnodes with same pointer."""
        node_origin = self.tree_main.currentItem()
        parent = node_origin.parent()
        parent.insertChild(parent.indexOfChild(node_origin) + 1, node_origin.clone())
    
    @pyqtSlot()
    def saveProj(self, index: Optional[int] = None, *, all: bool = False):
        """Save project and files."""
        if all:
            for row in range(self.tree_main.topLevelItemCount()):
                self.saveProj(row)
            return
        node = self.tree_main.currentItem()
        if not node:
            return
        if index is None:
            root = _get_root(node)
        else:
            root = self.tree_main.topLevelItem(index)
        self.__save_current()
        save_file(root, self.data)
        self.data.saveAll()
    
    def __save_current(self):
        """Save the current text of editor."""
        self.data[int(self.tree_main.currentItem().text(2))] = self.text_editor.text()
    
    @pyqtSlot()
    def on_action_save_all_triggered(self):
        """Save all project."""
        self.saveProj(all = True)
    
    @pyqtSlot()
    def deleteNode(self):
        """Delete the current item."""
        node = self.tree_main.currentItem()
        parent = node.parent()
        self.tree_main.setCurrentItem(parent)
        self.__delete_node_data(node)
        parent.removeChild(node)
    
    def __delete_node_data(self, node: QTreeWidgetItem):
        """Delete data from data structure."""
        name = node.text(0)
        if name.startswith('@'):
            for action in self.macros_toolbar.actions():
                if action.text() == name[1:]:
                    self.macros_toolbar.removeAction(action)
        del self.data[int(node.text(2))]
        for i in range(node.childCount()):
            self.__delete_node_data(node.child(i))
    
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
        self.__delete_node_data(root)
        self.tree_main.takeTopLevelItem(self.tree_main.indexOfTopLevelItem(root))
        self.text_editor.clear()
    
    @pyqtSlot()
    def __moveUpNode(self):
        """Move up current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        tree_main = node.treeWidget()
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
            index = tree_main.indexOfTopLevelItem(node)
            if index == 0:
                return
            tree_main.takeTopLevelItem(index)
            tree_main.insertTopLevelItem(index - 1, node)
        tree_main.setCurrentItem(node)
        self.__root_unsaved()
    
    @pyqtSlot()
    def __moveDownNode(self):
        """Move down current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        tree_main = node.treeWidget()
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
            index = tree_main.indexOfTopLevelItem(node)
            if index == tree_main.topLevelItemCount() - 1:
                return
            tree_main.takeTopLevelItem(index)
            tree_main.insertTopLevelItem(index + 1, node)
        tree_main.setCurrentItem(node)
        self.__root_unsaved()
    
    @pyqtSlot()
    def __moveRightNode(self):
        """Move right current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        tree_main = node.treeWidget()
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
            index = tree_main.indexOfTopLevelItem(node)
            if index == 0:
                return
            tree_main.takeTopLevelItem(index)
            tree_main.topLevelItem(index - 1).addChild(node)
        tree_main.setCurrentItem(node)
        self.__root_unsaved()
    
    @pyqtSlot()
    def __moveLeftNode(self):
        """Move left current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        tree_main = node.treeWidget()
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
        tree_main.setCurrentItem(node)
        self.__root_unsaved()
    
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
        """Run the script from current text editor."""
        self.__exec_script(self.text_editor.text())
    
    def __exec_script(self, code: Union[int, str]):
        """Run a script in a new thread."""
        self.__save_current()
        
        def run(script: str):
            __veriables__.clear()
            node = self.tree_main.currentItem()
            __veriables__['node'] = node
            node_path = ''
            if node:
                root = _get_root(node)
                __veriables__['root'] = root
                root_path = QFileInfo(root.text(1)).absoluteFilePath()
                __veriables__['root_path'] = root_path
                node_path = getpath(node)
                __veriables__['node_path'] = node_path
            
            def chdir(path: str):
                from os import chdir
                if QFileInfo(path).isDir():
                    chdir(path)
                elif QFileInfo(path).isFile():
                    chdir(QFileInfo(path).absolutePath())
            
            __veriables__['chdir'] = chdir
            exec(script)
        
        from threading import Thread
        Thread(target=run, args=(self.data[code] if type(code) == int else code,)).start()
    
    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def on_tree_main_currentItemChanged(self,
        current: QTreeWidgetItem,
        previous: QTreeWidgetItem
    ):
        """Switch node function.
        
        + Auto collapse and expand function.
        + Important: Store the string data.
        """
        if self.auto_expand_option.isChecked():
            self.tree_main.expandItem(current)
        self.tree_main.scrollToItem(current)
        
        if previous:
            self.data[int(previous.text(2))] = self.text_editor.text()
        if current:
            #Auto highlight.
            path = current.text(1)
            filename = QFileInfo(path).fileName()
            suffix = QFileInfo(filename).suffix()
            if current.text(0).startswith('@'):
                self.highlighter_option.setCurrentText("Python")
            else:
                self.highlighter_option.setCurrentText("Markdown")
            if path:
                for name_m, suffix_m in HIGHLIGHTER_SUFFIX.items():
                    if suffix in suffix_m:
                        self.highlighter_option.setCurrentText(name_m)
                        break
                else:
                    for name_m, filename_m in HIGHLIGHTER_FILENAME.items():
                        if filename in filename_m:
                            self.highlighter_option.setCurrentText(name_m)
                            break
            self.text_editor.setText(self.data[int(current.text(2))])
        
        self.__actionChanged()
    
    @pyqtSlot(QTreeWidgetItem, int)
    def on_tree_main_itemChanged(self, node: QTreeWidgetItem, column: int):
        """Mark edited node as unsaved."""
        name = node.text(0)
        code = int(node.text(2))
        if name.startswith('@'):
            self.__add_macro(name[1:], code)
        self.__root_unsaved()
    
    def __root_unsaved(self):
        """Let tree to re-save."""
        node = self.tree_main.currentItem()
        if node:
            self.data.setSaved(int(_get_root(node).text(2)), False)
    
    def __actionChanged(self):
        node = self.tree_main.currentItem()
        has_item = bool(node)
        is_root = (not node.parent()) if has_item else False
        for action in (
            self.action_open,
            self.action_new_project,
        ):
            action.setVisible(is_root or not has_item)
        self.tree_close.setVisible(has_item and is_root)
        for action in (
            self.tree_add,
            self.tree_refresh,
            self.tree_openurl,
            self.action_save,
        ):
            action.setVisible(has_item)
        for action in (
            self.tree_copy,
            self.tree_clone,
            self.tree_copy_tree,
            self.tree_clone_tree,
            self.tree_path,
            self.tree_delete,
        ):
            action.setVisible(has_item and not is_root)
    
    def __add_macros(self):
        """Add macro buttons from data structure."""
        for name, code in self.data.macros():
            self.__add_macro(name, code)
    
    def __add_macro(self, name: str, code: int):
        """Add macro button."""
        for action in self.macros_toolbar.actions():
            if action.text() == name:
                break
        else:
            action = self.macros_toolbar.addAction(name)
            action.triggered.connect(lambda: self.__exec_script(code))
    
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
        self.text_editor.findNext()
    
    @pyqtSlot()
    def on_find_project_button_clicked(self):
        """Find in all project."""
        self.find_list.clear()
        node = self.tree_main.currentItem()
        if not node:
            return
        root = _get_root(node)
        if not self.search_bar.text():
            self.search_bar.setText(self.search_bar.placeholderText())
        text = self.search_bar.text()
        flags = re.MULTILINE
        if not self.re_option.isChecked():
            text = re.escape(text)
        if self.whole_word_option.isChecked():
            text = r'\b' + text + r'\b'
        if not self.match_case_option.isChecked():
            flags |= re.IGNORECASE
        
        def add_find_result(code: int, lastname: str, start: int, end: int):
            """Add result to list."""
            item = QListWidgetItem("{}: [{}, {}]".format(code, start, end))
            item.setToolTip(lastname)
            self.find_list.addItem(item)
        
        def find_in_nodes(node: QTreeWidgetItem, lastname: str = ''):
            """Find the word in all nodes."""
            lastname += node.text(0)
            if node.childCount():
                lastname += '->'
            code = int(node.text(2))
            doc = self.data[code]
            pattern = re.compile(text, flags)
            for m in pattern.finditer(doc):
                add_find_result(code, lastname, *m.span())
            for i in range(node.childCount()):
                find_in_nodes(node.child(i), lastname)
        
        find_in_nodes(root)
    
    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def on_find_list_currentItemChanged(self,
        current: QListWidgetItem,
        previous: QListWidgetItem
    ):
        """TODO: Switch to target node."""
        raise NotImplementedError
