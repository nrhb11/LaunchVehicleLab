"""Command-line interface for LaunchVehicleLab analyses."""

import argparse
import json
from collections.abc import Sequence
from math import radians

from launchvehiclelab import __version__
from launchvehiclelab.core import (
    EARTH_EQUATORIAL_RADIUS_M,
    EARTH_MU_M3_PER_S2,
    EARTH_ROTATION_RATE_RAD_PER_S,
    STANDARD_GRAVITY_M_PER_S2,
    OrbitTarget,
    StageSpec,
    calculate_delta_v_budget,
    ideal_delta_v,
    optimize_two_stage,
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
        else:  # pragma: no cover - argparse enforces known commands.
            parser.error(f"unsupported command: {args.command}")
    except ValueError as error:
        parser.error(str(error))

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
