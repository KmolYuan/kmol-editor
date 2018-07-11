# -*- coding: utf-8 -*-

"""Tree widget transformer.

Pointer problem: Hash value.
"""

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
    QTreeWidgetItem,
    QFileInfo,
    QDir,
)
from core.data_structure import DataDict
from core.info import __version__


SUPPORT_FILE_SUFFIX = [
    'kmol',
    'md',
    'html',
    'py',
    'bib',
    'txt',
]
SUPPORTFORMAT = [
    "Kmol Project",
    "Markdown",
    "HTML",
    "Python script",
    "Bibtex",
    "Text file",
    "All files",
]
SUPPORT_FILE_FORMATS = ';;'.join(
    "{} (*.{})".format(name, suffix if suffix else '*')
    for name, suffix in zip(SUPPORTFORMAT, SUPPORT_FILE_SUFFIX + [''])
)


def _suffix(filename: str) -> str:
    """Return suffix of file name."""
    return QFileInfo(filename).suffix()


def _getpath(node: QTreeWidgetItem) -> str:
    """Get the path from parent."""
    path = node.text(1)
    parent = node.parent()
    if not parent:
        if _suffix(path) == 'kmol':
            return QFileInfo(path).absolutePath()
        else:
            return path
    return QFileInfo(QDir(_getpath(parent)), path + '/' if path else '').absolutePath()


def _tree_write(projname: str, root_node: QTreeWidgetItem, data: DataDict):
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
        if (
            (_suffix(node.text(1)) in SUPPORT_FILE_SUFFIX) or
            (QFileInfo(node.text(1)).fileName() == 'Makefile')
        ):
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


def saveFile(node: QTreeWidgetItem, data: DataDict) -> str:
    """Recursive to all the contents of nodes."""
    text_data = []
    for i in range(node.childCount()):
        text_data.append(saveFile(node.child(i), data))
    my_content_list = data[int(node.text(2))].splitlines()
    for i in range(len(my_content_list)):
        text = my_content_list[i]
        if text.endswith("@others"):
            preffix = text[:-len("@others")]
            my_content_list[i] = '\n\n'.join(preffix + t for t in text_data)
    my_content_list = '\n'.join(my_content_list)
    path_text = QFileInfo(node.text(1)).fileName()
    if path_text:
        suffix = QFileInfo(path_text).suffix()
        if suffix in ('md', 'html', 'py', 'txt'):
            #Save text files.
            filepath = QDir(QFileInfo(_getpath(node)).absolutePath())
            if not filepath.exists():
                filepath.mkpath('.')
                print("Create Folder: {}".format(filepath.absolutePath()))
            filename = filepath.filePath(path_text)
            #Add end new line.
            if my_content_list[-1] != '\n':
                my_content_list += '\n'
            with open(filename, 'w') as f:
                f.write(my_content_list)
            print("Saved: {}".format(filename))
        elif suffix == 'kmol':
            #Save project.
            _tree_write(node.text(1), node, data)
    return my_content_list


def _tree_parse(root_node: QTreeWidgetItem, data: DataDict):
    """Parse in to tree widget."""
    tree = ElementTree(file=root_node.text(1))
    root = tree.getroot()
    root_node.setText(2, root.attrib['code'])
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
            parse_list.append(sub)
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
    
    for node in parse_list:
        parse(node, data)
    
    data.saveAll()


def parse(node: QTreeWidgetItem, data: DataDict):
    """Parse file to tree format."""
    node.takeChildren()
    parent = node.parent()
    if parent:
        filename = QDir(_getpath(parent)).filePath(QFileInfo(node.text(1)).fileName())
    else:
        filename = node.text(1)
    suffix = _suffix(filename)
    if node.text(2):
        code = int(node.text(2))
    else:
        code = data.newNum()
        node.setText(2, str(code))
    if suffix == 'md':
        #Markdown
        _parseMarkdown(filename, node, code, data)
    elif suffix == 'html':
        #TODO: Need to parse HTML (reveal.js index.html)
        _parseText(filename, code, data)
    elif suffix == 'kmol':
        #Kmol project
        _tree_parse(node, data)
    else:
        #Text files and Python scripts.
        _parseText(filename, code, data)
    print("Loaded: {}".format(node.text(1)))


def _parseText(
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


def _parseMarkdown(
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
    
    #Read the first level of title mark.
    #titles = [(line_num, level), ...]
    titles = []
    previous_line = ""
    in_code_block = False
    for line_num, line in enumerate(string_list):
        if line.startswith('```'):
            in_code_block = not in_code_block
        if in_code_block:
            previous_line = line
            continue
        for level, string in enumerate(['===', '---']):
            if not line.startswith(string):
                continue
            if len(set(line)) == 1 and previous_line:
                #Under line with its title.
                titles.append((line_num - 1, level))
        if line:
            prefix = line.split(maxsplit=1)[0]
            if set(prefix) == {'#'}:
                titles.append((line_num, len(prefix) - 1))
        previous_line = line
    
    #Joint nodes.
    if not titles:
        #Plain text.
        data[code] = '\n'.join(string_list)
        return
    if titles[0][0] == 0:
        #Start with line 0.
        data[code] = "@others"
    else:
        data[code] = '\n'.join(string_list[:titles[0][0]])
    tree_items = []
    
    def parent(index: int, level: int) -> QTreeWidgetItem:
        """The parent of current title."""
        for i, (pre_line, pre_level) in reversed(tuple(enumerate(titles[:index]))):
            if pre_level < level:
                return tree_items[i]
        return node
    
    titles_count = len(titles) - 1
    for index, (line_num, level) in enumerate(titles):
        code = data.newNum()
        if index == titles_count:
            doc = string_list[line_num:]
        else:
            doc = string_list[line_num:titles[index + 1][0]]
            if titles[index + 1][1] > level:
                #Has child.
                doc.append('@others')
                doc.append('')
        data[code] = '\n'.join(doc)
        title = doc[0]
        if title.startswith("#"):
            title = title.split(maxsplit=1)[1]
        item = QTreeItem(title, '', str(code))
        parent(index, level).addChild(item)
        tree_items.append(item)
