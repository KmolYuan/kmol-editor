# -*- coding: utf-8 -*-

"""Main window of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import (
    Dict,
    Hashable,
    Optional,
    Union,
    Any,
)
from os import (
    chdir,
    remove,
    rmdir,
    system as os_system,
)
from os.path import isdir, isfile
import re
from threading import Thread
from subprocess import check_output
from markdown2 import markdown
from core.QtModules import (
    pyqtSlot,
    QTextCursor,
    QPoint,
    QTreeItem,
    QTreeRoot,
    QTreeWidgetItem,
    QListWidgetItem,
    QMessageBox,
    QUrl,
    QFileDialog,
    QStandardPaths,
    QFileInfo,
    QDir,
    QDesktopServices,
    QIcon,
    QPixmap,
    HIGHLIGHTER_SUFFIX,
    HIGHLIGHTER_FILENAME,
)
from core.info import INFO, ARGUMENTS
from core.parsers import (
    getpath,
    parse,
    save_file,
    file_suffix,
    file_icon,
    CODE_STYLE,
    pandoc_markdown,
    SUPPORT_FILE_FORMATS,
)
from .custom import MainWindowBase


def _get_root(node: QTreeWidgetItem) -> QTreeWidgetItem:
    """Return the top-level parent if exist."""
    parent = node.parent()
    return _get_root(parent) if parent else node


def _grand_parent(node: QTreeWidgetItem) -> QTreeWidgetItem:
    """Return the grand parent if exist."""
    parent = node.parent()
    return (parent.parent() if parent else node.treeWidget()) or node.treeWidget()


def _str_between(s: str, front: str, back: str) -> str:
    """Get from parenthesis."""
    return s[(s.find(front) + 1):s.find(back)]


class MainWindow(MainWindowBase):

    """Main window of kmol editor."""

    def __init__(self):
        super(MainWindow, self).__init__()
        if ARGUMENTS.file:
            file_name = ARGUMENTS.file
            root_node = QTreeRoot(QFileInfo(file_name).baseName(), file_name, '')
            self.tree_main.addTopLevelItem(root_node)
            parse(root_node, self.data)
        else:
            prev_open: str = self.settings.value("prev_open", "", type=str)
            for file_name in prev_open.split('#'):
                if not file_name:
                    continue
                root_node = QTreeRoot(QFileInfo(file_name).baseName(), file_name, '')
                self.tree_main.addTopLevelItem(root_node)
                parse(root_node, self.data)

        self.__add_macros()

    def showMaximized(self):
        """Change splitter sizes after maximized."""
        super(MainWindow, self).showMaximized()
        self.h1_splitter.setSizes([20, 2000])
        self.h2_splitter.setSizes([200, 200])
        self.v_splitter.setSizes([300, 300])

    def dragEnterEvent(self, event):
        """Drag file in to our window."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Drop file in to our window."""
        for url in event.mimeData().urls():
            file_name = url.toLocalFile()
            root_node = QTreeRoot(QFileInfo(file_name).baseName(), file_name, '')
            self.tree_main.addTopLevelItem(root_node)
            parse(root_node, self.data)
            self.tree_main.setCurrentItem(root_node)
        self.__add_macros()
        event.acceptProposedAction()

    def closeEvent(self, event):
        """Close event."""
        if not self.__ask_exit():
            event.ignore()
            return

        self.settings.setValue("prev_open", '#'.join({
            self.tree_main.topLevelItem(i).text(1)
            for i in range(self.tree_main.topLevelItemCount())
        }))
        event.accept()

    def __ask_exit(self) -> bool:
        """Ask when exit. Return True if the user want to leave."""
        if self.data.is_all_saved():
            return True

        reply = QMessageBox.question(
            self,
            "Not saved",
            "Do you went to save the project?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        if reply == QMessageBox.Save:
            self.save_proj()
            return True
        elif reply == QMessageBox.Discard:
            return True
        else:
            return False

    @pyqtSlot()
    def close_proj(self):
        """Close project node."""
        if not self.__ask_exit():
            return

        root = self.tree_main.currentItem()
        self.__delete_node_data(root)
        self.tree_main.takeTopLevelItem(self.tree_main.indexOfTopLevelItem(root))
        self.text_editor.clear()
        self.reload_html_viewer()

    def reload_html_viewer(self):
        """Reload HTML content."""
        doc = self.text_editor.text()
        option = self.text_editor.lexer_option
        if option == "HTML":
            self.html_previewer.setHtml(doc)
        elif option == "Markdown":
            self.html_previewer.setHtml(
                f"<style>{CODE_STYLE}</style>" +
                markdown(pandoc_markdown(doc), extras=[
                    'numbering',
                    'tables',
                    'metadata',
                    'fenced-code-blocks',
                    'cuddled-lists',
                    'tag-friendly',
                ])
            )
        else:
            self.html_previewer.setContent(b"", "text/plain")
            self.html_previewer.setVisible(False)
            return

        self.html_previewer.setVisible(True)

    @pyqtSlot()
    def set_not_saved_title(self):
        """Show star sign on window title."""
        if '*' not in self.windowTitle():
            self.setWindowTitle(self.windowTitle() + '*')

    @pyqtSlot()
    def set_saved_title(self):
        """Remove star sign on window title."""
        self.setWindowTitle(self.windowTitle().replace('*', ''))

    @pyqtSlot(str)
    def append_to_console(self, log: str):
        """After inserted the text, move cursor to end."""
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(log)
        self.console.moveCursor(QTextCursor.End)

    @pyqtSlot(QPoint)
    def tree_context_menu(self, point: QPoint):
        """Operations."""
        self.__action_changed()
        self.pop_menu_tree.exec_(self.tree_widget.mapToGlobal(point))

    @pyqtSlot(name='on_action_new_project_triggered')
    def __new_proj(self):
        """New file."""
        file_name, suffix_type = QFileDialog.getSaveFileName(
            self,
            "New Project",
            self.env,
            SUPPORT_FILE_FORMATS
        )
        if not file_name:
            return
        suffix = _str_between(suffix_type, '(', ')').split('*')[-1]
        if QFileInfo(file_name).completeSuffix() != suffix[1:]:
            file_name += suffix
        self.env = QFileInfo(file_name).absolutePath()
        root_node = QTreeRoot(
            QFileInfo(file_name).baseName(),
            file_name,
            str(self.data.new_num())
        )
        suffix_text = file_suffix(file_name)
        if suffix_text == 'md':
            root_node.setIcon(0, file_icon("markdown"))
        elif suffix_text == 'py':
            root_node.setIcon(0, file_icon("python"))
        elif suffix_text == 'html':
            root_node.setIcon(0, file_icon("html"))
        elif suffix_text == 'kmol':
            root_node.setIcon(0, file_icon("kmol"))
        else:
            root_node.setIcon(0, file_icon("txt"))
        self.tree_main.addTopLevelItem(root_node)

    @pyqtSlot(name='on_action_open_triggered')
    def __open_proj(self):
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
            else:
                self.tree_main.setCurrentItem(self.tree_main.topLevelItem(index))

        self.__add_macros()

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
            return
        parse(node, self.data)
        self.tree_main.setCurrentItem(node)
        self.text_editor.setText(self.data[int(node.text(2))])

    @pyqtSlot()
    def open_path(self):
        """Open path of current node."""
        node = self.tree_main.currentItem()
        file_name = getpath(node)
        QDesktopServices.openUrl(QUrl(file_name))
        print("Open: {}".format(file_name))

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
        file_name, ok = QFileDialog.getOpenFileName(
            self,
            "Open File",
            self.env,
            SUPPORT_FILE_FORMATS
        )
        if not ok:
            return
        self.env = QFileInfo(file_name).absolutePath()
        project_path = QDir(_get_root(node).text(1))
        project_path.cdUp()
        node.setText(1, project_path.relativeFilePath(file_name))

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
        if node is None:
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
        item = self.tree_main.currentItem()
        if item is not None:
            self.data[int(item.text(2))] = self.text_editor.text()
        self.text_editor.spell_check_all()

    @pyqtSlot()
    def delete_node(self):
        """Delete the current item."""
        node: Optional[QTreeWidgetItem] = self.tree_main.currentItem()
        if node is None:
            return

        parent = node.parent()
        if parent is None:
            return

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
        self.data.pop(int(node.text(2)))
        for i in range(node.childCount()):
            self.__delete_node_data(node.child(i))

    @pyqtSlot()
    def move_up_node(self):
        """Move up current node."""
        node = self.tree_main.currentItem()
        if node is None:
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
    def move_down_node(self):
        """Move down current node."""
        node = self.tree_main.currentItem()
        if node is None:
            return

        tree_main = node.treeWidget()
        parent = node.parent()
        if parent is not None:
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
    def move_right_node(self):
        """Move right current node."""
        node = self.tree_main.currentItem()
        if node is None:
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
    def move_left_node(self):
        """Move left current node."""
        node = self.tree_main.currentItem()
        if node is None:
            return

        tree_main = node.treeWidget()
        parent = node.parent()
        if parent is None:
            return

        # Must be a sub-node.
        grand_parent = parent.parent()
        if grand_parent is None:
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

        variables: Dict[str, Any] = {
            # Shell functions.
            "is_file": isfile,
            "is_dir": isdir,
            "rm_file": remove,
            "rm_dir": rmdir,
            "run_shell": os_system,
            "run_shell_out": lambda *command: check_output(command).decode('utf-8'),

            # Qt file operation classes.
            'QStandardPaths': QStandardPaths,
            'QFileInfo': QFileInfo,
            'QDir': QDir,
        }
        node = self.tree_main.currentItem()
        if node is not None:
            root = _get_root(node)
            variables['root'] = root
            variables['root_file'] = QFileInfo(root.text(1)).absoluteFilePath()
            variables['root_path'] = QFileInfo(variables['root_file']).absolutePath()
            variables['node_file'] = getpath(node)
            variables['node_path'] = QFileInfo(variables['node_file']).absolutePath()

        def chdir_tree(path: str):
            if QFileInfo(path).isDir():
                chdir(path)
            elif QFileInfo(path).isFile():
                chdir(QFileInfo(path).absolutePath())

        variables['chdir'] = chdir_tree
        thread = Thread(
            target=exec,
            args=(self.data[code] if type(code) == int else code, variables)
        )
        thread.start()

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
            file_name = QFileInfo(path).fileName()
            suffix = QFileInfo(file_name).suffix()
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
                        if file_name in filename_m:
                            self.highlighter_option.setCurrentText(name_m)
                            break
            self.text_editor.setText(self.data[int(current.text(2))])

        self.reload_html_viewer()
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
        for action in [
            self.tree_add,
            self.tree_refresh,
            self.tree_openurl,
            self.action_save,
        ]:
            action.setVisible(has_item)
        for action in [
            self.tree_copy,
            self.tree_clone,
            self.tree_copy_tree,
            self.tree_clone_tree,
            self.tree_path,
            self.tree_delete,
        ]:
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

    def start_finder(self):
        """Start finder when press the hot key."""
        self.panel_widget.setCurrentIndex(1)
        keyword = self.text_editor.selectedText() or self.text_editor.word
        if keyword:
            self.search_bar.setText(keyword)

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
        self.find_list_node.clear()
        node_current = self.tree_main.currentItem()
        if node_current is None:
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

        def find_in_nodes(node: QTreeWidgetItem, last_name: str = ''):
            """Find the word in all nodes."""
            last_name += node.text(0)
            if node.childCount():
                last_name += '->'
            code = int(node.text(2))
            doc = self.data[code]
            pattern = re.compile(text.encode('utf-8'), flags)
            for m in pattern.finditer(doc.encode('utf-8')):
                start, end = m.span()
                item = QListWidgetItem(last_name)
                item.setToolTip(f"{code}:{start}:{end}")
                self.find_list_node[code] = node
                self.find_list.addItem(item)
            for i in range(node.childCount()):
                find_in_nodes(node.child(i), last_name)

        find_in_nodes(root)
        count = self.find_list.count()
        QMessageBox.information(self, "Find in project", f"Found {count} result.")

    @pyqtSlot(
        QListWidgetItem,
        QListWidgetItem,
        name='on_find_list_currentItemChanged')
    @pyqtSlot(QListWidgetItem, name='on_find_list_itemDoubleClicked')
    def __find_results(
        self,
        item: QListWidgetItem,
        _: Optional[QListWidgetItem] = None
    ):
        """Switch to target node."""
        if item is None:
            return

        tool_tips = item.toolTip().split(':')
        code = int(tool_tips[0])
        start = int(tool_tips[1])
        end = int(tool_tips[2])
        self.tree_main.setCurrentItem(self.find_list_node[code])
        self.text_editor.setSelection(start, end)

    @pyqtSlot(name='on_replace_project_button_clicked')
    def __replace_project(self):
        """Replace in project."""
        count = self.find_list.count()
        if count == 0:
            return

        reply = QMessageBox.question(
            self,
            "Replace in project",
            f"Replace all? ({count})"
        )
        if reply != QMessageBox.Yes:
            return

        # TODO: Replace in project.
