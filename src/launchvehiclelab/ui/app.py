"""Desktop application entrypoint for LaunchVehicleLab."""

import sys
from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from launchvehiclelab.ui.theme import DARK_STYLESHEET
from launchvehiclelab.ui.widgets.main_window import MainWindow


def main(argv: Sequence[str] | None = None) -> int:
    """Launch the LaunchVehicleLab PySide6 desktop application."""
    if argv is None:
        argv = sys.argv

    # Support headless verification (for automated tests / CI environments)
    is_headless = "--headless-check" in argv

    app = QApplication.instance()
    if app is None:
        app = QApplication(list(argv))

    app.setApplicationName("LaunchVehicleLab")
    app.setOrganizationName("LaunchVehicleLab")
    app.setStyleSheet(DARK_STYLESHEET)

    window = MainWindow()

    if is_headless:
        # Verify initialization and close immediately
        window.close()
        return 0

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
