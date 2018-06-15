# -*- coding: utf-8 -*-

"""XML and tree widget transformer."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from xml.etree.ElementTree import (
    Element,
    SubElement,
    tostring,
)
from xml.dom import minidom
from core.QtModules import (
    QTreeWidget,
    QTreeWidgetItem,
)
from core.data_structure import DataDict
from core.info import __version__


def tree_parse(filename: str, tree_main: QTreeWidget):
    """Parse in to tree widget."""


def tree_wirte(filename: str, root_node: QTreeWidgetItem, data: DataDict):
    """Write to XML file."""
    root = Element('kmolroot', {
        'version': __version__,
        'code': root_node.text(2),
    })
    
    def addNode(node: QTreeWidgetItem, root: Element):
        attr = {
            'name': node.text(0),
            'path': node.text(1),
            'code': node.text(2),
        }
        sub = SubElement(root, 'node', attr)
        for i in range(node.childCount()):
            addNode(node.child(i), sub)
    
    for i in range(root_node.childCount()):
        addNode(root_node.child(i), root)
    data_node = SubElement(root, 'data-structure')
    for code, context in data.items():
        context_node = SubElement(data_node, 'data', {'code': str(code)})
        context_node.text = context
    xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent=" "*3)
    with open(filename, 'w') as f:
        f.write(xmlstr)
