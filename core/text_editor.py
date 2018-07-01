# -*- coding: utf-8 -*-

"""Text editor of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from core.QtModules import (
    pyqtSlot,
    Qt,
    QWidget,
    QsciScintilla,
    QsciLexerMarkdown,
    QsciLexerHTML,
    QsciLexerPython,
    QFont,
    QFontMetrics,
    QColor,
)


class TextEditor(QsciScintilla):
    
    """QScintilla text editor."""
    
    HIGHLIGHTERS = [
        QsciLexerMarkdown,
        QsciLexerHTML,
        QsciLexerPython,
    ]
    
    def __init__(self, parent: QWidget):
        """UI settings."""
        super(TextEditor, self).__init__(parent)
        
        #Set the default font
        self.font = QFont()
        self.font.setFamily('Courier')
        self.font.setFixedPitch(True)
        self.font.setPointSize(14)
        self.setFont(self.font)
        self.setMarginsFont(self.font)
        
        #Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(self.font)
        self.setMarginsFont(self.font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 5)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))
        
        #Brace matching.
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        
        #Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))
        
        #Set lexer
        self.setHighlighter(0)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, b'Courier')
        
        #Don't want to see the horizontal scrollbar at all.
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        
        #Auto completion.
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionSource(QsciScintilla.AcsDocument)
        self.setAutoCompletionThreshold(1)
        
        #Edge mode.
        self.setEdgeMode(QsciScintilla.EdgeLine)
        self.setEdgeColumn(80)
        self.setEdgeColor(Qt.blue)
        
        #Indentations.
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)
        self.setIndentationGuides(True)
        
        self.setMinimumSize(600, 450)
    
    @pyqtSlot(int)
    def setHighlighter(self, option: int):
        lexer = self.HIGHLIGHTERS[option]()
        lexer.setDefaultFont(self.font)
        self.setLexer(lexer)
