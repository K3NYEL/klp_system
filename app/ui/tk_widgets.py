from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

def _color(value: Any, widget: Any) -> Any:
    if value in (None, "transparent"):
        try:
            return widget.master.cget("background")
        except Exception:
            return "#11141B"
    return value

def _translate(options: dict, widget: Any, kind: str) -> dict:
    values = dict(options)
    aliases = {"fg_color": "background", "text_color": "foreground"}
    if kind == "button":
        aliases.update({"hover_color": "activebackground", "border_color": "highlightbackground"})
    elif kind in {"entry", "frame", "label", "check"}:
        aliases["border_color"] = "highlightbackground"
    for old, new in aliases.items():
        if old in values:
            value = values.pop(old)
            if old in {"fg_color", "hover_color"}:
                value = _color(value, widget)
            values[new] = value
    for key in ("corner_radius", "border_width", "placeholder_text", "placeholder_text_color", "dropdown_fg_color",
                "dropdown_text_color", "dropdown_hover_color", "button_color", "button_hover_color",
                "hover_color", "checkbox_width", "checkbox_height", "progress_color",
                "scrollbar_button_color", "scrollbar_button_hover_color"):
        values.pop(key, None)
    return values

class _Compat:
    _kind = "frame"
    def configure(self, cnf=None, **kwargs):
        opts = {} if cnf is None else dict(cnf)
        opts.update(kwargs)
        return super().configure(**_translate(opts, self, self._kind))
    config = configure

class Frame(_Compat, tk.Frame):
    _kind = "frame"
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, self._kind)
        kwargs.setdefault("background", "#11141B")
        super().__init__(master, **kwargs)

class Label(_Compat, tk.Label):
    _kind = "label"
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, self._kind)
        kwargs.setdefault("background", _color("transparent", master))
        kwargs.setdefault("foreground", "#F1F3F5")
        kwargs.setdefault("padx", 0)
        kwargs.setdefault("pady", 0)
        super().__init__(master, **kwargs)

class Button(_Compat, tk.Button):
    _kind = "button"
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, self._kind)
        kwargs.setdefault("background", "#E53935")
        kwargs.setdefault("foreground", "#FFFFFF")
        kwargs.setdefault("activebackground", "#EF5350")
        kwargs.setdefault("activeforeground", "#FFFFFF")
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("borderwidth", 0)
        kwargs.setdefault("cursor", "hand2")
        super().__init__(master, **kwargs)

class Entry(_Compat, tk.Entry):
    _kind = "entry"
    def __init__(self, master=None, **kwargs):
        placeholder = kwargs.get("placeholder_text")
        kwargs = _translate(kwargs, master, self._kind)
        kwargs.setdefault("background", "#151922")
        kwargs.setdefault("foreground", "#F1F3F5")
        kwargs.setdefault("insertbackground", "#F1F3F5")
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("highlightthickness", 1)
        super().__init__(master, **kwargs)
        self._placeholder = placeholder
        self._placeholder_active = False
        if placeholder and not kwargs.get("textvariable"):
            self.bind("<FocusIn>", self._clear_placeholder, add="+")
            self.bind("<FocusOut>", self._set_placeholder, add="+")
            self._set_placeholder()
    def _clear_placeholder(self, _event=None):
        if self._placeholder_active:
            self.delete(0, "end")
            self.configure(foreground="#F1F3F5")
            self._placeholder_active = False
    def _set_placeholder(self, _event=None):
        if self._placeholder and not self.get():
            self.insert(0, self._placeholder)
            self.configure(foreground="#737D8C")
            self._placeholder_active = True
    def get(self):
        value = super().get()
        return "" if self._placeholder_active else value

class ComboBox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        for key in ("fg_color", "text_color", "border_color", "corner_radius", "height",
                    "button_color", "button_hover_color", "dropdown_fg_color",
                    "dropdown_hover_color", "dropdown_text_color"):
            kwargs.pop(key, None)
        if "variable" in kwargs and "textvariable" not in kwargs:
            kwargs["textvariable"] = kwargs.pop("variable")
        command = kwargs.pop("command", None)
        super().__init__(master, **kwargs)
        if command:
            self.bind("<<ComboboxSelected>>", lambda event: command(self.get()), add="+")
    def configure(self, cnf=None, **kwargs):
        options = {} if cnf is None else dict(cnf)
        options.update(kwargs)
        if "variable" in options and "textvariable" not in options:
            options["textvariable"] = options.pop("variable")
        for key in ("fg_color", "text_color", "border_color", "corner_radius", "height",
                    "button_color", "button_hover_color", "dropdown_fg_color",
                    "dropdown_hover_color", "dropdown_text_color"):
            options.pop(key, None)
        return super().configure(options)
    config = configure

