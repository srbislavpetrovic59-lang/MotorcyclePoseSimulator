import pytest
from pose.analyzers.foot_analyzer import FootAnalyzer
from pose.models.rear_brake_calibration import RearBrakeCalibration
from pose.analyzers.gear_shift_detector import GearShiftDetector

from types import SimpleNamespace

def test_detector_waits_for_footpeg_before_tracking_shift():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.090,
        left_foot_angle=150.0,
    )

    assert detector._state == "IDLE"

def test_detector_becomes_ready_on_footpeg():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    assert detector._state == "READY"

def test_ready_detector_remembers_zone_path():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    detector.update(0.040)
    detector.update(0.055)
    detector.update(0.075)

    assert detector._zone_history == [
        "LOW",
        "MID",
        "HIGH",
    ]
def test_ready_detector_does_not_repeat_same_zone():
    detector = GearShiftDetector()

    # FOOTPEG -> READY
    detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    detector.update(0.040)
    detector.update(0.041)
    detector.update(0.042)

    assert detector._zone_history == ["LOW"]

def test_shift_up_path():
    detector = GearShiftDetector()

    # FOOTPEG -> READY
    detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    # Foot moves under the shifter.
    detector.update(
        left_foot_drop=0.040,
        left_foot_angle=120.0,
    )

    # Foot lifts the shifter.
    detector.update(
        left_foot_drop=0.075,
        left_foot_angle=142.0,
    )

    # Return to footpeg.
    result = detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    assert result == "SHIFT_UP"

def test_shift_down_path():
    detector = GearShiftDetector()

    # FOOTPEG -> READY
    detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    # Foot moves above the shifter.
    detector.update(
        left_foot_drop=0.075,
        left_foot_angle=142.0,
    )

    # Foot presses the shifter down.
    detector.update(
        left_foot_drop=0.040,
        left_foot_angle=120.0,
    )

    # Return to footpeg.
    result = detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    assert result == "SHIFT_DOWN"

def test_incomplete_path_does_not_emit_shift():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    detector.update(
        left_foot_drop=0.040,
        left_foot_angle=120.0,
    )

    result = detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    assert result is None

def test_invalid_path_does_not_emit_shift():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    detector.update(0.040, 120.0)
    detector.update(0.055, 126.0)
    detector.update(0.040, 120.0)

    result = detector.update(
        left_foot_drop=0.060,
        left_foot_angle=132.0,
    )

    assert result is None

def test_footpeg_does_not_enter_zone_history():
    detector = GearShiftDetector()

    detector.update(0.060, 132.0)  # IDLE -> READY

    detector.update(0.059, 131.0)
    detector.update(0.058, 130.0)
    detector.update(0.061, 133.0)

    assert detector._zone_history == []

def test_real_footpeg_measurements_do_not_enter_history():
    detector = GearShiftDetector()

    detector.update(0.060, 132.0)  # -> READY

    detector.update(0.0546, 128.3)
    detector.update(0.0592, 130.9)
    detector.update(0.0565, 128.7)

    assert detector._zone_history == []

def test_real_footpeg_measurement_does_not_start_history():
    detector = GearShiftDetector()

    # Clearly establish FOOTPEG -> READY first.
    detector.update(
        0.060,
        132.0,
    )

    assert detector._state == "READY"

    # Value observed live while the foot was still around footpeg.
    detector.update(
        0.0591,
        125.2,
    )

    assert detector._zone_history == []

def test_shift_movement_leaves_footpeg_and_starts_history():
    detector = GearShiftDetector()

    # FOOTPEG -> READY
    detector.update(
        0.060,
        132.0,
    )

    # Beginning of a real shift movement.
    detector.update(
        0.040,
        120.0,
    )

    assert detector._zone_history == ["LOW"]