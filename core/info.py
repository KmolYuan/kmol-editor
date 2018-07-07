# -*- coding: utf-8 -*-

"""Module information of kmol editor."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"
__version__ = "18.07"

from sys import version_info
import platform
import argparse
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

_POWEREDBY = (
    "Python IDE Eric 6",
    "PyQt 5",
    "QScintilla 2",
)

#--help arguments
_parser = argparse.ArgumentParser(
    description = ("Pyslvs - Open Source Planar Linkage Mechanism Simulation" +
        "and Mechanical Synthesis System."),
    epilog = "Powered by {}.".format(", ".join(_POWEREDBY))
)
_parser.add_argument(
    '-f',
    '--fusion',
    action = 'store_true',
    help = "run Pyslvs in Fusion style"
)
_parser.add_argument(
    'r',
    metavar = "file path",
    default = (),
    nargs = '*',
    type = str,
    help = "read file from the file path"
)
_parser.add_argument(
    '-t',
    '--test',
    action = 'store_true',
    help = "just test module states and exit"
)
ARGUMENTS = _parser.parse_args()
