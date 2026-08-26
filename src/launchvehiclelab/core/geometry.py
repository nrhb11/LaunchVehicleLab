"""Launch vehicle tank, stage, and fairing geometric packaging."""

from math import atan, isfinite, log, pi, sqrt

from launchvehiclelab.core.domain import (
    FairingGeometry,
    PropellantCombination,
    PropellantSpec,
    StageGeometry,
    TankGeometry,
    VehicleGeometry,
)

# Standard Propellant Definitions (SI units: kg/m^3)
LOX = PropellantSpec(
    name="Liquid Oxygen",
    density_kg_per_m3=1141.0,
    description="Cryogenic oxidizer at 90 K",
)
RP1 = PropellantSpec(
    name="RP-1 Kerosene",
    density_kg_per_m3=810.0,
    description="Refined hydrocarbon kerosene fuel",
)
CH4 = PropellantSpec(
    name="Liquid Methane",
    density_kg_per_m3=422.6,
    description="Cryogenic liquefied natural gas at 111 K",
)
LH2 = PropellantSpec(
    name="Liquid Hydrogen",
    density_kg_per_m3=70.85,
    description="Deep cryogenic high-energy fuel at 20 K",
)

# Standard Bipropellant Combinations
PROPELLANT_COMBINATIONS: dict[str, PropellantCombination] = {
    "KEROLOX": PropellantCombination(
        name="Kerolox (LOX/RP-1)",
        oxidizer=LOX,
        fuel=RP1,
        default_mixture_ratio_of=2.56,
        default_sea_level_isp_s=300.0,
        default_vacuum_isp_s=325.0,
    ),
    "METHALOX": PropellantCombination(
        name="Methalox (LOX/LCH4)",
        oxidizer=LOX,
        fuel=CH4,
        default_mixture_ratio_of=3.50,
        default_sea_level_isp_s=330.0,
        default_vacuum_isp_s=365.0,
    ),
    "HYDROLOX": PropellantCombination(
        name="Hydrolox (LOX/LH2)",
        oxidizer=LOX,
        fuel=LH2,
        default_mixture_ratio_of=5.50,
        default_sea_level_isp_s=380.0,
        default_vacuum_isp_s=450.0,
    ),
}


def _require_positive(name: str, value: float) -> None:
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite value")


def _ellipsoid_2to1_dome_area(diameter_m: float) -> float:
    """Surface area of one 2:1 oblate ellipsoidal dome head (semi-axes R, R, R/2).

    Formula:
        A_dome = 0.5 * pi * a^2 * (1 + ((1 - e^2)/e) * atanh(e))
    where a = D/2, e = sqrt(1 - (b/a)^2) = sqrt(3)/2 ~ 0.8660254.
    """
    radius = diameter_m / 2.0
    # For b/a = 0.5, e = sqrt(1 - 0.25) = sqrt(3)/2
    e = sqrt(3.0) / 2.0
    # atanh(e) = 0.5 * ln((1+e)/(1-e))
    atanh_e = 0.5 * log((1.0 + e) / (1.0 - e))
    factor = 1.0 + ((1.0 - e**2) / e) * atanh_e
    return 0.5 * pi * (radius**2) * factor


def size_tank_geometry(
    propellant_mass_kg: float,
    density_kg_per_m3: float,
    diameter_m: float,
    ullage_fraction: float = 0.04,
) -> TankGeometry:
    """Size a cylindrical propellant tank with 2:1 ellipsoidal bulkheads.

    Total volume:
        V_req = (m_prop / rho) * (1 + ullage_fraction)
    """
    _require_positive("propellant_mass_kg", propellant_mass_kg)
    _require_positive("density_kg_per_m3", density_kg_per_m3)
    _require_positive("diameter_m", diameter_m)
    if ullage_fraction < 0.0 or ullage_fraction >= 0.5:
        raise ValueError("ullage_fraction must be between 0.0 and 0.5")

    radius = diameter_m / 2.0
    cross_section = pi * (radius**2)
    dome_height = diameter_m / 4.0  # 2:1 ellipse height

    required_volume = (propellant_mass_kg / density_kg_per_m3) * (1.0 + ullage_fraction)

    # Volume of 2 domes (top and bottom heads combined) = (pi * D^3) / 12
    two_domes_volume = (pi * (diameter_m**3)) / 12.0

    if required_volume <= two_domes_volume:
        # Pure ellipsoidal / squashed tank
        cylinder_length = 0.0
        actual_volume = two_domes_volume
    else:
        cylinder_volume = required_volume - two_domes_volume
        cylinder_length = cylinder_volume / cross_section
        actual_volume = required_volume

    total_length = cylinder_length + 2.0 * dome_height
    single_dome_area = _ellipsoid_2to1_dome_area(diameter_m)
    surface_area = 2.0 * single_dome_area + 2.0 * pi * radius * cylinder_length

    return TankGeometry(
        diameter_m=diameter_m,
        cylinder_length_m=cylinder_length,
        dome_height_m=dome_height,
        total_length_m=total_length,
        volume_m3=actual_volume,
        surface_area_m2=surface_area,
    )


