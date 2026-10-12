"""Разбор команд и выполнение действий эмулятора."""

from src.vfs import VFS


class Shell:
    """Минимальный обработчик команд первого этапа."""

    def __init__(self, vfs=None):
        """Создать состояние сеанса."""
        self.running = True
        self.vfs = vfs if vfs is not None else VFS()

    def execute(self, line):
        """Разобрать строку по пробелам и вернуть ответ."""
        parts = line.split()
        if not parts:
            return ""
        command, *args = parts
        if command == "vfs-init":
            if args:
                return "Ошибка: vfs-init не принимает аргументы"
            try:
                self.vfs.reset()
            except OSError as error:
                return f"Ошибка: сброс VFS не выполнен: {error}"
            return "VFS сброшена к состоянию по умолчанию"
        if command in ("ls", "cd"):
            if len(args) > 1:
                return "Ошибка: слишком много аргументов"
            return f"Команда: {command}; аргументы: {args}"
        if command == "exit":
            if args:
                return "Ошибка: exit не принимает аргументы"
            self.running = False
            return "До свидания!"
        return f"Ошибка: неизвестная команда: {command}"
