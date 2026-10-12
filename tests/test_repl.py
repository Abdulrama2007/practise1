"""Проверки прототипа первого этапа."""

import unittest

from src.shell import Shell


class ReplTests(unittest.TestCase):
    """Проверить диалог, разбор строки и ошибки."""

    def test_parser(self):
        """Пробелы отделяют команду от аргумента."""
        shell = Shell()
        self.assertEqual(shell.execute("  cd   home  "), "")
        self.assertEqual(shell.execute("pwd"), "/home")

    def test_unknown(self):
        """Незнакомая команда не завершает сеанс."""
        shell = Shell()
        self.assertIn("Ошибка", shell.execute("unknown"))
        self.assertTrue(shell.running)

    def test_invalid_exit(self):
        """Неверный exit не закрывает эмулятор."""
        shell = Shell()
        self.assertIn("Ошибка", shell.execute("exit extra"))
        self.assertTrue(shell.running)

    def test_exit(self):
        """Правильный exit завершает сеанс."""
        shell = Shell()
        shell.execute("exit")
        self.assertFalse(shell.running)

    def test_blank(self):
        """Пустая строка не является ошибкой."""
        self.assertEqual(Shell().execute("   "), "")
