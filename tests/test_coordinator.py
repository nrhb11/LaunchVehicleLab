import pytest

from launchvehiclelab.application import run_coupled_sizing
from launchvehiclelab.core import (
    PROPELLANT_COMBINATIONS,
    MissionSpec,
    OrbitTarget,
)


def test_run_coupled_sizing_convergence() -> None:
    mission = MissionSpec(
        payload_mass_kg=500.0,
        target=OrbitTarget(altitude_m=500_000.0),
        launch_latitude_rad=0.4974,  # 28.5 deg
    )

    result = run_coupled_sizing(
        mission=mission,
        stage1_combo=PROPELLANT_COMBINATIONS["KEROLOX"],
        stage2_combo=PROPELLANT_COMBINATIONS["METHALOX"],
        stage1_diameter_m=1.4,
        stage2_diameter_m=1.4,
    )

    assert result.iterations_to_converge < 30
    assert 12_000.0 < result.gross_liftoff_weight_kg < 25_000.0
    assert result.payload_ratio_percent > 1.5
    assert result.vehicle_geometry.total_length_m > 12.0
    assert 8.0 < result.vehicle_geometry.fineness_ratio < 25.0
    assert result.stage1.propellant_mass_kg > result.stage2.propellant_mass_kg
    assert result.stage1.effective_structural_fraction > 0.05
    assert result.stage2.effective_structural_fraction > 0.06
