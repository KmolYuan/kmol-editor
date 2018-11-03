# -*- coding: utf-8 -*-

"""Text editor of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import Tuple, Iterator
import platform
import re
from spellchecker import SpellChecker
from core.QtModules import (
    pyqtSignal,
    pyqtSlot,
    Qt,
    QApplication,
    QWidget,
    QFont,
    QFontMetrics,
    QColor,
    QTimer,
    # QScintilla widget
    QsciScintilla,
    # Other highlighters
    QSCIHIGHLIGHTERS,
)


_spell = SpellChecker()
_parentheses = (
    (Qt.Key_ParenLeft, Qt.Key_ParenRight, '(', ')'),
    (Qt.Key_BracketLeft, Qt.Key_BracketRight, '[', ']'),
    (Qt.Key_BraceLeft, Qt.Key_BraceRight, '{', '}'),
    (Qt.Key_QuoteDbl, None, '"', '"'),
    (Qt.Key_Apostrophe, None, "'", "'"),
)
_parentheses_html = (
    (Qt.Key_Less, Qt.Key_Greater, '<', '>'),
)
_parentheses_markdown = (
    (Qt.Key_Dollar, Qt.Key_Dollar, '$', '$'),
    (Qt.Key_Asterisk, Qt.Key_Asterisk, '*', '*'),
    _parentheses_html[0],
)
_commas = (
    Qt.Key_Comma,
)
_commas_markdown = (
    Qt.Key_Semicolon,
    Qt.Key_Colon,
    Qt.Key_Period,
)


def _spell_check(doc: str) -> Iterator[Tuple[int, int]]:
    """Yield unknown words and position."""
    words = []
    for s in re.split(r"(\W|\d|_)+", doc):
        if len(s) < 2:
            continue
        # Camel case.
        for m in re.finditer(r'.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', s):
            words.append(m.group(0).lower())

    for unknown in _spell.unknown(words):
        for m in re.finditer(unknown, doc):
            yield m.start(), m.end()


class TextEditor(QsciScintilla):

    """QScintilla text editor."""

    currentWordChanged = pyqtSignal(str)

    def __init__(self, parent: QWidget):
        """UI settings."""
        super(TextEditor, self).__init__(parent)

        # Set the default font.
        if platform.system() == "Windows":
            font_name = "Courier New"
        else:
            font_name = "Mono"
        self.font = QFont(font_name)
        self.font.setFixedPitch(True)
        self.font.setPointSize(14)
        self.setFont(self.font)
        self.setMarginsFont(self.font)
        self.setUtf8(True)

        # Margin 0 is used for line numbers.
        font_metrics = QFontMetrics(self.font)
        self.setMarginsFont(self.font)
        self.setMarginWidth(0, font_metrics.width("0000") + 4)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # Brace matching.
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color.
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))

        # Set lexer.
        self.lexer_option = "Markdown"
        self.set_highlighter("Markdown")
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, font_name.encode('utf-8'))

        # Don't want to see the horizontal scrollbar at all.
        self.setWrapMode(QsciScintilla.WrapWord)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Auto completion.
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionSource(QsciScintilla.AcsDocument)
        self.setAutoCompletionThreshold(1)

        # Edge mode.
        self.setEdgeMode(QsciScintilla.EdgeNone)
        self.setEdgeColumn(80)
        self.setEdgeColor(Qt.blue)

        # Indentations.
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)
        self.setIndentationGuides(True)

        # Widget size.
        self.setMinimumSize(400, 450)

        # Remove trailing blanks.
        self.__no_trailing_blanks = True

        # Check timer.
        self.check_timer = QTimer(self)

        # Spell checker indicator.
        self.indicatorDefine(QsciScintilla.SquiggleIndicator, 0)
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)

    @pyqtSlot(str)
    def set_highlighter(self, option: str):
        """Set highlighter by list."""
        self.lexer_option = option
        lexer = QSCIHIGHLIGHTERS[option]()
        lexer.setDefaultFont(self.font)
        self.setLexer(lexer)

    @pyqtSlot(bool)
    def setEdgeMode(self, option: bool):
        """Set edge mode option."""
        super(TextEditor, self).setEdgeMode(
            QsciScintilla.EdgeLine if option else QsciScintilla.EdgeNone
        )

    @pyqtSlot(bool)
    def set_remove_trailing_blanks(self, option: bool):
        """Set remove trailing blanks during 'setText' method."""
        self.__no_trailing_blanks = option

    def wheelEvent(self, event):
        """Mouse wheel event."""
        if QApplication.keyboardModifiers() != Qt.ControlModifier:
            super(TextEditor, self).wheelEvent(event)
            return
        if event.angleDelta().y() >= 0:
            self.zoomIn()
        else:
            self.zoomOut()

    def __cursor_move_next(self):
        """Move text cursor to next character."""
        line, index = self.getCursorPosition()
        self.setCursorPosition(line, index + 1)

    def __cursor_next_char(self) -> str:
        """Next character of cursor."""
        pos = self.positionFromLineIndex(*self.getCursorPosition())
        return self.text(pos, pos + 1)

    def keyPressEvent(self, event):
        """Input key event."""
        key = event.key()
        text = self.selectedText()

        # Commas and parentheses.
        parentheses = list(_parentheses)
        commas = list(_commas)
        if self.lexer_option == "Markdown":
            parentheses.extend(_parentheses_markdown)
            commas.extend(_commas_markdown)
        elif self.lexer_option == "HTML":
            parentheses.extend(_parentheses_html)
            commas.extend(_commas_markdown)

        # Skip the closed parentheses.
        for k1, k2, t0, t1 in parentheses:
            if key == k2:
                if self.__cursor_next_char() == t1:
                    self.__cursor_move_next()
                    return

        # Wrap the selected text.
        if text:
            for k1, k2, t0, t1 in parentheses:
                if key == k1:
                    self.replaceSelectedText(t0 + text + t1)
                    return

        super(TextEditor, self).keyPressEvent(event)
        self.__spell_check_line()

        # Auto close of parentheses.
        for k1, k2, t0, t1 in parentheses:
            if key == k1:
                self.insert(t1)
                return

        # Add space for commas.
        for co in commas:
            if key == co:
                self.insert(" ")
                self.__cursor_move_next()
                return

    def __clear_indicator_all(self, indicator: int):
        """Clear all indicators."""
        self.clearIndicatorRange(0, 0, *self.lineIndexFromPosition(self.length()), indicator)

    def __spell_check_all(self):
        """Spell check for all text."""
        self.__clear_indicator_all(0)
        for start, end in _spell_check(self.text()):
            self.fillIndicatorRange(
                *self.lineIndexFromPosition(start),
                *self.lineIndexFromPosition(end),
                0
            )

    def __clear_line_indicator(self, line: int, indicator: int):
        """Clear all indicators."""
        self.clearIndicatorRange(line, 0, line, self.lineLength(line), indicator)

    def __spell_check_line(self):
        """Spell check for current line."""
        line, index = self.getCursorPosition()
        self.__clear_line_indicator(line, 0)
        for start, end in _spell_check(self.text(line)):
            self.fillIndicatorRange(line, start, line, end, 0)

    def remove_trailing_blanks(self):
        """Remove trailing blanks in text editor."""
        line, index = self.getCursorPosition()
        doc = ""
        for line_str in self.text().splitlines():
            doc += line_str.rstrip() + '\n'
        super(TextEditor, self).setText(doc)
        self.setCursorPosition(line, self.lineLength(line) - 1)

    def setText(self, doc: str):
        """Remove trailing blanks in text editor."""
        super(TextEditor, self).setText(doc)
        if self.__no_trailing_blanks:
            self.remove_trailing_blanks()
        self.__spell_check_all()
