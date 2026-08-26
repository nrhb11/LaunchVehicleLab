"""Validated, interface-independent scientific models."""

from launchvehiclelab.core.aerodynamics import (
    calculate_aerodynamics,
    drag_coefficient_curve,
)
from launchvehiclelab.core.atmosphere import us_standard_atmosphere_1976
from launchvehiclelab.core.delta_v import (
    EARTH_EQUATORIAL_RADIUS_M,
    EARTH_MU_M3_PER_S2,
    EARTH_ROTATION_RATE_RAD_PER_S,
    calculate_delta_v_budget,
    circular_orbit_velocity,
    earth_rotation_boost,
)
from launchvehiclelab.core.domain import (
    AerodynamicState,
    AtmosphereState,
    CoupledStageResult,
    CoupledVehicleResult,
    DeltaVBudget,
    FairingGeometry,
    FlightEvent,
    MissionSpec,
    OrbitTarget,
    PropellantCombination,
    PropellantSpec,
    StageGeometry,
    StageSizingResult,
    StageSpec,
    SubsystemMassBreakdown,
    TankGeometry,
    TrajectoryPoint,
    TrajectoryResult,
    TwoStageVehicleResult,
    VehicleGeometry,
)
from launchvehiclelab.core.geometry import (
    CH4,
    LH2,
    LOX,
    PROPELLANT_COMBINATIONS,
    RP1,
    assemble_vehicle_geometry,
    size_fairing_geometry,
    size_stage_geometry,
    size_tank_geometry,
)
from launchvehiclelab.core.mass import (
    estimate_fairing_mass,
    estimate_stage_subsystems,
)
from launchvehiclelab.core.rocket_equation import (
    STANDARD_GRAVITY_M_PER_S2,
    ideal_delta_v,
)
from launchvehiclelab.core.staging import (
    evaluate_two_stage,
    optimize_two_stage,
)
from launchvehiclelab.core.trajectory import simulate_ascent_trajectory

__all__ = [
    "CH4",
    "EARTH_EQUATORIAL_RADIUS_M",
    "EARTH_MU_M3_PER_S2",
    "EARTH_ROTATION_RATE_RAD_PER_S",
    "LH2",
    "LOX",
    "PROPELLANT_COMBINATIONS",
    "RP1",
    "STANDARD_GRAVITY_M_PER_S2",
    "AerodynamicState",
    "AtmosphereState",
    "CoupledStageResult",
    "CoupledVehicleResult",
    "DeltaVBudget",
    "FairingGeometry",
    "FlightEvent",
    "MissionSpec",
    "OrbitTarget",
    "PropellantCombination",
    "PropellantSpec",
    "StageGeometry",
    "StageSizingResult",
    "StageSpec",
    "SubsystemMassBreakdown",
    "TankGeometry",
    "TrajectoryPoint",
    "TrajectoryResult",
    "TwoStageVehicleResult",
    "VehicleGeometry",
    "assemble_vehicle_geometry",
    "calculate_aerodynamics",
    "calculate_delta_v_budget",
    "circular_orbit_velocity",
    "drag_coefficient_curve",
    "earth_rotation_boost",
    "estimate_fairing_mass",
    "estimate_stage_subsystems",
    "evaluate_two_stage",
    "ideal_delta_v",
    "optimize_two_stage",
    "simulate_ascent_trajectory",
    "size_fairing_geometry",
    "size_stage_geometry",
    "size_tank_geometry",
    "us_standard_atmosphere_1976",
]
