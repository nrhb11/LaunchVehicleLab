"""Apple Final Cut Pro for iPad inspired dark-mode design system & stylesheet."""

# -------------------------------------------------------------
# Color Palette Tokens (Apple Pro Video Suite)
# -------------------------------------------------------------
SPACE_BLACK = "#000000"
BG_CANVAS = "#08080a"
BG_PANEL = "#121214"
BG_CARD = "#1c1c1e"
BG_CARD_HOVER = "#242426"
BG_ELEVATED = "#2c2c2e"

BORDER_SUBTLE = "#27272a"
BORDER_ACCENT = "#3f3f46"
BORDER_GLOW = "rgba(10, 132, 255, 0.4)"

TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#a1a1aa"
TEXT_TERTIARY = "#71717a"
TEXT_MUTED = "#52525b"

# Accent Colors (Apple Neon Pro System)
COLOR_ELECTRIC_BLUE = "#0A84FF"
COLOR_FLIGHT_GREEN = "#30D158"
COLOR_ALERT_CORAL = "#FF453A"
COLOR_SUNSET_AMBER = "#FF9F0A"
COLOR_METHANE_VIOLET = "#BF5AF2"
COLOR_HYDROLOX_ROSE = "#FF375F"
COLOR_CYAN = "#64D2FF"

# Propellant Aesthetic Colors
PROPELLANT_COLORS = {
    "LOX": "#38BDF8",       # Liquid Oxygen Electric Cyan
    "RP1": "#F59E0B",       # Kerosene Amber Gold
    "CH4": "#A855F7",       # Liquid Methane Neon Violet
    "LH2": "#EC4899",       # Liquid Hydrogen Bright Rose
    "FAIRING": "#64748B",   # Carbon Composite Slate
    "STRUCTURE": "#334155", # Aerospace Titanium
}

# -------------------------------------------------------------
# Apple Final Cut Pro Dark Theme QSS Stylesheet
# -------------------------------------------------------------
FCP_STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {SPACE_BLACK};
    color: {TEXT_PRIMARY};
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
}}

QWidget {{
    color: {TEXT_PRIMARY};
    background-color: transparent;
    font-size: 13px;
    selection-background-color: {COLOR_ELECTRIC_BLUE};
    selection-color: #ffffff;
}}

/* Top Navigation & Toolbars */
QMenuBar {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER_SUBTLE};
    padding: 4px 8px;
    font-size: 12px;
}}
QMenuBar::item {{
    padding: 6px 12px;
    background: transparent;
    border-radius: 6px;
    color: {TEXT_SECONDARY};
}}
QMenuBar::item:selected {{
    background: {BG_CARD};
    color: {TEXT_PRIMARY};
}}

QToolBar {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER_SUBTLE};
    padding: 6px 12px;
    spacing: 8px;
}}

QStatusBar {{
    background-color: {BG_PANEL};
    border-top: 1px solid {BORDER_SUBTLE};
    color: {TEXT_SECONDARY};
    font-size: 12px;
    padding: 6px 14px;
}}

/* Frosted Acrylic Group Cards */
QGroupBox {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 12px;
    margin-top: 26px;
    padding: 16px 14px 14px 14px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    color: {COLOR_ELECTRIC_BLUE};
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}

/* Buttons & Segmented Chips */
QPushButton {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {BG_CARD_HOVER};
    border-color: {BORDER_ACCENT};
}}
QPushButton:pressed {{
    background-color: {BG_ELEVATED};
}}
QPushButton:checked {{
    background-color: {COLOR_ELECTRIC_BLUE};
    color: #ffffff;
    border-color: {COLOR_ELECTRIC_BLUE};
    font-weight: 600;
}}

QPushButton#PrimaryButton {{
    background-color: {COLOR_ELECTRIC_BLUE};
    color: #ffffff;
    border: 1px solid {COLOR_ELECTRIC_BLUE};
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    padding: 10px 20px;
}}
QPushButton#PrimaryButton:hover {{
    background-color: #2693ff;
}}
QPushButton#PrimaryButton:pressed {{
    background-color: #0071e3;
}}

QPushButton#TransportButton {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 16px;
}}
QPushButton#TransportButton:hover {{
    background-color: {BG_ELEVATED};
    border-color: {COLOR_ELECTRIC_BLUE};
}}

/* Segmented Pill Chip Style */
QFrame#SegmentedGroup {{
    background-color: {BG_CANVAS};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 2px;
}}
QPushButton#SegmentChip {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton#SegmentChip:hover {{
    color: {TEXT_PRIMARY};
    background-color: {BG_CARD};
}}
QPushButton#SegmentChip:checked {{
    background-color: {BG_CARD};
    color: {COLOR_ELECTRIC_BLUE};
    font-weight: 700;
    border: 1px solid {BORDER_SUBTLE};
}}

/* Spinboxes, LineEdits, and Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {COLOR_ELECTRIC_BLUE};
    background-color: {BG_CARD_HOVER};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_ACCENT};
    border-radius: 8px;
    selection-background-color: {COLOR_ELECTRIC_BLUE};
    selection-color: #ffffff;
    padding: 4px;
}}

/* Sliders */
QSlider::groove:horizontal {{
    height: 6px;
    background: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 3px;
}}
QSlider::sub-page:horizontal {{
    background: {COLOR_ELECTRIC_BLUE};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: #ffffff;
    border: 2px solid {COLOR_ELECTRIC_BLUE};
    width: 16px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 8px;
}}
QSlider::handle:horizontal:hover {{
    background: #e0f2fe;
    transform: scale(1.1);
}}

/* Tabs (FCP Floating Bar Style) */
QTabWidget::pane {{
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 12px;
    background-color: {BG_PANEL};
    top: -1px;
}}
QTabBar::tab {{
    background: {BG_CANVAS};
    color: {TEXT_SECONDARY};
    padding: 8px 18px;
    border: 1px solid {BORDER_SUBTLE};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border-color: {BORDER_SUBTLE};
    border-bottom: 2px solid {COLOR_ELECTRIC_BLUE};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    color: {TEXT_PRIMARY};
    background: {BG_CARD};
}}

/* Tables (Apple Inset List Style) */
QTableWidget {{
    background-color: {BG_PANEL};
    border: none;
    border-radius: 8px;
    gridline-color: {BORDER_SUBTLE};
}}
QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {BORDER_SUBTLE};
}}
QTableWidget::item:selected {{
    background-color: rgba(10, 132, 255, 0.2);
    color: {TEXT_PRIMARY};
}}
QHeaderView::section {{
    background-color: {BG_CARD};
    color: {TEXT_SECONDARY};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {BORDER_SUBTLE};
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_ACCENT};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0;
}}
"""

# Alias for backward compatibility
DARK_STYLESHEET = FCP_STYLESHEET


