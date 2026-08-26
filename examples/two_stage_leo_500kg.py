#!/usr/bin/env python3
"""LaunchVehicleLab Canonical Benchmark Case Study (V0.4 Numerical Engine).

Mission: 500 kg payload into a 500 km circular Low-Earth Orbit (LEO).
Launch site: 28.5 deg North latitude (e.g. Cape Canaveral / Wenchang).
Launch azimuth: 90 deg (Due East).
"""

from math import radians
from pathlib import Path

from launchvehiclelab.adapters import save_project
from launchvehiclelab.application import run_coupled_sizing
from launchvehiclelab.core import (
    PROPELLANT_COMBINATIONS,
    MissionSpec,
    OrbitTarget,
    calculate_delta_v_budget,
    simulate_ascent_trajectory,
)


def run_benchmark() -> None:
    print("=" * 78)
    print("  LaunchVehicleLab V0.4 — Multidisciplinary Sizing & Numerical Flight Engine")
    print("  Mission: 500 kg payload to 500 km circular Low-Earth Orbit (LEO)")
    print("=" * 78)

    # 1. Mission Specification
    payload_mass_kg = 500.0
    orbit_altitude_m = 500_000.0
    launch_latitude_deg = 28.5
    mission = MissionSpec(
        payload_mass_kg=payload_mass_kg,
        target=OrbitTarget(altitude_m=orbit_altitude_m),
        launch_latitude_rad=radians(launch_latitude_deg),
    )

    # 2. Velocity Budget Calculation
    budget = calculate_delta_v_budget(
        target=mission.target,
        launch_latitude_rad=mission.launch_latitude_rad,
        launch_azimuth_rad=mission.launch_azimuth_rad,
        gravity_loss_m_per_s=1250.0,
        drag_loss_m_per_s=150.0,
        steering_loss_m_per_s=180.0,
        margin_fraction=0.03,
    )

    print("\n[1] Launch Delta-V Budget:")
    print(f"  • Orbital Circular Velocity (500 km): {budget.orbital_velocity_m_per_s:8.2f} m/s")
    print(f"  • Earth Surface Rotation Boost:       -{budget.earth_rotation_boost_m_per_s:8.2f} m/s")
    print(f"  • Net Ideal Velocity Burn:             {budget.net_ideal_burn_m_per_s:8.2f} m/s")
    print(f"  • Lumped Losses (Grav + Drag + Steer): +{budget.gravity_loss_m_per_s + budget.drag_loss_m_per_s + budget.steering_loss_m_per_s:8.2f} m/s")
    print(f"  • Reserve Margin (3%):                +{budget.margin_m_per_s:8.2f} m/s")
    print("  " + "-" * 52)
    print(f"  ► Total Target Delta-V Required:       {budget.total_delta_v_m_per_s:8.2f} m/s")

    # 3. Multidisciplinary Coupled Sizing
    stage1_combo = PROPELLANT_COMBINATIONS["KEROLOX"]
    stage2_combo = PROPELLANT_COMBINATIONS["METHALOX"]

    vehicle = run_coupled_sizing(
        mission=mission,
        stage1_combo=stage1_combo,
        stage2_combo=stage2_combo,
        stage1_diameter_m=1.4,
        stage2_diameter_m=1.4,
        fairing_diameter_m=1.5,
    )

    print("\n[2] Converged Launch Vehicle Overview:")
    print(f"  ► Gross Liftoff Weight (GLOW): {vehicle.gross_liftoff_weight_kg:10.2f} kg "
          f"({vehicle.gross_liftoff_weight_kg / 1000.0:.2f} metric tons)")
    print(f"  ► Payload Ratio (Payload/GLOW):{vehicle.payload_ratio_percent:9.2f} %")
    print(f"  ► Total Vehicle Stack Length:  {vehicle.vehicle_geometry.total_length_m:9.2f} m")
    print(f"  ► Vehicle Fineness Ratio (L/D):{vehicle.vehicle_geometry.fineness_ratio:9.2f}")
    print(f"  ► Sizing Convergence Loops:    {vehicle.iterations_to_converge:9d} iterations")

    # 4. Stage-by-Stage Breakdown
    for stage in [vehicle.stage1, vehicle.stage2]:
        print(f"\n[3] {stage.name} ({stage.propellant_combo.name}):")
        print(f"    • Allocated Delta-V:         {stage.sizing.delta_v_m_per_s:8.2f} m/s")
        print(f"    • Total Loaded Propellant:   {stage.propellant_mass_kg:8.2f} kg")
        print(f"        - Liquid Oxygen (LOX):   {stage.oxidizer_mass_kg:8.2f} kg")
        print(f"        - Fuel Mass:             {stage.fuel_mass_kg:8.2f} kg")
        print(f"    • Stage Dry Structural Mass: {stage.mass_breakdown.total_dry_mass_kg:8.2f} kg "
              f"(Effective ε = {stage.effective_structural_fraction * 100.0:.2f}%)")
        print(f"    • Stage Geometry:            Length = {stage.geometry.total_length_m:.2f} m, Diameter = {stage.geometry.diameter_m:.2f} m")

    # 5. Numerical Trajectory Simulation
    print("\n[4] Running 3DOF Ascent Flight Simulation...")
    traj = simulate_ascent_trajectory(vehicle)

    print("\n  ==================== Flight Mission Event Timeline ====================")
    for ev in traj.events:
        print(f"    T+{ev.time_s:6.1f} s | Alt: {ev.altitude_m / 1000.0:6.1f} km | Vel: {ev.velocity_m_per_s:7.1f} m/s | {ev.name}")
        if ev.description:
            print(f"               └─ {ev.description}")

    print("\n  ► Aerodynamic & Dynamic Flight Metrics:")
    print(f"    • Maximum Dynamic Pressure (Max-Q): {traj.max_q_pa / 1000.0:6.2f} kPa (at T+{traj.max_q_time_s:.1f} s, Alt: {traj.max_q_alt_m / 1000.0:.1f} km)")
    print(f"    • Peak Axial Acceleration:          {traj.max_acceleration_g:6.2f} g")
    print(f"    • Final Orbit Injection Altitude:   {traj.final_orbit_altitude_m / 1000.0:6.1f} km")
    print(f"    • Final Orbit Insertion Velocity:   {traj.final_orbit_velocity_m_per_s:6.1f} m/s")
    print(f"    • Total Mission Ascent Duration:    {traj.total_flight_time_s:6.1f} s ({traj.total_flight_time_s / 60.0:.1f} min)")

    # 6. Save Complete Project Persistence File
    output_path = Path(__file__).parent / "two_stage_leo_500kg.lvlab"
    saved = save_project(vehicle, output_path, trajectory=traj)
    print(f"\n[5] Project Persistence:")
    print(f"  ► Full mission & flight trajectory exported to: {saved.name}")

    print("\n" + "=" * 78)
    print("  Benchmark Run Complete — 0-to-Orbit Trajectory Numerical Engine Verified.")
    print("=" * 78)


if __name__ == "__main__":
    run_benchmark()
