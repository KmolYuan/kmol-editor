# -*- coding: utf-8 -*-

"""Text file parser."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from core.data_structure import DataDict


def parse_text(
    filename: str,
    code: int,
    data: DataDict
):
    """Just store file content to data structure."""
    try:
        f = open(filename, encoding='utf-8')
    except FileNotFoundError as e:
        data[code] = str(e)
        return

    with f:
        doc = f.read()
    data[code] = doc
