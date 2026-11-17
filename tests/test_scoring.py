import pytest

from risk_intel.scoring import calculate_risk_score


def test_minimum_score_is_20():
    assert calculate_risk_score(1, 1, 1) == 20


def test_maximum_score_is_100():
    assert calculate_risk_score(5, 5, 5) == 100


def test_severity_has_largest_effect():
    baseline = calculate_risk_score(2, 2, 2)
    assert calculate_risk_score(3, 2, 2) - baseline == 10
    assert calculate_risk_score(2, 3, 2) - baseline == 6
    assert calculate_risk_score(2, 2, 3) - baseline == 4


@pytest.mark.parametrize("value", [0, 6, 2.5, "3"])
def test_invalid_component_is_rejected(value):
    with pytest.raises(ValueError):
        calculate_risk_score(value, 3, 3)
