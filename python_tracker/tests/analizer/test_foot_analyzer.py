import pytest
from pose.analyzers.foot_analyzer import FootAnalyzer
from pose.models.rear_brake_calibration import RearBrakeCalibration

def test_rear_brake_ready_when_foot_is_over_brake():
    assert FootAnalyzer._is_rear_brake_ready(
        65.0
    ) is True


def test_rear_brake_not_ready_when_foot_is_on_footpeg():
    assert FootAnalyzer._is_rear_brake_ready(
        140.0
    ) is False

def test_rear_brake_not_ready_without_rotation():
    assert FootAnalyzer._is_rear_brake_ready(
        None
    ) is False
def test_rear_brake_ready_uses_hysteresis():
    analyzer = FootAnalyzer()

    # Foot starts on the footpeg.
    assert analyzer._update_rear_brake_ready(140.0) is False

    # Foot moves onto the brake.
    assert analyzer._update_rear_brake_ready(70.0) is True

    # Measurement enters the uncertain area.
    # Previous READY state must be preserved.
    assert analyzer._update_rear_brake_ready(95.0) is True

    # Foot clearly returns to the footpeg.
    assert analyzer._update_rear_brake_ready(120.0) is False

def test_rear_brake_calibration_starts_empty():
    calibration = RearBrakeCalibration()

    assert calibration.released_drop is None
    assert calibration.full_drop is None
    assert calibration.is_complete() is False

def test_rear_brake_calibration_can_set_endpoints():
    calibration = RearBrakeCalibration()

    calibration.set_released(0.08)
    calibration.set_full(0.12)

    assert calibration.released_drop == 0.08
    assert calibration.full_drop == 0.12

    assert calibration.is_complete() is True

def test_rear_brake_progress_is_zero_when_released():
    progress = FootAnalyzer._rear_brake_progress(
        released_drop=0.08,
        full_drop=0.12,
        current_drop=0.08,
    )

    assert progress == 0.0


def test_rear_brake_progress_is_half_when_half_pressed():
    progress = FootAnalyzer._rear_brake_progress(
        released_drop=0.0,
        full_drop=10.0,
        current_drop=5.0,
    )

    assert progress == 0.5

@pytest.mark.parametrize(
    "current_drop, expected",
    [
        (-2.0, 0.0),
        (12.0, 1.0),
    ],
)
def test_rear_brake_progress_is_clamped(
    current_drop,
    expected,
):
    progress = FootAnalyzer._rear_brake_progress(
        released_drop=0.0,
        full_drop=10.0,
        current_drop=current_drop,
    )

    assert progress == expected

def test_rear_brake_progress_is_one_when_fully_pressed():
    progress = FootAnalyzer._rear_brake_progress(
        released_drop=0.08,
        full_drop=0.12,
        current_drop=0.12,
    )

    assert progress == 1.0

def test_rear_brake_becomes_active_when_progress_is_high():
    analyzer = FootAnalyzer()

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=0.5
    )

    assert active is True

def test_rear_brake_is_inactive_when_released():
    analyzer = FootAnalyzer()

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=0.0
    )

    assert active is False

def test_rear_brake_is_inactive_when_progress_is_none():
    analyzer = FootAnalyzer()

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=None
    )

    assert active is False

def test_rear_brake_hysteresis_keeps_active_state():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_active(
        rear_brake_progress=0.5
    )

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=0.15
    )

    assert active is True

def test_rear_brake_hysteresis_releases_below_lower_threshold():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_active(
        rear_brake_progress=0.5
    )

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=0.05
    )

    assert active is False

def test_rear_brake_detection_loss_keeps_previous_state():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_active(
        rear_brake_progress=0.5
    )

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=None
    )

    assert active is True

