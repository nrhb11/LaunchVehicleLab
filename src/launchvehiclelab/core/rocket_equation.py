"""Ideal rocket-equation calculations."""

from math import isfinite, log

STANDARD_GRAVITY_M_PER_S2 = 9.80665


def _require_positive_finite(name: str, value: float) -> None:
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite value")


def ideal_delta_v(
    specific_impulse_s: float,
    initial_mass_kg: float,
    final_mass_kg: float,
) -> float:
    """Return ideal delta-v in metres per second.

    The calculation uses the Tsiolkovsky rocket equation with standard gravity:

        delta_v = g0 * Isp * ln(initial_mass / final_mass)

    Masses must use the same unit. Kilograms are required by the public API to
    make that convention explicit, even though only their ratio affects the
    result.
    """

    _require_positive_finite("specific_impulse_s", specific_impulse_s)
    _require_positive_finite("initial_mass_kg", initial_mass_kg)
    _require_positive_finite("final_mass_kg", final_mass_kg)

    if final_mass_kg > initial_mass_kg:
        raise ValueError("final_mass_kg must not exceed initial_mass_kg")

    return STANDARD_GRAVITY_M_PER_S2 * specific_impulse_s * log(
        initial_mass_kg / final_mass_kg
    )
