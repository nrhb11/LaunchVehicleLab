from math import pi

import pytest

from launchvehiclelab.core import (
    calculate_aerodynamics,
    drag_coefficient_curve,
    us_standard_atmosphere_1976,
)


def test_drag_coefficient_curve_regimes() -> None:
    cd_sub = drag_coefficient_curve(0.5)
    cd_sonic = drag_coefficient_curve(1.05)
    cd_super = drag_coefficient_curve(2.5)
    cd_hyper = drag_coefficient_curve(8.0)

    # Transonic peak must be strictly higher than subsonic & supersonic
    assert cd_sub == pytest.approx(0.22, abs=1e-3)
    assert cd_sonic > cd_sub
    assert cd_sonic > cd_super
    assert cd_super > cd_hyper
    assert cd_hyper == pytest.approx(0.20, abs=0.05)


def test_calculate_aerodynamics_sea_level() -> None:
    atm = us_standard_atmosphere_1976(0.0)
    ref_area = (pi * (1.4**2)) / 4.0
    vel = 100.0  # 100 m/s

    aero = calculate_aerodynamics(vel, atm, ref_area)

    expected_mach = 100.0 / atm.speed_of_sound_m_per_s
    expected_q = 0.5 * atm.density_kg_per_m3 * (vel**2)
    expected_drag = expected_q * ref_area * aero.drag_coefficient

    assert aero.mach == pytest.approx(expected_mach, rel=1e-6)
    assert aero.dynamic_pressure_pa == pytest.approx(expected_q, rel=1e-6)
    assert aero.drag_force_n == pytest.approx(expected_drag, rel=1e-6)


def test_calculate_aerodynamics_invalid_inputs() -> None:
    atm = us_standard_atmosphere_1976(1000.0)
    with pytest.raises(ValueError):
        calculate_aerodynamics(-50.0, atm, 1.5)
    with pytest.raises(ValueError):
        calculate_aerodynamics(100.0, atm, -1.0)
