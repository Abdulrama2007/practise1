"""Последовательное выполнение команд из файла или потока."""

from pathlib import Path


def execute_lines(shell, lines, write):
    """Показать ввод/вывод, продолжить после ошибки, учесть exit."""
    errors = 0
    for line in lines:
        if not shell.running:
            break
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        prompt = getattr(shell, "prompt", "$")
        write(f"{prompt} {line}")
        answer = shell.execute(line)
        write(answer)
        errors += answer.startswith("Ошибка:")
    return errors


def run_script(shell, path, write):
    """Прочитать UTF-8-скрипт и сообщить об ошибках чтения."""
    try:
        lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as error:
        write(f"Ошибка: не удалось прочитать скрипт: {error}")
        return 1
    return execute_lines(shell, lines, write)
