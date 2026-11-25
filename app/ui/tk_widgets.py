from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Any

def _color(value: Any, widget: Any) -> Any:
    if value in (None, "transparent"):
        try:
            return widget.cget("background")
        except Exception:
            return "#FFFFFF"
    return value

def _translate(options: dict, widget: Any, kind: str) -> dict:
    values = dict(options)
    aliases = {"fg_color": "background", "text_color": "foreground"}
    if kind == "frame":
        values.pop("text_color", None)
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
                "scrollbar_button_color", "scrollbar_button_hover_color", "segmented_button_fg_color",
                "segmented_button_selected_color", "segmented_button_selected_hover_color",
                "segmented_button_unselected_color", "segmented_button_unselected_hover_color"):
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
        kwargs.setdefault("background", "#FFFFFF")
        super().__init__(master, **kwargs)

class Label(_Compat, tk.Label):
    _kind = "label"
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, self._kind)
        if isinstance(kwargs.get("width"), (int, float)) and kwargs["width"] > 40:
            kwargs["width"] = max(1, round(kwargs["width"] / 8))
        if isinstance(kwargs.get("height"), (int, float)) and kwargs["height"] > 4:
            kwargs["height"] = max(1, round(kwargs["height"] / 20))
        kwargs.setdefault("background", _color("transparent", master))
        kwargs.setdefault("foreground", "#1C1C1A")
        kwargs.setdefault("padx", 0)
        kwargs.setdefault("pady", 0)
        super().__init__(master, **kwargs)

class Button(_Compat, tk.Button):
    _kind = "button"
    def __init__(self, master=None, **kwargs):
        kwargs = _translate(kwargs, master, self._kind)
        if isinstance(kwargs.get("width"), (int, float)) and kwargs["width"] > 40:
            kwargs["width"] = max(8, round(kwargs["width"] / 8))
        if isinstance(kwargs.get("height"), (int, float)) and kwargs["height"] > 4:
            kwargs["height"] = max(1, round(kwargs["height"] / 24))
        kwargs.setdefault("padx", 10)
        kwargs.setdefault("pady", 6)
        kwargs.setdefault("background", "#C8312E")
        kwargs.setdefault("foreground", "#FFFFFF")
        kwargs.setdefault("activebackground", "#B52B28")
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
        kwargs.pop("height", None)
        if isinstance(kwargs.get("width"), (int, float)) and kwargs["width"] > 40:
            kwargs["width"] = max(8, round(kwargs["width"] / 8))
        kwargs.setdefault("background", "#FFFFFF")
        kwargs.setdefault("foreground", "#1C1C1A")
        kwargs.setdefault("insertbackground", "#1C1C1A")
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
            self.configure(foreground="#1C1C1A")
            self._placeholder_active = False
    def _set_placeholder(self, _event=None):
        if self._placeholder and not self.get():
            self.insert(0, self._placeholder)
            self.configure(foreground="#8A8983")
            self._placeholder_active = True
    def get(self):
        value = super().get()
        return "" if self._placeholder_active else value

