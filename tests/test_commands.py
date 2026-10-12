"""Основные команды, пути и режимы вывода."""

import unittest
from pathlib import Path

from src.shell import Shell
from src.vfs import VFS

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class CommandTests(unittest.TestCase):
    """Проверить поведение полноценной оболочки."""

    def setUp(self):
        """Открыть независимое дерево для каждой проверки."""
        self.shell = Shell(VFS(EXAMPLES / "deep.xml"))

    def test_ls(self):
        """ls скрывает точечные имена, -a показывает их."""
        self.assertEqual(self.shell.execute("ls"), "data.bin\nempty/\nhome/")
        self.assertIn(".hidden", self.shell.execute("ls -a"))

    def test_ls_file(self):
        """ls принимает путь к файлу."""
        self.assertEqual(self.shell.execute("ls /data.bin"), "data.bin")

    def test_cd_pwd(self):
        """Переходы меняют путь; без аргументов cd ведёт в корень."""
        self.shell.execute("cd /home/student/documents")
        self.assertEqual(self.shell.execute("pwd"), "/home/student/documents")
        self.shell.execute("cd ../empty")
        self.assertEqual(self.shell.execute("pwd"), "/home/student/empty")
        self.shell.execute("cd")
        self.assertEqual(self.shell.execute("pwd"), "/")

    def test_cd_failure_keeps_cwd(self):
        """Неудачный переход не меняет текущую папку."""
        self.shell.execute("cd /home")
        self.assertTrue(self.shell.execute("cd missing").startswith("Ошибка:"))
        self.assertEqual(self.shell.execute("pwd"), "/home")

    def test_du_bytes(self):
        """du суммирует UTF-8-байты и двоичные данные."""
        self.assertEqual(self.shell.execute("du -s /"), "35\t/")
        self.assertEqual(self.shell.execute("du /data.bin"), "4\t/data.bin")
        self.assertIn("12\t/home/student/documents/tasks",
                      self.shell.execute("du /home"))

    def test_invalid_commands(self):
        """Неверные режимы команд возвращают ошибку."""
        commands = [
            "ls -z", "ls a b", "cd a b", "cd /data.bin",
            "du -z", "du a b", "du missing", "pwd extra",
            "vfs-init extra", "exit extra", "ls -a -a",
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assertTrue(
                    self.shell.execute(command).startswith("Ошибка:"),
                )

    def test_commands_do_not_write_xml(self):
        """Просмотр и навигация не меняют физический XML."""
        path = EXAMPLES / "deep.xml"
        before = path.read_bytes()
        for command in ("ls", "cd home", "pwd", "du"):
            self.shell.execute(command)
        self.assertEqual(path.read_bytes(), before)
