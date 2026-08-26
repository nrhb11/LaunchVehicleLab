"""Modern dark-theme stylesheet and visual styling tokens for LaunchVehicleLab."""

# Color Tokens
DARK_BG_MAIN = "#0d1117"
DARK_BG_PANEL = "#161b22"
DARK_BG_CARD = "#21262d"
DARK_BORDER = "#30363d"
DARK_TEXT_PRIMARY = "#f0f6fc"
DARK_TEXT_SECONDARY = "#8b949e"
DARK_TEXT_MUTED = "#6e7681"

ACCENT_BLUE = "#58a6ff"
ACCENT_BLUE_HOVER = "#79c0ff"
ACCENT_GREEN = "#3fb950"
ACCENT_RED = "#f85149"
ACCENT_AMBER = "#d29922"
ACCENT_PURPLE = "#bc8cff"

# Propellant Visual Colors
PROPELLANT_COLORS = {
    "LOX": "#38bdf8",       # Bright sky blue
    "RP1": "#f59e0b",       # Golden kerosene amber
    "CH4": "#a855f7",       # Methane purple
    "LH2": "#ec4899",       # Liquid hydrogen rose
    "FAIRING": "#94a3b8",   # Carbon composite silver-slate
    "STRUCTURE": "#475569", # Structural titanium/aluminum
}

DARK_STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {DARK_BG_MAIN};
    color: {DARK_TEXT_PRIMARY};
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, sans-serif;
}}

QWidget {{
    color: {DARK_TEXT_PRIMARY};
    background-color: transparent;
    font-size: 13px;
}}

/* Top Menu & ToolBar */
QMenuBar {{
    background-color: {DARK_BG_PANEL};
    border-bottom: 1px solid {DARK_BORDER};
    padding: 2px 6px;
}}
QMenuBar::item {{
    padding: 6px 10px;
    background: transparent;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background: {DARK_BG_CARD};
}}

QToolBar {{
    background-color: {DARK_BG_PANEL};
    border-bottom: 1px solid {DARK_BORDER};
    padding: 6px 12px;
    spacing: 8px;
}}

QStatusBar {{
    background-color: {DARK_BG_PANEL};
    border-top: 1px solid {DARK_BORDER};
    color: {DARK_TEXT_SECONDARY};
    padding: 4px 10px;
}}

/* Panels and Group Boxes */
QGroupBox {{
    background-color: {DARK_BG_PANEL};
    border: 1px solid {DARK_BORDER};
    border-radius: 8px;
    margin-top: 24px;
    padding: 14px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {ACCENT_BLUE};
    font-size: 13px;
}}

/* Buttons */
QPushButton {{
    background-color: {DARK_BG_CARD};
    color: {DARK_TEXT_PRIMARY};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {DARK_BORDER};
    border-color: {DARK_TEXT_MUTED};
}}
QPushButton:pressed {{
    background-color: #1b1f24;
}}
QPushButton#PrimaryButton {{
    background-color: {ACCENT_BLUE};
    color: #ffffff;
    border: 1px solid #1f6feb;
    font-weight: 600;
}}
QPushButton#PrimaryButton:hover {{
    background-color: {ACCENT_BLUE_HOVER};
}}

/* Inputs & Spinboxes */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {DARK_BG_MAIN};
    color: {DARK_TEXT_PRIMARY};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {ACCENT_BLUE};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {DARK_BG_CARD};
    border: 1px solid {DARK_BORDER};
    selection-background-color: {ACCENT_BLUE};
    selection-color: #ffffff;
}}

/* Sliders */
QSlider::groove:horizontal {{
    height: 4px;
    background: {DARK_BORDER};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT_BLUE};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: #ffffff;
    border: 2px solid {ACCENT_BLUE};
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {DARK_BORDER};
    border-radius: 8px;
    background-color: {DARK_BG_PANEL};
    top: -1px;
}}
QTabBar::tab {{
    background: {DARK_BG_MAIN};
    color: {DARK_TEXT_SECONDARY};
    padding: 8px 18px;
    border: 1px solid {DARK_BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    background: {DARK_BG_PANEL};
    color: {ACCENT_BLUE};
    border-color: {DARK_BORDER};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    color: {DARK_TEXT_PRIMARY};
}}

/* Tables */
QTableWidget {{
    background-color: {DARK_BG_MAIN};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    gridline-color: {DARK_BORDER};
}}
QTableWidget::item {{
    padding: 6px;
}}
QHeaderView::section {{
    background-color: {DARK_BG_CARD};
    color: {DARK_TEXT_SECONDARY};
    padding: 8px;
    border: none;
    border-right: 1px solid {DARK_BORDER};
    border-bottom: 1px solid {DARK_BORDER};
    font-weight: 600;
}}

/* ScrollBars */
QScrollBar:vertical {{
    background: {DARK_BG_MAIN};
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {DARK_BORDER};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {DARK_TEXT_MUTED};
}}
"""
