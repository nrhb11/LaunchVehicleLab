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
    DeltaVBudget,
    MissionSpec,
    OrbitTarget,
    StageSizingResult,
    StageSpec,
    TwoStageVehicleResult,
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
    "EARTH_EQUATORIAL_RADIUS_M",
    "EARTH_MU_M3_PER_S2",
    "EARTH_ROTATION_RATE_RAD_PER_S",
    "STANDARD_GRAVITY_M_PER_S2",
    "DeltaVBudget",
    "MissionSpec",
    "OrbitTarget",
    "StageSizingResult",
    "StageSpec",
    "TwoStageVehicleResult",
    "calculate_delta_v_budget",
    "circular_orbit_velocity",
    "earth_rotation_boost",
    "evaluate_two_stage",
    "ideal_delta_v",
    "optimize_two_stage",
]
