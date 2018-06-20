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
from core.syntax import SUPPORT_FILE_FORMATS


def _suffix(filename: str) -> str:
    """Return suffix of file name."""
    return QFileInfo(filename).suffix()


def tree_write(filename: str, root_node: QTreeWidgetItem, data: DataDict):
    """Write to XML file."""
    root = Element('kmolroot', {
        'version': __version__,
        'code': root_node.text(2),
    })
    
    #The strings that need to save.
    codes = set()
    
    def addNode(node: QTreeWidgetItem, root: Element):
        attr = {
            'name': node.text(0),
            'path': node.text(1),
            'code': node.text(2),
        }
        sub = SubElement(root, 'node', attr)
        if _suffix(node.text(1)) in SUPPORT_FILE_FORMATS:
            #Files do not need to make any copy.
            return
        codes.add(attr['code'])
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
        suffix = _suffix(attr['path'])
        if suffix:
            if suffix == 'md':
                parse = parseMarkdown
            elif suffix == 'html':
                #TODO: Need to parse HTML (reveal.js index.html)
                parse = parseText
            else:
                #Text files and Python scripts.
                parse = parseText
            parse(attr['path'], sub, int(attr['code']), data)
        else:
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


def parseText(
    filename: str,
    node: QTreeWidgetItem,
    code: int,
    data: DataDict
):
    """Just store file content to data structure."""
    string_list = []
    with open(filename, 'r') as f:
        for line in f:
            string_list.append(line)
    data[code] = '\n'.join(string_list)

def parseMarkdown(
    filename: str,
    node: QTreeWidgetItem,
    code: int,
    data: DataDict
):
    """Parse Markdown file to tree nodes."""
    string_list = []
    with open(filename, 'r') as f:
        for line in f:
            string_list.append(line)
    
    #Read the first level of title mark.
    #titles: {line_num: level}
    titles = {}
    previous_line = ""
    line_num = 0
    for line in tuple(string_list):
        for level, string in enumerate(['===', '---']):
            if not line.startswith(string):
                continue
            if len(set(line)) == 1 and previous_line:
                #Merge under line with its title.
                doc = previous_line + '\n' + line
                string_list[line_num - 1] = doc
                titles[line_num - 1] = level
                del string_list[line_num]
                line_num -= 1
        for level in range(1, 5):
            if not line.startswith('#' * level + " "):
                continue
            titles[line_num] = level
        previous_line = line
        line_num += 1
    
    #TODO: Joint nodes.
    titles_sorted = sorted(titles)
    for index, line_num in enumerate(titles_sorted):
        level = titles[line_num]
        doc = '\n'.join(string_list[titles_sorted[index]:titles_sorted[index + 1]])
