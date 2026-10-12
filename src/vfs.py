"""Виртуальные файлы и папки: состояние хранится в памяти."""

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

from src.xml_format import decode_content, validate_name


@dataclass
class Node:
    """Папка с дочерними узлами либо файл с байтами содержимого."""

    name: str
    is_dir: bool = True
    data: bytes = b""
    children: dict = field(default_factory=dict)

    def size(self):
        """Вернуть сумму байтов содержимого, без XML-разметки."""
        if not self.is_dir:
            return len(self.data)
        return sum(child.size() for child in self.children.values())


def parse_node(element):
    """Построить узел и проверить XML-схему и уникальность имён."""
    if element.tag not in ("directory", "file"):
        raise ValueError(f"неизвестный XML-элемент: {element.tag}")
    name = element.get("name", "")
    validate_name(name)
    allowed = {"name"} if element.tag == "directory" else {"name", "encoding"}
    if set(element.attrib) - allowed:
        raise ValueError(f"неизвестные атрибуты: {name}")
    node = Node(name, element.tag == "directory")
    if not node.is_dir:
        if len(element):
            raise ValueError(f"файл содержит вложенные элементы: {name}")
        node.data = decode_content(element)
        return node
    for child in element:
        add_child(node, parse_node(child))
    return node


def add_child(parent, child):
    """Добавить ребёнка, не допуская повторяющихся имён."""
    if child.name in parent.children:
        raise ValueError(f"повторяющееся имя: {child.name}")
    parent.children[child.name] = child


def default_root():
    """Создать исходное дерево: /home, /empty и приветственный файл."""
    root = Node("")
    home = Node("home")
    home.children["readme.txt"] = Node(
        "readme.txt", False, "Добро пожаловать!\n".encode("utf-8"),
    )
    root.children = {"home": home, "empty": Node("empty")}
    return root


def atomic_write(path, text):
    """Заменить исходный XML; при ошибке сохранить старый файл."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=".vfs-", suffix=".xml", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class VFS:
    """Дерево файлов, текущий путь и путь исходного XML."""

    def __init__(self, source=None):
        """Загрузить XML либо создать дерево по умолчанию."""
        self.source = Path(source).resolve() if source else None
        self.root = default_root()
        self.name = "default"
        self.cwd = "/"
        if self.source:
            self.load()

    def load(self):
        """Прочитать XML в память без распаковки файлов."""
        element = ET.fromstring(self.source.read_bytes())
        if element.tag != "vfs" or set(element.attrib) - {"name"}:
            raise ValueError("ожидается корневой элемент <vfs name=...>")
        root = Node("")
        for child in element:
            add_child(root, parse_node(child))
        self.root = root
        self.name = element.get("name", "unnamed")

    def resolve(self, path="."):
        """Найти узел; поддержать /, ., .. и относительные пути."""
        if not path:
            raise ValueError("пустой путь")
        absolute = path if path.startswith("/") else self.cwd + "/" + path
        stack = [self.root]
        names = []
        for part in absolute.split("/"):
            if not stack[-1].is_dir:
                raise ValueError("компонент пути не является папкой")
            if not part or part == ".":
                continue
            if part == "..":
                if names:
                    stack.pop()
                    names.pop()
                continue
            if part not in stack[-1].children:
                raise ValueError(f"путь не найден: {path}")
            stack.append(stack[-1].children[part])
            names.append(part)
        return stack[-1], "/" + "/".join(names)

    def reset(self):
        """Сбросить VFS и её XML, если он задан при запуске."""
        from src.xml_format import serialize_vfs

        root = default_root()
        if self.source:
            atomic_write(self.source, serialize_vfs(root, "default"))
        self.root = root
        self.cwd = "/"
        self.name = "default"
