from __future__ import annotations

import os
import sys
import time
import tkinter as tk
from abc import ABC, abstractmethod
from io import StringIO, TextIOBase
from threading import Lock, Thread
from typing import overload, Literal, Callable, Any, IO

from main import Game


class HVScrolledText(tk.Text):
    # noinspection SpellCheckingInspection
    @overload
    def __init__(
            self, master: tk.Misc | None, *,
            autoseparators: bool = ...,
            background: str = ...,
            bd: str | float = ...,
            bg: str = ...,
            blockcursor: bool = ...,
            border: str | float = ...,
            borderwidth: str | float = ...,
            cursor: str | tuple[str] | tuple[str, str] | tuple[str, str, str] | tuple[
                str, str, str, str] = ...,
            endline: int | Literal[""] = ...,
            exportselection: bool = ...,
            fg: str = ...,
            font: Any = ...,
            foreground: str = ...,
            height: str | float = ...,
            highlightbackground: str = ...,
            highlightcolor: str = ...,
            highlightthickness: str | float = ...,
            inactiveselectbackground: str = ...,
            insertbackground: str = ...,
            insertborderwidth: str | float = ...,
            insertofftime: int = ...,
            insertontime: int = ...,
            insertunfocussed: Literal["none", "hollow", "solid"] = ...,
            insertwidth: str | float = ...,
            maxundo: int = ...,
            name: str = ...,
            padx: str | float = ...,
            pady: str | float = ...,
            relief: Literal["raised", "sunken", "flat", "ridge", "solid", "groove"] = ...,
            selectbackground: str = ...,
            selectborderwidth: str | float = ...,
            selectforeground: str = ...,
            setgrid: bool = ...,
            spacing1: str | float = ...,
            spacing2: str | float = ...,
            spacing3: str | float = ...,
            startline: int | Literal[""] = ...,
            state: Literal["normal", "disabled"] = ...,
            tabs: str | float | tuple[str | float, ...] = ...,
            tabstyle: Literal["tabular", "wordprocessor"] = ...,
            takefocus: int | Literal[""] | Callable[[str], bool | None] = ...,
            undo: bool = ...,
            width: int = ...,
            wrap: Literal["none", "char", "word"] = ...,
            xscrollcommand: str | Callable[[float, float], Any] = ...,
            yscrollcommand: str | Callable[[float, float], Any] = ...):
        ...

    def __init__(self, master=None, **kw):
        self.frame = tk.Frame(master)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        self.vbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.vbar.grid(column=1, row=0, sticky=tk.NSEW)
        self.vbar.configure(command=self.yview)
        self.hbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.hbar.grid(column=0, row=1, sticky=tk.NSEW)
        self.hbar.configure(command=self.xview)

        super().__init__(self.frame, **kw)
        self.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.grid(column=0, row=0, sticky=tk.NSEW)

        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))


class IBackend(ABC):
    @abstractmethod
    def send_input(self, text: str):
        raise NotImplementedError

    @abstractmethod
    def update_app_output(self):
        ...

    def start(self, app: GuiApp):
        ...


class DummyBackend(IBackend):
    def send_input(self, text: str):
        print(f'Sent {text}')


class WriteStreamWrapper(TextIOBase):
    def __init__(self, app: GuiApp, orig: IO[str], is_stderr=False):
        self.is_stderr = is_stderr
        self.app = app
        self.orig = orig
        self.queued = StringIO()
        self.queue_lock = Lock()

    def write(self, s: str, /) -> int:
        self.orig.write(s)
        with self.queue_lock:
            return self.queued.write(s)

    def update_app(self):
        """Main thread ONLY"""
        with self.queue_lock:
            value = self.queued.getvalue()
            self.queued.seek(0, os.SEEK_SET)
            self.queued.truncate(0)
        if self.is_stderr:
            self.app.write_stderr(value)
        else:
            self.app.write_stdout(value)


class ReadStreamWrapper(TextIOBase):
    def __init__(self, app: GuiApp):
        self.app = app
        self.content = ''
        self._content_lock = Lock()
        self.requesting = False
        self._remainder = ''

    def read(self, size: int | None = ...) -> str:
        self.requesting = True
        self.clear()  # clear previous results (only want new ones)
        content = self._remainder
        while len(content) < size:
            while True:
                with self._content_lock:
                    if self.content:
                        content += self.content
                        self.content = ''  # consume content
                        break
                time.sleep(0.001)  # don't waste CPU too much
        self.requesting = False
        self._remainder = content[size:]
        return content[:size]

    def readline(self, size: int = None) -> str:
        c = ''
        s = []
        while c != '\n' and (size is None or len(c) < size):
            c = self.read(1)
            s.append(c)
        return ''.join(s)

    def clear(self):
        with self._content_lock:
            self.content = ''

    def update_from_app(self, text: str):
        if not self.requesting:
            return
        with self._content_lock:
            self.content = text


