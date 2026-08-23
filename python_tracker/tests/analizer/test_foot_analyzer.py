import pytest
from pose.analyzers.foot_analyzer import FootAnalyzer
from pose.models.rear_brake_calibration import RearBrakeCalibration
from pose.analyzers.gear_shift_detector import GearShiftDetector

from types import SimpleNamespace

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

def test_rear_brake_progress_is_none_when_measurement_missing():
    progress = FootAnalyzer._rear_brake_progress(
        released_drop=0.08,
        full_drop=0.12,
        current_drop=None,
    )

    assert progress is None



def test_right_foot_not_visible_when_landmark_visibility_is_low():
    right_heel = SimpleNamespace(
        visibility=0.9
    )
    
    right_ankle = SimpleNamespace(
        visibility=0.9
    )

    right_foot = SimpleNamespace(
        visibility=0.2
    )

    assert (
        FootAnalyzer._right_foot_visible(
            right_heel,
            right_ankle,
            right_foot,
        )
        is False
    )

def test_right_foot_visible_when_landmarks_are_visible():
    right_heel = SimpleNamespace(
        visibility=0.9
    )   

    right_ankle = SimpleNamespace(
        visibility=0.9
    )
    right_foot = SimpleNamespace(
        visibility=0.8
    )

    assert (
        FootAnalyzer._right_foot_visible(
            right_heel,
            right_ankle,
            right_foot,
        )
        is True
    )

def test_zone_is_low():
    assert GearShiftDetector._zone(0.040) == "LOW"


def test_zone_is_transition():
    assert GearShiftDetector._zone(0.055) == "TRANSITION"


def test_zone_is_high():
    assert GearShiftDetector._zone(0.075) == "HIGH"

def test_zone_is_none_without_measurement():
    assert GearShiftDetector._zone(None) is None

def test_update_remembers_last_valid_zone():
    detector = GearShiftDetector()

    detector.update(0.040)

    assert detector._last_zone == "LOW"

def test_update_keeps_last_zone_when_measurement_is_missing():
    detector = GearShiftDetector()

    detector.update(0.040)
    detector.update(None)

    assert detector._last_zone == "LOW"

def test_update_detects_low_to_high_sequence():
    detector = GearShiftDetector()

    detector.update(0.040)
    detector.update(0.055)
    detector.update(0.075)

    assert detector._state == "LOW_TO_HIGH"

def test_update_emits_shift_up_after_low_to_high_and_return():
    detector = GearShiftDetector()

    assert detector.update(0.040) is None
    assert detector.update(0.055) is None
    assert detector.update(0.075) is None
    assert detector.update(0.055) == "SHIFT_UP"

def test_update_detects_high_to_low_sequence():
    detector = GearShiftDetector()

    detector.update(0.075)
    detector.update(0.055)
    detector.update(0.040)

    assert detector._state == "HIGH_TO_LOW"

def test_update_detects_high_to_low_sequence():
    detector = GearShiftDetector()

    detector.update(0.075)
    detector.update(0.055)
    detector.update(0.040)

    assert detector._state == "HIGH_TO_LOW"

def test_update_emits_shift_down_after_high_to_low_and_return():
    detector = GearShiftDetector()

    assert detector.update(0.075) is None
    assert detector.update(0.055) is None
    assert detector.update(0.040) is None
    assert detector.update(0.055) is None
    assert detector.update(0.075) == "SHIFT_DOWN"

def test_holding_high_does_not_emit_shift():
    detector = GearShiftDetector()

    assert detector.update(0.075) is None
    assert detector.update(0.078) is None
    assert detector.update(0.080) is None
    assert detector.update(0.076) is None

def test_holding_low_does_not_emit_shift():
    detector = GearShiftDetector()

    assert detector.update(0.040) is None
    assert detector.update(0.042) is None
    assert detector.update(0.038) is None
    assert detector.update(0.041) is None

def test_missing_measurement_does_not_break_shift_up_sequence():
    detector = GearShiftDetector()

    assert detector.update(0.040) is None   # LOW
    assert detector.update(0.055) is None   # TRANSITION
    assert detector.update(None) is None    # tracking lost
    assert detector.update(0.075) is None   # HIGH
    assert detector.update(0.055) == "SHIFT_UP"

def test_missing_measurement_does_not_break_shift_down_sequence():
    detector = GearShiftDetector()

    assert detector.update(0.075) is None   # HIGH
    assert detector.update(0.055) is None   # TRANSITION
    assert detector.update(None) is None    # tracking lost
    assert detector.update(0.040) is None   # LOW
    assert detector.update(0.055) is None   # TRANSITION
    assert detector.update(0.075) == "SHIFT_DOWN"

def test_missing_measurement_does_not_break_shift_down_sequence():
    detector = GearShiftDetector()

    assert detector.update(0.075) is None   # HIGH
    assert detector.update(0.055) is None   # TRANSITION
    assert detector.update(None) is None    # tracking lost
    assert detector.update(0.040) is None   # LOW
    assert detector.update(0.055) is None   # TRANSITION
    assert detector.update(0.075) == "SHIFT_DOWN"

def test_shift_up_is_emitted_only_once():
    detector = GearShiftDetector()

    assert detector.update(0.040) is None
    assert detector.update(0.055) is None
    assert detector.update(0.075) is None
    assert detector.update(0.055) == "SHIFT_UP"

    # No new gesture.
    assert detector.update(0.055) is None
    assert detector.update(0.075) is None
    assert detector.update(0.078) is None

def test_zone_classifies_measured_shift_up_peak_as_high():
    detector = GearShiftDetector()

    assert detector._zone(0.060) == "HIGH"

def test_zone_keeps_value_below_high_threshold_in_transition():
    detector = GearShiftDetector()

    assert detector._zone(0.055) == "TRANSITION"