class CheckBox(_Compat, tk.Checkbutton):
    _kind = "check"
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, self._kind)
        kwargs.setdefault("background", _color("transparent", master))
        kwargs.setdefault("foreground", "#F1F3F5")
        kwargs.setdefault("activebackground", kwargs["background"])
        kwargs.setdefault("selectcolor", "#252B36")
        kwargs.setdefault("relief", "flat")
        super().__init__(master, **kwargs)

class Switch(CheckBox):
    pass

class Slider(tk.Scale):
    def __init__(self, master=None, **kwargs):
        for key in ("progress_color", "button_color", "button_hover_color"):
            kwargs.pop(key, None)
        kwargs.setdefault("orient", "horizontal")
        super().__init__(master, **kwargs)

class ProgressBar(ttk.Progressbar):
    def configure(self, cnf=None, **kwargs):
        options = {} if cnf is None else dict(cnf)
        options.update(kwargs)
        for key in ("progress_color", "fg_color", "text_color", "corner_radius"):
            options.pop(key, None)
        return super().configure(options)
    config = configure
    def set(self, value):
        self.configure(value=float(value) * 100)

class Scrollbar(ttk.Scrollbar):
    def __init__(self, master=None, **kwargs):
        for key in ("fg_color", "button_color", "button_hover_color"):
            kwargs.pop(key, None)
        super().__init__(master, **kwargs)
    def configure(self, cnf=None, **kwargs):
        options = {} if cnf is None else dict(cnf)
        options.update(kwargs)
        for key in ("fg_color", "button_color", "button_hover_color"):
            options.pop(key, None)
        return super().configure(options)
    config = configure

class Toplevel(tk.Toplevel):
    pass

class ScrollableFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        options = _translate(kwargs, master, "frame")
        background = options.pop("background", "#11141B")
        self._container = tk.Frame(master, background=background)
        self._canvas = tk.Canvas(self._container, background=background, highlightthickness=0)
        self._scrollbar = ttk.Scrollbar(self._container, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        super().__init__(self._canvas, background=background, **options)
        self._window_id = self._canvas.create_window((0, 0), window=self, anchor="nw")
        self.bind("<Configure>", self._update_scroll_region, add="+")
        self._canvas.bind("<Configure>", self._resize_content, add="+")
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
    def _update_scroll_region(self, _event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
    def _resize_content(self, event):
        self._canvas.itemconfigure(self._window_id, width=event.width)
    def _on_mousewheel(self, event):
        try:
            if self.winfo_exists() and self.winfo_containing(event.x_root, event.y_root) is not None:
                self._canvas.yview_scroll(int(-event.delta / 120), "units")
        except tk.TclError:
            pass
    def pack(self, *args, **kwargs):
        return self._container.pack(*args, **kwargs)
    def grid(self, *args, **kwargs):
        return self._container.grid(*args, **kwargs)
    def place(self, *args, **kwargs):
        return self._container.place(*args, **kwargs)
    def configure(self, cnf=None, **kwargs):
        options = {} if cnf is None else dict(cnf)
        options.update(kwargs)
        options = _translate(options, self, "frame")
        if "background" in options:
            self._container.configure(background=options["background"])
            self._canvas.configure(background=options["background"])
        return super().configure(options)
    config = configure

class Tabview(tk.Frame):
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, "frame")
        kwargs.setdefault("background", "#090B10")
        super().__init__(master, **kwargs)
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)
        self._tabs = {}
    def configure(self, cnf=None, **kwargs):
        options = {} if cnf is None else dict(cnf)
        options.update(kwargs)
        options = _translate(options, self, "frame")
        return super().configure(options)
    config = configure
    def add(self, name):
        frame = Frame(self._notebook, background="#090B10")
        self._tabs[name] = frame
        self._notebook.add(frame, text=name)
        return frame
    def tab(self, name):
        return self._tabs[name]
    def set(self, name):
        if name in self._tabs:
            self._notebook.select(self._tabs[name])
    def get(self):
        selected = self._notebook.select()
        for name, frame in self._tabs.items():
            if str(frame) == selected:
                return name
        return ""

def set_appearance_mode(_mode):
    return None

def set_default_color_theme(_theme):
    return None

StringVar = tk.StringVar
BooleanVar = tk.BooleanVar
IntVar = tk.IntVar
DoubleVar = tk.DoubleVar
