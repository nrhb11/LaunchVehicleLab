"""Multi-stage rocket sizing and optimization."""

from math import exp, isfinite, log

from launchvehiclelab.core.domain import (
    StageSizingResult,
    StageSpec,
    TwoStageVehicleResult,
)
from launchvehiclelab.core.rocket_equation import STANDARD_GRAVITY_M_PER_S2


def _require_positive_finite(name: str, value: float) -> None:
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be a positive finite value")


def _require_fraction(name: str, value: float) -> None:
    if not isfinite(value) or value <= 0.0 or value >= 1.0:
        raise ValueError(f"{name} must be strictly between 0 and 1 (exclusive)")


def evaluate_two_stage(
    payload_mass_kg: float,
    stage1_spec: StageSpec,
    stage2_spec: StageSpec,
    stage1_propellant_kg: float,
    stage2_propellant_kg: float,
) -> TwoStageVehicleResult:
    """Evaluate performance of a two-stage launcher given stage propellant masses.

    Mass relations for each stage i:
        structural_fraction epsilon_i = m_struct / (m_struct + m_prop)
        m_struct_i = m_prop_i * epsilon_i / (1 - epsilon_i)
        m_total_stage_i = m_struct_i + m_prop_i
    """
    _require_positive_finite("payload_mass_kg", payload_mass_kg)
    _require_positive_finite("stage1_propellant_kg", stage1_propellant_kg)
    _require_positive_finite("stage2_propellant_kg", stage2_propellant_kg)
    _require_positive_finite("stage1_spec.specific_impulse_s", stage1_spec.specific_impulse_s)
    _require_positive_finite("stage2_spec.specific_impulse_s", stage2_spec.specific_impulse_s)
    _require_fraction("stage1_spec.structural_fraction", stage1_spec.structural_fraction)
    _require_fraction("stage2_spec.structural_fraction", stage2_spec.structural_fraction)

    # Stage 2 sizing
    eps2 = stage2_spec.structural_fraction
    m_struct2 = stage2_propellant_kg * (eps2 / (1.0 - eps2))
    m_burnout2 = m_struct2 + payload_mass_kg
    m_initial2 = stage2_propellant_kg + m_struct2 + payload_mass_kg
    ratio2 = m_initial2 / m_burnout2
    dv2 = STANDARD_GRAVITY_M_PER_S2 * stage2_spec.specific_impulse_s * log(ratio2)

    stage2_result = StageSizingResult(
        name=stage2_spec.name,
        delta_v_m_per_s=dv2,
        propellant_mass_kg=stage2_propellant_kg,
        structural_mass_kg=m_struct2,
        burnout_mass_kg=m_burnout2,
        initial_mass_kg=m_initial2,
        mass_ratio=ratio2,
    )

    # Stage 1 sizing (payload for stage 1 is m_initial2)
    eps1 = stage1_spec.structural_fraction
    m_struct1 = stage1_propellant_kg * (eps1 / (1.0 - eps1))
    m_burnout1 = m_struct1 + m_initial2
    m_initial1 = stage1_propellant_kg + m_struct1 + m_initial2
    ratio1 = m_initial1 / m_burnout1
    dv1 = STANDARD_GRAVITY_M_PER_S2 * stage1_spec.specific_impulse_s * log(ratio1)

    stage1_result = StageSizingResult(
        name=stage1_spec.name,
        delta_v_m_per_s=dv1,
        propellant_mass_kg=stage1_propellant_kg,
        structural_mass_kg=m_struct1,
        burnout_mass_kg=m_burnout1,
        initial_mass_kg=m_initial1,
        mass_ratio=ratio1,
    )

    return TwoStageVehicleResult(
        payload_mass_kg=payload_mass_kg,
        stage1=stage1_result,
        stage2=stage2_result,
        gross_liftoff_weight_kg=m_initial1,
        total_delta_v_m_per_s=dv1 + dv2,
    )


def _step_growth_factor(delta_v: float, c_eff: float, epsilon: float) -> float:
    """Return m_0_i / m_pl_i for a given stage delta-v increment."""
    ratio = exp(delta_v / c_eff)
    denom = 1.0 - epsilon * ratio
    if denom <= 0.0:
        return float("inf")
    return ((1.0 - epsilon) * ratio) / denom


