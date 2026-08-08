import json
from math import log

import pytest

from launchvehiclelab.cli import main
from launchvehiclelab.core import STANDARD_GRAVITY_M_PER_S2, ideal_delta_v


def test_ideal_delta_v_matches_hand_calculation() -> None:
    expected = STANDARD_GRAVITY_M_PER_S2 * 300.0 * log(10_000.0 / 4_000.0)

    result = ideal_delta_v(
        specific_impulse_s=300.0,
        initial_mass_kg=10_000.0,
        final_mass_kg=4_000.0,
    )

    assert result == pytest.approx(expected, rel=1e-12)


def test_equal_masses_produce_zero_delta_v() -> None:
    assert ideal_delta_v(300.0, 4_000.0, 4_000.0) == 0.0


@pytest.mark.parametrize(
    ("specific_impulse_s", "initial_mass_kg", "final_mass_kg"),
    [
        (0.0, 10_000.0, 4_000.0),
        (300.0, -1.0, 4_000.0),
        (300.0, 4_000.0, 10_000.0),
        (float("nan"), 10_000.0, 4_000.0),
    ],
)
def test_invalid_inputs_are_rejected(
    specific_impulse_s: float,
    initial_mass_kg: float,
    final_mass_kg: float,
) -> None:
    with pytest.raises(ValueError):
        ideal_delta_v(specific_impulse_s, initial_mass_kg, final_mass_kg)


def test_cli_emits_versioned_json(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(
        [
            "rocket-equation",
            "--specific-impulse-s",
            "300",
            "--initial-mass-kg",
            "10000",
            "--final-mass-kg",
            "4000",
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["schema_version"] == "0.1"
    assert output["model"] == "ideal_rocket_equation_v0.1"
    assert output["outputs"]["ideal_delta_v_m_per_s"] == pytest.approx(
        2695.722751720105
    )
