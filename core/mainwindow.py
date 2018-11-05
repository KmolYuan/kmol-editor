# -*- coding: utf-8 -*-

"""Main window of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import Hashable, Optional, Union
import re
from core.QtModules import (
    pyqtSlot,
    Qt,
    QApplication,
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
    QIcon,
    QPixmap,
    QAction,
    QMenu,
    QSCIHIGHLIGHTERS,
    HIGHLIGHTER_SUFFIX,
    HIGHLIGHTER_FILENAME,
)
from core.info import INFO, ARGUMENTS
from core.text_editor import TextEditor
from core.loggingHandler import XStream
from core.data_structure import DataDict
from core.parsers import (
    getpath,
    parse,
    save_file,
    SUPPORT_FILE_FORMATS,
)
from .Ui_mainwindow import Ui_MainWindow
__variables__ = {}


def _get_root(node: QTreeWidgetItem) -> QTreeWidgetItem:
    """Return the top-level parent if exist."""
    parent = node.parent()
    return _get_root(parent) if parent else node


def _grand_parent(node: QTreeWidgetItem) -> QTreeWidgetItem:
    """Return the grand parent if exist."""
    parent = node.parent()
    return (parent.parent() if parent else node.treeWidget()) or node.treeWidget()


class MainWindow(QMainWindow, Ui_MainWindow):

    """Main window of kmol editor."""

    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.setupUi(self)

        # Start new window.
        @pyqtSlot()
        def new_main_window():
            XStream.back()
            run = self.__class__()
            run.show()

        self.action_New_Window.triggered.connect(new_main_window)

        # Text editor
        self.text_editor = TextEditor(self)
        self.h_splitter.addWidget(self.text_editor)
        self.text_editor.word_changed.connect(self.__set_not_saved_title)
        self.edge_line_option.toggled.connect(self.text_editor.setEdgeMode)
        self.trailing_blanks_option.toggled.connect(self.text_editor.set_remove_trailing_blanks)

        # Highlighters
        self.highlighter_option.addItems(sorted(QSCIHIGHLIGHTERS))
        self.highlighter_option.setCurrentText("Markdown")
        self.highlighter_option.currentTextChanged.connect(
            self.text_editor.set_highlighter
        )

        # Tree widget
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
        self.tree_main.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Console
        self.console.setFont(self.text_editor.font)
        if not ARGUMENTS.debug_mode:
            XStream.stdout().messageWritten.connect(self.__append_to_console)
            XStream.stderr().messageWritten.connect(self.__append_to_console)
        for info in INFO:
            print(info)
        print('-' * 7)

        # Searching function.
        find_next = QShortcut(QKeySequence("F3"), self)
        find_next.activated.connect(self.find_next_button.click)
        find_previous = QShortcut(QKeySequence("F4"), self)
        find_previous.activated.connect(self.find_previous_button.click)
        find_tab = QShortcut(QKeySequence("Ctrl+F"), self)
        find_tab.activated.connect(lambda: self.panel_widget.setCurrentIndex(1))
        find_project = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        find_project.activated.connect(self.find_project_button.click)

        # Replacing function.
        replace = QShortcut(QKeySequence("Ctrl+R"), self)
        replace.activated.connect(self.replace_node_button.click)
        replace_project = QShortcut(QKeySequence("Ctrl+Shift+R"), self)
        replace_project.activated.connect(self.replace_project_button.click)

        # Node edit function. (Ctrl + ArrowKey)
        move_up_node = QShortcut(QKeySequence("Ctrl+Up"), self)
        move_up_node.activated.connect(self.__move_up_node)
        move_down_node = QShortcut(QKeySequence("Ctrl+Down"), self)
        move_down_node.activated.connect(self.__move_down_node)
        move_right_node = QShortcut(QKeySequence("Ctrl+Right"), self)
        move_right_node.activated.connect(self.__move_right_node)
        move_left_node = QShortcut(QKeySequence("Ctrl+Left"), self)
        move_left_node.activated.connect(self.__move_left_node)

        # Run script button.
        run_sript = QShortcut(QKeySequence("F5"), self)
        run_sript.activated.connect(self.exec_button.click)
        self.macros_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # Splitter
        self.h_splitter.setStretchFactor(0, 10)
        self.h_splitter.setStretchFactor(1, 60)
        self.v_splitter.setStretchFactor(0, 30)
        self.v_splitter.setStretchFactor(1, 10)

        # Data
        self.data = DataDict()
        self.data.not_saved.connect(self.__set_not_saved_title)
        self.data.all_saved.connect(self.__set_saved_title)
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
        self.tree_main.setCurrentItem(root_node)
        self.__add_macros()
        event.acceptProposedAction()

    @pyqtSlot()
    def __set_not_saved_title(self):
        """Show star sign on window title."""
        if '*' not in self.windowTitle():
            self.setWindowTitle(self.windowTitle() + '*')

    @pyqtSlot()
    def __set_saved_title(self):
        """Remove star sign on window title."""
        self.setWindowTitle(self.windowTitle().replace('*', ''))

    @pyqtSlot(str)
    def __append_to_console(self, log):
        """After inserted the text, move cursor to end."""
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(log)
        self.console.moveCursor(QTextCursor.End)

    @pyqtSlot(QPoint)
    def on_tree_widget_context_menu(self, point: QPoint):
        """Operations."""
        self.__action_changed()
        self.popMenu_tree.exec_(self.tree_widget.mapToGlobal(point))

    @pyqtSlot(name='on_action_new_project_triggered')
    def new_proj(self):
        """New file."""
        filename, suffix = QFileDialog.getSaveFileName(
            self,
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
            str(self.data.new_num())
        ))

    @pyqtSlot(name='on_action_open_triggered')
    def open_proj(self):
        """Open file."""
        file_names, ok = QFileDialog.getOpenFileNames(
            self,
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

        for file_name in file_names:
            self.env = QFileInfo(file_name).absolutePath()
            index = in_widget(file_name)
            if index == -1:
                root_node = QTreeRoot(QFileInfo(file_name).baseName(), file_name, '')
                self.tree_main.addTopLevelItem(root_node)
                parse(root_node, self.data)
                self.tree_main.setCurrentItem(root_node)
                self.__add_macros()
            else:
                self.tree_main.setCurrentItem(self.tree_main.topLevelItem(index))

        self.text_editor.clear()

    @pyqtSlot(name='on_action_open_from_dir_triggered')
    def open_dir(self):
        """TODO: Open dir as project."""

    @pyqtSlot()
    def refresh_proj(self):
        """Re-parse the file node."""
        node = self.tree_main.currentItem()
        if not node.text(1):
            QMessageBox.warning(
                self,
                "No path",
                "Can only refresh from valid path."
            )
        parse(node, self.data)
        self.tree_main.setCurrentItem(node)
        self.text_editor.setText(self.data[int(node.text(2))])

    @pyqtSlot()
    def open_path(self):
        """Open path of current node."""
        node = self.tree_main.currentItem()
        filename = getpath(node)
        QDesktopServices.openUrl(QUrl(filename))
        print("Open: {}".format(filename))

    @pyqtSlot()
    def add_node(self):
        """Add a node at current item."""
        node = self.tree_main.currentItem()
        new_node = QTreeItem(
            "New node",
            "",
            str(self.data.new_num())
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
    def set_path(self):
        """Set file directory."""
        node = self.tree_main.currentItem()
        filename, ok = QFileDialog.getOpenFileName(
            self,
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
    def copy_node(self):
        """Copy current node."""
        node_origin = self.tree_main.currentItem()
        parent = node_origin.parent()
        node = node_origin.clone()
        node.takeChildren()
        code = self.data.new_num()
        self.data[code] = self.data[int(node.text(2))]
        node.setText(2, str(code))
        parent.insertChild(parent.indexOfChild(node_origin) + 1, node)

    @pyqtSlot()
    def clone_node(self):
        """Copy current node with same pointer."""
        node_origin = self.tree_main.currentItem()
        parent = node_origin.parent()
        node = node_origin.clone()
        node.takeChildren()
        parent.insertChild(parent.indexOfChild(node_origin) + 1, node)

    @pyqtSlot()
    def copy_node_recursive(self):
        """Copy current node and its sub-nodes."""
        node_origin = self.tree_main.currentItem()
        parent = node_origin.parent()
        node_origin_copy = node_origin.clone()

        def new_pointer(node: QTreeWidgetItem):
            """Give a new pointer code for node."""
            code = self.data.new_num()
            self.data[code] = self.data[int(node.text(2))]
            node.setText(2, str(code))
            for i in range(node.childCount()):
                new_pointer(node.child(i))

        new_pointer(node_origin_copy)
        parent.insertChild(parent.indexOfChild(node_origin) + 1, node_origin_copy)

    @pyqtSlot()
    def clone_node_recursive(self):
        """Copy current node and its sub-nodes with same pointer."""
        node_origin = self.tree_main.currentItem()
        parent = node_origin.parent()
        parent.insertChild(parent.indexOfChild(node_origin) + 1, node_origin.clone())

    @pyqtSlot()
    def save_proj(self, index: Optional[int] = None, *, for_all: bool = False):
        """Save project and files."""
        if for_all:
            for row in range(self.tree_main.topLevelItemCount()):
                self.save_proj(row)
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
        self.data.save_all()

    def __save_current(self):
        """Save the current text of editor."""
        self.text_editor.remove_trailing_blanks()
        self.data[int(self.tree_main.currentItem().text(2))] = self.text_editor.text()

    @pyqtSlot()
    def delete_node(self):
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
    def close_file(self):
        """Close project node."""
        if not self.data.is_all_saved():
            reply = QMessageBox.question(
                self,
                "Not saved",
                "Do you went to save the project?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if reply == QMessageBox.Save:
                self.save_proj()
            elif reply == QMessageBox.Cancel:
                return

        root = self.tree_main.currentItem()
        self.__delete_node_data(root)
        self.tree_main.takeTopLevelItem(self.tree_main.indexOfTopLevelItem(root))
        self.text_editor.clear()

    @pyqtSlot()
    def __move_up_node(self):
        """Move up current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        tree_main = node.treeWidget()
        parent = node.parent()
        if parent:
            # Is sub-node.
            index = parent.indexOfChild(node)
            if index == 0:
                return
            parent.removeChild(node)
            parent.insertChild(index - 1, node)
        else:
            # Is root.
            index = tree_main.indexOfTopLevelItem(node)
            if index == 0:
                return
            tree_main.takeTopLevelItem(index)
            tree_main.insertTopLevelItem(index - 1, node)
        tree_main.setCurrentItem(node)
        self.__root_unsaved()

    @pyqtSlot()
    def __move_down_node(self):
        """Move down current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        tree_main = node.treeWidget()
        parent = node.parent()
        if parent:
            # Is sub-node.
            index = parent.indexOfChild(node)
            if index == parent.childCount() - 1:
                return
            parent.removeChild(node)
            parent.insertChild(index + 1, node)
        else:
            # Is root.
            index = tree_main.indexOfTopLevelItem(node)
            if index == tree_main.topLevelItemCount() - 1:
                return
            tree_main.takeTopLevelItem(index)
            tree_main.insertTopLevelItem(index + 1, node)
        tree_main.setCurrentItem(node)
        self.__root_unsaved()

    @pyqtSlot()
    def __move_right_node(self):
        """Move right current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        tree_main = node.treeWidget()
        parent = node.parent()
        if parent:
            # Is sub-node.
            index = parent.indexOfChild(node)
            if index == 0:
                return
            parent.removeChild(node)
            parent.child(index - 1).addChild(node)
        else:
            # Is root.
            index = tree_main.indexOfTopLevelItem(node)
            if index == 0:
                return
            tree_main.takeTopLevelItem(index)
            tree_main.topLevelItem(index - 1).addChild(node)
        tree_main.setCurrentItem(node)
        self.__root_unsaved()

    @pyqtSlot()
    def __move_left_node(self):
        """Move left current node."""
        node = self.tree_main.currentItem()
        if not node:
            return
        tree_main = node.treeWidget()
        parent = node.parent()
        if not parent:
            return
        # Must be a sub-node.
        grand_parent = parent.parent()
        if not grand_parent:
            return
        index = grand_parent.indexOfChild(parent)
        parent.removeChild(node)
        grand_parent.insertChild(index + 1, node)
        tree_main.setCurrentItem(node)
        self.__root_unsaved()

    @pyqtSlot(name='on_action_about_qt_triggered')
    def __about_qt(self):
        """Qt about."""
        QMessageBox.aboutQt(self)

    @pyqtSlot(name='on_action_about_triggered')
    def __about(self):
        """Kmol editor about."""
        QMessageBox.about(self, "About Kmol Editor", '\n'.join(INFO + (
            '',
            "Author: " + __author__,
            "Email: " + __email__,
            __copyright__,
            "License: " + __license__,
        )))

    @pyqtSlot(name='on_action_mde_tw_triggered')
    def __mde_tw(self):
        """Mde website."""
        QDesktopServices.openUrl(QUrl("http://mde.tw"))

    @pyqtSlot(name='on_exec_button_clicked')
    def __exec(self):
        """Run the script from current text editor."""
        self.__exec_script(self.text_editor.text())

    def __exec_script(self, code: Union[int, str]):
        """Run a script in a new thread."""
        self.__save_current()

        def run(script: str):
            __variables__.clear()
            node = self.tree_main.currentItem()
            __variables__['node'] = node
            if node:
                root = _get_root(node)
                __variables__['root'] = root
                root_path = QFileInfo(root.text(1)).absoluteFilePath()
                __variables__['root_path'] = root_path
                node_path = getpath(node)
                __variables__['node_path'] = node_path

            def chdir(path: str):
                from os import chdir
                if QFileInfo(path).isDir():
                    chdir(path)
                elif QFileInfo(path).isFile():
                    chdir(QFileInfo(path).absolutePath())

            __variables__['chdir'] = chdir
            exec(script)

        from threading import Thread
        Thread(target=run, args=(self.data[code] if type(code) == int else code,)).start()

    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem, name='on_tree_main_currentItemChanged')
    def __switch_data(
        self,
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
            # Auto highlight.
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

        self.__action_changed()

    @pyqtSlot(QTreeWidgetItem, int, name='on_tree_main_itemChanged')
    def __reload_nodes(self, node: QTreeWidgetItem, _: int):
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
            self.data.set_saved(int(_get_root(node).text(2)), False)

    def __action_changed(self):
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

    def __add_macro(self, name: str, code: Union[int, Hashable]):
        """Add macro button."""
        for action in self.macros_toolbar.actions():
            if action.text() == name:
                break
        else:
            action = self.macros_toolbar.addAction(QIcon(QPixmap(":icons/python.png")), name)
            action.triggered.connect(lambda: self.__exec_script(code))

    def __find_text(self, forward: bool):
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
            QMessageBox.information(
                self,
                "Text not found.",
                "\"{}\" is not in current document".format(
                    self.search_bar.text()
                )
            )

    @pyqtSlot(name='on_find_next_button_clicked')
    def __find_next(self):
        """Find to next."""
        self.__find_text(True)

    @pyqtSlot(name='on_find_previous_button_clicked')
    def __find_previous(self):
        """Find to previous."""
        self.__find_text(False)

    @pyqtSlot(name='on_replace_node_button_clicked')
    def __replace(self):
        """Replace current text by replace bar."""
        self.text_editor.replace(self.replace_bar.text())
        self.text_editor.findNext()

    @pyqtSlot(name='on_find_project_button_clicked')
    def __find_project(self):
        """Find in all project."""
        self.find_list.clear()
        node_current = self.tree_main.currentItem()
        if not node_current:
            return
        root = _get_root(node_current)
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

        def add_find_result(code: int, last_name: str, start: int, end: int):
            """Add result to list."""
            item = QListWidgetItem("{}: [{}, {}]".format(code, start, end))
            item.setToolTip(last_name)
            self.find_list.addItem(item)

        def find_in_nodes(node: QTreeWidgetItem, last_name: str = ''):
            """Find the word in all nodes."""
            last_name += node.text(0)
            if node.childCount():
                last_name += '->'
            code = int(node.text(2))
            doc = self.data[code]
            pattern = re.compile(text, flags)
            for m in pattern.finditer(doc):
                add_find_result(code, last_name, *m.span())
            for i in range(node.childCount()):
                find_in_nodes(node.child(i), last_name)

        find_in_nodes(root)

    @pyqtSlot(
        QListWidgetItem,
        QListWidgetItem,
        name='on_find_list_currentItemChanged')
    def __find_results(self, *_: QListWidgetItem):
        """TODO: Switch to target node."""
        print("Not Implemented.")
