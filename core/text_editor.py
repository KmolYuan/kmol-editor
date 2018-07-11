# -*- coding: utf-8 -*-

"""Text editor of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

import platform
from typing import Tuple
from core.QtModules import (
    pyqtSignal,
    pyqtSlot,
    Qt,
    QApplication,
    QWidget,
    QFont,
    QFontMetrics,
    QColor,
    #QScintilla widget
    QsciScintilla,
    #Other highlighters
    QSCIHIGHLIGHTERS,
)


class TextEditor(QsciScintilla):
    
    """QScintilla text editor."""
    
    currtWordChanged = pyqtSignal(str)
    
    def __init__(self, parent: QWidget):
        """UI settings."""
        super(TextEditor, self).__init__(parent)
        
        #Set the default font.
        if platform.system().lower() == "windows":
            font_name = "Courier New"
        else:
            font_name = "Mono"
        self.font = QFont(font_name)
        self.font.setFixedPitch(True)
        self.font.setPointSize(14)
        self.setFont(self.font)
        self.setMarginsFont(self.font)
        self.setUtf8(True)
        
        #Margin 0 is used for line numbers.
        fontmetrics = QFontMetrics(self.font)
        self.setMarginsFont(self.font)
        self.setMarginWidth(0, fontmetrics.width("0000") + 4)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))
        
        #Brace matching.
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        
        #Current line visible with special background color.
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))
        
        #Set lexer.
        self.setHighlighter("Markdown")
        self.SendScintilla(
            QsciScintilla.SCI_STYLESETFONT,
            1,
            font_name.encode('utf-8')
        )
        
        #Don't want to see the horizontal scrollbar at all.
        self.setWrapMode(QsciScintilla.WrapWord)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        
        #Auto completion.
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionSource(QsciScintilla.AcsDocument)
        self.setAutoCompletionThreshold(1)
        
        #Edge mode.
        self.setEdgeMode(QsciScintilla.EdgeNone)
        self.setEdgeColumn(80)
        self.setEdgeColor(Qt.blue)
        
        #Indentations.
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)
        self.setIndentationGuides(True)
        
        #Indicator.
        self.indicatorDefine(QsciScintilla.BoxIndicator, 0)
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)
        self.cursorPositionChanged.connect(self.__catchWords)
        
        #Widget size.
        self.setMinimumSize(400, 450)
    
    @pyqtSlot(str)
    def setHighlighter(self, option: str):
        lexer = QSCIHIGHLIGHTERS[option]()
        lexer.setDefaultFont(self.font)
        self.setLexer(lexer)
    
    @pyqtSlot(bool)
    def setEdgeMode(self, option: bool):
        """Set edge mode option."""
        super(TextEditor, self).setEdgeMode(
            QsciScintilla.EdgeLine if option else QsciScintilla.EdgeNone
        )
    
    def __currentWordPosition(self) -> Tuple[int, int]:
        """Return pos of current word."""
        pos = self.positionFromLineIndex(*self.getCursorPosition())
        return (
            self.SendScintilla(QsciScintilla.SCI_WORDSTARTPOSITION, pos, True),
            self.SendScintilla(QsciScintilla.SCI_WORDENDPOSITION, pos, True),
        )
    
    @pyqtSlot(int, int)
    def __catchWords(self, line: int, index: int):
        """Catch words that is same with current word."""
        self.clearIndicatorRange(
            0, 0,
            *self.lineIndexFromPosition(self.length()),
            0
        )
        wpos_start, wpos_end = self.__currentWordPosition()
        self.currtWordChanged.emit(self.text()[wpos_start:wpos_end])
        self.fillIndicatorRange(
            *self.lineIndexFromPosition(wpos_start),
            *self.lineIndexFromPosition(wpos_end),
            0
        )
    
    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() != Qt.ControlModifier:
            super(TextEditor, self).wheelEvent(event)
            return
        if event.angleDelta().y() >= 0:
            self.zoomIn()
        else:
            self.zoomOut()
