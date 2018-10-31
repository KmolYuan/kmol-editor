# -*- coding: utf-8 -*-

"""Tree widget transformer.

Pointer problem: Hash value.
"""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import Tuple
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

SUPPORT_FILE_SUFFIX = (
    'kmol',
    'md',
    'html',
    'py',
    'tex',
    'txt',
)
SUPPORTFORMAT = (
    "Kmol Project",
    "Markdown",
    "HTML",
    "Python script",
    "Latex",
    "Text file",
    "All files",
)
SUPPORT_FILE_FORMATS = ';;'.join(
    "{} (*.{})".format(name, suffix if suffix else '*')
    for name, suffix in zip(SUPPORTFORMAT, SUPPORT_FILE_SUFFIX + ('',))
)


def _suffix(filename: str) -> str:
    """Return suffix of file name."""
    return QFileInfo(filename).suffix()


def _getpath(node: QTreeWidgetItem) -> str:
    """Recursive return the path of the node."""
    path = node.text(1)
    parent = node.parent()
    if not parent:
        if _suffix(path) == 'kmol':
            return QFileInfo(path).absolutePath()
        else:
            return path
    return QDir(_getpath(parent)).filePath(path)


def getpath(node: QTreeWidgetItem) -> str:
    """Get the path of current node."""
    parent = node.parent()
    filename = node.text(1)
    if parent:
        return QFileInfo(QDir(_getpath(parent)).filePath(filename)).absoluteFilePath()
    return filename


def _write_tree(projname: str, root_node: QTreeWidgetItem, data: DataDict):
    """Write to XML file."""
    root = Element('kmolroot', {
        'version': __version__,
        'code': root_node.text(2),
    })

    # The strings that need to save.
    codes = set()

    def add_node(node: QTreeWidgetItem, n_root: Element):
        attr = {
            'name': node.text(0),
            'path': node.text(1),
            'code': node.text(2),
        }
        sub = SubElement(n_root, 'node', attr)
        if QFileInfo(QDir(_getpath(node.parent())).filePath(node.text(1))).isFile():
            # Files do not need to make a copy.
            return
        codes.add(attr['code'])
        for j in range(node.childCount()):
            add_node(node.child(j), sub)

    for i in range(root_node.childCount()):
        add_node(root_node.child(i), root)
    data_node = SubElement(root, 'data-structure')
    for code, context in data.items():
        if str(code) not in codes:
            continue
        context_node = SubElement(data_node, 'data', {'code': str(code)})
        context_node.text = context
    data.save_all()

    xml_str = minidom.parseString(tostring(root)).toprettyxml(indent=" " * 4)
    with open(projname, 'w', encoding='utf8') as f:
        f.write(xml_str)

    print("Saved: {}".format(projname))


def save_file(node: QTreeWidgetItem, data: DataDict) -> Tuple[str, bool]:
    """Recursive to all the contents of nodes."""
    text_data = []
    all_saved = data.is_saved(int(node.text(2)))
    for i in range(node.childCount()):
        doc, saved = save_file(node.child(i), data)
        text_data.append(doc)
        all_saved &= saved
    my_content = data[int(node.text(2))].splitlines()
    for i in range(len(my_content)):
        text = my_content[i]
        if text.endswith("@others"):
            preffix = text[:-len("@others")]
            my_content[i] = '\n\n'.join(preffix + t for t in text_data)
    my_content = '\n'.join(my_content)
    path_text = QFileInfo(node.text(1)).fileName()
    if path_text and not all_saved:
        suffix = QFileInfo(path_text).suffix()
        if suffix == 'kmol':
            # Save project.
            _write_tree(node.text(1), node, data)
        elif suffix in SUPPORT_FILE_SUFFIX:
            # Save text files.
            filepath = QDir(QFileInfo(_getpath(node)).absolutePath())
            if not filepath.exists():
                filepath.mkpath('.')
                print("Create Folder: {}".format(filepath.absolutePath()))
            filename = filepath.filePath(path_text)
            # Add end new line.
            if my_content and (my_content[-1] != '\n'):
                my_content += '\n'
            with open(filename, 'w', encoding='utf8') as f:
                f.write(my_content)
            print("Saved: {}".format(filename))
    return my_content, all_saved


