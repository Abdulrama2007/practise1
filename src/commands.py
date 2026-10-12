"""Команды оболочки работают только с виртуальным деревом."""


def parse_path(args, option=None):
    """Прочитать один путь и необязательный поддерживаемый флаг."""
    flags = [item for item in args if item.startswith("-")]
    if any(flag != option for flag in flags) or len(flags) > 1:
        raise ValueError("неподдерживаемый или повторяющийся флаг")
    paths = [item for item in args if not item.startswith("-")]
    if len(paths) > 1:
        raise ValueError("слишком много аргументов")
    return paths[0] if paths else ".", bool(flags)


def require_no_args(args):
    """Отклонить аргументы команды, которая их не принимает."""
    if args:
        raise ValueError("команда не принимает аргументы")


def list_files(vfs, args):
    """ls [-a] [путь]: показать имена, добавляя / для папок."""
    path, show_hidden = parse_path(args, "-a")
    node, canonical = vfs.resolve(path)
    if not node.is_dir:
        return node.name
    items = sorted(node.children.values(), key=lambda child: child.name)
    return "\n".join(
        item.name + ("/" if item.is_dir else "")
        for item in items if show_hidden or not item.name.startswith(".")
    )


def change_directory(vfs, args):
    """cd [путь]: сменить папку; без аргументов перейти в корень."""
    path, unused = parse_path(args)
    node, canonical = vfs.resolve(path if args else "/")
    if not node.is_dir:
        raise ValueError("указанный путь не является папкой")
    vfs.cwd = canonical
    return ""


def current_directory(vfs, args):
    """pwd: вернуть абсолютный путь текущей папки."""
    require_no_args(args)
    return vfs.cwd


def usage_lines(node, path):
    """Рекурсивно получить объём каждой папки, включая вложенные."""
    lines = []
    if node.is_dir:
        for child in sorted(node.children.values(), key=lambda n: n.name):
            if child.is_dir:
                child_path = path.rstrip("/") + "/" + child.name
                lines.extend(usage_lines(child, child_path))
    lines.append(f"{node.size()}\t{path}")
    return lines


def disk_usage(vfs, args):
    """du [-s] [путь]: объём содержимого в байтах, не блоках ОС."""
    path, summary = parse_path(args, "-s")
    node, canonical = vfs.resolve(path)
    if summary:
        return f"{node.size()}\t{canonical}"
    return "\n".join(usage_lines(node, canonical))


def initialize_vfs(vfs, args):
    """vfs-init: сбросить дерево и его физическое представление."""
    require_no_args(args)
    vfs.reset()
    return "VFS сброшена к состоянию по умолчанию"
