# -*- coding: utf-8 -*-

"""Text editor of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from core.QtModules import (
    pyqtSlot,
    Qt,
    QApplication,
    QWidget,
    QPlainTextEdit,
    QTextCursor,
)
from core.syntax import (
    HtmlHighlighter,
    MarkdownHighlighter,
    PythonHighlighter,
)


class TextEditor(QPlainTextEdit):
    
    """Custom text editor."""
    
    highlighters = (
        MarkdownHighlighter,
        HtmlHighlighter,
        PythonHighlighter,
    )
    
    def __init__(self, parent: QWidget):
        super(TextEditor, self).__init__(parent)
        self.setStyleSheet(
            "QPlainTextEdit{" +
            "font-family:'Mono';" +
            "color: #ccc;" +
            "background-color: #2b2b2b;" +
            "}"
        )
        self.zoomIn(6)
        self.setHighlighter(0)
        
        self.tab = " " * 4
    
    @pyqtSlot(int)
    def setHighlighter(self, highlight: int):
        """Highlighter setting."""
        self.__hl = self.highlighters[highlight](self.document())
    
    def wheelEvent(self, event):
        """Set zoom factor by control key."""
        super(TextEditor, self).wheelEvent(event)
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
    
    def keyPressEvent(self, event):
        """Change key behavior."""
        key = event.key()
        cur = self.textCursor()
        if key == Qt.Key_Tab:
            cur.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            text = cur.selectedText()
            if text:
                cur.insertText('\n'.join(
                    self.tab + s for s in text.splitlines()
                ))
            else:
                cur.insertText(self.tab)
        elif key == Qt.Key_Backtab:
            cur.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            text = cur.selectedText()
            cur.insertText('\n'.join(
                s[len(self.tab):] if s.startswith(self.tab) else s
                for s in text.splitlines()
            ))
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            pos = cur.position()
            anchor = cur.anchor()
            cur.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            text = cur.selectedText()
            space_count = len(text) - len(text.lstrip())
            cur.setPosition(anchor)
            cur.setPosition(pos, QTextCursor.KeepAnchor)
            cur.insertText('\n' + " " * space_count)
        elif key == Qt.Key_Backspace:
            pos = cur.position()
            anchor = cur.anchor()
            cur.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            text = cur.selectedText()[1:]
            if text.isspace():
                cur.insertText(text.replace(text.replace(self.tab, ''), ''))
            else:
                cur.setPosition(pos, QTextCursor.KeepAnchor)
                super(TextEditor, self).keyPressEvent(event)
        else:
            super(TextEditor, self).keyPressEvent(event)
