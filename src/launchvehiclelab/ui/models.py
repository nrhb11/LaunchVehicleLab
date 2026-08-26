"""Reactive UI State Coordinator & ViewModel bridging UI events to scientific core."""

from math import radians
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from launchvehiclelab.adapters import load_project, save_project
from launchvehiclelab.application import run_coupled_sizing
from launchvehiclelab.core import (
    PROPELLANT_COMBINATIONS,
    CoupledVehicleResult,
    MissionSpec,
    OrbitTarget,
    TrajectoryResult,
    simulate_ascent_trajectory,
)


class VehicleViewModel(QObject):
    """Manages reactive launcher sizing state, trajectory runs, and persistence."""

    # Qt Signals
    vehicle_sized = Signal(object)        # Emits CoupledVehicleResult
    trajectory_ready = Signal(object)     # Emits TrajectoryResult
    error_occurred = Signal(str)          # Emits error message
    status_message = Signal(str)          # Emits status bar text

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._current_vehicle: CoupledVehicleResult | None = None
        self._current_trajectory: TrajectoryResult | None = None

        # Default Canonical Mission Settings (500 kg to 500 km LEO)
        self.payload_mass_kg: float = 500.0
        self.target_altitude_m: float = 500_000.0
        self.launch_latitude_deg: float = 28.5
        self.stage1_diameter_m: float = 1.4
        self.stage2_diameter_m: float = 1.4
        self.fairing_diameter_m: float = 1.5
        self.stage1_prop_name: str = "KEROLOX"
        self.stage2_prop_name: str = "METHALOX"

    @property
    def current_vehicle(self) -> CoupledVehicleResult | None:
        return self._current_vehicle

    @property
    def current_trajectory(self) -> TrajectoryResult | None:
        return self._current_trajectory

    def run_sizing_and_simulation(self) -> None:
        """Run multidisciplinary vehicle sizing followed by 3DOF trajectory simulation."""
        try:
            self.status_message.emit("Calculating optimal multidisciplinary vehicle sizing...")
            mission = MissionSpec(
                payload_mass_kg=self.payload_mass_kg,
                target=OrbitTarget(altitude_m=self.target_altitude_m),
                launch_latitude_rad=radians(self.launch_latitude_deg),
            )

            stage1_combo = PROPELLANT_COMBINATIONS[self.stage1_prop_name]
            stage2_combo = PROPELLANT_COMBINATIONS[self.stage2_prop_name]

            vehicle = run_coupled_sizing(
                mission=mission,
                stage1_combo=stage1_combo,
                stage2_combo=stage2_combo,
                stage1_diameter_m=self.stage1_diameter_m,
                stage2_diameter_m=self.stage2_diameter_m,
                fairing_diameter_m=self.fairing_diameter_m,
            )
            self._current_vehicle = vehicle
            self.vehicle_sized.emit(vehicle)

            self.status_message.emit("Simulating 3DOF ascent flight trajectory...")
            trajectory = simulate_ascent_trajectory(vehicle)
            self._current_trajectory = trajectory
            self.trajectory_ready.emit(trajectory)

            glow_t = vehicle.gross_liftoff_weight_kg / 1000.0
            max_q_kpa = trajectory.max_q_pa / 1000.0
            self.status_message.emit(
                f"Converged GLOW: {glow_t:.2f} t | Total Length: {vehicle.vehicle_geometry.total_length_m:.2f} m | Max-Q: {max_q_kpa:.2f} kPa"
            )
        except Exception as exc:  # pylint: disable=broad-except
            self.error_occurred.emit(str(exc))
            self.status_message.emit(f"Error: {exc}")

    def save_to_file(self, filepath: str | Path) -> Path | None:
        """Export current vehicle and trajectory to .lvlab JSON."""
        if self._current_vehicle is None:
            self.error_occurred.emit("No vehicle design available to save.")
            return None
        try:
            saved_path = save_project(
                self._current_vehicle,
                filepath,
                trajectory=self._current_trajectory,
            )
            self.status_message.emit(f"Successfully saved project to {saved_path.name}")
            return saved_path
        except Exception as exc:
            self.error_occurred.emit(f"Failed to save file: {exc}")
            return None

    def load_from_file(self, filepath: str | Path) -> bool:
        """Load mission inputs from .lvlab file and trigger recalculation."""
        try:
            data = load_project(filepath)
            mission_data = data.get("mission", {})
            self.payload_mass_kg = float(mission_data.get("payload_mass_kg", 500.0))
            self.target_altitude_m = float(mission_data.get("target_altitude_m", 500000.0))
            self.run_sizing_and_simulation()
            self.status_message.emit(f"Loaded project: {Path(filepath).name}")
            return True
        except Exception as exc:
            self.error_occurred.emit(f"Failed to load file: {exc}")
            return False
