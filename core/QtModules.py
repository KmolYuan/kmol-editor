# -*- coding: utf-8 -*-

"""This module contain all the Qt objects we needed.

Customized class will define below.
"""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot,
    QCoreApplication,
    QDir,
    QFileInfo,
    QModelIndex,
    QMutex,
    QMutexLocker,
    QObject,
    QPoint,
    QPointF,
    QRectF,
    QRegExp,
    QSettings,
    QSize,
    QSizeF,
    QStandardPaths,
    QThread,
    QTimer,
    QUrl,
    Qt,
)
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDial,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressDialog,
    QPushButton,
    QShortcut,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QSplashScreen,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTableWidgetSelectionRange,
    QTextEdit,
    QToolTip,
    QTreeWidget,
    QTreeWidgetItem,
    QUndoCommand,
    QUndoGroup,
    QUndoStack,
    QUndoView,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QDesktopServices,
    QFont,
    QFontMetrics,
    QIcon,
    QImage,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextOption,
)
from PyQt5.Qsci import (
    QsciScintilla,
    QsciLexerBash,
    QsciLexerBatch,
    QsciLexerCMake,
    QsciLexerCPP,
    QsciLexerCSharp,
    QsciLexerCSS,
    QsciLexerDiff,
    QsciLexerFortran,
    QsciLexerFortran77,
    QsciLexerHTML,
    QsciLexerJava,
    QsciLexerJavaScript,
    QsciLexerJSON,
    QsciLexerLua,
    QsciLexerMakefile,
    QsciLexerMarkdown,
    QsciLexerMatlab,
    QsciLexerPython,
    QsciLexerSQL,
    QsciLexerTeX,
    QsciLexerXML,
    QsciLexerYAML,
)
from PyQt5.QtCore import qVersion, PYQT_VERSION_STR

__all__ = [
    'pyqtSignal',
    'pyqtSlot',
    'qVersion',
    'PYQT_VERSION_STR',
    'QAbstractItemView',
    'QAction',
    'QApplication',
    'QBrush',
    'QCheckBox',
    'QColor',
    'QColorDialog',
    'QComboBox',
    'QCoreApplication',
    'QCursor',
    'QDesktopServices',
    'QDial',
    'QDialog',
    'QDialogButtonBox',
    'QDir',
    'QDoubleSpinBox',
    'QFileDialog',
    'QFileInfo',
    'QFont',
    'QFontMetrics',
    'QGraphicsScene',
    'QGraphicsView',
    'QHBoxLayout',
    'QHeaderView',
    'QIcon',
    'QImage',
    'QInputDialog',
    'QKeySequence',
    'QLabel',
    'QLineEdit',
    'QListWidget',
    'QListWidgetItem',
    'QMainWindow',
    'QMenu',
    'QMessageBox',
    'QModelIndex',
    'QMutex',
    'QMutexLocker',
    'QObject',
    'QPainter',
    'QPainterPath',
    'QPen',
    'QPixmap',
    'QPoint',
    'QPointF',
    'QPolygonF',
    'QPlainTextEdit',
    'QProgressDialog',
    'QPushButton',
    'QRectF',
    'QRegExp',
    'QSpacerItem',
    'QSettings',
    'QShortcut',
    'QSize',
    'QSizeF',
    'QSizePolicy',
    'QSpinBox',
    'QSplashScreen',
    'QStandardPaths',
    'QSyntaxHighlighter',
    'QTabWidget',
    'QTableWidget',
    'QTableWidgetItem',
    'QTableWidgetSelectionRange',
    'QTextCharFormat',
    'QTextCursor',
    'QTextEdit',
    'QTextOption',
    'QThread',
    'QTimer',
    'QToolTip',
    'QTreeItem',
    'QTreeRoot',
    'QTreeWidget',
    'QTreeWidgetItem',
    'QUndoCommand',
    'QUndoGroup',
    'QUndoStack',
    'QUndoView',
    'QUrl',
    'QVBoxLayout',
    'QWidget',
    'QsciScintilla',
    'QSCIHIGHLIGHTERS',
    'Qt',
    'HIGHLIGHTER_SUFFIX',
    'HIGHLIGHTER_FILENAME',
]


