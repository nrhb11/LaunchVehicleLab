"""Subsystem mass breakdown and engineering mass scaling models."""

from math import isfinite, pi

from launchvehiclelab.core.domain import (
    FairingGeometry,
    StageGeometry,
    SubsystemMassBreakdown,
)
from launchvehiclelab.core.rocket_equation import STANDARD_GRAVITY_M_PER_S2


def _require_positive(name: str, value: float) -> None:
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite value")


def estimate_fairing_mass(
    fairing_geom: FairingGeometry,
    areal_density_kg_per_m2: float = 10.5,
    mechanism_fraction: float = 0.20,
) -> float:
    """Estimate total payload fairing dry mass including separation mechanisms."""
    _require_positive("areal_density_kg_per_m2", areal_density_kg_per_m2)
    shell_mass = fairing_geom.surface_area_m2 * areal_density_kg_per_m2
    return shell_mass * (1.0 + mechanism_fraction)


def estimate_stage_subsystems(
    stage_geom: StageGeometry,
    propellant_mass_kg: float,
    stage_initial_mass_kg: float,
    thrust_to_weight: float = 1.3,
    engine_thrust_to_weight: float = 75.0,
    tank_areal_density_kg_per_m2: float = 15.0,
    avionics_mass_kg: float = 45.0,
    interstage_mass_kg: float = 0.0,
    fairing_mass_kg: float = 0.0,
    residual_fraction: float = 0.012,
) -> SubsystemMassBreakdown:
    """Compute bottom-up subsystem mass breakdown for a launch stage.

    Calculates:
    - Tank structure mass (wetted area * areal density)
    - Propulsion system (engines, gimbal, plumbing)
    - Avionics and telemetry
    - Interstage / fairing allocations
    - Residual / unusable propellants and design margins
    """
    _require_positive("propellant_mass_kg", propellant_mass_kg)
    _require_positive("stage_initial_mass_kg", stage_initial_mass_kg)
    _require_positive("thrust_to_weight", thrust_to_weight)
    _require_positive("engine_thrust_to_weight", engine_thrust_to_weight)
    _require_positive("tank_areal_density_kg_per_m2", tank_areal_density_kg_per_m2)

    # 1. Tank shells & domes
    ox_tank_area = stage_geom.oxidizer_tank.surface_area_m2
    fuel_tank_area = stage_geom.fuel_tank.surface_area_m2
    skirt_area = pi * stage_geom.diameter_m * (stage_geom.intertank_length_m + stage_geom.skirt_length_m)
    total_wetted_area = ox_tank_area + fuel_tank_area + skirt_area
    tanks_mass = total_wetted_area * tank_areal_density_kg_per_m2

    # 2. Propulsion System
    required_thrust_n = stage_initial_mass_kg * STANDARD_GRAVITY_M_PER_S2 * thrust_to_weight
    bare_engine_mass = required_thrust_n / (STANDARD_GRAVITY_M_PER_S2 * engine_thrust_to_weight)
    # Add 25% for thrust structure, gimbal actuators, feedlines, pressurization valves
    propulsion_mass = bare_engine_mass * 1.25

    # 3. Residuals & holdup
    residuals = propellant_mass_kg * residual_fraction

    total_dry = (
        tanks_mass
        + propulsion_mass
        + avionics_mass_kg
        + interstage_mass_kg
        + fairing_mass_kg
        + residuals
    )

    return SubsystemMassBreakdown(
        tanks_mass_kg=tanks_mass,
        propulsion_mass_kg=propulsion_mass,
        avionics_mass_kg=avionics_mass_kg,
        interstage_mass_kg=interstage_mass_kg,
        fairing_mass_kg=fairing_mass_kg,
        residuals_and_margin_kg=residuals,
        total_dry_mass_kg=total_dry,
    )
