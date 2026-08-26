import pytest

from launchvehiclelab.core import us_standard_atmosphere_1976


def test_atmosphere_sea_level() -> None:
    atm = us_standard_atmosphere_1976(0.0)
    assert atm.temperature_k == pytest.approx(288.15, abs=1e-2)
    assert atm.pressure_pa == pytest.approx(101325.0, abs=1.0)
    assert atm.density_kg_per_m3 == pytest.approx(1.2250, abs=1e-3)
    assert atm.speed_of_sound_m_per_s == pytest.approx(340.294, abs=1e-2)


def test_atmosphere_tropopause_11km() -> None:
    atm = us_standard_atmosphere_1976(11000.0)
    # Geopotential is ~10981 m
    assert 216.0 < atm.temperature_k < 217.0
    assert 22000.0 < atm.pressure_pa < 23000.0
    assert 0.35 < atm.density_kg_per_m3 < 0.40


def test_atmosphere_stratosphere_20km() -> None:
    atm = us_standard_atmosphere_1976(20000.0)
    assert atm.temperature_k == pytest.approx(216.65, abs=0.5)
    assert 5000.0 < atm.pressure_pa < 6000.0


def test_atmosphere_high_altitude_vacuum_transition() -> None:
    atm_80k = us_standard_atmosphere_1976(80_000.0)
    atm_120k = us_standard_atmosphere_1976(120_000.0)

    assert atm_80k.pressure_pa > atm_120k.pressure_pa
    assert atm_120k.pressure_pa < 0.1
    assert atm_120k.density_kg_per_m3 < 1e-6
    assert atm_120k.speed_of_sound_m_per_s > 0.0


def test_atmosphere_invalid_altitude() -> None:
    with pytest.raises(ValueError):
        us_standard_atmosphere_1976(-10.0)
    with pytest.raises(ValueError):
        us_standard_atmosphere_1976(float("nan"))
