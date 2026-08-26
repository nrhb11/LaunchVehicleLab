"""Low-order aerodynamic loads, dynamic pressure, and drag coefficient modeling."""

from math import isfinite, pi, sin

from launchvehiclelab.core.domain import AerodynamicState, AtmosphereState


def _require_positive(name: str, value: float) -> None:
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite value")


def drag_coefficient_curve(
    mach: float,
    cd_subsonic: float = 0.22,
    cd_transonic_peak: float = 0.48,
    cd_hypersonic: float = 0.20,
) -> float:
    """Calculate aerodynamic drag coefficient CD as a function of Mach number.

    Implements:
    - Subsonic plateau (skin friction + base drag)
    - Transonic wave drag rise peaking near Mach 1.05 - 1.2
    - Supersonic wave drag decay toward Newtonian hypersonic limit
    """
    if not isfinite(mach) or mach < 0.0:
        raise ValueError("Mach number must be a non-negative finite value")

    if mach < 0.8:
        return cd_subsonic
    elif mach <= 1.2:
        # Transonic sinusoidal interpolation to peak
        progress = (mach - 0.8) / 0.4
        return cd_subsonic + (cd_transonic_peak - cd_subsonic) * (sin(progress * pi / 2.0) ** 2)
    else:
        # Supersonic decay
        decay = 1.0 + 0.75 * (mach - 1.2)
        return cd_hypersonic + (cd_transonic_peak - cd_hypersonic) / decay


def calculate_aerodynamics(
    velocity_m_per_s: float,
    atmosphere: AtmosphereState,
    reference_area_m2: float,
    cd_subsonic: float = 0.22,
    cd_transonic_peak: float = 0.48,
) -> AerodynamicState:
    """Compute instantaneous Mach number, dynamic pressure, CD, and drag force."""
    if not isfinite(velocity_m_per_s) or velocity_m_per_s < 0.0:
        raise ValueError("velocity_m_per_s must be non-negative and finite")
    _require_positive("reference_area_m2", reference_area_m2)

    speed_of_sound = max(1.0, atmosphere.speed_of_sound_m_per_s)
    mach = velocity_m_per_s / speed_of_sound
    dynamic_pressure = 0.5 * atmosphere.density_kg_per_m3 * (velocity_m_per_s**2)

    cd = drag_coefficient_curve(
        mach=mach,
        cd_subsonic=cd_subsonic,
        cd_transonic_peak=cd_transonic_peak,
    )
    drag_force = dynamic_pressure * reference_area_m2 * cd

    return AerodynamicState(
        mach=mach,
        dynamic_pressure_pa=dynamic_pressure,
        drag_coefficient=cd,
        drag_force_n=drag_force,
    )
