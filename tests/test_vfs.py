"""Проверки XML, памяти, путей и сброса VFS."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.vfs import VFS
from src.xml_format import serialize_vfs

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class VfsTests(unittest.TestCase):
    """Проверить модель без реальных папок пользователя."""

    def test_minimal(self):
        """Пустая VFS корректно загружается."""
        self.assertEqual(VFS(EXAMPLES / "minimal.xml").root.size(), 0)

    def test_binary(self):
        """Base64 восстанавливает байты, а не длину строки XML."""
        vfs = VFS(EXAMPLES / "multiple.xml")
        self.assertEqual(vfs.resolve("b.bin")[0].data, bytes(range(4)))
        self.assertEqual(vfs.root.size(), 7)

    def test_deep_paths(self):
        """Поддерживается более трёх уровней вложенности."""
        vfs = VFS(EXAMPLES / "deep.xml")
        path = "/home/student/documents/tasks/plan.txt"
        self.assertEqual(vfs.resolve(path)[0].data, b"Learn Python")

    def test_relative_paths(self):
        """Точка и родитель разрешаются относительно текущей папки."""
        vfs = VFS(EXAMPLES / "deep.xml")
        vfs.cwd = "/home/student"
        self.assertEqual(vfs.resolve("../student/./empty")[1],
                         "/home/student/empty")
        self.assertEqual(vfs.resolve("../../../../")[1], "/")

    def test_missing_intermediate(self):
        """Нельзя обходить отсутствующую папку через .. ."""
        with self.assertRaises(ValueError):
            VFS().resolve("/missing/../home")

    def test_file_is_not_directory(self):
        """Компонент файла не может использоваться как папка."""
        with self.assertRaises(ValueError):
            VFS().resolve("/home/readme.txt/..")

    def test_reset_disk(self):
        """vfs-init заменяет XML и сбрасывает текущий путь."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "vfs.xml"
            path.write_bytes((EXAMPLES / "deep.xml").read_bytes())
            vfs = VFS(path)
            vfs.cwd = "/home/student"
            vfs.reset()
            self.assertEqual(vfs.cwd, "/")
            self.assertEqual(VFS(path).name, "default")
            self.assertNotIn("student", path.read_text(encoding="utf-8"))

    def test_reset_failure_keeps_state(self):
        """Ошибка диска не оставляет VFS наполовину сброшенной."""
        vfs = VFS(EXAMPLES / "deep.xml")
        original = vfs.root
        with patch("src.vfs.atomic_write", side_effect=OSError("denied")):
            with self.assertRaises(OSError):
                vfs.reset()
        self.assertIs(vfs.root, original)

    def test_roundtrip(self):
        """XML-сериализация не меняет двоичные и русские данные."""
        original = VFS(EXAMPLES / "deep.xml")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "copy.xml"
            path.write_text(serialize_vfs(original.root, original.name),
                            encoding="utf-8")
            loaded = VFS(path)
        self.assertEqual(original.root.size(), loaded.root.size())
        self.assertEqual(loaded.resolve("/data.bin")[0].data, bytes(range(4)))

    def test_invalid_documents(self):
        """Ошибки схемы, имён, кодировки и повторов не скрываются."""
        documents = [
            "<bad />",
            '<vfs><file name="a" encoding="base64">???</file></vfs>',
            '<vfs><directory name="../bad" /></vfs>',
            '<vfs><file name="a" /><file name="a" /></vfs>',
            '<vfs><other name="a" /></vfs>',
            '<vfs><file name="a" encoding="bad" /></vfs>',
            '<vfs><file name="a"><file name="b" /></file></vfs>',
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.xml"
            for document in documents:
                with self.subTest(document=document):
                    path.write_text(document, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        VFS(path)
