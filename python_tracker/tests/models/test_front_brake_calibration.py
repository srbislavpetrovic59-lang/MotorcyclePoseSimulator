import pytest
from  pose.analyzers.hand_control_analyzer import HandControlAnalyzer
from pose.models.front_brake_calibration import FrontBrakeCalibration

def test_front_brake_progress_returns_zero_when_released():
    progress = HandControlAnalyzer._front_brake_progress(
        released_angle=165.0,
        pulled_angle=100.0,
        current_angle=165.0,
    )

    assert progress == 0.0

def test_front_brake_progress_returns_one_when_fully_pulled():
    progress = HandControlAnalyzer._front_brake_progress(
        released_angle=165.0,
        pulled_angle=100.0,
        current_angle=100.0,
    )

    assert progress == 1.0

def test_front_brake_progress_returns_halfway_value():
    progress = HandControlAnalyzer._front_brake_progress(
        released_angle=165.0,
        pulled_angle=100.0,
        current_angle=132.5,
    )

    assert progress == 0.5




@pytest.mark.parametrize(
    "current_angle, expected",
    [
        (170.0, 0.0),
        (90.0, 1.0),
    ],
)
def test_front_brake_progress_is_clamped(
    current_angle,
    expected,
):
    progress = HandControlAnalyzer._front_brake_progress(
        released_angle=165.0,
        pulled_angle=100.0,
        current_angle=current_angle,
    )

    assert progress == expected

def test_current_front_brake_progress_returns_none_without_calibration():
    analyzer = HandControlAnalyzer()

    progress = analyzer._current_front_brake_progress(
        current_angle=120.0
    )

    assert progress is None

def test_current_front_brake_progress_uses_calibration():
    analyzer = HandControlAnalyzer()

    analyzer._front_brake_calibration.released_angle = 165.0
    analyzer._front_brake_calibration.pulled_angle = 100.0

    progress = analyzer._current_front_brake_progress(
        current_angle=132.5
    )

    assert progress == 0.5

def test_front_brake_calibration_set_released():
    calibration = FrontBrakeCalibration()

    calibration.set_released(150.0)

    assert calibration.released_angle == 150.0

def test_front_brake_calibration_set_pulled():
    calibration = FrontBrakeCalibration()

    calibration.set_pulled(106.0)

    assert calibration.pulled_angle == 106.0


def test_front_brake_progress_after_calibration():
    analyzer = HandControlAnalyzer()

    analyzer._front_brake_calibration.set_released(150.0)
    analyzer._front_brake_calibration.set_pulled(106.0)

    progress = analyzer._current_front_brake_progress(
        current_angle=128.0,
    )

    assert progress == 0.5

def test_calibrate_front_brake_released():
    analyzer = HandControlAnalyzer()

    analyzer.calibrate_front_brake_released(150.0)

    assert (
        analyzer._front_brake_calibration.released_angle
        == 150.0
    )

def test_calibrate_front_brake_pulled():
    analyzer = HandControlAnalyzer()

    analyzer.calibrate_front_brake_pulled(106.0)

    assert (
        analyzer._front_brake_calibration.pulled_angle
        == 106.0
    )