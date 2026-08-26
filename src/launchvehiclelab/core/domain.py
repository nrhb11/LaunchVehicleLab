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
    launch_latitude_rad: float = 0.0
    launch_azimuth_rad: float = 1.5707963267948966  # Due East (pi / 2)


@dataclass(frozen=True, slots=True)
class DeltaVBudget:
    """Breakdown of velocity increments and losses for orbital insertion."""

    orbital_velocity_m_per_s: float
    earth_rotation_boost_m_per_s: float
    net_ideal_burn_m_per_s: float
    gravity_loss_m_per_s: float
    drag_loss_m_per_s: float
    steering_loss_m_per_s: float
    margin_m_per_s: float
    total_delta_v_m_per_s: float


@dataclass(frozen=True, slots=True)
class StageSpec:
    """Preliminary technological specifications for a rocket stage."""

    name: str
    specific_impulse_s: float
    structural_fraction: float  # epsilon = m_struct / (m_struct + m_prop)


@dataclass(frozen=True, slots=True)
class StageSizingResult:
    """Mass and performance breakdown of an individual sized stage."""

    name: str
    delta_v_m_per_s: float
    propellant_mass_kg: float
    structural_mass_kg: float
    burnout_mass_kg: float
    initial_mass_kg: float
    mass_ratio: float


@dataclass(frozen=True, slots=True)
class TwoStageVehicleResult:
    """Complete performance and mass breakdown of a two-stage launcher."""

    payload_mass_kg: float
    stage1: StageSizingResult
    stage2: StageSizingResult
    gross_liftoff_weight_kg: float
    total_delta_v_m_per_s: float
