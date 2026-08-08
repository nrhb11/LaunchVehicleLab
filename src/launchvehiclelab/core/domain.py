"""Transparent domain objects shared by LaunchVehicleLab analyses."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OrbitTarget:
    """A simplified circular-orbit target."""

    altitude_m: float
    inclination_rad: float | None = None


@dataclass(frozen=True, slots=True)
class MissionSpec:
    """Top-level mission inputs used by preliminary analyses."""

    payload_mass_kg: float
    target: OrbitTarget
