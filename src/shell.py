"""Разбор команд и выполнение действий эмулятора."""


class Shell:
    """Минимальный обработчик команд первого этапа."""

    def __init__(self):
        """Создать состояние сеанса."""
        self.running = True

    def execute(self, line):
        """Разобрать строку по пробелам и вернуть ответ."""
        parts = line.split()
        if not parts:
            return ""
        command, *args = parts
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
