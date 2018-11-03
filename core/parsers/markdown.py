# -*- coding: utf-8 -*-

"""Markdown file parser."""

__author__ = "Yuan Chang"
__copyright__ = "Copyright (C) 2018"
__license__ = "AGPL"
__email__ = "pyslvs@gmail.com"

from core.QtModules import QTreeWidgetItem, QTreeItem
from core.data_structure import DataDict


def parse_markdown(
    filename: str,
    node: QTreeWidgetItem,
    code: int,
    data: DataDict
):
    """Parse Markdown file to tree nodes."""
    try:
        f = open(filename, encoding='utf-8')
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
