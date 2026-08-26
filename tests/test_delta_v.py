import json
from math import pi, sqrt

import pytest

from launchvehiclelab.cli import main
from launchvehiclelab.core import (
    EARTH_EQUATORIAL_RADIUS_M,
    EARTH_MU_M3_PER_S2,
    EARTH_ROTATION_RATE_RAD_PER_S,
    OrbitTarget,
    calculate_delta_v_budget,
    circular_orbit_velocity,
    earth_rotation_boost,
)


def test_circular_orbit_velocity_500km_leo() -> None:
    alt = 500_000.0
    r = EARTH_EQUATORIAL_RADIUS_M + alt
    expected = sqrt(EARTH_MU_M3_PER_S2 / r)

    result = circular_orbit_velocity(alt)
    assert result == pytest.approx(expected, rel=1e-12)
    assert result == pytest.approx(7612.607, abs=1e-2)


def test_circular_orbit_velocity_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        circular_orbit_velocity(-100.0)
    with pytest.raises(ValueError):
        circular_orbit_velocity(float("nan"))
    with pytest.raises(ValueError):
        circular_orbit_velocity(float("inf"))


def test_earth_rotation_boost_equator_east() -> None:
    expected = EARTH_ROTATION_RATE_RAD_PER_S * EARTH_EQUATORIAL_RADIUS_M
    result = earth_rotation_boost(launch_latitude_rad=0.0, launch_azimuth_rad=pi / 2.0)
    assert result == pytest.approx(expected, rel=1e-12)
    assert result == pytest.approx(465.101, abs=1e-2)


def test_earth_rotation_boost_pole_and_north() -> None:
    # At pole, latitude = pi/2 -> cos(latitude) = 0 -> boost = 0
    assert earth_rotation_boost(launch_latitude_rad=pi / 2.0) == pytest.approx(0.0, abs=1e-10)

    # Launching due North -> azimuth = 0 -> sin(azimuth) = 0 -> boost = 0
    assert earth_rotation_boost(launch_latitude_rad=0.0, launch_azimuth_rad=0.0) == pytest.approx(
        0.0, abs=1e-10
    )


def test_calculate_delta_v_budget_accounting() -> None:
    target = OrbitTarget(altitude_m=500_000.0)
    budget = calculate_delta_v_budget(
        target=target,
        launch_latitude_rad=0.0,
        launch_azimuth_rad=pi / 2.0,
        gravity_loss_m_per_s=1200.0,
        drag_loss_m_per_s=150.0,
        steering_loss_m_per_s=200.0,
        margin_fraction=0.03,
    )

    v_circ = circular_orbit_velocity(500_000.0)
    v_boost = earth_rotation_boost(0.0, pi / 2.0)
    net_ideal = v_circ - v_boost
    losses = 1200.0 + 150.0 + 200.0
    subtotal = net_ideal + losses
    margin = subtotal * 0.03
    total = subtotal + margin

    assert budget.orbital_velocity_m_per_s == pytest.approx(v_circ, rel=1e-12)
    assert budget.earth_rotation_boost_m_per_s == pytest.approx(v_boost, rel=1e-12)
    assert budget.net_ideal_burn_m_per_s == pytest.approx(net_ideal, rel=1e-12)
    assert budget.margin_m_per_s == pytest.approx(margin, rel=1e-12)
    assert budget.total_delta_v_m_per_s == pytest.approx(total, rel=1e-12)


def test_cli_delta_v_budget(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(
        [
            "delta-v-budget",
            "--altitude-m",
            "500000",
            "--latitude-deg",
            "28.5",
            "--azimuth-deg",
            "90",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["schema_version"] == "0.1"
    assert output["model"] == "delta_v_budget_v0.1"
    assert output["inputs"]["target_altitude_m"] == 500_000.0
    assert output["outputs"]["orbital_velocity_m_per_s"] == pytest.approx(7612.607, abs=1e-2)
    assert output["outputs"]["total_delta_v_m_per_s"] > 8500.0
