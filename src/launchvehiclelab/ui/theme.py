"""Apple Human Interface Guidelines (HIG) Pro Studio Design System."""

# -------------------------------------------------------------
# Apple Pro Palette Tokens (True Black OLED & Frosted Glass)
# -------------------------------------------------------------
SPACE_BLACK = "#000000"
BG_BASE = "#050507"
BG_PANEL = "#0e0e11"
BG_CARD = "#161619"
BG_CARD_HOVER = "#1e1e23"
BG_ELEVATED = "#26262b"

BORDER_HAIRLINE = "#232328"
BORDER_FOCUS = "#0A84FF"
BORDER_CARD = "#1c1c21"

# Backward compatibility aliases
BG_CANVAS = BG_BASE
BORDER_SUBTLE = BORDER_HAIRLINE
BORDER_ACCENT = BORDER_HAIRLINE

# Typography Colors
TEXT_PRIMARY = "#f4f4f5"
TEXT_SECONDARY = "#a1a1aa"
TEXT_TERTIARY = "#71717a"
TEXT_MUTED = "#52525b"

# Apple Pro Accents
COLOR_ELECTRIC_BLUE = "#0A84FF"
COLOR_FLIGHT_GREEN = "#30D158"
COLOR_ALERT_CORAL = "#FF453A"
COLOR_SUNSET_AMBER = "#FF9F0A"
COLOR_METHANE_VIOLET = "#BF5AF2"
COLOR_CYAN = "#64D2FF"
COLOR_GOLD = "#FFD60A"

# Propellant Aesthetic Colors (Technical Aerospace)
PROPELLANT_COLORS = {
    "LOX": "#38BDF8",       # Liquid Oxygen Cyan
    "RP1": "#F59E0B",       # Kerosene Amber
    "CH4": "#A855F7",       # Methane Purple
    "LH2": "#EC4899",       # Liquid Hydrogen Rose
    "FAIRING": "#64748B",   # Carbon Composite
    "STRUCTURE": "#334155", # Titanium / Al-Li
}

# -------------------------------------------------------------
# Apple Human Interface Guidelines Pro Stylesheet
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

/* Top Navigation Menu */
QMenuBar {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER_HAIRLINE};
    padding: 3px 6px;
    font-size: 12px;
}}
QMenuBar::item {{
    padding: 5px 10px;
    background: transparent;
    border-radius: 5px;
    color: {TEXT_SECONDARY};
}}
QMenuBar::item:selected {{
    background: {BG_CARD};
    color: {TEXT_PRIMARY};
}}

QToolBar {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER_HAIRLINE};
    padding: 6px 12px;
    spacing: 8px;
}}

QStatusBar {{
    background-color: {BG_PANEL};
    border-top: 1px solid {BORDER_HAIRLINE};
    color: {TEXT_SECONDARY};
    font-size: 12px;
    padding: 5px 12px;
}}

/* Inset Grouped Section Cards */
QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_HAIRLINE};
    border-radius: 12px;
    margin-top: 22px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {COLOR_ELECTRIC_BLUE};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

/* Primary & Action Buttons */
QPushButton {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_HAIRLINE};
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 500;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {BG_CARD_HOVER};
    border-color: {BORDER_HAIRLINE};
}}
QPushButton:pressed {{
    background-color: {BG_ELEVATED};
}}

QPushButton#PrimaryButton {{
    background-color: {COLOR_ELECTRIC_BLUE};
    color: #ffffff;
    border: 1px solid {COLOR_ELECTRIC_BLUE};
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    padding: 9px 16px;
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
    border: 1px solid {BORDER_HAIRLINE};
    border-radius: 16px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    font-size: 14px;
}}
QPushButton#TransportButton:hover {{
    background-color: {BG_ELEVATED};
    border-color: {COLOR_ELECTRIC_BLUE};
}}

/* Apple Segmented Pill Selector */
QFrame#SegmentedGroup {{
    background-color: {BG_BASE};
    border: 1px solid {BORDER_HAIRLINE};
    border-radius: 8px;
    padding: 2px;
}}
QPushButton#SegmentChip {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    border: none;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
}}
QPushButton#SegmentChip:hover {{
    color: {TEXT_PRIMARY};
    background-color: {BG_CARD};
}}
QPushButton#SegmentChip:checked {{
    background-color: {BG_CARD};
    color: {COLOR_ELECTRIC_BLUE};
    font-weight: 700;
    border: 1px solid {BORDER_HAIRLINE};
}}

/* Input Controls */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {BG_BASE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_HAIRLINE};
    border-radius: 7px;
    padding: 5px 8px;
    font-size: 12px;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 1px solid {COLOR_ELECTRIC_BLUE};
    background-color: {BG_CARD};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_HAIRLINE};
    border-radius: 8px;
    selection-background-color: {COLOR_ELECTRIC_BLUE};
    selection-color: #ffffff;
    padding: 4px;
}}

/* Sliders */
QSlider::groove:horizontal {{
    height: 4px;
    background: {BG_BASE};
    border: 1px solid {BORDER_HAIRLINE};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {COLOR_ELECTRIC_BLUE};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: #ffffff;
    border: 1.5px solid {COLOR_ELECTRIC_BLUE};
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}}

/* Tab Widget (Apple Segmented Bar Style) */
QTabWidget::pane {{
    border: 1px solid {BORDER_HAIRLINE};
    border-radius: 12px;
    background-color: {BG_PANEL};
    top: -1px;
}}
QTabBar::tab {{
    background: {BG_BASE};
    color: {TEXT_SECONDARY};
    padding: 7px 16px;
    border: 1px solid {BORDER_HAIRLINE};
    border-bottom: none;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    margin-right: 3px;
    font-size: 12px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border-color: {BORDER_HAIRLINE};
    border-bottom: 2px solid {COLOR_ELECTRIC_BLUE};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    color: {TEXT_PRIMARY};
    background: {BG_CARD};
}}

/* Tables (Apple Inset Card Style) */
QTableWidget {{
    background-color: {BG_PANEL};
    border: none;
    border-radius: 8px;
    gridline-color: {BORDER_HAIRLINE};
}}
QTableWidget::item {{
    padding: 7px;
    border-bottom: 1px solid {BORDER_HAIRLINE};
    font-size: 12px;
}}
QTableWidget::item:selected {{
    background-color: rgba(10, 132, 255, 0.15);
    color: {TEXT_PRIMARY};
}}
QHeaderView::section {{
    background-color: {BG_CARD};
    color: {TEXT_SECONDARY};
    padding: 7px;
    border: none;
    border-bottom: 1px solid {BORDER_HAIRLINE};
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_HAIRLINE};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER_HAIRLINE};
    border-radius: 3px;
    min-width: 20px;
}}
"""

DARK_STYLESHEET = FCP_STYLESHEET
