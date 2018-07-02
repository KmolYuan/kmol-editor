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
    QTreeItem,
    QTreeRoot,
    QTreeWidget,
    QTreeWidgetItem,
    QFileInfo,
    QDir,
)
from core.data_structure import DataDict
from core.info import __version__


SUPPORT_FILE_FORMATS = ['py', 'md', 'html']


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
    root_node = QTreeRoot(
        QFileInfo(projname).baseName(),
        projname,
        root.attrib['code']
    )
    tree_main.addTopLevelItem(root_node)
    data[int(root.attrib['code'])] = ""
    
    parse_list = []
    
    def addNode(node: Element, root: QTreeWidgetItem):
        """Add node in to tree widget."""
        attr = node.attrib
        sub = QTreeItem(attr['name'], attr['path'], attr['code'])
        root.addChild(sub)
        suffix = _suffix(attr['path'])
        data[int(attr['code'])] = ""
        if suffix:
            filename = QDir(getpath(root)).filePath(QFileInfo(attr['path']).fileName())
            parse_list.append((filename, sub))
        else:
            for child in node:
                if child.tag == 'node':
                    addNode(child, sub)
    
    for child in root:
        if child.tag == 'data-structure':
            for d in child:
                if d.tag == 'data':
                    data[int(d.attrib['code'])] = d.text or ""
        elif child.tag == 'node':
            addNode(child, root_node)
    
    for filename, sub in parse_list:
        suffix = _suffix(sub.text(1))
        if suffix == 'md':
            #Markdown
            parseMarkdown(filename, sub, int(sub.text(2)), data)
        elif suffix == 'html':
            #TODO: Need to parse HTML (reveal.js index.html)
            parseText(filename, int(sub.text(2)), data)
        else:
            #Text files and Python scripts.
            parseText(filename, int(sub.text(2)), data)
    
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
                #Under line with its title.
                titles[line_num - 1] = level
                titles_sorted.append(line_num - 1)
        if line:
            prefix = line.split(maxsplit=1)[0]
            if set(prefix) == {'#'}:
                titles[line_num] = len(prefix)
        previous_line = line
        line_num += 1
    
    #Joint nodes.
    tree_items = []
    titles_count = len(titles_sorted) - 1
    buttom_level = max(titles.values())
    
    def parent(index: int, level: int) -> QTreeWidgetItem:
        """The parent of current title."""
        for i, pre_index in reversed(tuple(enumerate(titles_sorted[:index]))):
            if titles[pre_index] == level - 1:
                return tree_items[i]
        return node
    
    for index, line_num in enumerate(titles_sorted):
        level = titles[line_num]
        code = data.newNum()
        if index == titles_count:
            doc = string_list[line_num:]
        else:
            doc = string_list[line_num:titles_sorted[index + 1]]
        if level != buttom_level and index != titles_count:
            doc += ['@others', '']
        data[code] = '\n'.join(doc)
        title = doc[0]
        if title.startswith("#"):
            title = title.split(maxsplit=1)[1]
        item = QTreeItem(title, '', str(code))
        parent(index, level).addChild(item)
        tree_items.append(item)
    
    del tree_items
