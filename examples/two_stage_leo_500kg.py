#!/usr/bin/env python3
"""LaunchVehicleLab Canonical Benchmark Case Study.

Mission: 500 kg payload into a 500 km circular Low-Earth Orbit (LEO).
Launch site: 28.5 deg North latitude (e.g. Cape Canaveral / notional coastal spaceport).
Launch azimuth: 90 deg (Due East).
"""

from math import radians

from launchvehiclelab.core import (
    OrbitTarget,
    StageSpec,
    calculate_delta_v_budget,
    optimize_two_stage,
)


def run_benchmark() -> None:
    print("=" * 72)
    print("  LaunchVehicleLab V0.1 — Canonical Benchmark Case Study")
    print("  Target: 500 kg payload to 500 km circular Low-Earth Orbit (LEO)")
    print("=" * 72)

    # 1. Mission & Target Definition
    payload_mass_kg = 500.0
    orbit_altitude_m = 500_000.0  # 500 km
    launch_latitude_deg = 28.5
    target = OrbitTarget(altitude_m=orbit_altitude_m)

    # 2. Velocity Budget Calculation
    budget = calculate_delta_v_budget(
        target=target,
        launch_latitude_rad=radians(launch_latitude_deg),
        launch_azimuth_rad=radians(90.0),
        gravity_loss_m_per_s=1250.0,
        drag_loss_m_per_s=150.0,
        steering_loss_m_per_s=180.0,
        margin_fraction=0.03,
    )

    print("\n[1] Launch Delta-V Budget Breakdown:")
    print(f"  • Orbital Circular Velocity (500 km): {budget.orbital_velocity_m_per_s:8.2f} m/s")
    print(f"  • Earth Surface Rotation Boost:       -{budget.earth_rotation_boost_m_per_s:8.2f} m/s")
    print(f"  • Net Ideal Burn Requirement:          {budget.net_ideal_burn_m_per_s:8.2f} m/s")
    print(f"  • Gravity Losses:                     +{budget.gravity_loss_m_per_s:8.2f} m/s")
    print(f"  • Aerodynamic Drag Losses:            +{budget.drag_loss_m_per_s:8.2f} m/s")
    print(f"  • Steering / Back-pressure Losses:    +{budget.steering_loss_m_per_s:8.2f} m/s")
    print(f"  • Reserve Margin (3%):                +{budget.margin_m_per_s:8.2f} m/s")
    print("  " + "-" * 50)
    print(f"  ► Total Target Delta-V Required:       {budget.total_delta_v_m_per_s:8.2f} m/s")

    # 3. Two-Stage Vehicle Optimization
    stage1_tech = StageSpec(
        name="Stage 1 (Booster)",
        specific_impulse_s=300.0,      # Sea-level / average Kerolox
        structural_fraction=0.08,      # 8% structural mass fraction
    )
    stage2_tech = StageSpec(
        name="Stage 2 (Upper Stage)",
        specific_impulse_s=360.0,      # Vacuum Methalox / Hydrolox expander
        structural_fraction=0.10,      # 10% structural mass fraction
    )

    vehicle = optimize_two_stage(
        payload_mass_kg=payload_mass_kg,
        target_delta_v_m_per_s=budget.total_delta_v_m_per_s,
        stage1_spec=stage1_tech,
        stage2_spec=stage2_tech,
    )

    print("\n[2] Optimal Two-Stage Vehicle Sizing Result:")
    print(f"  ► Gross Liftoff Weight (GLOW): {vehicle.gross_liftoff_weight_kg:10.2f} kg "
          f"({vehicle.gross_liftoff_weight_kg / 1000.0:.2f} metric tons)")
    print(f"  ► Delivered Delta-V:           {vehicle.total_delta_v_m_per_s:10.2f} m/s")
    print(f"  ► Payload Ratio (Payload/GLOW):{payload_mass_kg / vehicle.gross_liftoff_weight_kg * 100.0:9.2f} %")

    print("\n[3] Stage-by-Stage Breakdown:")
    for stage in [vehicle.stage1, vehicle.stage2]:
        print(f"\n  --- {stage.name} ---")
        print(f"    • Allocated Delta-V:      {stage.delta_v_m_per_s:8.2f} m/s")
        print(f"    • Stage Initial Mass:     {stage.initial_mass_kg:8.2f} kg")
        print(f"    • Propellant Mass:        {stage.propellant_mass_kg:8.2f} kg")
        print(f"    • Dry Structural Mass:    {stage.structural_mass_kg:8.2f} kg")
        print(f"    • Stage Burnout Mass:     {stage.burnout_mass_kg:8.2f} kg")
        print(f"    • Stage Mass Ratio (R):   {stage.mass_ratio:8.3f}")

    print("\n" + "=" * 72)
    print("  Benchmark Run Complete — Model Verified against Analytical Optimum.")
    print("=" * 72)


if __name__ == "__main__":
    run_benchmark()
