"""Versioned project file persistence (.lvlab) serializer and deserializer."""

import json
from pathlib import Path

from launchvehiclelab import __version__
from launchvehiclelab.core.domain import CoupledVehicleResult, TrajectoryResult

PERSISTENCE_SCHEMA_VERSION = "0.4"
SUPPORTED_SCHEMA_VERSIONS = {"0.2", "0.4"}


def _serialize_vehicle(
    result: CoupledVehicleResult,
    trajectory: TrajectoryResult | None = None,
) -> dict[str, object]:
    """Convert a CoupledVehicleResult object and optional trajectory into a serializable dictionary."""
    data: dict[str, object] = {
        "schema_version": PERSISTENCE_SCHEMA_VERSION,
        "generator": f"LaunchVehicleLab {__version__}",
        "mission": {
            "payload_mass_kg": result.mission.payload_mass_kg,
            "target_altitude_m": result.mission.target.altitude_m,
            "launch_latitude_rad": result.mission.launch_latitude_rad,
            "launch_azimuth_rad": result.mission.launch_azimuth_rad,
        },
        "delta_v_budget": {
            "orbital_velocity_m_per_s": result.delta_v_budget.orbital_velocity_m_per_s,
            "earth_rotation_boost_m_per_s": result.delta_v_budget.earth_rotation_boost_m_per_s,
            "net_ideal_burn_m_per_s": result.delta_v_budget.net_ideal_burn_m_per_s,
            "gravity_loss_m_per_s": result.delta_v_budget.gravity_loss_m_per_s,
            "drag_loss_m_per_s": result.delta_v_budget.drag_loss_m_per_s,
            "steering_loss_m_per_s": result.delta_v_budget.steering_loss_m_per_s,
            "margin_m_per_s": result.delta_v_budget.margin_m_per_s,
            "total_delta_v_m_per_s": result.delta_v_budget.total_delta_v_m_per_s,
        },
        "vehicle_summary": {
            "gross_liftoff_weight_kg": result.gross_liftoff_weight_kg,
            "payload_ratio_percent": result.payload_ratio_percent,
            "total_length_m": result.vehicle_geometry.total_length_m,
            "fineness_ratio": result.vehicle_geometry.fineness_ratio,
            "iterations_to_converge": result.iterations_to_converge,
        },
        "vehicle_geometry": {
            "fairing": {
                "diameter_m": result.vehicle_geometry.fairing.diameter_m,
                "total_length_m": result.vehicle_geometry.fairing.total_length_m,
                "surface_area_m2": result.vehicle_geometry.fairing.surface_area_m2,
                "internal_volume_m3": result.vehicle_geometry.fairing.internal_volume_m3,
            },
            "interstage_length_m": result.vehicle_geometry.interstage_length_m,
        },
        "stages": [
            {
                "name": result.stage1.name,
                "propellant_combination": result.stage1.propellant_combo.name,
                "propellant_mass_kg": result.stage1.propellant_mass_kg,
                "oxidizer_mass_kg": result.stage1.oxidizer_mass_kg,
                "fuel_mass_kg": result.stage1.fuel_mass_kg,
                "effective_structural_fraction": result.stage1.effective_structural_fraction,
                "sizing": {
                    "delta_v_m_per_s": result.stage1.sizing.delta_v_m_per_s,
                    "initial_mass_kg": result.stage1.sizing.initial_mass_kg,
                    "burnout_mass_kg": result.stage1.sizing.burnout_mass_kg,
                    "mass_ratio": result.stage1.sizing.mass_ratio,
                },
                "geometry": {
                    "diameter_m": result.stage1.geometry.diameter_m,
                    "total_length_m": result.stage1.geometry.total_length_m,
                    "oxidizer_tank_length_m": result.stage1.geometry.oxidizer_tank.total_length_m,
                    "fuel_tank_length_m": result.stage1.geometry.fuel_tank.total_length_m,
                },
                "mass_breakdown": {
                    "tanks_mass_kg": result.stage1.mass_breakdown.tanks_mass_kg,
                    "propulsion_mass_kg": result.stage1.mass_breakdown.propulsion_mass_kg,
                    "avionics_mass_kg": result.stage1.mass_breakdown.avionics_mass_kg,
                    "interstage_mass_kg": result.stage1.mass_breakdown.interstage_mass_kg,
                    "residuals_and_margin_kg": result.stage1.mass_breakdown.residuals_and_margin_kg,
                    "total_dry_mass_kg": result.stage1.mass_breakdown.total_dry_mass_kg,
                },
            },
            {
                "name": result.stage2.name,
                "propellant_combination": result.stage2.propellant_combo.name,
                "propellant_mass_kg": result.stage2.propellant_mass_kg,
                "oxidizer_mass_kg": result.stage2.oxidizer_mass_kg,
                "fuel_mass_kg": result.stage2.fuel_mass_kg,
                "effective_structural_fraction": result.stage2.effective_structural_fraction,
                "sizing": {
                    "delta_v_m_per_s": result.stage2.sizing.delta_v_m_per_s,
                    "initial_mass_kg": result.stage2.sizing.initial_mass_kg,
                    "burnout_mass_kg": result.stage2.sizing.burnout_mass_kg,
                    "mass_ratio": result.stage2.sizing.mass_ratio,
                },
                "geometry": {
                    "diameter_m": result.stage2.geometry.diameter_m,
                    "total_length_m": result.stage2.geometry.total_length_m,
                    "oxidizer_tank_length_m": result.stage2.geometry.oxidizer_tank.total_length_m,
                    "fuel_tank_length_m": result.stage2.geometry.fuel_tank.total_length_m,
                },
                "mass_breakdown": {
                    "tanks_mass_kg": result.stage2.mass_breakdown.tanks_mass_kg,
                    "propulsion_mass_kg": result.stage2.mass_breakdown.propulsion_mass_kg,
                    "avionics_mass_kg": result.stage2.mass_breakdown.avionics_mass_kg,
                    "residuals_and_margin_kg": result.stage2.mass_breakdown.residuals_and_margin_kg,
                    "total_dry_mass_kg": result.stage2.mass_breakdown.total_dry_mass_kg,
                },
            },
        ],
    }

    if trajectory is not None:
        data["trajectory_simulation"] = {
            "max_q_pa": trajectory.max_q_pa,
            "max_q_time_s": trajectory.max_q_time_s,
            "max_q_alt_m": trajectory.max_q_alt_m,
            "max_acceleration_g": trajectory.max_acceleration_g,
            "total_flight_time_s": trajectory.total_flight_time_s,
            "final_orbit_altitude_m": trajectory.final_orbit_altitude_m,
            "final_orbit_velocity_m_per_s": trajectory.final_orbit_velocity_m_per_s,
            "flight_events": [
                {
                    "name": ev.name,
                    "time_s": ev.time_s,
                    "altitude_m": ev.altitude_m,
                    "velocity_m_per_s": ev.velocity_m_per_s,
                    "description": ev.description,
                }
                for ev in trajectory.events
            ],
        }

    return data


def save_project(
    result: CoupledVehicleResult,
    filepath: str | Path,
    trajectory: TrajectoryResult | None = None,
) -> Path:
    """Serialize a CoupledVehicleResult (and optional trajectory) to a schema-versioned .lvlab JSON file."""
    path = Path(filepath)
    if not path.name.endswith(".lvlab") and not path.name.endswith(".json"):
        path = path.with_suffix(".lvlab")

    data = _serialize_vehicle(result, trajectory=trajectory)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    return path


def load_project(filepath: str | Path) -> dict[str, object]:
    """Load and validate a .lvlab JSON project file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Project file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Invalid project file format: root must be a JSON object")

    version = data.get("schema_version")
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(
            f"Unsupported project schema version '{version}'. Supported: {sorted(SUPPORTED_SCHEMA_VERSIONS)}."
        )

    return data
