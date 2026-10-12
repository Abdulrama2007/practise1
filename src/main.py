"""Точка входа графического эмулятора и режима проверки."""

import sys
from xml.etree.ElementTree import ParseError

from src.config import describe_config, parse_args
from src.shell import Shell
from src.startup import execute_lines, run_script
from src.vfs import VFS


def run_gui(shell, startup, debug):
    """Создать окно и превратить ошибку дисплея в понятное сообщение."""
    import tkinter as tk

    from src.gui import Terminal

    try:
        terminal = Terminal(shell)
        terminal.write(debug)
        terminal.run(startup)
    except tk.TclError as error:
        raise RuntimeError(f"не удалось открыть окно: {error}") from error


def main(argv=None):
    """Прочитать настройки и запустить выбранный интерфейс."""
    args = parse_args(argv)
    debug = describe_config(args)
    print(debug)
    try:
        shell = Shell(VFS(args.vfs))
    except (OSError, ValueError, ParseError, RecursionError) as error:
        print(f"Ошибка загрузки VFS: {error}", file=sys.stderr)
        return 1
    if args.headless:
        if args.startup:
            return bool(run_script(shell, args.startup, print))
        return bool(execute_lines(shell, sys.stdin, print))
    try:
        run_gui(shell, args.startup, debug)
    except (ImportError, RuntimeError) as error:
        print(f"Ошибка GUI: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
