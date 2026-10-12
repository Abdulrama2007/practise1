"""Проверить реальный запуск отдельного процесса Python."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def launch(*args, text=None):
    """Запустить headless-интерфейс как пользователь."""
    return subprocess.run(
        [sys.executable, "-m", "src.main", "--headless", *args],
        cwd=ROOT, input=text, capture_output=True, text=True,
        encoding="utf-8", timeout=10,
    )


class CliTests(unittest.TestCase):
    """Проверить коды возврата, сообщения и полный сценарий."""

    def test_demo(self):
        """Демонстрационный скрипт исполняется без ошибок."""
        result = launch("--vfs", "examples/deep.xml", "--startup",
                        "examples/demo.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("35\t/", result.stdout)
        self.assertNotIn("Ошибка:", result.stdout)

    def test_invalid_xml(self):
        """Неверный XML выводит сообщение без traceback."""
        result = launch("--vfs", "examples/invalid.xml", text="pwd\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Ошибка загрузки VFS", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_vfs(self):
        """Несуществующий XML не подменяется молча новым деревом."""
        with tempfile.TemporaryDirectory() as folder:
            result = launch("--vfs", str(Path(folder) / "absent.xml"))
        self.assertEqual(result.returncode, 1)

    def test_missing_startup(self):
        """Ошибка чтения сценария отражается в коде возврата."""
        result = launch("--startup", "examples/absent.txt")
        self.assertEqual(result.returncode, 1)
        self.assertIn("не удалось прочитать скрипт", result.stdout)

    def test_stdin(self):
        """Без скрипта команды читаются из стандартного ввода."""
        result = launch(text="cd home\npwd\nexit\nunknown\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("/home", result.stdout)
        self.assertNotIn("unknown", result.stdout)

    def test_full_scenario(self):
        """Все команды работают, ошибки не прерывают сценарий."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "work.xml"
            path.write_bytes((ROOT / "examples/deep.xml").read_bytes())
            result = launch("--vfs", str(path), "--startup",
                            "examples/all_commands.txt")
            self.assertIn('name="default"', path.read_text("utf-8"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("До свидания!", result.stdout)
        self.assertNotIn("unknown_after_exit", result.stdout)
