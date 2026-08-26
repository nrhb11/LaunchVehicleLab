"""Command-line interface for LaunchVehicleLab analyses."""

import argparse
import json
from collections.abc import Sequence
from math import pi, radians

from launchvehiclelab import __version__
from launchvehiclelab.adapters import load_project, save_project
from launchvehiclelab.application import run_coupled_sizing
from launchvehiclelab.core import (
    EARTH_EQUATORIAL_RADIUS_M,
    EARTH_MU_M3_PER_S2,
    EARTH_ROTATION_RATE_RAD_PER_S,
    PROPELLANT_COMBINATIONS,
    STANDARD_GRAVITY_M_PER_S2,
    MissionSpec,
    OrbitTarget,
    StageSpec,
    calculate_aerodynamics,
    calculate_delta_v_budget,
    ideal_delta_v,
    optimize_two_stage,
    simulate_ascent_trajectory,
    us_standard_atmosphere_1976,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lvlab",
        description="Run transparent launch-vehicle preliminary analyses.",
    )
    parser.add_argument("--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: rocket-equation
    rocket_equation = subparsers.add_parser(
        "rocket-equation",
        help="Calculate ideal delta-v using the Tsiolkovsky rocket equation.",
    )
    rocket_equation.add_argument("--specific-impulse-s", type=float, required=True)
    rocket_equation.add_argument("--initial-mass-kg", type=float, required=True)
    rocket_equation.add_argument("--final-mass-kg", type=float, required=True)

    # Subcommand: delta-v-budget
    delta_v_parser = subparsers.add_parser(
        "delta-v-budget",
        help="Calculate circular orbit velocity and complete launch delta-v budget.",
    )
    delta_v_parser.add_argument("--altitude-m", type=float, required=True, help="Target circular orbit altitude in metres")
    delta_v_parser.add_argument("--latitude-deg", type=float, default=0.0, help="Launch site latitude in degrees")
    delta_v_parser.add_argument("--azimuth-deg", type=float, default=90.0, help="Launch azimuth in degrees (90 = East)")
    delta_v_parser.add_argument("--gravity-loss-m-per-s", type=float, default=1200.0, help="Estimated gravity losses (m/s)")
    delta_v_parser.add_argument("--drag-loss-m-per-s", type=float, default=150.0, help="Estimated aerodynamic drag losses (m/s)")
    delta_v_parser.add_argument("--steering-loss-m-per-s", type=float, default=200.0, help="Estimated steering losses (m/s)")
    delta_v_parser.add_argument("--margin-fraction", type=float, default=0.03, help="Reserve delta-v margin fraction (default 3%%)")

    # Subcommand: two-stage-sizing
    staging_parser = subparsers.add_parser(
        "two-stage-sizing",
        help="Analytically optimize mass and delta-v distribution for a two-stage launch vehicle.",
    )
    staging_parser.add_argument("--payload-kg", type=float, required=True, help="Payload mass in kilograms")
    staging_parser.add_argument("--target-delta-v", type=float, required=True, help="Total target delta-v in m/s")
    staging_parser.add_argument("--stage1-isp", type=float, required=True, help="Stage 1 specific impulse in seconds")
    staging_parser.add_argument("--stage2-isp", type=float, required=True, help="Stage 2 specific impulse in seconds")
    staging_parser.add_argument("--stage1-eps", type=float, default=0.08, help="Stage 1 structural fraction (default 0.08)")
    staging_parser.add_argument("--stage2-eps", type=float, default=0.10, help="Stage 2 structural fraction (default 0.10)")

    # Subcommand: coupled-sizing (V0.2)
    coupled_parser = subparsers.add_parser(
        "coupled-sizing",
        help="Perform multidisciplinary mass-geometry coupled vehicle sizing and packaging.",
    )
    coupled_parser.add_argument("--payload-kg", type=float, required=True, help="Payload mass in kilograms")
    coupled_parser.add_argument("--altitude-m", type=float, required=True, help="Target circular orbit altitude in metres")
    coupled_parser.add_argument("--latitude-deg", type=float, default=28.5, help="Launch site latitude in degrees")
    coupled_parser.add_argument("--stage1-diameter-m", type=float, default=1.4, help="Stage 1 outer diameter (m)")
    coupled_parser.add_argument("--stage2-diameter-m", type=float, default=1.4, help="Stage 2 outer diameter (m)")
    coupled_parser.add_argument("--stage1-prop", choices=["KEROLOX", "METHALOX", "HYDROLOX"], default="KEROLOX", help="Stage 1 propellant")
    coupled_parser.add_argument("--stage2-prop", choices=["KEROLOX", "METHALOX", "HYDROLOX"], default="METHALOX", help="Stage 2 propellant")
    coupled_parser.add_argument("--export-file", type=str, default=None, help="Optional path to save .lvlab project file")

    # Subcommand: inspect-project (V0.2)
    inspect_parser = subparsers.add_parser(
        "inspect-project",
        help="Inspect and display contents of a saved .lvlab project file.",
    )
    inspect_parser.add_argument("--file", type=str, required=True, help="Path to .lvlab project file")

    # Subcommand: atmosphere (V0.3)
    atm_parser = subparsers.add_parser(
        "atmosphere",
        help="Query 1976 US Standard Atmosphere thermodynamic state at any altitude.",
    )
    atm_parser.add_argument("--altitude-m", type=float, required=True, help="Geometric altitude above sea level in metres")

    # Subcommand: aerodynamics (V0.3)
    aero_parser = subparsers.add_parser(
        "aerodynamics",
        help="Calculate Mach number, dynamic pressure, CD, and drag force.",
    )
    aero_parser.add_argument("--altitude-m", type=float, required=True, help="Geometric altitude in metres")
    aero_parser.add_argument("--velocity-m-per-s", type=float, required=True, help="Flight velocity in m/s")
    aero_parser.add_argument("--diameter-m", type=float, default=1.4, help="Vehicle reference diameter in metres")

    # Subcommand: simulate-trajectory (V0.4)
    traj_parser = subparsers.add_parser(
        "simulate-trajectory",
        help="Simulate complete 0-to-orbit numerical ascent flight trajectory and event history.",
    )
    traj_parser.add_argument("--payload-kg", type=float, default=500.0, help="Payload mass in kg")
    traj_parser.add_argument("--altitude-m", type=float, default=500_000.0, help="Target orbit altitude in metres")
    traj_parser.add_argument("--stage1-diameter-m", type=float, default=1.4, help="Stage 1 diameter in metres")
    traj_parser.add_argument("--stage2-diameter-m", type=float, default=1.4, help="Stage 2 diameter in metres")
    traj_parser.add_argument("--export-file", type=str, default=None, help="Optional export path for .lvlab project file")

    return parser


def _run_rocket_equation(args: argparse.Namespace) -> dict[str, object]:
    delta_v_m_per_s = ideal_delta_v(
        specific_impulse_s=args.specific_impulse_s,
        initial_mass_kg=args.initial_mass_kg,
        final_mass_kg=args.final_mass_kg,
    )
    return {
        "schema_version": "0.1",
        "model": "ideal_rocket_equation_v0.1",
        "inputs": {
            "specific_impulse_s": args.specific_impulse_s,
            "initial_mass_kg": args.initial_mass_kg,
            "final_mass_kg": args.final_mass_kg,
        },
        "constants": {
            "standard_gravity_m_per_s2": STANDARD_GRAVITY_M_PER_S2,
        },
        "outputs": {
            "ideal_delta_v_m_per_s": delta_v_m_per_s,
        },
        "assumptions": [
            "ideal impulsive velocity change",
            "constant specific impulse",
            "no gravity, aerodynamic, steering, or residual-propellant losses",
        ],
    }


def _run_delta_v_budget(args: argparse.Namespace) -> dict[str, object]:
    budget = calculate_delta_v_budget(
        target=OrbitTarget(altitude_m=args.altitude_m),
        launch_latitude_rad=radians(args.latitude_deg),
        launch_azimuth_rad=radians(args.azimuth_deg),
        gravity_loss_m_per_s=args.gravity_loss_m_per_s,
        drag_loss_m_per_s=args.drag_loss_m_per_s,
        steering_loss_m_per_s=args.steering_loss_m_per_s,
        margin_fraction=args.margin_fraction,
    )
    return {
        "schema_version": "0.1",
        "model": "delta_v_budget_v0.1",
        "inputs": {
            "target_altitude_m": args.altitude_m,
            "launch_latitude_deg": args.latitude_deg,
            "launch_azimuth_deg": args.azimuth_deg,
            "gravity_loss_m_per_s": args.gravity_loss_m_per_s,
            "drag_loss_m_per_s": args.drag_loss_m_per_s,
            "steering_loss_m_per_s": args.steering_loss_m_per_s,
            "margin_fraction": args.margin_fraction,
        },
        "constants": {
            "earth_mu_m3_per_s2": EARTH_MU_M3_PER_S2,
            "earth_equatorial_radius_m": EARTH_EQUATORIAL_RADIUS_M,
            "earth_rotation_rate_rad_per_s": EARTH_ROTATION_RATE_RAD_PER_S,
        },
        "outputs": {
            "orbital_velocity_m_per_s": budget.orbital_velocity_m_per_s,
            "earth_rotation_boost_m_per_s": budget.earth_rotation_boost_m_per_s,
            "net_ideal_burn_m_per_s": budget.net_ideal_burn_m_per_s,
            "gravity_loss_m_per_s": budget.gravity_loss_m_per_s,
            "drag_loss_m_per_s": budget.drag_loss_m_per_s,
            "steering_loss_m_per_s": budget.steering_loss_m_per_s,
            "margin_m_per_s": budget.margin_m_per_s,
            "total_delta_v_m_per_s": budget.total_delta_v_m_per_s,
        },
        "assumptions": [
            "spherical Earth gravity field (J2 and higher perturbations neglected)",
            "circular orbit target",
            "lumped empirical loss allocations for preliminary sizing",
        ],
    }


def _run_two_stage_sizing(args: argparse.Namespace) -> dict[str, object]:
    result = optimize_two_stage(
        payload_mass_kg=args.payload_kg,
        target_delta_v_m_per_s=args.target_delta_v,
        stage1_spec=StageSpec(
            name="Stage 1",
            specific_impulse_s=args.stage1_isp,
            structural_fraction=args.stage1_eps,
        ),
        stage2_spec=StageSpec(
            name="Stage 2",
            specific_impulse_s=args.stage2_isp,
            structural_fraction=args.stage2_eps,
        ),
    )
    return {
        "schema_version": "0.1",
        "model": "two_stage_optimal_sizing_v0.1",
        "inputs": {
            "payload_mass_kg": args.payload_kg,
            "target_delta_v_m_per_s": args.target_delta_v,
            "stage1_specific_impulse_s": args.stage1_isp,
            "stage2_specific_impulse_s": args.stage2_isp,
            "stage1_structural_fraction": args.stage1_eps,
            "stage2_structural_fraction": args.stage2_eps,
        },
        "constants": {
            "standard_gravity_m_per_s2": STANDARD_GRAVITY_M_PER_S2,
        },
        "outputs": {
            "gross_liftoff_weight_kg": result.gross_liftoff_weight_kg,
            "total_delta_v_m_per_s": result.total_delta_v_m_per_s,
            "stage1": {
                "name": result.stage1.name,
                "delta_v_m_per_s": result.stage1.delta_v_m_per_s,
                "propellant_mass_kg": result.stage1.propellant_mass_kg,
                "structural_mass_kg": result.stage1.structural_mass_kg,
                "burnout_mass_kg": result.stage1.burnout_mass_kg,
                "initial_mass_kg": result.stage1.initial_mass_kg,
                "mass_ratio": result.stage1.mass_ratio,
            },
            "stage2": {
                "name": result.stage2.name,
                "delta_v_m_per_s": result.stage2.delta_v_m_per_s,
                "propellant_mass_kg": result.stage2.propellant_mass_kg,
                "structural_mass_kg": result.stage2.structural_mass_kg,
                "burnout_mass_kg": result.stage2.burnout_mass_kg,
                "initial_mass_kg": result.stage2.initial_mass_kg,
                "mass_ratio": result.stage2.mass_ratio,
            },
        },
        "assumptions": [
            "two-stage serial configuration without strap-on boosters",
            "independent constant stage specific impulses",
            "linear structural fraction scaling model",
            "optimal delta-v partition minimizing GLOW",
        ],
    }


def _run_coupled_sizing(args: argparse.Namespace) -> dict[str, object]:
    mission = MissionSpec(
        payload_mass_kg=args.payload_kg,
        target=OrbitTarget(altitude_m=args.altitude_m),
        launch_latitude_rad=radians(args.latitude_deg),
    )
    s1_combo = PROPELLANT_COMBINATIONS[args.stage1_prop]
    s2_combo = PROPELLANT_COMBINATIONS[args.stage2_prop]

    result = run_coupled_sizing(
        mission=mission,
        stage1_combo=s1_combo,
        stage2_combo=s2_combo,
        stage1_diameter_m=args.stage1_diameter_m,
        stage2_diameter_m=args.stage2_diameter_m,
    )

    if args.export_file:
        save_project(result, args.export_file)

    return {
        "schema_version": "0.2",
        "model": "coupled_mass_geometry_sizing_v0.2",
        "inputs": {
            "payload_mass_kg": args.payload_kg,
            "target_altitude_m": args.altitude_m,
            "launch_latitude_deg": args.latitude_deg,
            "stage1_propellant": args.stage1_prop,
            "stage2_propellant": args.stage2_prop,
            "stage1_diameter_m": args.stage1_diameter_m,
            "stage2_diameter_m": args.stage2_diameter_m,
        },
        "outputs": {
            "gross_liftoff_weight_kg": result.gross_liftoff_weight_kg,
            "payload_ratio_percent": result.payload_ratio_percent,
            "total_length_m": result.vehicle_geometry.total_length_m,
            "fineness_ratio": result.vehicle_geometry.fineness_ratio,
            "iterations_to_converge": result.iterations_to_converge,
            "stage1": {
                "name": result.stage1.name,
                "propellant_mass_kg": result.stage1.propellant_mass_kg,
                "total_dry_mass_kg": result.stage1.mass_breakdown.total_dry_mass_kg,
                "length_m": result.stage1.geometry.total_length_m,
                "diameter_m": result.stage1.geometry.diameter_m,
                "effective_structural_fraction": result.stage1.effective_structural_fraction,
            },
            "stage2": {
                "name": result.stage2.name,
                "propellant_mass_kg": result.stage2.propellant_mass_kg,
                "total_dry_mass_kg": result.stage2.mass_breakdown.total_dry_mass_kg,
                "length_m": result.stage2.geometry.total_length_m,
                "diameter_m": result.stage2.geometry.diameter_m,
                "effective_structural_fraction": result.stage2.effective_structural_fraction,
            },
            "fairing": {
                "diameter_m": result.vehicle_geometry.fairing.diameter_m,
                "length_m": result.vehicle_geometry.fairing.total_length_m,
            },
        },
        "exported_file": str(args.export_file) if args.export_file else None,
        "assumptions": [
            "standard 2:1 ellipsoidal tank bulkheads",
            "coupled mass-geometry iterative convergence",
            "bottom-up subsystem dry mass accounting",
        ],
    }


def _run_inspect_project(args: argparse.Namespace) -> dict[str, object]:
    return load_project(args.file)


def _run_atmosphere(args: argparse.Namespace) -> dict[str, object]:
    atm = us_standard_atmosphere_1976(args.altitude_m)
    return {
        "schema_version": "0.3",
        "model": "us_standard_atmosphere_1976_v0.3",
        "inputs": {"altitude_m": args.altitude_m},
        "outputs": {
            "temperature_k": atm.temperature_k,
            "pressure_pa": atm.pressure_pa,
            "density_kg_per_m3": atm.density_kg_per_m3,
            "speed_of_sound_m_per_s": atm.speed_of_sound_m_per_s,
        },
    }


def _run_aerodynamics(args: argparse.Namespace) -> dict[str, object]:
    atm = us_standard_atmosphere_1976(args.altitude_m)
    ref_area = (pi * (args.diameter_m**2)) / 4.0
    aero = calculate_aerodynamics(args.velocity_m_per_s, atm, ref_area)
    return {
        "schema_version": "0.3",
        "model": "aerodynamic_loads_v0.3",
        "inputs": {
            "altitude_m": args.altitude_m,
            "velocity_m_per_s": args.velocity_m_per_s,
            "diameter_m": args.diameter_m,
            "reference_area_m2": ref_area,
        },
        "outputs": {
            "mach": aero.mach,
            "dynamic_pressure_pa": aero.dynamic_pressure_pa,
            "drag_coefficient": aero.drag_coefficient,
            "drag_force_n": aero.drag_force_n,
        },
    }


def _run_simulate_trajectory(args: argparse.Namespace) -> dict[str, object]:
    mission = MissionSpec(
        payload_mass_kg=args.payload_kg,
        target=OrbitTarget(altitude_m=args.altitude_m),
    )
    vehicle = run_coupled_sizing(
        mission=mission,
        stage1_diameter_m=args.stage1_diameter_m,
        stage2_diameter_m=args.stage2_diameter_m,
    )
    traj = simulate_ascent_trajectory(vehicle)

    if args.export_file:
        save_project(vehicle, args.export_file, trajectory=traj)

    return {
        "schema_version": "0.4",
        "model": "ascent_trajectory_simulation_v0.4",
        "inputs": {
            "payload_mass_kg": args.payload_kg,
            "target_altitude_m": args.altitude_m,
        },
        "outputs": {
            "max_q_pa": traj.max_q_pa,
            "max_q_altitude_m": traj.max_q_alt_m,
            "max_q_time_s": traj.max_q_time_s,
            "max_acceleration_g": traj.max_acceleration_g,
            "total_flight_time_s": traj.total_flight_time_s,
            "final_orbit_altitude_m": traj.final_orbit_altitude_m,
            "final_orbit_velocity_m_per_s": traj.final_orbit_velocity_m_per_s,
            "events": [
                {
                    "name": ev.name,
                    "time_s": ev.time_s,
                    "altitude_m": ev.altitude_m,
                    "velocity_m_per_s": ev.velocity_m_per_s,
                    "description": ev.description,
                }
                for ev in traj.events
            ],
        },
        "exported_file": str(args.export_file) if args.export_file else None,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "rocket-equation":
            result = _run_rocket_equation(args)
        elif args.command == "delta-v-budget":
            result = _run_delta_v_budget(args)
        elif args.command == "two-stage-sizing":
            result = _run_two_stage_sizing(args)
        elif args.command == "coupled-sizing":
            result = _run_coupled_sizing(args)
        elif args.command == "inspect-project":
            result = _run_inspect_project(args)
        elif args.command == "atmosphere":
            result = _run_atmosphere(args)
        elif args.command == "aerodynamics":
            result = _run_aerodynamics(args)
        elif args.command == "simulate-trajectory":
            result = _run_simulate_trajectory(args)
        else:  # pragma: no cover - argparse enforces known commands.
            parser.error(f"unsupported command: {args.command}")
    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
