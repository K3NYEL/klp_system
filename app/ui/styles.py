"""
Estilos globales de KLP SYSTEM.

Este archivo contiene únicamente constantes de diseño:
colores, fuentes, tamaños y configuraciones generales.
"""

import customtkinter as ctk


# ============================================================
# COLORES
# ============================================================

class Colors:
    """Paleta de colores principal de KLP SYSTEM."""

    # --------------------------------------------------------
    # Fondos
    # --------------------------------------------------------

    BACKGROUND = "#0F1117"
    SURFACE = "#171A21"
    SURFACE_HOVER = "#1D212A"

    # --------------------------------------------------------
    # Superficies secundarias
    # --------------------------------------------------------

    CARD = "#181B23"
    CARD_HOVER = "#20242D"
    INPUT = "#20242B"

    # --------------------------------------------------------
    # Bordes
    # --------------------------------------------------------

    BORDER = "#2A2F3A"
    BORDER_LIGHT = "#343A46"

    # --------------------------------------------------------
    # Texto
    # --------------------------------------------------------

    TEXT = "#F5F5F5"
    TEXT_SECONDARY = "#A7ADB8"
    TEXT_MUTED = "#737B89"
    TEXT_DISABLED = "#555C68"

    # --------------------------------------------------------
    # Rojo KLP SYSTEM
    # --------------------------------------------------------

    PRIMARY = "#E53935"
    PRIMARY_HOVER = "#C62828"
    PRIMARY_DARK = "#8E1B1B"

    # --------------------------------------------------------
    # Estados
    # --------------------------------------------------------

    SUCCESS = "#43A047"
    SUCCESS_HOVER = "#388E3C"

    WARNING = "#F9A825"
    WARNING_HOVER = "#F57F17"

    DANGER = "#E53935"
    DANGER_HOVER = "#C62828"

    INFO = "#1E88E5"
    INFO_HOVER = "#1565C0"

    # --------------------------------------------------------
    # Botón secundario / neutro
    # --------------------------------------------------------

    SECONDARY = "#2A2F3A"
    SECONDARY_HOVER = "#353B48"

    # Alias para compatibilidad con el código existente.
    NEUTRAL = SECONDARY
    NEUTRAL_HOVER = SECONDARY_HOVER

    # --------------------------------------------------------
    # Transparencia
    # --------------------------------------------------------

    TRANSPARENT = "transparent"


# ============================================================
# FUENTES
# ============================================================

class Fonts:
    """Fuentes utilizadas por KLP SYSTEM."""

    FAMILY = "Cantarell"

    # Botones
    BUTTON = (FAMILY, 11, "bold")
    BUTTON_SMALL = (FAMILY, 10, "bold")
    BUTTON_LARGE = (FAMILY, 12, "bold")

    # Títulos
    TITLE = (FAMILY, 24, "bold")
    SUBTITLE = (FAMILY, 17, "bold")

    # Texto
    BODY = (FAMILY, 11)
    BODY_BOLD = (FAMILY, 11, "bold")

    # Texto pequeño
    SMALL = (FAMILY, 10)
    SMALL_BOLD = (FAMILY, 10, "bold")


# ============================================================
# TAMAÑOS DE BOTONES
# ============================================================

class ButtonSizes:
    """Tamaños estándar de los botones de KLP SYSTEM."""

    SMALL = {
        "width": 100,
        "height": 32,
        "corner_radius": 7,
    }

    MEDIUM = {
        "width": 130,
        "height": 38,
        "corner_radius": 8,
    }

    LARGE = {
        "width": 160,
        "height": 44,
        "corner_radius": 9,
    }

    FULL = {
        "height": 42,
        "corner_radius": 8,
    }


# ============================================================
# CONFIGURACIÓN GLOBAL DE CUSTOMTKINTER
# ============================================================

def configure_app_style() -> None:
    """
    Configura el aspecto global de CustomTkinter.

    Los colores concretos de KLP SYSTEM se controlan mediante
    Colors y los componentes reutilizables.
    """

    ctk.set_appearance_mode("dark")

    # Tema base de CTk.
    # Los componentes de KLP SYSTEM sobrescriben sus colores
    # mediante Colors.
    ctk.set_default_color_theme("dark-blue")