# -*- coding: utf-8 -*-

"""A data contianer of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import (
    Tuple,
    Iterable,
    Hashable,
    Dict,
)
from core.QtModules import (
    pyqtSignal,
    QObject,
)


class DataDict(QObject):

    """A wrapper class contain the data of nodes."""

    not_saved = pyqtSignal()
    all_saved = pyqtSignal()

    def __init__(self):
        super(DataDict, self).__init__()
        self.__data = {}
        self.__saved = {}
        self.__macros = {}

    def clear(self):
        """Clear data."""
        self.__data.clear()
        self.__saved.clear()
        self.__macros.clear()

    def __getitem__(self, key: Hashable) -> str:
        """Get item string."""
        if key in self.__data:
            return self.__data[key]
        else:
            return ""

    def __setitem__(self, key: Hashable, context: str):
        """Set item."""
        self.__saved[key] = self[key] == context
        if not self.__saved[key]:
            self.not_saved.emit()
        self.__data[key] = context

    def __delitem__(self, key: Hashable):
        """Delete the key and avoid raise error."""
        if key in self.__data:
            del self.__data[key]
            del self.__saved[key]
            for m, code in tuple(self.__macros.items()):
                if code == key:
                    del self.__macros[m]

    def __len__(self) -> int:
        """Length."""
        return len(self.__data)

    def __repr__(self) -> str:
        """Text format."""
        return str(self.__data)

    def __contains__(self, key: Hashable) -> bool:
        """Return True if index is in the data."""
        return key in self.__data

    def update(self, target: Dict[Hashable, str]):
        """Update data."""
        for key, context in target.items():
            self[key] = context

    def items(self) -> Iterable[Tuple[int, str]]:
        """Items of data."""
        return self.__data.items()

    def set_saved(self, key: Hashable, saved: bool):
        """Saved status adjustment."""
        self.__saved[key] = saved

    def is_saved(self, key: Hashable) -> bool:
        """Return saved status."""
        return self.__saved[key]

    def is_all_saved(self) -> bool:
        """Return True if all saved."""
        return all(self.is_saved(key) for key in self.__data)

    def save_all(self):
        """Change all saved status."""
        for key in self.__data:
            self.__saved[key] = True
        self.all_saved.emit()

    def new_num(self) -> int:
        """Get a unused number."""
        i = hash('kmol')
        while i in self.__data:
            i = hash(str(i))
        else:
            self[i] = ""
            return i

    def add_macro(self, name: str, key: Hashable):
        """Add a macro."""
        if key not in self.__data:
            raise KeyError("{} is not in data.".format(key))
        self.__macros[name] = key

    def macros(self) -> Iterable[Tuple[str, Hashable]]:
        """Return macro scripts."""
        return self.__macros.items()
