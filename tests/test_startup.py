"""Проверки выполнения стартовых скриптов."""

import tempfile
import unittest
from pathlib import Path

from src.config import parse_args
from src.shell import Shell
from src.startup import execute_lines, run_script


class StartupTests(unittest.TestCase):
    """Проверить ошибки, порядок строк и завершение."""

    def test_continue_after_error(self):
        """Ошибка не мешает выполнению последующей команды."""
        output = []
        count = execute_lines(Shell(), ["bad", "ls"], output.append)
        self.assertEqual(count, 1)
        self.assertIn("ls", output[-2])

    def test_exit_stops_script(self):
        """Команды после exit не выполняются."""
        output = []
        execute_lines(Shell(), ["exit", "ls"], output.append)
        self.assertEqual(len(output), 2)

    def test_comments(self):
        """Пустые строки и комментарии пропускаются."""
        output = []
        execute_lines(Shell(), ["# comment", " ", "exit"], output.append)
        self.assertEqual(len(output), 2)

    def test_missing_script(self):
        """Отсутствующий файл возвращает понятную ошибку."""
        with tempfile.TemporaryDirectory() as folder:
            output = []
            result = run_script(Shell(), Path(folder) / "no", output.append)
        self.assertEqual(result, 1)
        self.assertIn("Ошибка", output[0])

    def test_bom(self):
        """Скрипты Windows с UTF-8 BOM поддерживаются."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "start.txt"
            path.write_text("exit", encoding="utf-8-sig")
            shell = Shell()
            self.assertEqual(run_script(shell, path, lambda text: None), 0)
            self.assertFalse(shell.running)

    def test_parameters(self):
        """Оба пути передаются через командную строку."""
        args = parse_args(["--vfs", "a.xml", "--startup", "b.txt"])
        self.assertEqual((args.vfs, args.startup), ("a.xml", "b.txt"))
