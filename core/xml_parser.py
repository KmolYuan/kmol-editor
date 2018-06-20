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
    QDir,
)
from core.data_structure import DataDict
from core.info import __version__
from core.syntax import SUPPORT_FILE_FORMATS


def _suffix(filename: str) -> str:
    """Return suffix of file name."""
    return QFileInfo(filename).suffix()


def getpath(node: QTreeWidgetItem) -> str:
    """Get the path from parent."""
    parent = node.parent()
    if parent:
        path = node.text(1)
        return QFileInfo(
            QDir(getpath(parent)),
            path + '/' if path else ''
        ).absolutePath()
    else:
        return QFileInfo(node.text(1)).absolutePath()


def tree_write(projname: str, root_node: QTreeWidgetItem, data: DataDict):
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
    with open(projname, 'w') as f:
        f.write(xmlstr)
    
    print("Saved: {}".format(projname))


def tree_parse(projname: str, tree_main: QTreeWidget, data: DataDict):
    """Parse in to tree widget."""
    tree = ElementTree(file=projname)
    root = tree.getroot()
    root_node = QTreeWidgetItem([
        QFileInfo(projname).baseName(),
        projname,
        root.attrib['code']
    ])
    root_node.setFlags(root_node.flags() & ~Qt.ItemIsDragEnabled)
    tree_main.addTopLevelItem(root_node)
    data[int(root.attrib['code'])] = ""
    
    def addNode(node: Element, root: QTreeWidgetItem):
        """Add node in to tree widget."""
        attr = node.attrib
        sub = QTreeWidgetItem([attr['name'], attr['path'], attr['code']])
        sub.setFlags(sub.flags() | Qt.ItemIsEditable)
        root.addChild(sub)
        
        code = int(attr['code'])
        suffix = _suffix(attr['path'])
        if suffix:
            filename = QDir(getpath(root)).filePath(QFileInfo(attr['path']).fileName())
            if suffix == 'md':
                parseMarkdown(filename, sub, code, data)
            elif suffix == 'html':
                #TODO: Need to parse HTML (reveal.js index.html)
                parseText(filename, code, data)
            else:
                #Text files and Python scripts.
                parseText(filename, code, data)
        else:
            data[code] = ""
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
    
    print("Loaded: {}".format(projname))


def parseText(
    filename: str,
    code: int,
    data: DataDict
):
    """Just store file content to data structure."""
    try:
        f = open(filename, 'r')
    except FileNotFoundError as e:
        data[code] = str(e)
        return
    
    with f:
        doc = f.read()
    data[code] = doc


def parseMarkdown(
    filename: str,
    node: QTreeWidgetItem,
    code: int,
    data: DataDict
):
    """Parse Markdown file to tree nodes."""
    try:
        f = open(filename, 'r')
    except FileNotFoundError as e:
        data[code] = str(e)
        return
    
    with f:
        string_list = f.read().split('\n')
    
    data[code] = "@others"
    
    #Read the first level of title mark.
    #titles: {line_num: level}
    #titles_sorted: [num: line_num]
    titles = {}
    titles_sorted = []
    previous_line = ""
    line_num = 0
    for line in tuple(string_list):
        for level, string in enumerate(['===', '---']):
            if not line.startswith(string):
                continue
            if len(set(line)) == 1 and previous_line:
                #Merge under line with its title.
                doc = previous_line + '\n' + line
                line_num -= 1
                string_list[line_num] = doc
                titles[line_num] = level
                titles_sorted.append(line_num)
                del string_list[line_num + 1]
        for level in range(1, 5):
            if not line.startswith('#' * level + " "):
                continue
            titles[line_num] = level
        previous_line = line
        line_num += 1
    
    #Joint nodes.
    items = []
    
    def section_root(i: int) -> int:
        """Level setting."""
        for j, line_num_pre in reversed(tuple(enumerate(titles_sorted[:i]))):
            if titles[line_num_pre] > titles[titles_sorted[i]]:
                return j
        return -1
    
    for i, line_num in enumerate(titles_sorted):
        title = string_list[line_num]
        if title.startswith('#'):
            title = title.split(maxsplit=1)[-1]
        else:
            title = title.split('\n')[0]
        
        code_node = data.newNum()
        
        sub = QTreeWidgetItem([title, "", str(code_node)])
        sub.setFlags(sub.flags() | Qt.ItemIsEditable)
        items.append(sub)
        root = section_root(i)
        if root == -1:
            node.addChild(sub)
        else:
            items[root].addChild(sub)
        data[code_node] = '\n'.join(
            string_list[line_num:]
            if i + 1 == len(titles_sorted) else
            string_list[line_num:titles_sorted[i + 1]]
        )
