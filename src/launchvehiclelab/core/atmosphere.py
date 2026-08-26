"""US Standard Atmosphere 1976 model."""

from math import exp, isfinite, sqrt

from launchvehiclelab.core.domain import AtmosphereState
from launchvehiclelab.core.rocket_equation import STANDARD_GRAVITY_M_PER_S2

# Physical & Thermodynamic Constants
AIR_GAS_CONSTANT_J_PER_KG_K = 287.05287
AIR_SPECIFIC_HEAT_RATIO = 1.4
EARTH_GEOPOTENTIAL_RADIUS_M = 6356766.0

# 1976 US Standard Atmosphere 7 Defined Layers
# Format: (Base Geopotential Alt Hb [m], Base Temp Tb [K], Base Pressure pb [Pa], Lapse Rate Lb [K/m])
_ATMOSPHERE_LAYERS: list[tuple[float, float, float, float]] = [
    (0.0, 288.15, 101325.0, -0.0065),
    (11000.0, 216.65, 22632.06, 0.0),
    (20000.0, 216.65, 5474.889, 0.0010),
    (32000.0, 228.65, 868.0187, 0.0028),
    (47000.0, 270.65, 110.9063, 0.0),
    (51000.0, 270.65, 66.93887, -0.0028),
    (71000.0, 214.65, 3.956420, -0.0020),
]


def us_standard_atmosphere_1976(altitude_m: float) -> AtmosphereState:
    """Compute atmospheric state according to the 1976 US Standard Atmosphere.

    Accepts geometric altitude in metres (h >= 0).
    Valid from sea level through mesosphere (86 km) with continuous vacuum transition.
    """
    if not isfinite(altitude_m) or altitude_m < 0.0:
        raise ValueError("altitude_m must be a non-negative finite value")

    # Geopotential altitude H
    h_geopotential = (EARTH_GEOPOTENTIAL_RADIUS_M * altitude_m) / (
        EARTH_GEOPOTENTIAL_RADIUS_M + altitude_m
    )

    g0 = STANDARD_GRAVITY_M_PER_S2
    r_air = AIR_GAS_CONSTANT_J_PER_KG_K
    gamma = AIR_SPECIFIC_HEAT_RATIO

    # Check beyond standard tables (upper mesosphere / space vacuum boundary)
    if h_geopotential >= 84852.0:
        # Upper mesopause / thermosphere transition into space vacuum
        t_base = 186.87
        p_base = 0.3734
        dh = h_geopotential - 84852.0
        # Smooth barometric scale height decay (~7.5 km scale height)
        scale_height = (r_air * t_base) / g0
        pressure = p_base * exp(-dh / scale_height)
        temperature = t_base
        density = pressure / (r_air * temperature)
        speed_of_sound = sqrt(gamma * r_air * temperature)
        return AtmosphereState(
            altitude_m=altitude_m,
            temperature_k=temperature,
            pressure_pa=pressure,
            density_kg_per_m3=density,
            speed_of_sound_m_per_s=speed_of_sound,
        )

    # Locate active atmospheric layer
    active_layer = _ATMOSPHERE_LAYERS[0]
    for layer in _ATMOSPHERE_LAYERS:
        if h_geopotential >= layer[0]:
            active_layer = layer
        else:
            break

    h_b, t_b, p_b, l_b = active_layer
    dh = h_geopotential - h_b

    if abs(l_b) < 1e-12:
        # Isothermal layer
        temperature = t_b
        pressure = p_b * exp(- (g0 * dh) / (r_air * t_b))
    else:
        # Gradient layer
        temperature = t_b + l_b * dh
        exponent = - g0 / (r_air * l_b)
        pressure = p_b * ((temperature / t_b) ** exponent)

    density = pressure / (r_air * temperature)
    speed_of_sound = sqrt(gamma * r_air * temperature)

    return AtmosphereState(
        altitude_m=altitude_m,
        temperature_k=temperature,
        pressure_pa=pressure,
        density_kg_per_m3=density,
        speed_of_sound_m_per_s=speed_of_sound,
    )
