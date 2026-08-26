import pytest

from launchvehiclelab.application import run_coupled_sizing
from launchvehiclelab.core import (
    PROPELLANT_COMBINATIONS,
    MissionSpec,
    OrbitTarget,
    simulate_ascent_trajectory,
)


def test_simulate_ascent_trajectory_events_and_max_q() -> None:
    mission = MissionSpec(
        payload_mass_kg=500.0,
        target=OrbitTarget(altitude_m=500_000.0),
        launch_latitude_rad=0.4974,
    )

    vehicle = run_coupled_sizing(
        mission=mission,
        stage1_combo=PROPELLANT_COMBINATIONS["KEROLOX"],
        stage2_combo=PROPELLANT_COMBINATIONS["METHALOX"],
        stage1_diameter_m=1.4,
        stage2_diameter_m=1.4,
    )

    traj = simulate_ascent_trajectory(vehicle)

    # 1. Verification of Max-Q and Peak Loads
    assert 20_000.0 < traj.max_q_pa < 50_000.0  # Realistic 20 to 50 kPa Max-Q
    assert 9_000.0 < traj.max_q_alt_m < 16_000.0  # Max-Q occurs between 9-16 km
    assert 40.0 < traj.max_q_time_s < 80.0
    assert 2.0 < traj.max_acceleration_g < 6.5

    # 2. Verification of Final Orbit Insertion
    assert traj.final_orbit_altitude_m > 300_000.0
    assert traj.final_orbit_velocity_m_per_s > 7000.0
    assert traj.total_flight_time_s > 400.0

    # 3. Chronological Event Sequence Verification
    event_names = [ev.name for ev in traj.events]
    assert "Liftoff" in event_names[0]
    assert any("Transonic" in name for name in event_names)
    assert any("Max-Q" in name for name in event_names)
    assert any("MECO" in name for name in event_names)
    assert any("Stage 1 Separation" in name for name in event_names)
    assert any("Fairing Jettison" in name for name in event_names)
    assert "SECO & Target Orbit Insertion" in event_names[-1]

    # Verify time strictly monotonically non-decreasing across events
    event_times = [ev.time_s for ev in traj.events]
    for i in range(len(event_times) - 1):
        assert event_times[i] <= event_times[i + 1]
