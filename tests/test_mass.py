import pytest

from launchvehiclelab.core import (
    PROPELLANT_COMBINATIONS,
    estimate_fairing_mass,
    estimate_stage_subsystems,
    size_fairing_geometry,
    size_stage_geometry,
)


def test_estimate_fairing_mass() -> None:
    fairing_geom = size_fairing_geometry(500.0, 1.4, 1.8)
    mass = estimate_fairing_mass(fairing_geom, areal_density_kg_per_m2=10.0, mechanism_fraction=0.20)
    assert mass > 0.0
    assert mass == pytest.approx(fairing_geom.surface_area_m2 * 10.0 * 1.20, rel=1e-6)


def test_estimate_stage_subsystems_accounting() -> None:
    combo = PROPELLANT_COMBINATIONS["KEROLOX"]
    stage_geom = size_stage_geometry(12000.0, combo, 1.4)

    subsystems = estimate_stage_subsystems(
        stage_geom=stage_geom,
        propellant_mass_kg=12000.0,
        stage_initial_mass_kg=16000.0,
        thrust_to_weight=1.3,
        engine_thrust_to_weight=80.0,
        tank_areal_density_kg_per_m2=15.0,
        avionics_mass_kg=40.0,
        interstage_mass_kg=30.0,
    )

    expected_sum = (
        subsystems.tanks_mass_kg
        + subsystems.propulsion_mass_kg
        + subsystems.avionics_mass_kg
        + subsystems.interstage_mass_kg
        + subsystems.fairing_mass_kg
        + subsystems.residuals_and_margin_kg
    )

    assert subsystems.total_dry_mass_kg == pytest.approx(expected_sum, rel=1e-6)
    assert subsystems.tanks_mass_kg > 0.0
    assert subsystems.propulsion_mass_kg > 0.0
    assert subsystems.residuals_and_margin_kg > 0.0
