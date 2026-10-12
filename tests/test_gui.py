"""Проверки обработчиков GUI без графического дисплея."""

import unittest
from unittest.mock import MagicMock

from src.gui import Terminal
from src.shell import Shell


class GuiHandlerTests(unittest.TestCase):
    """Проверить связь ввода, обработчика команды и состояния окна."""

    def setUp(self):
        """Заменить только виджеты; Shell остаётся настоящим."""
        self.terminal = Terminal.__new__(Terminal)
        self.terminal.shell = Shell()
        self.terminal.entry = MagicMock()
        self.terminal.root = MagicMock()
        self.terminal.prompt = MagicMock()
        self.output = []
        self.terminal.write = self.output.append

    def test_navigation_updates_prompt(self):
        """Enter выполняет команду и обновляет приглашение."""
        self.terminal.entry.get.return_value = "cd home"
        self.terminal.submit()
        self.assertEqual(self.terminal.shell.vfs.cwd, "/home")
        self.terminal.prompt.configure.assert_called_once_with(
            text=self.terminal.shell.prompt,
        )
        self.terminal.root.destroy.assert_not_called()

    def test_exit_closes_window(self):
        """exit вызывает закрытие окна."""
        self.terminal.entry.get.return_value = "exit"
        self.terminal.submit()
        self.terminal.root.destroy.assert_called_once()
        self.assertFalse(self.terminal.shell.running)

    def test_error_keeps_window(self):
        """Ошибка команды видна и не закрывает интерфейс."""
        self.terminal.entry.get.return_value = "unknown"
        self.terminal.submit()
        self.assertTrue(self.output[-1].startswith("Ошибка:"))
        self.terminal.root.destroy.assert_not_called()

    def test_missing_script_keeps_window(self):
        """Отсутствующий скрипт не мешает дальнейшему ручному вводу."""
        self.terminal.start_script("examples/missing-startup.txt")
        self.assertTrue(self.output[-1].startswith("Ошибка:"))
        self.terminal.root.destroy.assert_not_called()