def optimize_two_stage(
    payload_mass_kg: float,
    target_delta_v_m_per_s: float,
    stage1_spec: StageSpec,
    stage2_spec: StageSpec,
) -> TwoStageVehicleResult:
    """Analytically size and optimize a two-stage launch vehicle minimizing GLOW.

    Finds the optimal delta-v partition (dv1, dv2) such that:
        dv1 + dv2 = target_delta_v_m_per_s
    minimizing total vehicle initial mass m0_1 = payload * X1(dv1) * X2(dv2).
    """
    _require_positive_finite("payload_mass_kg", payload_mass_kg)
    _require_positive_finite("target_delta_v_m_per_s", target_delta_v_m_per_s)
    _require_positive_finite("stage1_spec.specific_impulse_s", stage1_spec.specific_impulse_s)
    _require_positive_finite("stage2_spec.specific_impulse_s", stage2_spec.specific_impulse_s)
    _require_fraction("stage1_spec.structural_fraction", stage1_spec.structural_fraction)
    _require_fraction("stage2_spec.structural_fraction", stage2_spec.structural_fraction)

    c1 = STANDARD_GRAVITY_M_PER_S2 * stage1_spec.specific_impulse_s
    c2 = STANDARD_GRAVITY_M_PER_S2 * stage2_spec.specific_impulse_s
    eps1 = stage1_spec.structural_fraction
    eps2 = stage2_spec.structural_fraction

    # Theoretical maximum delta-v for each stage (when payload -> 0 and propellant ratio -> 1 - eps)
    dv1_max = c1 * log(1.0 / eps1)
    dv2_max = c2 * log(1.0 / eps2)

    if target_delta_v_m_per_s >= (dv1_max + dv2_max):
        raise ValueError(
            f"Target delta-v ({target_delta_v_m_per_s:.1f} m/s) exceeds combined theoretical limit "
            f"({dv1_max + dv2_max:.1f} m/s) for given structural fractions"
        )

    # Feasible search bounds for dv1
    dv1_low = max(1e-3, target_delta_v_m_per_s - dv2_max + 1e-3)
    dv1_high = min(target_delta_v_m_per_s - 1e-3, dv1_max - 1e-3)

    if dv1_low >= dv1_high:
        raise ValueError("No feasible two-stage design space found for given target delta-v")

    def objective(dv1_val: float) -> float:
        dv2_val = target_delta_v_m_per_s - dv1_val
        x1 = _step_growth_factor(dv1_val, c1, eps1)
        x2 = _step_growth_factor(dv2_val, c2, eps2)
        return x1 * x2

    # Golden-section 1D optimization search
    invphi = (5.0**0.5 - 1.0) / 2.0  # ~0.6180339887
    invphi2 = (3.0 - 5.0**0.5) / 2.0  # ~0.3819660113

    a = dv1_low
    b = dv1_high
    h = b - a

    c = a + invphi2 * h
    d = a + invphi * h
    yc = objective(c)
    yd = objective(d)

    for _ in range(80):
        if yc < yd:
            b = d
            d = c
            yd = yc
            h = invphi * h
            c = a + invphi2 * h
            yc = objective(c)
        else:
            a = c
            c = d
            yc = yd
            h = invphi * h
            d = a + invphi * h
            yd = objective(d)

    optimal_dv1 = (a + b) / 2.0
    optimal_dv2 = target_delta_v_m_per_s - optimal_dv1

    # Reconstruct masses from optimal delta-vs
    x1 = _step_growth_factor(optimal_dv1, c1, eps1)
    x2 = _step_growth_factor(optimal_dv2, c2, eps2)

    m_initial2 = x2 * payload_mass_kg
    m_loaded2 = m_initial2 - payload_mass_kg
    m_struct2 = eps2 * m_loaded2
    m_prop2 = (1.0 - eps2) * m_loaded2
    m_burnout2 = m_struct2 + payload_mass_kg
    ratio2 = m_initial2 / m_burnout2

    stage2_result = StageSizingResult(
        name=stage2_spec.name,
        delta_v_m_per_s=optimal_dv1 if False else optimal_dv2,
        propellant_mass_kg=m_prop2,
        structural_mass_kg=m_struct2,
        burnout_mass_kg=m_burnout2,
        initial_mass_kg=m_initial2,
        mass_ratio=ratio2,
    )

    m_initial1 = x1 * m_initial2
    m_loaded1 = m_initial1 - m_initial2
    m_struct1 = eps1 * m_loaded1
    m_prop1 = (1.0 - eps1) * m_loaded1
    m_burnout1 = m_struct1 + m_initial2
    ratio1 = m_initial1 / m_burnout1

    stage1_result = StageSizingResult(
        name=stage1_spec.name,
        delta_v_m_per_s=optimal_dv1,
        propellant_mass_kg=m_prop1,
        structural_mass_kg=m_struct1,
        burnout_mass_kg=m_burnout1,
        initial_mass_kg=m_initial1,
        mass_ratio=ratio1,
    )

    return TwoStageVehicleResult(
        payload_mass_kg=payload_mass_kg,
        stage1=stage1_result,
        stage2=stage2_result,
        gross_liftoff_weight_kg=m_initial1,
        total_delta_v_m_per_s=optimal_dv1 + optimal_dv2,
    )
