"""Параметры запуска программы."""

import argparse


def parse_args(argv=None):
    """Прочитать пути VFS/скрипта и режим автоматической проверки."""
    parser = argparse.ArgumentParser(description="Эмулятор: вариант 21")
    parser.add_argument("--vfs", help="путь к XML-файлу VFS")
    parser.add_argument("--startup", help="путь к скрипту эмулятора")
    parser.add_argument(
        "--headless", action="store_true",
        help="выполнить команды без окна (для тестов)",
    )
    return parser.parse_args(argv)


def describe_config(args):
    """Сформировать обязательный отладочный вывод настроек."""
    return (
        f"VFS: {args.vfs or '(по умолчанию в памяти)'}\n"
        f"Стартовый скрипт: {args.startup or '(не задан)'}\n"
        f"Режим: {'без окна' if args.headless else 'GUI'}"
    )
