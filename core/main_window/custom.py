# -*- coding: utf-8 -*-

"""Custom script of Main window."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import (
    Dict,
    Optional,
)
from abc import abstractmethod
from core.QtModules import (
    pyqtSlot,
    Qt,
    QABCMeta,
    QMainWindow,
    QSettings,
    QShortcut,
    QKeySequence,
    QPoint,
    QTreeWidgetItem,
    QHeaderView,
    QStandardPaths,
    QAction,
    QMenu,
    QWebEngineView,
    QSCI_HIGHLIGHTERS,
)
from core.text_editor import TextEditor
from core.info import INFO, ARGUMENTS
from core.translator import TranslatorWidget
from core.data_structure import DataDict
from .logging_handler import XStream
from .Ui_main_window import Ui_MainWindow


class MainWindowBase(QMainWindow, Ui_MainWindow, metaclass=QABCMeta):

    """Base class of main window."""

    @abstractmethod
    def __init__(self):
        super(MainWindowBase, self).__init__()
        self.setupUi(self)

        # Start new window.
        @pyqtSlot()
        def new_main_window():
            XStream.back()
            run = self.__class__()
            run.show()

        self.action_New_Window.triggered.connect(new_main_window)

        # Settings
        self.settings = QSettings("Kmol", "Kmol Editor")

        # Text editor
        self.text_editor = TextEditor(self)
        self.h2_splitter.addWidget(self.text_editor)
        self.html_previewer = QWebEngineView()
        self.html_previewer.setContent(b"", "text/plain")
        self.h2_splitter.addWidget(self.html_previewer)
        self.text_editor.word_changed.connect(self.reload_html_view)
        self.text_editor.word_changed.connect(self.set_not_saved_title)
        self.edge_line_option.toggled.connect(self.text_editor.setEdgeMode)
        self.trailing_blanks_option.toggled.connect(self.text_editor.set_remove_trailing_blanks)

        # Highlighters
        self.highlighter_option.addItems(sorted(QSCI_HIGHLIGHTERS))
        self.highlighter_option.setCurrentText("Markdown")
        self.highlighter_option.currentTextChanged.connect(
            self.text_editor.set_highlighter
        )
        self.highlighter_option.currentTextChanged.connect(self.reload_html_view)

        # Tree widget context menu.
        self.tree_widget.customContextMenuRequested.connect(
            self.tree_context_menu
        )
        self.pop_menu_tree = QMenu(self)
        self.pop_menu_tree.setSeparatorsCollapsible(True)
        self.pop_menu_tree.addAction(self.action_new_project)
        self.pop_menu_tree.addAction(self.action_open)
        self.tree_add = QAction("&Add Node", self)
        self.tree_add.triggered.connect(self.add_node)
        self.tree_add.setShortcutContext(Qt.WindowShortcut)
        self.pop_menu_tree.addAction(self.tree_add)

        self.pop_menu_tree.addSeparator()

        self.tree_path = QAction("Set Path", self)
        self.tree_path.triggered.connect(self.set_path)
        self.pop_menu_tree.addAction(self.tree_path)
        self.tree_refresh = QAction("&Refresh from Path", self)
        self.tree_refresh.triggered.connect(self.refresh_proj)
        self.pop_menu_tree.addAction(self.tree_refresh)
        self.tree_openurl = QAction("&Open from Path", self)
        self.tree_openurl.triggered.connect(self.open_path)
        self.pop_menu_tree.addAction(self.tree_openurl)
        self.action_save.triggered.connect(self.save_proj)
        self.pop_menu_tree.addAction(self.action_save)
        self.tree_copy = QAction("Co&py", self)
        self.tree_copy.triggered.connect(self.copy_node)
        self.pop_menu_tree.addAction(self.tree_copy)
        self.tree_clone = QAction("C&lone", self)
        self.tree_clone.triggered.connect(self.clone_node)
        self.pop_menu_tree.addAction(self.tree_clone)
        self.tree_copy_tree = QAction("Recursive Copy", self)
        self.tree_copy_tree.triggered.connect(self.copy_node_recursive)
        self.pop_menu_tree.addAction(self.tree_copy_tree)
        self.tree_clone_tree = QAction("Recursive Clone", self)
        self.tree_clone_tree.triggered.connect(self.clone_node_recursive)
        self.pop_menu_tree.addAction(self.tree_clone_tree)

        self.pop_menu_tree.addSeparator()

        self.tree_delete = QAction("&Delete", self)
        self.tree_delete.triggered.connect(self.delete_node)
        self.pop_menu_tree.addAction(self.tree_delete)
        self.tree_close = QAction("&Close", self)
        self.tree_close.triggered.connect(self.close_proj)
        self.pop_menu_tree.addAction(self.tree_close)
        self.tree_main.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Console
        self.console.setFont(self.text_editor.font)
        if not ARGUMENTS.debug_mode:
            XStream.stdout().messageWritten.connect(self.append_to_console)
            XStream.stderr().messageWritten.connect(self.append_to_console)
        for info in INFO:
            print(info)
        print('-' * 7)

        # Searching function.
        find_next = QShortcut(QKeySequence("F3"), self)
        find_next.activated.connect(self.find_next_button.click)
        find_previous = QShortcut(QKeySequence("F4"), self)
        find_previous.activated.connect(self.find_previous_button.click)
        find_tab = QShortcut(QKeySequence("Ctrl+F"), self)
        find_tab.activated.connect(self.start_finder)
        find_project = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        find_project.activated.connect(self.find_project_button.click)
        self.find_list_node: Dict[int, QTreeWidgetItem] = {}

        # Replacing function.
        replace = QShortcut(QKeySequence("Ctrl+R"), self)
        replace.activated.connect(self.replace_node_button.click)
        replace_project = QShortcut(QKeySequence("Ctrl+Shift+R"), self)
        replace_project.activated.connect(self.replace_project_button.click)

        # Translator.
        self.panel_widget.addTab(TranslatorWidget(self), "Translator")

        # Node edit function. (Ctrl + ArrowKey)
        new_node = QShortcut(QKeySequence("Ctrl+Ins"), self)
        new_node.activated.connect(self.add_node)
        del_node = QShortcut(QKeySequence("Ctrl+Del"), self)
        del_node.activated.connect(self.delete_node)
        move_up_node = QShortcut(QKeySequence("Ctrl+Up"), self)
        move_up_node.activated.connect(self.move_up_node)
        move_down_node = QShortcut(QKeySequence("Ctrl+Down"), self)
        move_down_node.activated.connect(self.move_down_node)
        move_right_node = QShortcut(QKeySequence("Ctrl+Right"), self)
        move_right_node.activated.connect(self.move_right_node)
        move_left_node = QShortcut(QKeySequence("Ctrl+Left"), self)
        move_left_node.activated.connect(self.move_left_node)

        # Run script button.
        run_sript = QShortcut(QKeySequence("F5"), self)
        run_sript.activated.connect(self.exec_button.click)
        self.macros_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # Data
        self.data = DataDict()
        self.data.not_saved.connect(self.set_not_saved_title)
        self.data.all_saved.connect(self.set_saved_title)
        self.env = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)

    @abstractmethod
    def reload_html_view(self) -> None:
        ...

    @abstractmethod
    def set_not_saved_title(self) -> None:
        ...

    @abstractmethod
    def tree_context_menu(self, point: QPoint) -> None:
        ...

    @abstractmethod
    def add_node(self) -> None:
        ...

    @abstractmethod
    def set_path(self) -> None:
        ...

    @abstractmethod
    def refresh_proj(self) -> None:
        ...

    @abstractmethod
    def open_path(self) -> None:
        ...

    @abstractmethod
    def save_proj(self, index: Optional[int] = None, *, for_all: bool = False) -> None:
        ...

    @abstractmethod
    def copy_node(self) -> None:
        ...

    @abstractmethod
    def clone_node(self) -> None:
        ...

    @abstractmethod
    def copy_node_recursive(self) -> None:
        ...

    @abstractmethod
    def clone_node_recursive(self) -> None:
        ...

    @abstractmethod
    def delete_node(self) -> None:
        ...

    @abstractmethod
    def close_proj(self) -> None:
        ...

    @abstractmethod
    def append_to_console(self, log: str) -> None:
        ...

    @abstractmethod
    def move_up_node(self) -> None:
        ...

    @abstractmethod
    def move_down_node(self) -> None:
        ...

    @abstractmethod
    def move_right_node(self) -> None:
        ...

    @abstractmethod
    def move_left_node(self) -> None:
        ...

    @abstractmethod
    def set_saved_title(self) -> None:
        ...

    @abstractmethod
    def start_finder(self):
        ...
