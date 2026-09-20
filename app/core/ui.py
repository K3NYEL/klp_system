"""Punto de entrada historico de la configuracion visual de la aplicacion.

La implementacion real vive en :mod:`app.ui.theme` (paleta de colores, estilos
ttk, cambio de tema en caliente y utilidades de ventana). Este modulo se
conserva para no romper las importaciones existentes del tipo
``from app.core.ui import configure_app_style``.
"""

from app.ui.theme import (  # noqa: F401
    APP_NAME,
    APP_VERSION,
    CREATOR_URL,
    FONTS,
    ICON_FILES,
    ICON_IMAGES,
    INPUT_STYLE,
    THEMES,
    ThemeManager,
    Tooltip,
    apply_theme,
    button_palette,
    center_window,
    color,
    colors,
    configure_app_style,
    font,
    is_dark,
    prepare_toplevel,
    release_modal,
    remember,
    resource_path,
    restyle,
    role_colors,
    separator,
    set_app_icon,
    theme_name,
)

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "CREATOR_URL",
    "FONTS",
    "INPUT_STYLE",
    "THEMES",
    "ThemeManager",
    "Tooltip",
    "apply_theme",
    "button_palette",
    "center_window",
    "color",
    "colors",
    "configure_app_style",
    "font",
    "is_dark",
    "prepare_toplevel",
    "release_modal",
    "remember",
    "resource_path",
    "restyle",
    "role_colors",
    "separator",
    "set_app_icon",
    "theme_name",
]
