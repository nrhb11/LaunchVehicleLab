import json

import pytest

from launchvehiclelab.cli import main
from launchvehiclelab.core import (
    StageSpec,
    evaluate_two_stage,
    optimize_two_stage,
)


def test_evaluate_two_stage_mass_conservation() -> None:
    s1 = StageSpec(name="Booster", specific_impulse_s=300.0, structural_fraction=0.08)
    s2 = StageSpec(name="Upper", specific_impulse_s=350.0, structural_fraction=0.10)

    payload_kg = 500.0
    prop1_kg = 20_000.0
    prop2_kg = 5_000.0

    result = evaluate_two_stage(
        payload_mass_kg=payload_kg,
        stage1_spec=s1,
        stage2_spec=s2,
        stage1_propellant_kg=prop1_kg,
        stage2_propellant_kg=prop2_kg,
    )

    # Stage 2 checks
    expected_struct2 = prop2_kg * (0.10 / 0.90)
    assert result.stage2.structural_mass_kg == pytest.approx(expected_struct2, rel=1e-10)
    assert result.stage2.burnout_mass_kg == pytest.approx(expected_struct2 + payload_kg, rel=1e-10)
    assert result.stage2.initial_mass_kg == pytest.approx(
        prop2_kg + expected_struct2 + payload_kg, rel=1e-10
    )

    # Stage 1 checks
    expected_struct1 = prop1_kg * (0.08 / 0.92)
    assert result.stage1.structural_mass_kg == pytest.approx(expected_struct1, rel=1e-10)
    assert result.stage1.burnout_mass_kg == pytest.approx(
        expected_struct1 + result.stage2.initial_mass_kg, rel=1e-10
    )
    assert result.stage1.initial_mass_kg == pytest.approx(
        prop1_kg + expected_struct1 + result.stage2.initial_mass_kg, rel=1e-10
    )
    assert result.gross_liftoff_weight_kg == pytest.approx(result.stage1.initial_mass_kg, rel=1e-10)
    assert result.total_delta_v_m_per_s == pytest.approx(
        result.stage1.delta_v_m_per_s + result.stage2.delta_v_m_per_s, rel=1e-10
    )


def test_optimize_two_stage_equal_technologies_split_evenly() -> None:
    # Classical rocket theorem: When Isp and epsilon are identical, optimal delta-v is split equally
    s1 = StageSpec(name="S1", specific_impulse_s=320.0, structural_fraction=0.08)
    s2 = StageSpec(name="S2", specific_impulse_s=320.0, structural_fraction=0.08)

    target_dv = 8000.0
    payload_kg = 1000.0

    result = optimize_two_stage(
        payload_mass_kg=payload_kg,
        target_delta_v_m_per_s=target_dv,
        stage1_spec=s1,
        stage2_spec=s2,
    )

    assert result.total_delta_v_m_per_s == pytest.approx(target_dv, rel=1e-6)
    assert result.stage1.delta_v_m_per_s == pytest.approx(4000.0, rel=1e-3)
    assert result.stage2.delta_v_m_per_s == pytest.approx(4000.0, rel=1e-3)


def test_optimize_two_stage_higher_upper_isp_allocates_more_to_upper() -> None:
    s1 = StageSpec(name="Kero", specific_impulse_s=300.0, structural_fraction=0.08)
    s2 = StageSpec(name="Hydrolox", specific_impulse_s=450.0, structural_fraction=0.12)

    result = optimize_two_stage(
        payload_mass_kg=500.0,
        target_delta_v_m_per_s=9000.0,
        stage1_spec=s1,
        stage2_spec=s2,
    )

    assert result.total_delta_v_m_per_s == pytest.approx(9000.0, rel=1e-6)
    assert result.stage2.delta_v_m_per_s > result.stage1.delta_v_m_per_s


def test_optimize_two_stage_roundtrip_consistency() -> None:
    s1 = StageSpec(name="S1", specific_impulse_s=300.0, structural_fraction=0.08)
    s2 = StageSpec(name="S2", specific_impulse_s=360.0, structural_fraction=0.10)

    payload_kg = 500.0
    target_dv = 9200.0

    opt_result = optimize_two_stage(
        payload_mass_kg=payload_kg,
        target_delta_v_m_per_s=target_dv,
        stage1_spec=s1,
        stage2_spec=s2,
    )

    # Re-evaluate with forward model
    eval_result = evaluate_two_stage(
        payload_mass_kg=payload_kg,
        stage1_spec=s1,
        stage2_spec=s2,
        stage1_propellant_kg=opt_result.stage1.propellant_mass_kg,
        stage2_propellant_kg=opt_result.stage2.propellant_mass_kg,
    )

    assert eval_result.gross_liftoff_weight_kg == pytest.approx(
        opt_result.gross_liftoff_weight_kg, rel=1e-6
    )
    assert eval_result.total_delta_v_m_per_s == pytest.approx(target_dv, rel=1e-6)


def test_optimize_two_stage_rejects_unreachable_delta_v() -> None:
    s1 = StageSpec(name="S1", specific_impulse_s=300.0, structural_fraction=0.20)
    s2 = StageSpec(name="S2", specific_impulse_s=300.0, structural_fraction=0.20)

    # With eps=0.2, max dv per stage is g0 * 300 * ln(5) ~ 4734 m/s. Total max ~ 9468 m/s.
    with pytest.raises(ValueError, match="exceeds combined theoretical limit"):
        optimize_two_stage(
            payload_mass_kg=500.0,
            target_delta_v_m_per_s=15_000.0,
            stage1_spec=s1,
            stage2_spec=s2,
        )


def test_cli_two_stage_sizing(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(
        [
            "two-stage-sizing",
            "--payload-kg",
            "500",
            "--target-delta-v",
            "9200",
            "--stage1-isp",
            "300",
            "--stage2-isp",
            "360",
            "--stage1-eps",
            "0.08",
            "--stage2-eps",
            "0.10",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["schema_version"] == "0.1"
    assert output["model"] == "two_stage_optimal_sizing_v0.1"
    assert output["outputs"]["total_delta_v_m_per_s"] == pytest.approx(9200.0, rel=1e-5)
    assert output["outputs"]["gross_liftoff_weight_kg"] > 500.0
