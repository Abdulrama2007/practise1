"""Удаление папок не должно менять исходный XML."""

import unittest
from pathlib import Path

from src.shell import Shell
from src.vfs import VFS

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class RemoveTests(unittest.TestCase):
    """Проверить успех, ошибки и изоляцию изменений."""

    def setUp(self):
        """Подготовить новое независимое дерево."""
        self.shell = Shell(VFS(EXAMPLES / "deep.xml"))

    def test_remove_in_memory(self):
        """Удалённая папка исчезает из дерева, но остаётся в XML."""
        path = EXAMPLES / "deep.xml"
        before = path.read_bytes()
        self.assertEqual(self.shell.execute("rmdir /empty"), "")
        self.assertNotIn("empty/", self.shell.execute("ls /"))
        self.assertEqual(path.read_bytes(), before)
        self.assertIn("empty", VFS(path).root.children)

    def test_relative_remove(self):
        """Относительный путь работает из текущей папки."""
        self.shell.execute("cd /home/student")
        self.assertEqual(self.shell.execute("rmdir ./empty/"), "")
        self.assertNotIn("empty/", self.shell.execute("ls"))

    def test_failures(self):
        """Файлы, непустые папки и корень удалять нельзя."""
        commands = [
            "rmdir /home", "rmdir /data.bin", "rmdir missing",
            "rmdir /", "rmdir", "rmdir /home /empty", "rmdir -p /home",
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assertTrue(
                    self.shell.execute(command).startswith("Ошибка:"),
                )
        self.assertIn("home", self.shell.vfs.root.children)

    def test_current_directory(self):
        """Текущую пустую папку нельзя удалить из-под сеанса."""
        self.shell.execute("cd /empty")
        self.assertTrue(self.shell.execute("rmdir .").startswith("Ошибка:"))
        self.assertEqual(self.shell.execute("pwd"), "/empty")
