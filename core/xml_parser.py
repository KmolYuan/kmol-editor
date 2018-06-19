# -*- coding: utf-8 -*-

"""XML and tree widget transformer."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from xml.etree.ElementTree import (
    ElementTree,
    Element,
    SubElement,
    tostring,
)
from xml.dom import minidom
from core.QtModules import (
    Qt,
    QTreeWidget,
    QTreeWidgetItem,
    QFileInfo,
)
from core.data_structure import DataDict
from core.info import __version__


def tree_parse(filename: str, tree_main: QTreeWidget, data: DataDict):
    """Parse in to tree widget."""
    tree = ElementTree(file=filename)
    root = tree.getroot()
    root_node = QTreeWidgetItem([
        QFileInfo(filename).baseName(),
        filename,
        root.attrib['code']
    ])
    root_node.setFlags(root_node.flags() & ~Qt.ItemIsDragEnabled)
    tree_main.addTopLevelItem(root_node)
    
    def addNode(node: Element, root: QTreeWidgetItem):
        """Add node in to tree widget."""
        attr = node.attrib
        sub = QTreeWidgetItem([attr['name'], attr['path'], attr['code']])
        sub.setFlags(sub.flags() | Qt.ItemIsEditable)
        root.addChild(sub)
        for child in node:
            if child.tag == 'node':
                addNode(child, sub)
    
    for child in root:
        if child.tag == 'data-structure':
            for d in child:
                if d.tag == 'data':
                    data[int(d.attrib['code'])] = d.text if d.text else ""
        elif child.tag == 'node':
            addNode(child, root_node)
    data.saveAll()
    
    print("Loaded: {}".format(filename))


def tree_write(filename: str, root_node: QTreeWidgetItem, data: DataDict):
    """Write to XML file."""
    root = Element('kmolroot', {
        'version': __version__,
        'code': root_node.text(2),
    })
    
    codes = set()
    
    def addNode(node: QTreeWidgetItem, root: Element):
        attr = {
            'name': node.text(0),
            'path': node.text(1),
            'code': node.text(2),
        }
        print(attr['path'])
        sub = SubElement(root, 'node', attr)
        codes.add(attr['code'])
        if QFileInfo(node.text(1)).suffix() not in ('', 'kmol'):
            return
        for i in range(node.childCount()):
            addNode(node.child(i), sub)
    
    for i in range(root_node.childCount()):
        addNode(root_node.child(i), root)
    data_node = SubElement(root, 'data-structure')
    for code, context in data.items():
        if str(code) not in codes:
            continue
        context_node = SubElement(data_node, 'data', {'code': str(code)})
        context_node.text = context
    data.saveAll()
    
    xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent=" "*3)
    with open(filename, 'w') as f:
        f.write(xmlstr)
    
    print("Saved: {}".format(filename))
