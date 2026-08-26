"""Apple Final Cut Pro inspired Mission Control Inspector Panel with Segmented Chips & Telemetry Gauges."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from launchvehiclelab.core.domain import CoupledVehicleResult, TrajectoryPoint, TrajectoryResult
from launchvehiclelab.ui.models import VehicleViewModel
from launchvehiclelab.ui.theme import (
    BG_CARD,
    COLOR_ALERT_CORAL,
    COLOR_CYAN,
    COLOR_ELECTRIC_BLUE,
    COLOR_FLIGHT_GREEN,
    COLOR_SUNSET_AMBER,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class TelemetryMeter(QWidget):
    """Sleek Apple-style horizontal VU telemetry bar with value label."""

    def __init__(self, label: str, unit: str, max_val: float, bar_color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.max_val = max_val
        self.unit = unit

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 4)
        layout.setSpacing(4)

        header_layout = QHBoxLayout()
        self.title_lbl = QLabel(label)
        self.title_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
        self.val_lbl = QLabel(f"0.0 {unit}")
        self.val_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 12px; font-weight: bold; font-family: monospace;")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.val_lbl)
        layout.addLayout(header_layout)

        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(5)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BG_CARD};
                border: 1px solid #27272a;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {bar_color};
                border-radius: 2px;
            }}
        """)
        layout.addWidget(self.bar)

    def set_value(self, val: float) -> None:
        self.val_lbl.setText(f"{val:.1f} {self.unit}")
        percent = max(0.0, min(1.0, val / max(1e-3, self.max_val)))
        self.bar.setValue(int(percent * 1000))


