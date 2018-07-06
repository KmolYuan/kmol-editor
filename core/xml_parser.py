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
    path = node.text(1)
    parent = node.parent()
    if not parent:
        return QFileInfo(path).absolutePath()
    return QFileInfo(QDir(getpath(parent)), path + '/' if path else '').absolutePath()


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
            filepath = QDir(QFileInfo(getpath(node)).absolutePath())
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
    print("Loaded: {}".format(projname))


def parse(node: QTreeWidgetItem, data: DataDict):
    """Parse file to tree format."""
    _clearNode(node)
    filename = QDir(getpath(node.parent())).filePath(QFileInfo(node.text(1)).fileName())
    suffix = _suffix(node.text(1))
    code = int(node.text(2))
    if suffix == 'md':
        #Markdown
        _parseMarkdown(filename, node, code, data)
    elif suffix == 'html':
        #TODO: Need to parse HTML (reveal.js index.html)
        _parseText(filename, code, data)
    else:
        #Text files and Python scripts.
        _parseText(filename, code, data)


def _clearNode(node: QTreeWidgetItem):
    """Clear the children of node."""
    if node.childCount():
        parent = node.parent()
        tree_main = node.treeWidget()
        tree_main.setCurrentItem(parent)
        parent.removeChild(node)


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
    
    data[code] = "@others"
    
    #Read the first level of title mark.
    """
    #titles = (
        [0] line_num,
        [1] level,
    )
    """
    titles = []
    previous_line = ""
    line_num = 0
    for line in tuple(string_list):
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
        line_num += 1
    
    #Joint nodes.
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
    
    del tree_items
