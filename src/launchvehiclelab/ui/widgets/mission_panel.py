"""Mission parameters and input controls panel widget."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from launchvehiclelab.core.domain import CoupledVehicleResult, TrajectoryResult
from launchvehiclelab.ui.models import VehicleViewModel
from launchvehiclelab.ui.theme import (
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_RED,
    DARK_BG_CARD,
    DARK_TEXT_PRIMARY,
    DARK_TEXT_SECONDARY,
)


class MissionPanel(QWidget):
    """Left-hand sidebar for parameter controls and top-level mission summary."""

    run_requested = Signal()

    def __init__(self, view_model: VehicleViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.vm = view_model
        self._init_ui()
        self._bind_events()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # -------------------------------------------------------------
        # Section 1: Mission Target & Orbit
        # -------------------------------------------------------------
        mission_group = QGroupBox("🛰️ Target Mission & Payload")
        mission_form = QFormLayout(mission_group)
        mission_form.setSpacing(10)

        # Payload Mass
        self.payload_spin = QDoubleSpinBox()
        self.payload_spin.setRange(10.0, 50_000.0)
        self.payload_spin.setValue(self.vm.payload_mass_kg)
        self.payload_spin.setSuffix(" kg")
        self.payload_spin.setSingleStep(50.0)
        mission_form.addRow("Payload Mass:", self.payload_spin)

        # Orbit Altitude
        self.alt_spin = QDoubleSpinBox()
        self.alt_spin.setRange(150.0, 2000.0)
        self.alt_spin.setValue(self.vm.target_altitude_m / 1000.0)
        self.alt_spin.setSuffix(" km")
        self.alt_spin.setSingleStep(50.0)
        mission_form.addRow("Target LEO Alt:", self.alt_spin)

        # Launch Latitude
        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(0.0, 70.0)
        self.lat_spin.setValue(self.vm.launch_latitude_deg)
        self.lat_spin.setSuffix(" °")
        mission_form.addRow("Launch Latitude:", self.lat_spin)

        layout.addWidget(mission_group)

        # -------------------------------------------------------------
        # Section 2: Propulsion & Propellant Selection
        # -------------------------------------------------------------
        prop_group = QGroupBox("🔥 Stage Propellants & Geometry")
        prop_form = QFormLayout(prop_group)
        prop_form.setSpacing(10)

        self.s1_prop_combo = QComboBox()
        self.s1_prop_combo.addItems(["KEROLOX", "METHALOX", "HYDROLOX"])
        self.s1_prop_combo.setCurrentText(self.vm.stage1_prop_name)
        prop_form.addRow("Stage 1 Prop:", self.s1_prop_combo)

        self.s1_diam_spin = QDoubleSpinBox()
        self.s1_diam_spin.setRange(0.5, 6.0)
        self.s1_diam_spin.setValue(self.vm.stage1_diameter_m)
        self.s1_diam_spin.setSuffix(" m")
        self.s1_diam_spin.setSingleStep(0.1)
        prop_form.addRow("Stage 1 Diameter:", self.s1_diam_spin)

        self.s2_prop_combo = QComboBox()
        self.s2_prop_combo.addItems(["METHALOX", "KEROLOX", "HYDROLOX"])
        self.s2_prop_combo.setCurrentText(self.vm.stage2_prop_name)
        prop_form.addRow("Stage 2 Prop:", self.s2_prop_combo)

        self.s2_diam_spin = QDoubleSpinBox()
        self.s2_diam_spin.setRange(0.5, 6.0)
        self.s2_diam_spin.setValue(self.vm.stage2_diameter_m)
        self.s2_diam_spin.setSuffix(" m")
        self.s2_diam_spin.setSingleStep(0.1)
        prop_form.addRow("Stage 2 Diameter:", self.s2_diam_spin)

        self.fairing_diam_spin = QDoubleSpinBox()
        self.fairing_diam_spin.setRange(0.5, 6.5)
        self.fairing_diam_spin.setValue(self.vm.fairing_diameter_m)
        self.fairing_diam_spin.setSuffix(" m")
        self.fairing_diam_spin.setSingleStep(0.1)
        prop_form.addRow("Fairing Diameter:", self.fairing_diam_spin)

        layout.addWidget(prop_group)

        # -------------------------------------------------------------
        # Section 3: Action Button
        # -------------------------------------------------------------
        self.run_button = QPushButton("⚡ Size Rocket & Simulate 3DOF Flight")
        self.run_button.setObjectName("PrimaryButton")
        self.run_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_button.setMinimumHeight(42)
        layout.addWidget(self.run_button)

        # -------------------------------------------------------------
        # Section 4: Live KPI Summary Card
        # -------------------------------------------------------------
        kpi_group = QGroupBox("📊 Key Performance Indicators")
        kpi_layout = QVBoxLayout(kpi_group)
        kpi_layout.setSpacing(8)

        self.glow_label = QLabel("GLOW: --")
        self.glow_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {ACCENT_GREEN};")
        kpi_layout.addWidget(self.glow_label)

        self.length_label = QLabel("Stack Length: --")
        kpi_layout.addWidget(self.length_label)

        self.fineness_label = QLabel("Fineness (L/D): --")
        kpi_layout.addWidget(self.fineness_label)

        self.payload_ratio_label = QLabel("Payload Ratio: --")
        kpi_layout.addWidget(self.payload_ratio_label)

        self.max_q_label = QLabel("Max-Q: --")
        self.max_q_label.setStyleSheet(f"font-weight: bold; color: {ACCENT_RED};")
        kpi_layout.addWidget(self.max_q_label)

        self.burnout_v_label = QLabel("Insertion Vel: --")
        self.burnout_v_label.setStyleSheet(f"color: {ACCENT_BLUE};")
        kpi_layout.addWidget(self.burnout_v_label)

        layout.addWidget(kpi_group)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _bind_events(self) -> None:
        self.run_button.clicked.connect(self._on_run_clicked)
        self.vm.vehicle_sized.connect(self.update_vehicle_kpis)
        self.vm.trajectory_ready.connect(self.update_trajectory_kpis)

    def _on_run_clicked(self) -> None:
        self.vm.payload_mass_kg = self.payload_spin.value()
        self.vm.target_altitude_m = self.alt_spin.value() * 1000.0
        self.vm.launch_latitude_deg = self.lat_spin.value()
        self.vm.stage1_prop_name = self.s1_prop_combo.currentText()
        self.vm.stage2_prop_name = self.s2_prop_combo.currentText()
        self.vm.stage1_diameter_m = self.s1_diam_spin.value()
        self.vm.stage2_diameter_m = self.s2_diam_spin.value()
        self.vm.fairing_diameter_m = self.fairing_diam_spin.value()
        self.vm.run_sizing_and_simulation()

    def update_vehicle_kpis(self, vehicle: CoupledVehicleResult) -> None:
        glow_t = vehicle.gross_liftoff_weight_kg / 1000.0
        self.glow_label.setText(f"GLOW: {glow_t:.2f} t ({vehicle.gross_liftoff_weight_kg:,.0f} kg)")
        self.length_label.setText(f"Stack Length: {vehicle.vehicle_geometry.total_length_m:.2f} m")
        self.fineness_label.setText(f"Fineness Ratio (L/D): {vehicle.vehicle_geometry.fineness_ratio:.1f}")
        self.payload_ratio_label.setText(f"Payload Ratio: {vehicle.payload_ratio_percent:.2f}%")

    def update_trajectory_kpis(self, traj: TrajectoryResult) -> None:
        max_q_kpa = traj.max_q_pa / 1000.0
        self.max_q_label.setText(f"Max-Q: {max_q_kpa:.2f} kPa (@ {traj.max_q_alt_m / 1000.0:.1f} km)")
        self.burnout_v_label.setText(f"Insertion Vel: {traj.final_orbit_velocity_m_per_s:,.1f} m/s")