def QTreeItem(name: str, path: str, code: str) -> QTreeWidgetItem:
    """Add a normal tree item.
    
    + Editable
    """
    item = QTreeWidgetItem([name, path, code])
    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
    return item


def QTreeRoot(name: str, path: str, code: str) -> QTreeWidgetItem:
    """Add a root tree item.
    
    + Drag disabled
    """
    item = QTreeWidgetItem([name, path, code])
    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    return item


class QsciLexerCustomPython(QsciLexerPython):
    
    """Custom Python highter."""
    
    def __init__(self, *args):
        super(QsciLexerCustomPython, self).__init__(*args)
        self.setIndentationWarning(QsciLexerPython.Tabs)
    
    def keywords(self, set: int) -> str:
        if set == 2:
            return "self True False"
        else:
            return QsciLexerPython.keywords(self, set)
    
    def setDefaultFont(self, font: QFont):
        super(QsciLexerCustomPython, self).setDefaultFont(font)
        self.setFont(font, QsciLexerPython.Comment)
        self.setFont(font, QsciLexerPython.DoubleQuotedString)
        self.setFont(font, QsciLexerPython.UnclosedString)
        self.setFont(font, QsciLexerPython.SingleQuotedString)


class QsciLexerCustomMarkdown(QsciLexerMarkdown):
    
    """Custom Python highter."""
    
    def __init__(self, *args):
        super(QsciLexerCustomMarkdown, self).__init__(*args)
    
    def setDefaultFont(self, font: QFont):
        super(QsciLexerCustomMarkdown, self).setDefaultFont(font)
        for i in range(22):
            self.setFont(font, i)


QSCIHIGHLIGHTERS = {
    "Bash": QsciLexerBash,
    "Batch": QsciLexerBatch,
    "CMake": QsciLexerCMake,
    "C++": QsciLexerCPP,
    "C#": QsciLexerCSharp,
    "CSS": QsciLexerCSS,
    "Diff": QsciLexerDiff,
    "Fortran": QsciLexerFortran,
    "Fortran77": QsciLexerFortran77,
    "HTML": QsciLexerHTML,
    "Java": QsciLexerJava,
    "JavaScript": QsciLexerJavaScript,
    "JSON": QsciLexerJSON,
    "Lua": QsciLexerLua,
    "Makefile": QsciLexerMakefile,
    "Markdown": QsciLexerCustomMarkdown,
    "Matlab": QsciLexerMatlab,
    "Python": QsciLexerCustomPython,
    "SQL": QsciLexerSQL,
    "Tex": QsciLexerTeX,
    "XML": QsciLexerXML,
    "YAML": QsciLexerYAML,
}

HIGHLIGHTER_SUFFIX = {
    "Bash": {'sh',},
    "Batch": {'bat',},
    "C++": {'c', 'cpp', 'h', 'hpp', 'cxx'},
    "C#": {'cs',},
    "CSS": {'css', 'bib'},
    "Diff": {'diff',},
    "Fortran": {'f90',},
    "Fortran77": {'f77',},
    "HTML": {'html',},
    "Java": {'java',},
    "JavaScript": {'js',},
    "JSON": {'json',},
    "Lua": {'lua',},
    "Markdown": {'md',},
    "Matlab": {'m',},
    "Python": {'py',},
    "SQL": {'sql',},
    "Tex": {'tex',},
    "XML": {'xml',},
    "YAML": {'yml',},
}
HIGHLIGHTER_FILENAME = {
    "CMake": {'CMakeList.txt',},
    "Makefile": {'Makefile', 'Makefile.am', 'Makefile.in', 'Makefile.debug'},
}
