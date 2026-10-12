"""Точка входа графического эмулятора и режима проверки."""

import sys

from src.config import describe_config, parse_args
from src.shell import Shell
from src.startup import execute_lines, run_script


def main(argv=None):
    """Прочитать настройки и запустить выбранный интерфейс."""
    args = parse_args(argv)
    debug = describe_config(args)
    print(debug)
    shell = Shell()
    if args.headless:
        if args.startup:
            return bool(run_script(shell, args.startup, print))
        return bool(execute_lines(shell, sys.stdin, print))
    try:
        from src.gui import Terminal

        terminal = Terminal(shell)
        terminal.write(debug)
        terminal.run(args.startup)
    except (ImportError, RuntimeError) as error:
        print(f"Ошибка GUI: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
