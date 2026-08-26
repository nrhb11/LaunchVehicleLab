import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
import pytest

from launchvehiclelab.ui.app import main as app_main
from launchvehiclelab.ui.models import VehicleViewModel


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    # Set offscreen platform for headless test environments
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_vehicle_view_model_sizing_and_simulation(qapp: QApplication) -> None:
    vm = VehicleViewModel()

    received_vehicle = []
    received_trajectory = []

    vm.vehicle_sized.connect(received_vehicle.append)
    vm.trajectory_ready.connect(received_trajectory.append)

    vm.payload_mass_kg = 500.0
    vm.target_altitude_m = 500_000.0
    vm.run_sizing_and_simulation()

    assert len(received_vehicle) == 1
    assert len(received_trajectory) == 1

    vehicle = received_vehicle[0]
    traj = received_trajectory[0]

    assert vehicle.gross_liftoff_weight_kg > 15_000.0
    assert traj.max_q_pa > 20_000.0
    assert len(traj.events) >= 5


def test_vehicle_view_model_persistence(qapp: QApplication, tmp_path: Path) -> None:
    vm = VehicleViewModel()
    vm.payload_mass_kg = 750.0
    vm.run_sizing_and_simulation()

    save_file = tmp_path / "saved_ui_launcher.lvlab"
    saved_path = vm.save_to_file(save_file)
    assert saved_path is not None
    assert saved_path.exists()

    vm2 = VehicleViewModel()
    success = vm2.load_from_file(saved_path)
    assert success is True
    assert vm2.payload_mass_kg == 750.0


def test_app_headless_entrypoint(qapp: QApplication) -> None:
    exit_code = app_main(["lvlab-gui", "--headless-check"])
    assert exit_code == 0
