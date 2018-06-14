# -*- coding: utf-8 -*-

"""A data contianer of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2016-2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import Any


class DataDict:
    
    """A wrapper class contain the data of nodes."""
    
    def __init__(self):
        self.__data = {}
        self.clear()
    
    def clear(self):
        self.__data.clear()
    
    def __getitem__(self, key: Any) -> str:
        try:
            return self.__data[key]
        except KeyError:
            return ""
    
    def __setitem__(self, key: Any, context: str):
        self.__data[key] = context
