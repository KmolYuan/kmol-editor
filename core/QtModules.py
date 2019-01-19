# -*- coding: utf-8 -*-

"""This module contain all the Qt objects we needed.

Customized class will define below.
"""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import Type
from PyQt5.QtCore import qVersion, PYQT_VERSION_STR
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.Qsci import (
    QSCINTILLA_VERSION_STR,
    QsciScintilla,
    QsciLexer,
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
    'QScrollBar',
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
    'QTextBrowser',
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
    'QSCINTILLA_VERSION_STR',
    'HIGHLIGHTER_SUFFIX',
    'HIGHLIGHTER_FILENAME',
]


def QTreeItem(name: str, path: str, code: str) -> QTreeWidgetItem:
    """Add a normal tree item. (editable)"""
    item = QTreeWidgetItem([name, path, code])
    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
    return item


def QTreeRoot(name: str, path: str, code: str) -> QTreeWidgetItem:
    """Add a root tree item. (drag disabled)"""
    item = QTreeWidgetItem([name, path, code])
    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    return item


def _default_font_override(lexer: Type[QsciLexer]) -> Type[QsciLexer]:
    """Decorator to add default font method."""

    class NewLexer(lexer):

        __doc__ = lexer.__doc__

        def __init__(self, *args):
            super(NewLexer, self).__init__(*args)

        def setDefaultFont(self, font: QFont):
            super(NewLexer, self).setDefaultFont(font)
            m = 0
            for v in lexer.__bases__[-1].__dict__.values():
                if type(v) == int and v > m:
                    m = v
            for i in range(m):
                style_font: QFont = self.font(i)
                style_font.setFamily(font.family())
                style_font.setPointSizeF(font.pointSizeF())
                self.setFont(style_font, i)

    return NewLexer


@_default_font_override
class QsciLexerCustomPython(QsciLexerPython):

    """Custom Python highlighter."""

    def __init__(self, *args):
        QsciLexerPython.__init__(self, *args)
        self.setIndentationWarning(QsciLexerPython.Tabs)

    def keywords(self, order: int) -> str:
        if order == 2:
            return "self True False"
        else:
            return QsciLexerPython.keywords(self, order)


@_default_font_override
class QsciLexerCustomMarkdown(QsciLexerMarkdown):
    """Custom Markdown highlighter."""


@_default_font_override
class QsciLexerCustomYAML(QsciLexerYAML):
    """Custom YAML highlighter."""


@_default_font_override
class QsciLexerCustomHTML(QsciLexerHTML):
    """Custom HTML highlighter."""


@_default_font_override
class QsciLexerCustomLua(QsciLexerLua):
    """Custom Lua highlighter."""


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
    "HTML": QsciLexerCustomHTML,
    "Java": QsciLexerJava,
    "JavaScript": QsciLexerJavaScript,
    "JSON": QsciLexerJSON,
    "Lua": QsciLexerCustomLua,
    "Makefile": QsciLexerMakefile,
    "Markdown": QsciLexerCustomMarkdown,
    "Matlab": QsciLexerMatlab,
    "Python": QsciLexerCustomPython,
    "SQL": QsciLexerSQL,
    "Tex": QsciLexerTeX,
    "XML": QsciLexerXML,
    "YAML": QsciLexerCustomYAML,
}

HIGHLIGHTER_SUFFIX = {
    "Bash": {'sh'},
    "Batch": {'bat'},
    "C++": {'c', 'cpp', 'h', 'hpp', 'cxx'},
    "C#": {'cs'},
    "CSS": {'css', 'bib'},
    "Diff": {'diff'},
    "Fortran": {'f90'},
    "Fortran77": {'f77'},
    "HTML": {'html'},
    "Java": {'java'},
    "JavaScript": {'js'},
    "JSON": {'json'},
    "Lua": {'lua'},
    "Markdown": {'md'},
    "Matlab": {'m'},
    "Python": {'py'},
    "SQL": {'sql'},
    "Tex": {'tex'},
    "XML": {'xml'},
    "YAML": {'yml'},
}
HIGHLIGHTER_FILENAME = {
    "CMake": {'CMakeList.txt'},
    "Makefile": {'Makefile', 'Makefile.am', 'Makefile.in', 'Makefile.debug'},
}
