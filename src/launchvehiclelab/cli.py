"""Command-line interface for LaunchVehicleLab analyses."""

import argparse
import json
from collections.abc import Sequence

from launchvehiclelab import __version__
from launchvehiclelab.core import STANDARD_GRAVITY_M_PER_S2, ideal_delta_v


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lvlab",
        description="Run transparent launch-vehicle preliminary analyses.",
    )
    parser.add_argument("--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(dest="command", required=True)
    rocket_equation = subparsers.add_parser(
        "rocket-equation",
        help="Calculate ideal delta-v using the Tsiolkovsky rocket equation.",
    )
    rocket_equation.add_argument("--specific-impulse-s", type=float, required=True)
    rocket_equation.add_argument("--initial-mass-kg", type=float, required=True)
    rocket_equation.add_argument("--final-mass-kg", type=float, required=True)
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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "rocket-equation":
            result = _run_rocket_equation(args)
        else:  # pragma: no cover - argparse enforces known commands.
            parser.error(f"unsupported command: {args.command}")
    except ValueError as error:
        parser.error(str(error))

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