def size_stage_geometry(
    propellant_mass_kg: float,
    propellant_combo: PropellantCombination,
    diameter_m: float,
    mixture_ratio_of: float | None = None,
    intertank_spacing_m: float = 0.3,
    skirt_length_m: float | None = None,
    ullage_fraction: float = 0.04,
) -> StageGeometry:
    """Package oxidizer and fuel tanks into an integrated stage geometry."""
    _require_positive("propellant_mass_kg", propellant_mass_kg)
    _require_positive("diameter_m", diameter_m)

    mr = mixture_ratio_of if mixture_ratio_of is not None else propellant_combo.default_mixture_ratio_of
    _require_positive("mixture_ratio_of", mr)

    m_ox = propellant_mass_kg * (mr / (1.0 + mr))
    m_fuel = propellant_mass_kg * (1.0 / (1.0 + mr))

    ox_tank = size_tank_geometry(
        propellant_mass_kg=m_ox,
        density_kg_per_m3=propellant_combo.oxidizer.density_kg_per_m3,
        diameter_m=diameter_m,
        ullage_fraction=ullage_fraction,
    )

    fuel_tank = size_tank_geometry(
        propellant_mass_kg=m_fuel,
        density_kg_per_m3=propellant_combo.fuel.density_kg_per_m3,
        diameter_m=diameter_m,
        ullage_fraction=ullage_fraction,
    )

    skirt_len = skirt_length_m if skirt_length_m is not None else 0.8 * diameter_m
    total_length = ox_tank.total_length_m + fuel_tank.total_length_m + intertank_spacing_m + skirt_len

    return StageGeometry(
        diameter_m=diameter_m,
        total_length_m=total_length,
        oxidizer_tank=ox_tank,
        fuel_tank=fuel_tank,
        intertank_length_m=intertank_spacing_m,
        skirt_length_m=skirt_len,
    )


def size_fairing_geometry(
    payload_mass_kg: float,
    diameter_m: float,
    cylinder_length_m: float = 1.8,
    nose_cone_length_m: float | None = None,
) -> FairingGeometry:
    """Size aerodynamic satellite payload fairing."""
    _require_positive("payload_mass_kg", payload_mass_kg)
    _require_positive("diameter_m", diameter_m)
    _require_positive("cylinder_length_m", cylinder_length_m)

    nose_len = nose_cone_length_m if nose_cone_length_m is not None else 1.2 * diameter_m
    total_len = cylinder_length_m + nose_len
    radius = diameter_m / 2.0

    # Conical / ogive nose surface area & volume
    cone_slant = sqrt(nose_len**2 + radius**2)
    nose_area = pi * radius * cone_slant
    cyl_area = 2.0 * pi * radius * cylinder_length_m
    total_area = nose_area + cyl_area

    cyl_vol = pi * (radius**2) * cylinder_length_m
    nose_vol = (1.0 / 3.0) * pi * (radius**2) * nose_len
    total_vol = cyl_vol + nose_vol

    return FairingGeometry(
        diameter_m=diameter_m,
        total_length_m=total_len,
        cylinder_length_m=cylinder_length_m,
        nose_cone_length_m=nose_len,
        surface_area_m2=total_area,
        internal_volume_m3=total_vol,
    )


def assemble_vehicle_geometry(
    stage1_geom: StageGeometry,
    stage2_geom: StageGeometry,
    fairing_geom: FairingGeometry,
    interstage_length_m: float = 0.8,
) -> VehicleGeometry:
    """Assemble complete stack geometry and calculate fineness ratio."""
    _require_positive("interstage_length_m", interstage_length_m)

    total_length = (
        fairing_geom.total_length_m
        + stage2_geom.total_length_m
        + interstage_length_m
        + stage1_geom.total_length_m
    )
    fineness_ratio = total_length / stage1_geom.diameter_m

    return VehicleGeometry(
        fairing=fairing_geom,
        stage2=stage2_geom,
        interstage_length_m=interstage_length_m,
        stage1=stage1_geom,
        total_length_m=total_length,
        fineness_ratio=fineness_ratio,
    )
