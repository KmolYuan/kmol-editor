# -*- coding: utf-8 -*-

"""Markdown syntax highlighter."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from core.QtModules import (
    QRegExp,
    QSyntaxHighlighter,
)
from .styles import STYLES


class MarkdownHighlighter(QSyntaxHighlighter):
    
    """Syntax highlighter for the Markdown language."""
    
    # keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None',
    ]
    
    # braces
    braces = [
        '\{',
        '\}',
        '\(',
        '\)',
        '\[',
        '\]',
        r"^\\\s?$",
    ]
    
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)
        
        rules = []
        
        rules += [(b, 0, STYLES['brace']) for b in self.braces]
        
        # All other rules
        rules += [
            # Enhanced text
            (r'\*[\w]+\*', 0, STYLES['self']),
            (r'\*\*[\w]+\*\*', 0, STYLES['self']),
            (r'_[\w]+_', 0, STYLES['self']),
            (r'__[\w]+__', 0, STYLES['self']),
            
            # Odering
            (r'^[\s]*[0-9]+\.\s\b', 0, STYLES['numbers']),
            (r'^[\s]*[\+\-\*]\s\b', 0, STYLES['numbers']),
            (r'\+?@[\w]+\:', 0, STYLES['defclass']),
            
            # Title
            (r'^[\s]*[#]+\s\b', 0, STYLES['keyword']),
            
            # Line drawing
            (r'^--[-]+$', 0, STYLES['keyword']),
            (r'^==[=]+$', 0, STYLES['keyword']),
            
            # Maths
            (r'\$\w+\$', 0, STYLES['string2']),
            (r'\$\$\w+\$\$', 0, STYLES['string2']),
        ]
        
        # Build a QRegExp for each pattern
        self.rules = [
            (QRegExp(pat), index, fmt) for (pat, index, fmt) in rules
        ]
        
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)
            
            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        
        self.setCurrentBlockState(0)
    
    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)
        
        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
