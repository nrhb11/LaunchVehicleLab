"""Master application window integrating all LaunchVehicleLab UI components."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from launchvehiclelab import __version__
from launchvehiclelab.core.domain import CoupledVehicleResult, TrajectoryResult
from launchvehiclelab.ui.models import VehicleViewModel
from launchvehiclelab.ui.widgets.events_table import EventsTable
from launchvehiclelab.ui.widgets.mission_panel import MissionPanel
from launchvehiclelab.ui.widgets.rocket_canvas import RocketCanvas
from launchvehiclelab.ui.widgets.trajectory_view import TrajectoryView


class MainWindow(QMainWindow):
    """Main desktop interface window for LaunchVehicleLab."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"LaunchVehicleLab v{__version__} — Launch Vehicle Preliminary Sizing & Simulation")
        self.resize(1340, 840)

        self.vm = VehicleViewModel(self)

        self._init_ui()
        self._init_menus()
        self._bind_signals()

        # Run initial benchmark calculation on startup
        self.vm.run_sizing_and_simulation()

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Three-panel splitter: Controls | 2D Blueprint | Flight Dynamics / Events
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left Panel: Mission Controls
        self.mission_panel = MissionPanel(self.vm)
        self.mission_panel.setMinimumWidth(320)
        self.mission_panel.setMaximumWidth(420)
        splitter.addWidget(self.mission_panel)

        # 2. Middle Panel: 2D Rocket Canvas
        self.rocket_canvas = RocketCanvas()
        self.rocket_canvas.setMinimumWidth(320)
        splitter.addWidget(self.rocket_canvas)

        # 3. Right Panel: Trajectory Plots & Event Log Tabs
        right_tabs = QTabWidget()
        self.trajectory_view = TrajectoryView()
        self.events_table = EventsTable()

        right_tabs.addTab(self.trajectory_view, "📊 Ascent Flight Dynamics")
        right_tabs.addTab(self.events_table, "⏱️ Mission Event Timeline")
        splitter.addWidget(right_tabs)

        # Set initial splitter proportions (25% | 30% | 45%)
        splitter.setSizes([340, 400, 600])
        main_layout.addWidget(splitter)

        # Status Bar
        self.statusBar().showMessage("Ready")

    def _init_menus(self) -> None:
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Project (.lvlab)...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Project (.lvlab)...", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save_project)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        reset_action = QAction("&Reset to 500kg LEO Benchmark", self)
        reset_action.triggered.connect(self._on_reset_benchmark)
        file_menu.addAction(reset_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About LaunchVehicleLab", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _bind_signals(self) -> None:
        self.vm.vehicle_sized.connect(self._on_vehicle_sized)
        self.vm.trajectory_ready.connect(self._on_trajectory_ready)
        self.vm.status_message.connect(self.statusBar().showMessage)
        self.vm.error_occurred.connect(self._on_error)

    def _on_vehicle_sized(self, vehicle: CoupledVehicleResult) -> None:
        self.rocket_canvas.set_vehicle(vehicle)

    def _on_trajectory_ready(self, traj: TrajectoryResult) -> None:
        self.trajectory_view.update_trajectory(traj)
        self.events_table.update_events(traj)

    def _on_error(self, err: str) -> None:
        QMessageBox.critical(self, "Calculation Error", f"An error occurred during analysis:\n\n{err}")

    def _on_open_project(self) -> None:
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open LaunchVehicleLab Project",
            "",
            "LVLab Projects (*.lvlab *.json);;All Files (*)",
        )
        if filepath:
            self.vm.load_from_file(filepath)

    def _on_save_project(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save LaunchVehicleLab Project",
            "my_launcher.lvlab",
            "LVLab Projects (*.lvlab);;JSON Files (*.json)",
        )
        if filepath:
            self.vm.save_to_file(filepath)

    def _on_reset_benchmark(self) -> None:
        self.vm.payload_mass_kg = 500.0
        self.vm.target_altitude_m = 500_000.0
        self.vm.stage1_diameter_m = 1.4
        self.vm.stage2_diameter_m = 1.4
        self.mission_panel.payload_spin.setValue(500.0)
        self.mission_panel.alt_spin.setValue(500.0)
        self.mission_panel.s1_diam_spin.setValue(1.4)
        self.mission_panel.s2_diam_spin.setValue(1.4)
        self.vm.run_sizing_and_simulation()

    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            "About LaunchVehicleLab",
            f"<b>LaunchVehicleLab v{__version__}</b><br><br>"
            "Open-source launch vehicle preliminary design and 3DOF flight simulation platform.<br><br>"
            "Features:<br>"
            "• Multidisciplinary coupled mass-geometry sizing coordinator<br>"
            "• 2:1 ellipsoidal tank geometry & subsystem mass models<br>"
            "• 1976 US Standard Atmosphere & aerodynamic load modeling<br>"
            "• 3DOF point-mass ascent flight dynamics ODE solver<br>"
            "• Discrete mission event state machine",
        )
