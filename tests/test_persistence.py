import json
from pathlib import Path

import pytest

from launchvehiclelab.adapters import load_project, save_project
from launchvehiclelab.application import run_coupled_sizing
from launchvehiclelab.core import (
    PROPELLANT_COMBINATIONS,
    MissionSpec,
    OrbitTarget,
)


def test_persistence_roundtrip(tmp_path: Path) -> None:
    mission = MissionSpec(
        payload_mass_kg=500.0,
        target=OrbitTarget(altitude_m=500_000.0),
        launch_latitude_rad=0.4974,
    )

    result = run_coupled_sizing(
        mission=mission,
        stage1_combo=PROPELLANT_COMBINATIONS["KEROLOX"],
        stage2_combo=PROPELLANT_COMBINATIONS["METHALOX"],
        stage1_diameter_m=1.4,
        stage2_diameter_m=1.4,
    )

    project_file = tmp_path / "test_launcher.lvlab"
    saved_path = save_project(result, project_file)

    assert saved_path.exists()
    loaded_data = load_project(saved_path)

    assert loaded_data["schema_version"] == "0.4"
    assert loaded_data["mission"]["payload_mass_kg"] == 500.0
    assert loaded_data["vehicle_summary"]["gross_liftoff_weight_kg"] == pytest.approx(
        result.gross_liftoff_weight_kg, rel=1e-6
    )
    assert len(loaded_data["stages"]) == 2


def test_load_project_rejects_invalid_version(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.lvlab"
    bad_file.write_text(json.dumps({"schema_version": "999.0"}))

    with pytest.raises(ValueError, match="Unsupported project schema version"):
        load_project(bad_file)