class MissionPanel(QWidget):
    """Left-hand FCP inspector panel with segmented controls, mission inputs, and live telemetry."""

    def __init__(self, view_model: VehicleViewModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.vm = view_model
        self._init_ui()
        self._bind_events()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # -------------------------------------------------------------
        # Section 1: Target Mission Specification
        # -------------------------------------------------------------
        mission_group = QGroupBox("🛰️ Mission Specification")
        mission_form = QFormLayout(mission_group)
        mission_form.setSpacing(8)
        mission_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.payload_spin = QDoubleSpinBox()
        self.payload_spin.setRange(10.0, 50_000.0)
        self.payload_spin.setValue(self.vm.payload_mass_kg)
        self.payload_spin.setSuffix(" kg")
        self.payload_spin.setSingleStep(50.0)
        mission_form.addRow("Payload Mass", self.payload_spin)

        self.alt_spin = QDoubleSpinBox()
        self.alt_spin.setRange(150.0, 2000.0)
        self.alt_spin.setValue(self.vm.target_altitude_m / 1000.0)
        self.alt_spin.setSuffix(" km")
        self.alt_spin.setSingleStep(50.0)
        mission_form.addRow("Target Orbit", self.alt_spin)

        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(0.0, 70.0)
        self.lat_spin.setValue(self.vm.launch_latitude_deg)
        self.lat_spin.setSuffix(" °")
        mission_form.addRow("Launch Lat", self.lat_spin)

        layout.addWidget(mission_group)

        # -------------------------------------------------------------
        # Section 2: Propellant & Segmented Stage Architecture
        # -------------------------------------------------------------
        prop_group = QGroupBox("🔥 Stage Propulsion & Sizing")
        prop_layout = QVBoxLayout(prop_group)
        prop_layout.setSpacing(10)

        # Stage 1 Propellant Segmented Chips
        s1_lbl = QLabel("Stage 1 Booster Propellant")
        s1_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
        prop_layout.addWidget(s1_lbl)

        s1_seg_frame = QFrame()
        s1_seg_frame.setObjectName("SegmentedGroup")
        s1_seg_layout = QHBoxLayout(s1_seg_frame)
        s1_seg_layout.setContentsMargins(2, 2, 2, 2)
        s1_seg_layout.setSpacing(2)

        self.s1_group = QButtonGroup(self)
        for name in ["KEROLOX", "METHALOX", "HYDROLOX"]:
            chip = QPushButton(name)
            chip.setObjectName("SegmentChip")
            chip.setCheckable(True)
            if name == self.vm.stage1_prop_name:
                chip.setChecked(True)
            self.s1_group.addButton(chip)
            s1_seg_layout.addWidget(chip)
        prop_layout.addWidget(s1_seg_frame)

        # Stage 2 Propellant Segmented Chips
        s2_lbl = QLabel("Stage 2 Upper Stage Propellant")
        s2_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
        prop_layout.addWidget(s2_lbl)

        s2_seg_frame = QFrame()
        s2_seg_frame.setObjectName("SegmentedGroup")
        s2_seg_layout = QHBoxLayout(s2_seg_frame)
        s2_seg_layout.setContentsMargins(2, 2, 2, 2)
        s2_seg_layout.setSpacing(2)

        self.s2_group = QButtonGroup(self)
        for name in ["METHALOX", "KEROLOX", "HYDROLOX"]:
            chip = QPushButton(name)
            chip.setObjectName("SegmentChip")
            chip.setCheckable(True)
            if name == self.vm.stage2_prop_name:
                chip.setChecked(True)
            self.s2_group.addButton(chip)
            s2_seg_layout.addWidget(chip)
        prop_layout.addWidget(s2_seg_frame)

        # Stage Diameters
        diam_form = QFormLayout()
        diam_form.setSpacing(8)

        self.s1_diam_spin = QDoubleSpinBox()
        self.s1_diam_spin.setRange(0.6, 6.0)
        self.s1_diam_spin.setValue(self.vm.stage1_diameter_m)
        self.s1_diam_spin.setSuffix(" m")
        self.s1_diam_spin.setSingleStep(0.1)
        diam_form.addRow("S1 Diameter", self.s1_diam_spin)

        self.s2_diam_spin = QDoubleSpinBox()
        self.s2_diam_spin.setRange(0.6, 6.0)
        self.s2_diam_spin.setValue(self.vm.stage2_diameter_m)
        self.s2_diam_spin.setSuffix(" m")
        self.s2_diam_spin.setSingleStep(0.1)
        diam_form.addRow("S2 Diameter", self.s2_diam_spin)

        prop_layout.addLayout(diam_form)
        layout.addWidget(prop_group)

        # -------------------------------------------------------------
        # Section 3: Action Trigger
        # -------------------------------------------------------------
        self.run_button = QPushButton("⚡ Size Vehicle & Run 3DOF Ascent")
        self.run_button.setObjectName("PrimaryButton")
        self.run_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_button.setMinimumHeight(40)
        layout.addWidget(self.run_button)

        # -------------------------------------------------------------
        # Section 4: Live Instantaneous Flight Telemetry HUD
        # -------------------------------------------------------------
        hud_group = QGroupBox("📟 Flight Telemetry HUD")
        hud_layout = QVBoxLayout(hud_group)
        hud_layout.setSpacing(8)

        self.alt_meter = TelemetryMeter("Instant Altitude", "km", 500.0, COLOR_ELECTRIC_BLUE)
        self.vel_meter = TelemetryMeter("Velocity", "m/s", 8000.0, COLOR_CYAN)
        self.dyn_meter = TelemetryMeter("Dynamic Pressure", "kPa", 50.0, COLOR_ALERT_CORAL)
        self.g_meter = TelemetryMeter("Axial G-Force", "g", 6.0, COLOR_FLIGHT_GREEN)

        hud_layout.addWidget(self.alt_meter)
        hud_layout.addWidget(self.vel_meter)
        hud_layout.addWidget(self.dyn_meter)
        hud_layout.addWidget(self.g_meter)

        layout.addWidget(hud_group)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _bind_events(self) -> None:
        self.run_button.clicked.connect(self._on_run_clicked)

    def _on_run_clicked(self) -> None:
        self.vm.payload_mass_kg = self.payload_spin.value()
        self.vm.target_altitude_m = self.alt_spin.value() * 1000.0
        self.vm.launch_latitude_deg = self.lat_spin.value()

        # Selected propellant chips
        s1_checked = self.s1_group.checkedButton()
        if s1_checked:
            self.vm.stage1_prop_name = s1_checked.text()
        s2_checked = self.s2_group.checkedButton()
        if s2_checked:
            self.vm.stage2_prop_name = s2_checked.text()

        self.vm.stage1_diameter_m = self.s1_diam_spin.value()
        self.vm.stage2_diameter_m = self.s2_diam_spin.value()
        self.vm.run_sizing_and_simulation()

    def update_telemetry_hud(self, point: TrajectoryPoint) -> None:
        """Update live telemetry meters from scrubbed trajectory sample."""
        self.alt_meter.set_value(point.altitude_m / 1000.0)
        self.vel_meter.set_value(point.velocity_m_per_s)
        self.dyn_meter.set_value(point.dynamic_pressure_pa / 1000.0)
        self.g_meter.set_value(point.acceleration_g)
