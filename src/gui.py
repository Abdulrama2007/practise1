"""Графическое окно терминала на стандартном tkinter."""

import getpass
import socket
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from src.startup import run_script


class Terminal:
    """Окно с журналом диалога и строкой ввода."""

    def __init__(self, shell):
        """Построить окно на основе реальных данных ОС."""
        self.shell = shell
        self.user = getpass.getuser()
        self.host = socket.gethostname()
        self.root = tk.Tk()
        self.root.title(f"Эмулятор - [{self.user}@{self.host}]")
        self.root.geometry("920x600")
        self.root.minsize(620, 380)
        self.root.configure(bg="#101923")
        self.build_widgets()
        self.entry.bind("<Return>", self.submit)
        self.entry.focus_set()
        self.write("Вариант 21 | Эмулятор UNIX-оболочки")
        self.write("Команды: ls [-a], cd, pwd, du [-s], vfs-init, exit")
        self.update_prompt()

    def build_widgets(self):
        """Добавить журнал, приглашение и поле команды."""
        self.output = ScrolledText(
            self.root, bg="#101923", fg="#d9e4ee",
            insertbackground="#ffffff", font=("Consolas", 12),
            relief="flat", state="disabled", wrap="word",
        )
        self.output.pack(fill="both", expand=True, padx=16, pady=16)
        row = tk.Frame(self.root, bg="#101923")
        row.pack(fill="x", padx=16, pady=(0, 16))
        self.prompt = tk.Label(
            row, text="$", bg="#101923", fg="#5ce0ac",
            font=("Consolas", 12),
        )
        self.prompt.pack(side="left", padx=(0, 8))
        self.entry = tk.Entry(
            row, bg="#1b2b39", fg="#ffffff",
            insertbackground="#ffffff", font=("Consolas", 12),
            relief="flat",
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8)

    def write(self, text):
        """Добавить непустой текст в журнал терминала."""
        if text:
            self.output.configure(state="normal")
            self.output.insert("end", text + "\n")
            self.output.configure(state="disabled")
            self.output.see("end")

    def submit(self, event=None):
        """Выполнить введённую команду и обновить окно."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.write(f"{self.shell.prompt} {line}")
        self.write(self.shell.execute(line))
        if not self.shell.running:
            self.root.destroy()

    def start_script(self, path):
        """Выполнить сценарий после появления окна."""
        run_script(self.shell, path, self.write)
        if not self.shell.running:
            self.root.destroy()

    def run(self, startup=None):
        """Запустить события окна и необязательный стартовый скрипт."""
        if startup:
            self.root.after(100, lambda: self.start_script(startup))
        self.root.mainloop()

    def update_prompt(self):
        """Обновить путь после команды или стартового скрипта."""
        self.prompt.configure(text=self.shell.prompt)
