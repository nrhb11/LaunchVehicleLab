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


# --- V0.2 Physical, Propellant, and Geometry Domain Models ---


@dataclass(frozen=True, slots=True)
class PropellantSpec:
    """Thermophysical properties of an individual propellant fluid."""

    name: str
    density_kg_per_m3: float
    description: str = ""


@dataclass(frozen=True, slots=True)
class PropellantCombination:
    """Bipropellant combination with operational mixture ratio and specific impulses."""

    name: str
    oxidizer: PropellantSpec
    fuel: PropellantSpec
    default_mixture_ratio_of: float  # O/F mass ratio
    default_sea_level_isp_s: float
    default_vacuum_isp_s: float


@dataclass(frozen=True, slots=True)
class TankGeometry:
    """Cylindrical tank geometry with 2:1 ellipsoidal heads."""

    diameter_m: float
    cylinder_length_m: float
    dome_height_m: float
    total_length_m: float
    volume_m3: float
    surface_area_m2: float


@dataclass(frozen=True, slots=True)
class StageGeometry:
    """Packaged geometry for an individual stage."""

    diameter_m: float
    total_length_m: float
    oxidizer_tank: TankGeometry
    fuel_tank: TankGeometry
    intertank_length_m: float
    skirt_length_m: float


@dataclass(frozen=True, slots=True)
class FairingGeometry:
    """Payload fairing geometry with cylindrical body and ogive/conical nose."""

    diameter_m: float
    total_length_m: float
    cylinder_length_m: float
    nose_cone_length_m: float
    surface_area_m2: float
    internal_volume_m3: float


@dataclass(frozen=True, slots=True)
class VehicleGeometry:
    """Overall launch vehicle dimensional packaging and fineness ratio."""

    fairing: FairingGeometry
    stage2: StageGeometry
    interstage_length_m: float
    stage1: StageGeometry
    total_length_m: float
    fineness_ratio: float  # total_length / stage1_diameter


@dataclass(frozen=True, slots=True)
class SubsystemMassBreakdown:
    """Engineering mass accounting for all physical rocket subsystems."""

    tanks_mass_kg: float
    propulsion_mass_kg: float
    avionics_mass_kg: float
    interstage_mass_kg: float
    fairing_mass_kg: float
    residuals_and_margin_kg: float
    total_dry_mass_kg: float


@dataclass(frozen=True, slots=True)
class CoupledStageResult:
    """Comprehensive state of a sized, dimensioned, and mass-audited stage."""

    name: str
    propellant_combo: PropellantCombination
    propellant_mass_kg: float
    oxidizer_mass_kg: float
    fuel_mass_kg: float
    sizing: StageSizingResult
    geometry: StageGeometry
    mass_breakdown: SubsystemMassBreakdown
    effective_structural_fraction: float


@dataclass(frozen=True, slots=True)
class CoupledVehicleResult:
    """Final converged multi-disciplinary vehicle preliminary design solution."""

    mission: MissionSpec
    delta_v_budget: DeltaVBudget
    vehicle_geometry: VehicleGeometry
    stage1: CoupledStageResult
    stage2: CoupledStageResult
    gross_liftoff_weight_kg: float
    payload_ratio_percent: float
    iterations_to_converge: int


# --- V0.3 & V0.4 Atmosphere, Aerodynamics, and Trajectory Models ---


@dataclass(frozen=True, slots=True)
class AtmosphereState:
    """Local ambient atmospheric thermodynamic properties (US Standard Atmosphere 1976)."""

    altitude_m: float
    temperature_k: float
    pressure_pa: float
    density_kg_per_m3: float
    speed_of_sound_m_per_s: float


@dataclass(frozen=True, slots=True)
class AerodynamicState:
    """Instantaneous flight aerodynamic loads, Mach number, and dynamic pressure."""

    mach: float
    dynamic_pressure_pa: float
    drag_coefficient: float
    drag_force_n: float


@dataclass(frozen=True, slots=True)
class TrajectoryPoint:
    """State vector sample at a discrete flight trajectory timestep."""

    time_s: float
    altitude_m: float
    downrange_m: float
    velocity_m_per_s: float
    flight_path_angle_rad: float
    mass_kg: float
    thrust_n: float
    dynamic_pressure_pa: float
    mach: float
    acceleration_g: float


@dataclass(frozen=True, slots=True)
class FlightEvent:
    """Discrete mission milestone timestamp and flight state."""

    name: str
    time_s: float
    altitude_m: float
    velocity_m_per_s: float
    description: str = ""


@dataclass(frozen=True, slots=True)
class TrajectoryResult:
    """Complete 0-to-Orbit numerical flight simulation history and key observables."""

    points: list[TrajectoryPoint]
    events: list[FlightEvent]
    max_q_pa: float
    max_q_time_s: float
    max_q_alt_m: float
    max_acceleration_g: float
    final_orbit_altitude_m: float
    final_orbit_velocity_m_per_s: float
    total_flight_time_s: float