def _parse_tree(root_node: QTreeWidgetItem, data: DataDict):
    """Parse in to tree widget."""
    tree = ElementTree(file=root_node.text(1))
    root = tree.getroot()
    root_node.setText(2, root.attrib['code'])
    data[int(root.attrib['code'])] = ""

    parse_list = []

    def add_node(n_node: Element, item_root: QTreeWidgetItem):
        """Add node in to tree widget."""
        attr = n_node.attrib
        sub = QTreeItem(attr['name'], attr['path'], attr['code'])
        item_root.addChild(sub)
        suffix = _suffix(attr['path'])
        code = int(attr['code'])
        data[code] = ""
        if attr['name'].startswith('@'):
            data.add_macro(attr['name'][1:], code)
        if suffix:
            parse_list.append(sub)
        else:
            for n_child in n_node:
                if n_child.tag == 'node':
                    add_node(n_child, sub)

    for child in root:
        if child.tag == 'data-structure':
            for d in child:
                if d.tag == 'data':
                    data[int(d.attrib['code'])] = d.text or ''
        elif child.tag == 'node':
            add_node(child, root_node)

    for node in parse_list:
        parse(node, data)

    data.save_all()


def parse(node: QTreeWidgetItem, data: DataDict):
    """Parse file to tree format."""
    node.takeChildren()
    filename = getpath(node)
    suffix = _suffix(filename)
    if node.text(2):
        code = int(node.text(2))
    else:
        code = data.new_num()
        node.setText(2, str(code))
    if suffix == 'md':
        # Markdown
        _parse_markdown(filename, node, code, data)
    elif suffix == 'html':
        # TODO: Need to parse HTML (reveal.js index.html)
        _parse_text(filename, code, data)
    elif suffix == 'kmol':
        # Kmol project
        _parse_tree(node, data)
    else:
        # Text files and Python scripts.
        _parse_text(filename, code, data)
    print("Loaded: {}".format(node.text(1)))


def _parse_text(
    filename: str,
    code: int,
    data: DataDict
):
    """Just store file content to data structure."""
    try:
        f = open(filename, 'r', encoding='utf8')
    except FileNotFoundError as e:
        data[code] = str(e)
        return

    with f:
        doc = f.read()
    data[code] = doc


def _parse_markdown(
    filename: str,
    node: QTreeWidgetItem,
    code: int,
    data: DataDict
):
    """Parse Markdown file to tree nodes."""
    try:
        f = open(filename, 'r', encoding='utf8')
    except FileNotFoundError as e:
        data[code] = str(e)
        return

    with f:
        string_list = f.read().split('\n')

    # Read the first level of title mark.
    # titles = [(line_num, level), ...]
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
            if not line.startswith(string) or previous_line.startswith(" "):
                continue
            if len(set(line)) == 1 and previous_line:
                # Under line with its title.
                titles.append((line_num - 1, level))
        if len(set(line)) > 1:
            prefix = line.split(maxsplit=1)[0]
            if set(prefix) == {'#'}:
                titles.append((line_num, len(prefix) - 1))
        previous_line = line

    # Joint nodes.
    if not titles:
        # Plain text.
        data[code] = '\n'.join(string_list)
        return
    if titles[0][0] == 0:
        # Start with line 0.
        data[code] = "@others"
    else:
        data[code] = '\n'.join(string_list[:titles[0][0]])
    tree_items = []

    def parent(t_index: int, t_level: int) -> QTreeWidgetItem:
        """The parent of current title."""
        for i, (pre_line, pre_level) in reversed(tuple(enumerate(titles[:t_index]))):
            if pre_level < t_level:
                return tree_items[i]
        return node

    titles_count = len(titles) - 1
    for index, (line_num, level) in enumerate(titles):
        code = data.new_num()
        if index == titles_count:
            doc = string_list[line_num:]
        else:
            doc = string_list[line_num:titles[index + 1][0]]
            if titles[index + 1][1] > level:
                # Has child.
                doc.append('@others')
                doc.append('')
        data[code] = '\n'.join(doc)
        title = doc[0]
        if title.startswith("#"):
            title = title.split(maxsplit=1)[1]
        item = QTreeItem(title, '', str(code))
        parent(index, level).addChild(item)
        tree_items.append(item)