class ThreadedBackend(IBackend):
    def __init__(self, n_players=4):
        self.n_players = n_players

    def start(self, app: GuiApp):
        self.orig_stdin = sys.stdin
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr
        self.stdout = sys.stdout = WriteStreamWrapper(app, self.orig_stdout, False)
        self.stderr = sys.stderr = WriteStreamWrapper(app, self.orig_stderr, True)
        self.stdin = sys.stdin = ReadStreamWrapper(app)
        self.game = Game(self.n_players)
        self.game_thread = Thread(target=self._run, name='GameBackend')
        self.game_thread.daemon = True
        self.game_thread.start()
        return self

    def _run(self):
        self.game.run_game()

    def send_input(self, text: str):
        self.stdin.update_from_app(text)

    def update_app_output(self):
        self.stdout.update_app()
        self.stderr.update_app()


# class StdStreamBackend(IBackend):
#     def __init__(self, stdin: IO[str], stdout: IO[str], stderr: IO[str]):
#         self.stdin = stdin
#         self.stdout = stdout
#         self.stderr = stderr
#
#     def send_input(self, text: str):
#         self.stdin.write(text)
#
#     def update_app_output(self):
#         ...


class GuiApp:
    def __init__(self, backend: IBackend | ThreadedBackend = None):
        self.backend = backend

        self.root = tk.Tk()
        self.root.title('magusok kora')
        self.root.minsize(200, 200)
        self.root.grid_columnconfigure(0, weight=1)

        self.out_frame = tk.LabelFrame(self.root, text='Output')
        self.out_frame.grid(column=0, row=0, padx=5, pady=5, sticky=tk.NSEW)
        self.out_frame.grid_columnconfigure(0, weight=1)
        self.out = HVScrolledText(self.out_frame, font='TkFixedFont', wrap=tk.NONE, state=tk.DISABLED)
        self.out.grid(column=0, row=0, padx=5, pady=3, sticky=tk.NSEW)

        self.inp_frame = tk.LabelFrame(self.root, text='Input', font='TkFixedFont')
        self.inp_frame.grid(column=0, row=1, padx=5, pady=5, sticky=tk.NSEW)
        self.inp_frame.grid_columnconfigure(0, weight=1)
        self.inp = tk.Entry(self.inp_frame)
        self.inp.grid(column=0, row=0, padx=(5, 0), pady=5, sticky=tk.NSEW)
        self.inp_button = tk.Button(self.inp_frame, command=self.send_input, text='Enter')
        self.inp_button.grid(column=1, row=0, padx=(0, 5), pady=5, sticky=tk.NSEW)
        self.inp.bind('<Return>', self.send_input)

        self.err_frame = tk.LabelFrame(self.root, text='Error', fg='red')
        self.err_var = tk.StringVar()
        self.err = HVScrolledText(
            self.err_frame, state=tk.DISABLED, font='TkFixedFont', fg='red', wrap=tk.NONE)
        self.err.grid(padx=5, pady=5, column=0, row=0, sticky=tk.NSEW)

    def do_tick(self, *_):
        self.backend.update_app_output()
        self.root.after(10, self.do_tick)

    def set_backend(self, b: DummyBackend):
        self.backend = b

    def send_input(self, _event=None):
        text = self.inp.get()
        self.backend.send_input(text + '\n')
        self.inp.delete(0, tk.END)
        if self.backend.stdin.requesting:
            self.write_stdout('\n')

    def write_stdout(self, s: str):
        self.append_text(self.out, s)

    def write_stderr(self, s: str):
        self.append_text(self.err, s)
        self.show_err_frame()

    def append_text(self, widget: tk.Text, text: str):
        orig_state = widget['state']
        widget.configure(state=tk.NORMAL)
        widget.insert(tk.END, text)
        widget.configure(state=orig_state)
        if text:
            widget.yview_moveto(1.0)

    def set_text(self, widget: tk.Text, text: str):
        orig_state = widget['state']
        widget.configure(state=tk.NORMAL)
        widget.delete('1.0', tk.END)
        widget.insert('1.0', text)
        widget.configure(state=orig_state)

    def show_err_frame(self):
        self.err_frame.grid(column=0, row=2, padx=5, pady=5, sticky=tk.NSEW)
        self.err_frame.grid_columnconfigure(0, weight=1)

    def hide_err_frame(self):
        self.err_frame.grid_forget()

    def update_err_text(self, text: str):
        self.set_text(self.err, text)
        if text:
            self.show_err_frame()
        else:
            self.hide_err_frame()

    def mainloop(self):
        self.backend.start(self)
        self.do_tick()
        self.root.mainloop()


def main():
    app = GuiApp(ThreadedBackend(2))
    app.mainloop()


if __name__ == '__main__':
    main()
