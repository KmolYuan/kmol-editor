# -*- coding: utf-8 -*-

"""A data contianer of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import (
    Tuple,
    Iterator,
    Hashable,
)
from core.QtModules import (
    pyqtSignal,
    QObject,
)


class DataDict(QObject):
    
    """A wrapper class contain the data of nodes."""
    
    codeAdded = pyqtSignal(str)
    codeDeleted = pyqtSignal(str)
    
    def __init__(self):
        self.__data = {}
        self.__saved = {}
    
    def clear(self):
        """Clear data."""
        self.__data.clear()
        self.__saved.clear()
    
    def __getitem__(self, key: Hashable) -> str:
        """Get item string."""
        if key in self.__data:
            return self.__data[key]
        else:
            return ""
    
    def __setitem__(self, key: Hashable, context: str):
        """Set item."""
        if key not in self.__data:
            self.codeAdded.emit(str(key))
        old_context = self[key]
        self.__data[key] = context
        self.__saved[key] = old_context == context
    
    def __delitem__(self, key: Hashable):
        """Delete the key and avoid raise error."""
        if key in self.__data:
            del self.__data[key]
            del self.__saved[key]
            self.codeDeleted.emit(str(key))
    
    def __len__(self) -> int:
        """Length."""
        return len(self.__data)
    
    def __repr__(self) -> str:
        """Text format."""
        return str(self.__data)
    
    def __contains__(self, key: Hashable) -> bool:
        """Return True if index is in the data."""
        return key in self.__data
    
    def items(self) -> Iterator[Tuple[int, str]]:
        """Items of data."""
        return self.__data.items()
    
    def is_saved(self, key: Hashable) -> bool:
        """Return saved status."""
        return self.__saved[key]
    
    def is_all_saved(self) -> bool:
        """Return True if all saved."""
        return all(self.is_saved(key) for key in self.__data)
    
    def saveAll(self):
        """Change all saved status."""
        for key in self.__data:
            self.__saved[key] = True
    
    def newNum(self) -> int:
        """Get a unused number."""
        i = 0
        while i in self.__data:
            i += 1
        else:
            self[i] = ""
            return i
