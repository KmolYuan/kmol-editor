# -*- coding: utf-8 -*-

"""Text editor of kmol editor.

Warning:
    Regular expression (re) module should handle in bytes mode.
    So any pattern and source should be encoded to UTF-8.
"""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import (
    Tuple,
    Iterator,
    Match,
    overload,
)
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
    QMenu,
    QAction,
    QInputDialog,
    QScrollBar,
    # QScintilla widget
    QsciScintilla,
    # Other highlighters
    QSCI_HIGHLIGHTERS,
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
_commas = (
    Qt.Key_Comma,
)
_commas_markdown = (
    Qt.Key_Semicolon,
    Qt.Key_Colon,
)


def _finditer(p: str, d: str, flags: re.RegexFlag = 0) -> Iterator[Match[str]]:
    """Iterator of encoding version."""
    yield from re.finditer(p.encode('utf-8'), d.encode('utf-8'), flags)


def _spell_check(doc: str) -> Iterator[Tuple[int, int]]:
    """Yield unknown words and position."""
    words = []
    for s in re.split(r"(\W|\d|_)+", doc):
        if len(s) < 2:
            continue

        # Camel case.
        for m in _finditer(r'[A-Za-z][a-z]+', s):
            word: bytes = m.group(0)
            if len(word) == len(word.decode('utf-8')):
                words.append(word.decode('utf-8').lower())

    for unknown in _spell.unknown(words):
        for m in _finditer(unknown, doc, re.IGNORECASE):
            yield m.start(), m.end()


class TextEditor(QsciScintilla):

    """QScintilla text editor."""

    word_changed = pyqtSignal()

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
        self.setEolMode(QsciScintilla.EolUnix)

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

        # Spell checker indicator [0]
        self.indicatorDefine(QsciScintilla.SquiggleIndicator, 0)

        # Keyword indicator [1]
        self.indicatorDefine(QsciScintilla.BoxIndicator, 1)
        self.cursorPositionChanged.connect(self.__catch_word)
        self.word = ""

    @pyqtSlot(int, int)
    def __catch_word(self, line: int, index: int):
        """Catch and indicate current word."""
        self.__clear_indicator_all(1)
        pos = self.positionFromLineIndex(line, index)
        _, _, self.word = self.__word_at_pos(pos)
        for m in _finditer(r'\b' + self.word + r'\b', self.text(), re.IGNORECASE):
            self.fillIndicatorRange(
                *self.lineIndexFromPosition(m.start()),
                *self.lineIndexFromPosition(m.end()),
                1
            )

    @pyqtSlot(str)
    def set_highlighter(self, option: str):
        """Set highlighter by list."""
        self.lexer_option = option
        lexer = QSCI_HIGHLIGHTERS[option]()
        lexer.setDefaultFont(self.font)
        self.setLexer(lexer)

    @pyqtSlot(bool)
    def setEdgeMode(self, option: bool):
        """Set edge mode option."""
        super(TextEditor, self).setEdgeMode(
            QsciScintilla.EdgeLine if option else QsciScintilla.EdgeNone
        )

    @overload
    def setSelection(self, p1: int, p2: int, p3: int, p4: int) -> None:
        ...

    @overload
    def setSelection(self, p1: int, p2: int, *_: int) -> None:
        ...

    def setSelection(self, *args: int):
        if len(args) == 2:
            line1, index1 = self.lineIndexFromPosition(args[0])
            line2, index2 = self.lineIndexFromPosition(args[1])
            super(TextEditor, self).setSelection(line1, index1, line2, index2)
        else:
            super(TextEditor, self).setSelection(*args)

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

    def contextMenuEvent(self, event):
        """Custom context menu."""
        # Spell refactor.
        menu: QMenu = self.createStandardContextMenu()
        menu.addSeparator()
        correction_action = QAction("&Refactor Words", self)
        correction_action.triggered.connect(self.__spell_correction)
        menu.addAction(correction_action)
        menu.exec(self.mapToGlobal(event.pos()))

    def __replace_all(self, word: str, replace_word: str):
        """Replace the word for all occurrence."""
        found = self.findFirst(word, False, False, True, True)
        while found:
            self.replace(replace_word)
            found = self.findNext()

    def __word_at_pos(self, pos: int) -> Tuple[int, int, str]:
        """Return pos of current word."""
        return (
            self.SendScintilla(QsciScintilla.SCI_WORDSTARTPOSITION, pos, True),
            self.SendScintilla(QsciScintilla.SCI_WORDENDPOSITION, pos, True),
            self.wordAtLineIndex(*self.getCursorPosition())
        )

    @pyqtSlot()
    def __spell_correction(self):
        """Refactor words."""
        pos = self.positionFromLineIndex(*self.getCursorPosition())
        start, end, words = self.__word_at_pos(pos)
        if not words:
            return

        # Camel case.
        word = words
        for m in _finditer(r'[A-Za-z][a-z]+', words):
            if m.start() < pos - start < m.end():
                word = m.group(0)
                break

        answer, ok = QInputDialog.getItem(
            self,
            "Spell correction",
            f"Refactor word: \"{word}\"",
            _spell.candidates(word)
        )
        if ok:
            self.__replace_all(words, words.replace(word, answer))

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
        selected_text = self.selectedText()

        # Commas and parentheses.
        parentheses = list(_parentheses)
        commas = list(_commas)
        if self.lexer_option in {"Markdown", "HTML"}:
            parentheses.extend(_parentheses_html)
            commas.extend(_commas_markdown)

        # Skip the closed parentheses.
        for k1, k2, t0, t1 in parentheses:
            if key == k2:
                if self.__cursor_next_char() == t1:
                    self.__cursor_move_next()
                    return

        # Wrap the selected text.
        if selected_text:
            for k1, k2, t0, t1 in parentheses:
                if key == k1:
                    self.replaceSelectedText(t0 + selected_text + t1)
                    self.word_changed.emit()
                    return

        line, _ = self.getCursorPosition()
        doc_pre = self.text(line)
        super(TextEditor, self).keyPressEvent(event)
        doc_post = self.text(line)
        if doc_pre != doc_post:
            self.word_changed.emit()
        self.__spell_check_line()

        # Auto close of parentheses.
        for k1, k2, t0, t1 in parentheses:
            if key == k1:
                self.insert(t1)
                return

        # Add space for commas.
        for co in commas:
            if key == co and self.__cursor_next_char() != " ":
                self.insert(" ")
                self.__cursor_move_next()
                return

    def __clear_indicator_all(self, indicator: int):
        """Clear all indicators."""
        self.clearIndicatorRange(0, 0, *self.lineIndexFromPosition(self.length()), indicator)

    def spell_check_all(self):
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
        scroll_bar: QScrollBar = self.verticalScrollBar()
        pos = scroll_bar.sliderPosition()

        line, index = self.getCursorPosition()
        doc = ""
        for line_str in self.text().splitlines():
            doc += line_str.rstrip() + '\n'
        super(TextEditor, self).setText(doc)

        self.setCursorPosition(line, self.lineLength(line) - 1)
        scroll_bar.setSliderPosition(pos)

    def setText(self, doc: str):
        """Remove trailing blanks in text editor."""
        super(TextEditor, self).setText(doc)
        if self.__no_trailing_blanks:
            self.remove_trailing_blanks()
        self.spell_check_all()
