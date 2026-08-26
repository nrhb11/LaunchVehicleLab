"""Apple Final Cut Pro inspired Master Window integrating inspector, studio blueprint, trajectory, and magnetic timeline."""

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
from launchvehiclelab.core.domain import CoupledVehicleResult, TrajectoryPoint, TrajectoryResult
from launchvehiclelab.ui.models import VehicleViewModel
from launchvehiclelab.ui.theme import BG_CANVAS, BG_PANEL, BORDER_SUBTLE, SPACE_BLACK
from launchvehiclelab.ui.widgets.events_table import EventsTable
from launchvehiclelab.ui.widgets.mission_panel import MissionPanel
from launchvehiclelab.ui.widgets.rocket_canvas import RocketCanvas
from launchvehiclelab.ui.widgets.scrubber_bar import FlightScrubberBar
from launchvehiclelab.ui.widgets.trajectory_view import TrajectoryView


class MainWindow(QMainWindow):
    """Main desktop interface window with Apple FCP pro design and magnetic flight scrubber."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"LaunchVehicleLab Studio v{__version__} — Multidisciplinary Launcher Design & Flight Engine")
        self.resize(1380, 880)

        self.vm = VehicleViewModel(self)
        self._current_trajectory: TrajectoryResult | None = None

        self._init_ui()
        self._init_menus()
        self._bind_signals()

        # Run initial benchmark calculation on startup
        self.vm.run_sizing_and_simulation()

    def _init_ui(self) -> None:
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {SPACE_BLACK};")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(6)

        # -------------------------------------------------------------
        # 1. Main Three-Panel Horizontal Workspace
        # -------------------------------------------------------------
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {BORDER_SUBTLE}; width: 1px; }}")

        # Left Panel: Mission & Sizing Inspector
        self.mission_panel = MissionPanel(self.vm)
        self.mission_panel.setMinimumWidth(320)
        self.mission_panel.setMaximumWidth(420)
        splitter.addWidget(self.mission_panel)

        # Middle Panel: 2D Aerospace CAD Blueprint
        self.rocket_canvas = RocketCanvas()
        self.rocket_canvas.setMinimumWidth(340)
        splitter.addWidget(self.rocket_canvas)

        # Right Panel: Multi-view Trajectory & Mission Event Log
        right_tabs = QTabWidget()
        self.trajectory_view = TrajectoryView()
        self.events_table = EventsTable()

        right_tabs.addTab(self.trajectory_view, "📊 Ascent Dynamics")
        right_tabs.addTab(self.events_table, "⏱️ Event Timeline")
        splitter.addWidget(right_tabs)

        splitter.setSizes([340, 420, 620])
        root_layout.addWidget(splitter, 1)

        # -------------------------------------------------------------
        # 2. Bottom Magnetic Timeline & Transport Scrubber Deck
        # -------------------------------------------------------------
        self.scrubber_bar = FlightScrubberBar()
        root_layout.addWidget(self.scrubber_bar)

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

        # Timeline Scrubber connection to all views
        self.scrubber_bar.time_changed.connect(self._on_time_scrubbed)

    def _on_vehicle_sized(self, vehicle: CoupledVehicleResult) -> None:
        self.rocket_canvas.set_vehicle(vehicle)

    def _on_trajectory_ready(self, traj: TrajectoryResult) -> None:
        self._current_trajectory = traj
        self.rocket_canvas.set_trajectory(traj)
        self.trajectory_view.update_trajectory(traj)
        self.events_table.update_events(traj)
        self.scrubber_bar.set_trajectory(traj)
        if self.vm.current_vehicle is not None:
            self.mission_panel.update_hero_cards(self.vm.current_vehicle, traj)

    def _on_time_scrubbed(self, time_s: float) -> None:
        """Synchronize playhead across canvas, trajectory plots, telemetry HUD, and events."""
        self.rocket_canvas.set_flight_time(time_s)
        self.trajectory_view.set_flight_time(time_s)
        self.events_table.highlight_event_at_time(time_s)

        # Interpolate instantaneous telemetry point
        if self._current_trajectory and self._current_trajectory.points:
            pts = self._current_trajectory.points
            # Binary search or closest point lookup
            closest_pt = min(pts, key=lambda p: abs(p.time_s - time_s))
            self.mission_panel.update_telemetry_hud(closest_pt)

    def _on_error(self, err: str) -> None:
        QMessageBox.critical(self, "Analysis Error", f"An error occurred during analysis:\n\n{err}")

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
            f"<b>LaunchVehicleLab Studio v{__version__}</b><br><br>"
            "Open-source launch vehicle preliminary sizing & 3DOF flight trajectory simulation platform.<br><br>"
            "Design inspired by Apple Pro Video & Aerospace Telemetry Studios.",
        )
