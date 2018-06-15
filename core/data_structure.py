# -*- coding: utf-8 -*-

"""A data contianer of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2016-2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import Dict, Hashable


class DataDict:
    
    """A wrapper class contain the data of nodes."""
    
    def __init__(self, data: Dict[Hashable, str] = {}):
        self.__data = {}
        self.__data.update(data)
        self.__saved = {key: True for key in data}
    
    def clear(self):
        self.__data.clear()
        self.__saved.clear()
    
    def __getitem__(self, key: Hashable) -> str:
        try:
            return self.__data[key]
        except KeyError:
            return ""
    
    def __setitem__(self, key: Hashable, context: str):
        self.__data[key] = context
        self.__saved[key] = False
    
    def saved(self, key: Hashable) -> bool:
        return self.__saved[key]
    
    def saveAll(self):
        for key in self.__data:
            self.__saved[key] = True
