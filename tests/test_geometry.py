from math import pi

import pytest

from launchvehiclelab.core import (
    PROPELLANT_COMBINATIONS,
    assemble_vehicle_geometry,
    size_fairing_geometry,
    size_stage_geometry,
    size_tank_geometry,
)


def test_size_tank_geometry_volume_conservation() -> None:
    mass_kg = 10_000.0
    density = 1141.0  # LOX
    diameter = 1.4
    ullage = 0.04

    tank = size_tank_geometry(
        propellant_mass_kg=mass_kg,
        density_kg_per_m3=density,
        diameter_m=diameter,
        ullage_fraction=ullage,
    )

    expected_volume = (mass_kg / density) * (1.0 + ullage)
    assert tank.volume_m3 == pytest.approx(expected_volume, rel=1e-6)
    assert tank.diameter_m == diameter
    assert tank.dome_height_m == pytest.approx(diameter / 4.0, rel=1e-6)
    assert tank.total_length_m == pytest.approx(tank.cylinder_length_m + diameter / 2.0, rel=1e-6)
    assert tank.surface_area_m2 > 0.0


def test_size_stage_geometry_propellant_split() -> None:
    prop_mass = 12_000.0
    combo = PROPELLANT_COMBINATIONS["KEROLOX"]
    diameter = 1.4

    stage_geom = size_stage_geometry(
        propellant_mass_kg=prop_mass,
        propellant_combo=combo,
        diameter_m=diameter,
    )

    mr = combo.default_mixture_ratio_of
    m_ox = prop_mass * (mr / (1.0 + mr))
    m_fuel = prop_mass * (1.0 / (1.0 + mr))

    expected_ox_vol = (m_ox / combo.oxidizer.density_kg_per_m3) * 1.04
    expected_fuel_vol = (m_fuel / combo.fuel.density_kg_per_m3) * 1.04

    assert stage_geom.oxidizer_tank.volume_m3 == pytest.approx(expected_ox_vol, rel=1e-6)
    assert stage_geom.fuel_tank.volume_m3 == pytest.approx(expected_fuel_vol, rel=1e-6)
    assert stage_geom.total_length_m > (
        stage_geom.oxidizer_tank.total_length_m + stage_geom.fuel_tank.total_length_m
    )


def test_size_fairing_geometry() -> None:
    fairing = size_fairing_geometry(
        payload_mass_kg=500.0,
        diameter_m=1.5,
        cylinder_length_m=1.8,
    )

    assert fairing.diameter_m == 1.5
    assert fairing.cylinder_length_m == 1.8
    assert fairing.total_length_m > 1.8
    assert fairing.surface_area_m2 > 0.0
    assert fairing.internal_volume_m3 > 0.0


def test_assemble_vehicle_geometry() -> None:
    combo = PROPELLANT_COMBINATIONS["KEROLOX"]
    s1 = size_stage_geometry(12000.0, combo, 1.4)
    s2 = size_stage_geometry(3000.0, combo, 1.4)
    fairing = size_fairing_geometry(500.0, 1.4, 1.8)

    vehicle = assemble_vehicle_geometry(
        stage1_geom=s1,
        stage2_geom=s2,
        fairing_geom=fairing,
        interstage_length_m=0.8,
    )

    expected_len = s1.total_length_m + s2.total_length_m + fairing.total_length_m + 0.8
    assert vehicle.total_length_m == pytest.approx(expected_len, rel=1e-6)
    assert vehicle.fineness_ratio == pytest.approx(expected_len / 1.4, rel=1e-6)
