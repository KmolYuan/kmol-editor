# -*- coding: utf-8 -*-

"""Module information of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"
__version__ = "18.06"

from sys import version_info
import platform
from core.QtModules import (
    qVersion,
    PYQT_VERSION_STR,
)

_Qt_Version = qVersion().strip()
_PyQt_Version = PYQT_VERSION_STR.strip()

INFO = (
    "Kmol Editor {}".format(__version__),
    "OS Type: {} {} [{}]".format(platform.system(), platform.release(), platform.machine()),
    "Python Version: {v.major}.{v.minor}.{v.micro}({v.releaselevel})".format(v=version_info),
    "Python Compiler: {}".format(platform.python_compiler()),
    "Qt Version: {}".format(_Qt_Version),
    "PyQt Version: {}".format(_PyQt_Version)
)
