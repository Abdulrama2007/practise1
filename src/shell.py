"""Простой парсер и диспетчер команд эмулятора."""

import getpass
import socket

from src.commands import (
    change_directory, current_directory, disk_usage, initialize_vfs,
    list_files, require_no_args,
)
from src.vfs import VFS


class Shell:
    """Связать команды с VFS и состоянием интерактивного сеанса."""

    def __init__(self, vfs=None):
        """Подключить дерево файлов и зарегистрировать команды."""
        self.running = True
        self.vfs = vfs if vfs is not None else VFS()
        self.user = getpass.getuser()
        self.host = socket.gethostname()
        self.commands = {
            "ls": list_files,
            "cd": change_directory,
            "pwd": current_directory,
            "du": disk_usage,
            "vfs-init": initialize_vfs,
        }

    @property
    def prompt(self):
        """Показать пользователя, компьютер и виртуальный путь."""
        return f"{self.user}@{self.host}:{self.vfs.cwd}$"

    def execute(self, line):
        """Разобрать строку по пробелам, выполнить её, вернуть ответ."""
        parts = line.split()
        if not parts:
            return ""
        command, *args = parts
        try:
            if command == "exit":
                require_no_args(args)
                self.running = False
                return "До свидания!"
            if command not in self.commands:
                raise ValueError(f"неизвестная команда: {command}")
            return self.commands[command](self.vfs, args)
        except (ValueError, OSError, RecursionError) as error:
            return f"Ошибка: {command}: {error}"
