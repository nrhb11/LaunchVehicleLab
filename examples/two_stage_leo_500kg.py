#!/usr/bin/env python3
"""LaunchVehicleLab Canonical Benchmark Case Study (V0.2 Milestone).

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
)


def run_benchmark() -> None:
    print("=" * 76)
    print("  LaunchVehicleLab V0.2 — Multidisciplinary Coupled Sizing Benchmark")
    print("  Mission: 500 kg payload to 500 km circular Low-Earth Orbit (LEO)")
    print("=" * 76)

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

    result = run_coupled_sizing(
        mission=mission,
        stage1_combo=stage1_combo,
        stage2_combo=stage2_combo,
        stage1_diameter_m=1.4,
        stage2_diameter_m=1.4,
        fairing_diameter_m=1.5,
    )

    print("\n[2] Converged Launch Vehicle Overview:")
    print(f"  ► Gross Liftoff Weight (GLOW): {result.gross_liftoff_weight_kg:10.2f} kg "
          f"({result.gross_liftoff_weight_kg / 1000.0:.2f} metric tons)")
    print(f"  ► Payload Ratio (Payload/GLOW):{result.payload_ratio_percent:9.2f} %")
    print(f"  ► Total Vehicle Stack Length:  {result.vehicle_geometry.total_length_m:9.2f} m")
    print(f"  ► Vehicle Fineness Ratio (L/D):{result.vehicle_geometry.fineness_ratio:9.2f}")
    print(f"  ► Sizing Convergence Loops:    {result.iterations_to_converge:9d} iterations")

    # 4. Stage-by-Stage Detailed Breakdown
    for stage in [result.stage1, result.stage2]:
        print(f"\n[3] {stage.name} ({stage.propellant_combo.name}):")
        print(f"    • Allocated Delta-V:         {stage.sizing.delta_v_m_per_s:8.2f} m/s")
        print(f"    • Total Loaded Propellant:   {stage.propellant_mass_kg:8.2f} kg")
        print(f"        - Liquid Oxygen (LOX):   {stage.oxidizer_mass_kg:8.2f} kg")
        print(f"        - Fuel Mass:             {stage.fuel_mass_kg:8.2f} kg")
        print(f"    • Stage Dry Structural Mass: {stage.mass_breakdown.total_dry_mass_kg:8.2f} kg "
              f"(Effective ε = {stage.effective_structural_fraction * 100.0:.2f}%)")
        print(f"        - Tanks & Bulkheads:     {stage.mass_breakdown.tanks_mass_kg:8.2f} kg")
        print(f"        - Propulsion & Plumbing: {stage.mass_breakdown.propulsion_mass_kg:8.2f} kg")
        print(f"        - Avionics & Electrical: {stage.mass_breakdown.avionics_mass_kg:8.2f} kg")
        print(f"        - Unusable & Margin:     {stage.mass_breakdown.residuals_and_margin_kg:8.2f} kg")
        print(f"    • Stage Geometry:            Length = {stage.geometry.total_length_m:.2f} m, Diameter = {stage.geometry.diameter_m:.2f} m")
        print(f"        - Oxidizer Tank Length:  {stage.geometry.oxidizer_tank.total_length_m:.2f} m")
        print(f"        - Fuel Tank Length:      {stage.geometry.fuel_tank.total_length_m:.2f} m")

    # 5. Fairing Geometry
    fairing = result.vehicle_geometry.fairing
    print("\n[4] Payload Fairing:")
    print(f"    • Outer Diameter:            {fairing.diameter_m:8.2f} m")
    print(f"    • Total Length:              {fairing.total_length_m:8.2f} m")
    print(f"    • Internal Payload Volume:   {fairing.internal_volume_m3:8.2f} m^3")

    # 6. Save Project Persistence File
    output_path = Path(__file__).parent / "two_stage_leo_500kg.lvlab"
    saved = save_project(result, output_path)
    print(f"\n[5] Project Persistence:")
    print(f"  ► Project successfully exported to: {saved.name}")

    print("\n" + "=" * 76)
    print("  Benchmark Run Complete — Multidisciplinary Sizing Verified & Saved.")
    print("=" * 76)


if __name__ == "__main__":
    run_benchmark()