class ComboBox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        for key in ("fg_color", "text_color", "border_color", "border_width", "corner_radius", "height",
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
        for key in ("fg_color", "text_color", "border_color", "border_width", "corner_radius", "height",
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
        kwargs.setdefault("foreground", "#1C1C1A")
        kwargs.setdefault("activebackground", kwargs["background"])
        kwargs.setdefault("selectcolor", "#ECEAE6")
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
    """Scrollbar ttk con compatibilidad de argumentos de la API anterior."""

    @staticmethod
    def _normalize(options):
        options = dict(options)
        # CustomTkinter utilizaba orientation; ttk.Scrollbar utiliza orient.
        if "orientation" in options and "orient" not in options:
            options["orient"] = options.pop("orientation")
        else:
            options.pop("orientation", None)
        # ttk.Scrollbar no admite height; el grosor se controla con width.
        options.pop("height", None)
        for key in ("fg_color", "button_color", "button_hover_color"):
            options.pop(key, None)
        return options

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **self._normalize(kwargs))

    def configure(self, cnf=None, **kwargs):
        options = {} if cnf is None else dict(cnf)
        options.update(kwargs)
        return super().configure(self._normalize(options))

    config = configure

class Toplevel(tk.Toplevel):
    pass

class ScrollableFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        options = _translate(kwargs, master, "frame")
        background = options.pop("background", "#FFFFFF")
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
        self.bind_all("<Button-4>", self._on_mousewheel, add="+")
        self.bind_all("<Button-5>", self._on_mousewheel, add="+")
    def _update_scroll_region(self, _event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
    def _resize_content(self, event):
        self._canvas.itemconfigure(self._window_id, width=event.width)
    def _on_mousewheel(self, event):
        try:
            if not self.winfo_exists():
                return
            target = self.winfo_containing(event.x_root, event.y_root)
            inside = False
            while target is not None:
                if target is self:
                    inside = True
                    break
                target = getattr(target, "master", None)
            if not inside:
                return
            if getattr(event, "num", None) == 4:
                amount = -1
            elif getattr(event, "num", None) == 5:
                amount = 1
            else:
                amount = int(-event.delta / 120)
            if amount:
                self._canvas.yview_scroll(amount, "units")
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

class _SegmentedButtonCompat:
    def __init__(self, owner):
        self._owner = owner

    def cget(self, option):
        if option == "values":
            return tuple(self._owner._tabs.keys())
        raise tk.TclError(f"Opción desconocida: {option}")


class Tabview(tk.Frame):
    def __init__(self, master=None, **kwargs):
        self._show_tabs = kwargs.pop("show_tabs", True)
        self._on_change = kwargs.pop("on_change", None)
        kwargs = _translate(kwargs, master, "frame")
        kwargs.setdefault("background", "#FAFAF8")
        kwargs.pop("height", None)
        kwargs.pop("width", None)
        super().__init__(master, **kwargs)

        self._tab_bar = tk.Frame(self, background="#FFFFFF", highlightthickness=0)
        if self._show_tabs:
            self._tab_bar.pack(side="top", fill="x")

        self._pages = tk.Frame(self, background="#FAFAF8", highlightthickness=0)
        self._pages.pack(side="top", fill="both", expand=True)
        self._pages.grid_rowconfigure(0, weight=1)
        self._pages.grid_columnconfigure(0, weight=1)

        self._tabs = {}
        self._tab_buttons = {}
        self._selected = None
        self._segmented_button = _SegmentedButtonCompat(self)

    def configure(self, cnf=None, **kwargs):
        options = {} if cnf is None else dict(cnf)
        options.update(kwargs)
        options = _translate(options, self, "frame")
        return super().configure(options)

    config = configure

    def add(self, name):
        if name in self._tabs:
            return self._tabs[name]

        page = Frame(self._pages, background=self.cget("background"))
        page.grid(row=0, column=0, sticky="nsew")
        button = tk.Button(
            self._tab_bar,
            text=name,
            command=lambda tab_name=name: self.set(tab_name),
            background="#F3F2EF",
            foreground="#6B6B66",
            activebackground="#E8E6E1",
            activeforeground="#FFFFFF",
            disabledforeground="#FFFFFF",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=16,
            pady=11,
            cursor="hand2",
            font=(tkfont.nametofont("TkDefaultFont", root=self.winfo_toplevel()).actual("family"), 9, "bold"),
        )
        button.pack(side="left", fill="x", expand=True)
        self._tabs[name] = page
        self._tab_buttons[name] = button

        if self._selected is None:
            self.set(name)

        return page

    def tab(self, name):
        return self._tabs[name]

    def set(self, name):
        if name not in self._tabs:
            return
        self._selected = name
        self._tabs[name].tkraise()
        for tab_name, button in self._tab_buttons.items():
            if tab_name == name:
                button.configure(
                    background="#C8312E",
                    foreground="#FFFFFF",
                    activebackground="#B52B28",
                    activeforeground="#FFFFFF",
                )
            else:
                button.configure(
                    background="#F3F2EF",
                    foreground="#6B6B66",
                    activebackground="#E8E6E1",
                    activeforeground="#1C1C1A",
                )
        if callable(self._on_change):
            self._on_change(name)

    def get(self):
        return self._selected or ""

def set_appearance_mode(_mode):
    return None

def set_default_color_theme(_theme):
    return None

StringVar = tk.StringVar
BooleanVar = tk.BooleanVar
IntVar = tk.IntVar
DoubleVar = tk.DoubleVar
