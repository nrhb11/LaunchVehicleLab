"""Orbital velocity and launch velocity budget calculations."""

from math import cos, isfinite, pi, sin, sqrt

from launchvehiclelab.core.domain import DeltaVBudget, OrbitTarget

EARTH_MU_M3_PER_S2 = 3.986004418e14
EARTH_EQUATORIAL_RADIUS_M = 6378137.0
EARTH_ROTATION_RATE_RAD_PER_S = 7.292115e-5


def _require_non_negative_finite(name: str, value: float) -> None:
    if not isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be a non-negative finite value")


def _require_finite(name: str, value: float) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} must be a finite value")


def circular_orbit_velocity(
    altitude_m: float,
    body_mu_m3_per_s2: float = EARTH_MU_M3_PER_S2,
    body_radius_m: float = EARTH_EQUATORIAL_RADIUS_M,
) -> float:
    """Calculate the circular orbit velocity at a given altitude above a body.

    Formula:
        v_circ = sqrt(mu / (R + h))
    """
    _require_non_negative_finite("altitude_m", altitude_m)
    _require_non_negative_finite("body_mu_m3_per_s2", body_mu_m3_per_s2)
    _require_non_negative_finite("body_radius_m", body_radius_m)

    orbital_radius_m = body_radius_m + altitude_m
    if orbital_radius_m <= 0.0:
        raise ValueError("Orbital radius (body_radius + altitude) must be positive")

    return sqrt(body_mu_m3_per_s2 / orbital_radius_m)


def earth_rotation_boost(
    launch_latitude_rad: float,
    launch_azimuth_rad: float = pi / 2.0,
    body_radius_m: float = EARTH_EQUATORIAL_RADIUS_M,
    rotation_rate_rad_per_s: float = EARTH_ROTATION_RATE_RAD_PER_S,
) -> float:
    """Calculate the tangential surface velocity component imparted by planetary rotation.

    Formula:
        v_boost = omega * R * cos(latitude) * sin(azimuth)
    """
    _require_finite("launch_latitude_rad", launch_latitude_rad)
    _require_finite("launch_azimuth_rad", launch_azimuth_rad)
    _require_non_negative_finite("body_radius_m", body_radius_m)
    _require_non_negative_finite("rotation_rate_rad_per_s", rotation_rate_rad_per_s)

    return (
        rotation_rate_rad_per_s
        * body_radius_m
        * cos(launch_latitude_rad)
        * sin(launch_azimuth_rad)
    )


def calculate_delta_v_budget(
    target: OrbitTarget,
    launch_latitude_rad: float = 0.0,
    launch_azimuth_rad: float = pi / 2.0,
    gravity_loss_m_per_s: float = 1200.0,
    drag_loss_m_per_s: float = 150.0,
    steering_loss_m_per_s: float = 200.0,
    margin_fraction: float = 0.03,
) -> DeltaVBudget:
    """Compute complete velocity budget for orbital injection.

    Total Delta-V is:
        v_orbit - v_earth_boost + losses + margin
    """
    _require_non_negative_finite("gravity_loss_m_per_s", gravity_loss_m_per_s)
    _require_non_negative_finite("drag_loss_m_per_s", drag_loss_m_per_s)
    _require_non_negative_finite("steering_loss_m_per_s", steering_loss_m_per_s)
    _require_non_negative_finite("margin_fraction", margin_fraction)

    orbital_velocity = circular_orbit_velocity(target.altitude_m)
    boost = earth_rotation_boost(
        launch_latitude_rad=launch_latitude_rad,
        launch_azimuth_rad=launch_azimuth_rad,
    )
    net_ideal_burn = orbital_velocity - boost
    losses = gravity_loss_m_per_s + drag_loss_m_per_s + steering_loss_m_per_s
    subtotal = net_ideal_burn + losses
    margin = subtotal * margin_fraction
    total = subtotal + margin

    return DeltaVBudget(
        orbital_velocity_m_per_s=orbital_velocity,
        earth_rotation_boost_m_per_s=boost,
        net_ideal_burn_m_per_s=net_ideal_burn,
        gravity_loss_m_per_s=gravity_loss_m_per_s,
        drag_loss_m_per_s=drag_loss_m_per_s,
        steering_loss_m_per_s=steering_loss_m_per_s,
        margin_m_per_s=margin,
        total_delta_v_m_per_s=total,
    )
