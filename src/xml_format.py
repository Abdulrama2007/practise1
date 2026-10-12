"""Проверка имён и кодирование содержимого в XML."""

import base64
from xml.etree import ElementTree as ET


def validate_name(name):
    """Имена не должны содержать разделители и пробелы."""
    if not name or name in (".", ".."):
        raise ValueError("недопустимое имя файла или папки")
    if "/" in name or "\\" in name or any(c.isspace() for c in name):
        raise ValueError(f"имя содержит разделитель или пробел: {name}")


def decode_content(element):
    """Прочитать UTF-8 или строгий base64 с переносами строк."""
    encoding = element.get("encoding", "utf-8")
    text = element.text or ""
    if encoding == "utf-8":
        return text.encode("utf-8")
    if encoding == "base64":
        return base64.b64decode("".join(text.split()), validate=True)
    raise ValueError(f"неподдерживаемая кодировка: {encoding}")


def encode_node(node):
    """Преобразовать узел дерева в элемент XML."""
    tag = "directory" if node.is_dir else "file"
    element = ET.Element(tag, {"name": node.name})
    if node.is_dir:
        for child in node.children.values():
            element.append(encode_node(child))
    else:
        element.set("encoding", "base64")
        element.text = base64.b64encode(node.data).decode("ascii")
    return element


def serialize_vfs(root, name):
    """Создать XML в исходной схеме, сохраняя байты файлов."""
    element = ET.Element("vfs", {"name": name})
    for child in root.children.values():
        element.append(encode_node(child))
    ET.indent(element, space="  ")
    return ET.tostring(
        element, encoding="utf-8", xml_declaration=True,
    ).decode("utf-8")
