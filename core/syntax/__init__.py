# -*- coding: utf-8 -*-

"""Syntax module of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2016-2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from .html_syntax import HtmlHighlighter
from .markdown_syntax import MarkdownHighlighter
from .python_syntax import PythonHighlighter

__all__ = [
    'HtmlHighlighter',
    'MarkdownHighlighter',
    'PythonHighlighter',
]
