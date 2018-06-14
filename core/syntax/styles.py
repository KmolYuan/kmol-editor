# -*- coding: utf-8 -*-

"""Colored styles."""

from core.QtModules import (
    QColor,
    QTextCharFormat,
    QFont,
)

def _format(color, style=''):
    """
    Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _textformat = QTextCharFormat()
    _textformat.setForeground(_color)
    if 'bold' in style:
        _textformat.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _textformat.setFontItalic(True)

    return _textformat


STYLES = {
    'keyword': _format([200, 120, 50], 'bold'),
    'operator': _format([150, 150, 150]),
    'brace': _format('darkGray'),
    'defclass': _format([220, 220, 255], 'bold'),
    'string': _format([20, 110, 100]),
    'string2': _format([30, 120, 110]),
    'comment': _format([128, 128, 128]),
    'self': _format([150, 85, 140], 'italic'),
    'numbers': _format([100, 150, 190]),
}
