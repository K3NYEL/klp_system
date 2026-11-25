import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

class Colors:
    BACKGROUND="#FAFAF8"; SURFACE="#FFFFFF"; SURFACE_HOVER="#F3F2EF"
    CARD="#FFFFFF"; CARD_HOVER="#FAFAF8"; INPUT="#FFFFFF"
    BORDER="#ECEAE6"; BORDER_LIGHT="#DDDAD4"; TEXT="#1C1C1A"
    TEXT_SECONDARY="#6B6B66"; TEXT_MUTED="#8A8983"; TEXT_DISABLED="#A5A49F"
    PRIMARY="#C8312E"; PRIMARY_HOVER="#B52B28"; PRIMARY_DARK="#A92724"
    SUCCESS="#27834A"; SUCCESS_HOVER="#1E6B3C"; WARNING="#A66B12"
    WARNING_HOVER="#80520D"; DANGER="#C8312E"; DANGER_HOVER="#A92724"
    INFO="#286C9C"; INFO_HOVER="#20577F"; SECONDARY="#F3F2EF"
    SECONDARY_HOVER="#E8E6E1"; NEUTRAL=SECONDARY
    NEUTRAL_HOVER=SECONDARY_HOVER; TRANSPARENT="transparent"

class Fonts:
    FAMILY="Inter"; BUTTON=(FAMILY,10,"bold"); BUTTON_SMALL=(FAMILY,9,"bold")
    BUTTON_LARGE=(FAMILY,11,"bold"); TITLE=(FAMILY,22,"bold")
    SUBTITLE=(FAMILY,16,"bold"); BODY=(FAMILY,10); BODY_BOLD=(FAMILY,10,"bold")
    SMALL=(FAMILY,9); SMALL_BOLD=(FAMILY,9,"bold")

class ButtonSizes:
    SMALL={"width":100,"height":34}; MEDIUM={"width":132,"height":40}
    LARGE={"width":164,"height":46}; FULL={"height":44}

def configure_app_style(root=None):
    root = root or getattr(tk, "_default_root", None)
    available = {}
    if root is not None:
        try:
            available = {name.casefold(): name for name in tkfont.families(root)}
        except tk.TclError:
            pass
    family = next((available[name.casefold()] for name in ("Inter", "DejaVu Sans", "Noto Sans", "Liberation Sans", "Arial", "Helvetica") if name.casefold() in available), None)
    if family is None and root is not None:
        try:
            family = tkfont.nametofont("TkDefaultFont", root=root).actual("family")
        except tk.TclError:
            family = "DejaVu Sans"
    if family:
        Fonts.FAMILY = family
        Fonts.BUTTON=(family,10,"bold"); Fonts.BUTTON_SMALL=(family,9,"bold")
        Fonts.BUTTON_LARGE=(family,11,"bold"); Fonts.TITLE=(family,22,"bold")
        Fonts.SUBTITLE=(family,16,"bold"); Fonts.BODY=(family,10); Fonts.BODY_BOLD=(family,10,"bold")
        Fonts.SMALL=(family,9); Fonts.SMALL_BOLD=(family,9,"bold")
        for name in ("TkDefaultFont", "TkTextFont", "TkFixedFont", "TkMenuFont", "TkHeadingFont", "TkCaptionFont", "TkSmallCaptionFont", "TkIconFont", "TkTooltipFont"):
            try:
                tkfont.nametofont(name, root=root).configure(family=family)
            except tk.TclError:
                pass
    style=ttk.Style(root)
    try: style.theme_use("clam")
    except tk.TclError: pass
    style.configure(".",background=Colors.BACKGROUND,foreground=Colors.TEXT,font=Fonts.BODY)
    style.configure("TFrame",background=Colors.BACKGROUND)
    style.configure("Surface.TFrame",background=Colors.SURFACE)
    style.configure("Card.TFrame",background=Colors.CARD,borderwidth=1,relief="solid")
    style.configure("TLabel",background=Colors.BACKGROUND,foreground=Colors.TEXT,font=Fonts.BODY)
    style.configure("Title.TLabel",background=Colors.BACKGROUND,foreground=Colors.TEXT,font=Fonts.TITLE)
    style.configure("Subtitle.TLabel",background=Colors.BACKGROUND,foreground=Colors.TEXT_SECONDARY,font=Fonts.BODY)
    style.configure("Status.TLabel",background=Colors.SURFACE,foreground=Colors.TEXT_SECONDARY,font=Fonts.SMALL)
    style.configure("TButton",background=Colors.SECONDARY,foreground=Colors.TEXT,padding=(12,8),borderwidth=0,font=Fonts.BUTTON)
    style.map("TButton",background=[("active",Colors.SECONDARY_HOVER),("disabled",Colors.SURFACE_HOVER)],foreground=[("disabled",Colors.TEXT_DISABLED)])
    style.configure("Primary.TButton",background=Colors.PRIMARY,foreground="#FFFFFF")
    style.map("Primary.TButton",background=[("active",Colors.PRIMARY_HOVER),("disabled",Colors.PRIMARY_DARK)])
    style.configure("TEntry",fieldbackground=Colors.INPUT,foreground=Colors.TEXT,insertcolor=Colors.TEXT,padding=9,bordercolor=Colors.BORDER)
    style.configure("TCombobox",fieldbackground=Colors.INPUT,background=Colors.INPUT,foreground=Colors.TEXT,arrowcolor=Colors.TEXT,padding=8)
    style.map("TCombobox",fieldbackground=[("readonly",Colors.INPUT)],foreground=[("readonly",Colors.TEXT)])
    style.configure("TProgressbar",troughcolor=Colors.BORDER,background=Colors.PRIMARY,bordercolor=Colors.BORDER,lightcolor=Colors.PRIMARY,darkcolor=Colors.PRIMARY)
    style.configure("Treeview",background=Colors.CARD,fieldbackground=Colors.CARD,foreground=Colors.TEXT,rowheight=34,borderwidth=0,font=Fonts.BODY)
    style.configure("Treeview.Heading",background=Colors.SURFACE_HOVER,foreground=Colors.TEXT_SECONDARY,relief="flat",font=Fonts.SMALL_BOLD,padding=(8,10))
    style.map("Treeview",background=[("selected","#FBE9E8")],foreground=[("selected",Colors.TEXT)])
    return style
