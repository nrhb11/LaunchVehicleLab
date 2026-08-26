"""Validated, interface-independent scientific models."""

from launchvehiclelab.core.delta_v import (
    EARTH_EQUATORIAL_RADIUS_M,
    EARTH_MU_M3_PER_S2,
    EARTH_ROTATION_RATE_RAD_PER_S,
    calculate_delta_v_budget,
    circular_orbit_velocity,
    earth_rotation_boost,
)
from launchvehiclelab.core.domain import (
    CoupledStageResult,
    CoupledVehicleResult,
    DeltaVBudget,
    FairingGeometry,
    MissionSpec,
    OrbitTarget,
    PropellantCombination,
    PropellantSpec,
    StageGeometry,
    StageSizingResult,
    StageSpec,
    SubsystemMassBreakdown,
    TankGeometry,
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
    "CoupledStageResult",
    "CoupledVehicleResult",
    "DeltaVBudget",
    "FairingGeometry",
    "MissionSpec",
    "OrbitTarget",
    "PropellantCombination",
    "PropellantSpec",
    "StageGeometry",
    "StageSizingResult",
    "StageSpec",
    "SubsystemMassBreakdown",
    "TankGeometry",
    "TwoStageVehicleResult",
    "VehicleGeometry",
    "assemble_vehicle_geometry",
    "calculate_delta_v_budget",
    "circular_orbit_velocity",
    "earth_rotation_boost",
    "estimate_fairing_mass",
    "estimate_stage_subsystems",
    "evaluate_two_stage",
    "ideal_delta_v",
    "optimize_two_stage",
    "size_fairing_geometry",
    "size_stage_geometry",
    "size_tank_geometry",
]
