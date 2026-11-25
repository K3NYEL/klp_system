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
    for key in ("corner_radius", "border_width", "placeholder_text", "dropdown_fg_color",
                "dropdown_text_color", "dropdown_hover_color", "button_color",
                "button_hover_color", "checkbox_width", "checkbox_height",
                "progress_color", "scrollbar_button_color", "scrollbar_button_hover_color"):
        values.pop(key, None)
    return values

class _Compat:
    _kind = "frame"
    def configure(self, cnf=None, **kwargs):
        opts = {} if cnf is None else dict(cnf)
        opts.update(kwargs)
        return super().configure(**_translate(opts, self, self._kind))
    config = configure

class CTkFrame(_Compat, tk.Frame):
    _kind = "frame"
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, self._kind)
        kwargs.setdefault("background", "#11141B")
        super().__init__(master, **kwargs)

class CTkLabel(_Compat, tk.Label):
    _kind = "label"
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, self._kind)
        kwargs.setdefault("background", _color("transparent", master))
        kwargs.setdefault("foreground", "#F1F3F5")
        kwargs.setdefault("padx", 0)
        kwargs.setdefault("pady", 0)
        super().__init__(master, **kwargs)

class CTkButton(_Compat, tk.Button):
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

class CTkEntry(_Compat, tk.Entry):
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

class CTkComboBox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        for key in ("fg_color", "text_color", "border_color", "corner_radius", "font"):
            kwargs.pop(key, None)
        command = kwargs.pop("command", None)
        super().__init__(master, **kwargs)
        if command:
            self.bind("<<ComboboxSelected>>", lambda event: command(self.get()), add="+")

class CTkCheckBox(_Compat, tk.Checkbutton):
    _kind = "check"
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, self._kind)
        kwargs.setdefault("background", _color("transparent", master))
        kwargs.setdefault("foreground", "#F1F3F5")
        kwargs.setdefault("activebackground", kwargs["background"])
        kwargs.setdefault("selectcolor", "#252B36")
        kwargs.setdefault("relief", "flat")
        super().__init__(master, **kwargs)

class CTkSwitch(CTkCheckBox):
    pass

class CTkSlider(tk.Scale):
    def __init__(self, master=None, **kwargs):
        for key in ("progress_color", "button_color", "button_hover_color"):
            kwargs.pop(key, None)
        kwargs.setdefault("orient", "horizontal")
        super().__init__(master, **kwargs)

class CTkProgressBar(ttk.Progressbar):
    def set(self, value):
        self.configure(value=float(value) * 100)

class CTkScrollbar(ttk.Scrollbar):
    def __init__(self, master=None, **kwargs):
        for key in ("fg_color", "button_color", "button_hover_color"):
            kwargs.pop(key, None)
        super().__init__(master, **kwargs)

class CTkToplevel(tk.Toplevel):
    pass

class CTkScrollableFrame(CTkFrame):
    pass

class CTkTabview(tk.Frame):
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, "frame")
        kwargs.setdefault("background", "#090B10")
        super().__init__(master, **kwargs)
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)
        self._tabs = {}
    def add(self, name):
        frame = CTkFrame(self._notebook, background="#090B10")
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
