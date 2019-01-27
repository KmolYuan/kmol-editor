# -*- coding: utf-8 -*-

"""Tree widget transformer."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from typing import (
    Tuple,
    List,
    Dict,
    Union,
)
import yaml
from core.QtModules import (
    QTreeWidgetItem,
    QTreeItem,
    QFileInfo,
    QDir,
    QIcon,
    QPixmap,
)
from core.data_structure import DataDict
from core.info import __version__
from .misc import (
    file_suffix,
    node_getpath,
    getpath,
)
from .text import parse_text
from .markdown import (
    CODE_STYLE,
    parse_markdown,
    pandoc_markdown,
)

__all__ = [
    'getpath',
    'parse',
    'save_file',
    'file_suffix',
    'file_icon',
    'CODE_STYLE',
    'pandoc_markdown',
    'SUPPORT_FILE_FORMATS',
]


NodeDict = Dict[str, Union[int, str, List['NodeDict']]]
YMLData = Dict[str, Union[int, List[NodeDict], Dict[int, str]]]

_SUPPORT_FILE_SUFFIX: Tuple[str, ...] = (
    'kmol',
    'md',
    'html',
    'py',
    'tex',
    'txt',
)
_SUPPORT_FORMAT: Tuple[str, ...] = (
    "Kmol Project",
    "Markdown",
    "HTML",
    "Python script",
    "Latex",
    "Text file",
    "All files",
)
SUPPORT_FILE_FORMATS = ';;'.join(
    "{} (*.{})".format(name, suffix_text if suffix_text else '*')
    for name, suffix_text in zip(_SUPPORT_FORMAT, _SUPPORT_FILE_SUFFIX + ('',))
)


def file_icon(file_type: str) -> QIcon:
    """Return icon by file format."""
    return QIcon(QPixmap(f":/icons/{file_type}.png"))


def _write_tree(proj_name: str, root_node: QTreeWidgetItem, data: DataDict):
    """Write to YAML file."""
    yml_data: YMLData = {}
    my_codes: List[int] = []

    def add_node(node: QTreeWidgetItem) -> NodeDict:
        code_int = int(node.text(2))
        node_dict: NodeDict = {
            'code': code_int,
            'name': node.text(0),
            'path': node.text(1),
            'sub': [],
        }
        if file_suffix(node.text(1)) not in _SUPPORT_FILE_SUFFIX:
            my_codes.append(code_int)
        if QFileInfo(QDir(node_getpath(node.parent())).filePath(node.text(1))).isFile():
            # Files do not need to make a copy.
            return node_dict
        for j in range(node.childCount()):
            node_dict['sub'].append(add_node(node.child(j)))
        return node_dict

    root_code = int(root_node.text(2))
    yml_data['description'] = root_code

    yml_data['node'] = []
    for i in range(root_node.childCount()):
        yml_data['node'].append(add_node(root_node.child(i)))

    yml_data['data'] = {root_code: data[root_code]}
    for code in my_codes:
        yml_data['data'][code] = data[code]

    data.save_all()

    yml_str = (
        f"# Generated by Kmol editor {__version__}\n\n" +
        yaml.dump(yml_data, default_flow_style=False)
    )
    with open(proj_name, 'w', encoding='utf-8') as f:
        f.write(yml_str)

    print("Saved: {}".format(proj_name))


def _parse_tree(root_node: QTreeWidgetItem, data: DataDict):
    """Parse in to tree widget."""
    try:
        with open(root_node.text(1), encoding='utf-8') as f:
            yml_data: YMLData = yaml.load(f)
    except FileNotFoundError:
        return

    parse_list: List[QTreeWidgetItem] = []

    root_node.setText(2, str(yml_data['description']))
    data.update(yml_data['data'])

    def add_node(node_dict: NodeDict) -> QTreeWidgetItem:
        """Add node in to tree widget."""
        name: str = node_dict['name']
        code_int: int = node_dict['code']
        path: str = node_dict['path']
        node = QTreeItem(name, path, str(code_int))
        if name.startswith('@'):
            node.setIcon(0, file_icon("python"))
            data.add_macro(name[1:], code_int)
        suffix_text = file_suffix(path)
        if suffix_text:
            parse_list.append(node)
        elif path:
            node.setIcon(0, file_icon("directory"))
        subs: List[NodeDict] = node_dict['sub']
        for sub in subs:
            node.addChild(add_node(sub))
        return node

    child_node_dicts: List[NodeDict] = yml_data['node']
    for child_node_dict in child_node_dicts:
        root_node.addChild(add_node(child_node_dict))

    for node_item in parse_list:
        parse(node_item, data)

    data.save_all()


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
        content_text = my_content[i]
        if content_text.endswith("@others"):
            preffix = content_text[:-len("@others")]
            my_content[i] = '\n\n'.join(preffix + t for t in text_data)
    my_content = '\n'.join(my_content)
    path_text = QFileInfo(node.text(1)).fileName()
    if path_text and not all_saved:
        suffix_text = QFileInfo(path_text).suffix()
        if suffix_text == 'kmol':
            # Save project.
            _write_tree(node.text(1), node, data)
        else:
            # File path.
            file_path = QDir(QFileInfo(node_getpath(node)).absolutePath())
            if not file_path.exists():
                file_path.mkpath('.')
                print("Create Folder: {}".format(file_path.absolutePath()))
            file_name = file_path.filePath(path_text)

            if suffix_text in _SUPPORT_FILE_SUFFIX:
                # Add end new line.
                if my_content and (my_content[-1] != '\n'):
                    my_content += '\n'
                try:
                    with open(file_name, 'w', encoding='utf-8') as f:
                        f.write(my_content)
                except UnicodeError:
                    print(f"Unicode Error in: {file_name}")
                else:
                    print(f"Saved: {file_name}")
            elif suffix_text:
                print(f"Ignore file: {file_name}")

    return my_content, all_saved


def parse(node: QTreeWidgetItem, data: DataDict):
    """Parse file to tree format."""
    node.takeChildren()
    file_name = getpath(node)
    suffix_text = file_suffix(file_name)
    if node.text(2):
        code = int(node.text(2))
    else:
        code = data.new_num()
        node.setText(2, str(code))
    if suffix_text == 'md':
        # Markdown
        node.setIcon(0, file_icon("markdown"))
        parse_markdown(file_name, node, code, data)
    elif suffix_text == 'py':
        # Python script
        node.setIcon(0, file_icon("python"))
        parse_text(file_name, code, data)
    elif suffix_text == 'html':
        # TODO: Need to parse HTML (reveal.js index.html)
        node.setIcon(0, file_icon("html"))
        parse_text(file_name, code, data)
    elif suffix_text == 'kmol':
        # Kmol project
        node.setIcon(0, file_icon("kmol"))
        _parse_tree(node, data)
    else:
        # Text files and Python scripts.
        node.setIcon(0, file_icon("txt"))
        parse_text(file_name, code, data)
    print("Loaded: {}".format(node.text(1)))
