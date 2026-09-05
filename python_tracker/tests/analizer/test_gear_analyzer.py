from pickle import FALSE
import pytest
from pose.analyzers.gear_shift_detector import GearShiftDetector


def test_detector_waits_for_footpeg_before_tracking_shift():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.090,
        left_foot_angle=145.0,
    )

    assert detector._state == "IDLE"
def test_detector_becomes_ready_on_front_view_footpeg():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
    )

    assert detector._state == "READY"
def test_mixed_movement_does_not_emit_shift():
    detector = GearShiftDetector()

    detector.update(
        0.120,
        155.0,
    )

    detector.update(
        0.120,
        159.0,
    )
    detector.update(
        0.125,
        147.0,
    )
    detector.update(
        0.120,
        159.0,
    )

    result = detector.update(
        0.120,
        155.0,
    )

    assert result is None
def test_incomplete_up_path_does_not_emit_shift():
    detector = GearShiftDetector()

    detector.update(
        0.120,
        155.0,
    )

    # Only one UP frame - not enough to confirm exit.
    detector.update(
        0.120,
        159.0,
    )

    result = detector.update(
        0.120,
        155.0,
    )

    assert result is None

def test_invalid_path_does_not_emit_shift():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.040,
        left_foot_angle=132.0,
    )

    detector.update(0.040, 120.0)
    detector.update(0.055, 126.0)
    detector.update(0.040, 120.0)

    result = detector.update(
        left_foot_drop=0.040,
        left_foot_angle=132.0,
    )

    assert result is None

def test_footpeg_does_not_enter_zone_history():
    detector = GearShiftDetector()

    detector.update(0.040, 132.0)  # IDLE -> READY

    detector.update(0.059, 131.0)
    detector.update(0.058, 130.0)
    detector.update(0.061, 133.0)

    assert detector._zone_history == []


def test_movement_zone_detects_up():
    assert GearShiftDetector._movement_zone(
        0.120,
        161.0,
    ) == "UP"


def test_movement_zone_detects_down():
    assert GearShiftDetector._movement_zone(
        0.120,
        147.0,
    ) == "DOWN"


def test_movement_zone_detects_transition():
    assert GearShiftDetector._movement_zone(
        0.120,
        154.0,
    ) == "TRANSITION"


def test_movement_zone_is_invalid_without_angle():
    assert GearShiftDetector._movement_zone(
        0.120,
        None,
    ) is None

def test_footpeg_is_not_up():
    assert GearShiftDetector._movement_zone(
        0.120,
        155.0,
    ) == "TRANSITION"


def test_footpeg_is_not_down():
    assert GearShiftDetector._movement_zone(
        0.120,
        156.0,
    ) == "TRANSITION"
def test_front_view_shift_up_path():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
        left_foot_forward=0.015,
    )

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=159.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.130,
        left_foot_angle=161.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=160.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=166.0,
        left_foot_forward=0.04,
    )
    result = detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
        left_foot_forward=0.015,
    )

    assert result == "SHIFT_UP"

def test_front_view_shift_down_path():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
        left_foot_forward =0.015,
    )

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=149.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.130,
        left_foot_angle=147.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=148.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=142.0,
        left_foot_forward=0.04,
    )

    result = detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
        left_foot_forward=0.015,
    )

    assert result == "SHIFT_DOWN"

def test_front_view_footpeg_jitter_does_not_emit_shift():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
    )

    detector.update(
        left_foot_drop=0.118,
        left_foot_angle=154.0,
    )
    detector.update(
        left_foot_drop=0.123,
        left_foot_angle=156.0,
    )
    detector.update(
        left_foot_drop=0.119,
        left_foot_angle=153.0,
    )

    result = detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
    )

    assert result is None
def test_foot_moved_forward_is_false_on_footpeg():
    assert GearShiftDetector._is_foot_moved_forward(
        0.025
    ) is False


def test_foot_moved_forward_is_true_at_threshold():
    assert GearShiftDetector._is_foot_moved_forward(
        0.030
    ) is True


def test_foot_moved_forward_is_true_beyond_threshold():
    assert GearShiftDetector._is_foot_moved_forward(
        0.034
    ) is True

def test_angle_trend_is_rising():
    detector = GearShiftDetector()

    detector._angle_history = [
        154.0,
        156.0,
        158.0,
        160.0,
    ]

    assert detector._angle_trend() == "RISING"


def test_angle_trend_is_falling():
    detector = GearShiftDetector()

    detector._angle_history = [
        160.0,
        158.0,
        156.0,
        154.0,
    ]

    assert detector._angle_trend() == "FALLING"


def test_angle_trend_is_stable():
    detector = GearShiftDetector()

    detector._angle_history = [
        155.0,
        156.0,
        155.5,
        156.0,
    ]

    assert detector._angle_trend() == "STABLE"

def test_angle_history_keeps_last_four_angles():
    detector = GearShiftDetector()

    detector._update_angle_history(150.0)
    detector._update_angle_history(152.0)
    detector._update_angle_history(154.0)
    detector._update_angle_history(156.0)
    detector._update_angle_history(158.0)

    assert detector._angle_history == [
        152.0,
        154.0,
        156.0,
        158.0,
    ]
def test_angle_history_ignores_none():
    detector = GearShiftDetector()

    detector._update_angle_history(154.0)
    detector._update_angle_history(None)
    detector._update_angle_history(156.0)

    assert detector._angle_history == [
        154.0,
        156.0,
    ]

def test_update_builds_rising_angle_trend():
    detector = GearShiftDetector()

    detector.update(0.120, 154.0)
    detector.update(0.120, 156.0)
    detector.update(0.120, 158.0)
    detector.update(0.120, 160.0)

    assert detector._angle_history == [
        154.0,
        156.0,
        158.0,
        160.0,
    ]

    assert detector._angle_trend() == "RISING"

def test_update_builds_falling_angle_trend():
    detector = GearShiftDetector()

    detector.update(0.120, 160.0)
    detector.update(0.120, 158.0)
    detector.update(0.120, 156.0)
    detector.update(0.120, 154.0)

    assert detector._angle_history == [
        160.0,
        158.0,
        156.0,
        154.0,
    ]

    assert detector._angle_trend() == "FALLING"

def test_shift_candidate_does_not_start_without_forward_movement():
    detector = GearShiftDetector()

    # FOOTPEG / ready
    detector.update(
        0.120,
        155.0,
    )

    # Angle is moving upward,
    # but foot has not moved forward enough.
    detector.update(
        0.120,
        158.0,
        left_foot_forward=0.025,
    )
    detector.update(
        0.120,
        160.0,
        left_foot_forward=0.024,
    )
    detector.update(
        0.120,
        162.0,
        left_foot_forward=0.026,
    )

    assert detector._angle_trend() == "RISING"
    assert detector._zone_history == []

def test_forward_movement_with_rising_trend_builds_up_candidate():
    detector = GearShiftDetector()

    # FOOTPEG
    detector.update(
        0.120,
        155.0,
    )

    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.034,
    )
    detector.update(
        0.120,
        156.0,
        left_foot_forward=0.034,
    )
    detector.update(
        0.120,
        158.0,
        left_foot_forward=0.034,
    )
    detector.update(
        0.120,
        160.0,
        left_foot_forward=0.034,
    )

    assert detector._angle_trend() == "RISING"

def test_rising_trend_with_forward_movement_builds_up_history():
    detector = GearShiftDetector()

    # FOOTPEG
    detector.update(
        0.120,
        155.0,
        0.015,
    )

    # Forward movement starts, angle first dips slightly...
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.04,
    )

    # ...then rises through transition into UP.
    detector.update(
        0.120,
        156.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        158.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        160.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        162.0,
        left_foot_forward=0.04,
    )

    assert detector._angle_trend() == "RISING"
    assert detector._zone_history == ["UP"]

def test_falling_trend_with_forward_movement_builds_down_history():
    detector = GearShiftDetector()

    # FOOTPEG
    detector.update(
        0.120,
        155.0,
        0.015
    )

    detector.update(
        0.120,
        156.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        152.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        149.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        146.0,
        left_foot_forward=0.04,
    )

    assert detector._angle_trend() == "FALLING"
    assert detector._zone_history == ["DOWN"]

def test_rising_shift_emits_only_on_return_to_footpeg():
    detector = GearShiftDetector()

    # FOOTPEG
    detector.update(
        0.120,
        155.0,
        0.015   
    )

    # Forward + rising movement
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        156.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        158.0,
        left_foot_forward=0.04,
    )

    # While still away from footpeg, no event yet.
    result = detector.update(
        0.120,
        160.0,
        left_foot_forward=0.015,
    )
    result = detector.update(
        0.120,
        162.0,
        left_foot_forward=0.015,
    )

    assert result is None

    
    # Return to footpeg confirms the shift.
    result = detector.update(
        0.120,
        155.0,
        left_foot_forward=0.015,
    )

    assert result == "SHIFT_UP"

def test_falling_shift_emits_only_on_return_to_footpeg():
    detector = GearShiftDetector()

    # FOOTPEG
    detector.update(
        0.120,
        155.0,
        0.015
    )

    # Forward + falling movement
    detector.update(
        0.120,
        156.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.04,
    )
    detector.update(
        0.120,
        152.0,
        left_foot_forward=0.04,
    )

    # Still away from footpeg -> no event yet.
    result = detector.update(
        0.120,
        149.0,
        left_foot_forward=0.015,
    )
    result = detector.update(
        0.120,
        147.0,
        left_foot_forward=0.015,
    )

    assert result is None

    # Return to footpeg confirms the shift.
    result = detector.update(
        0.120,
        155.0,
        left_foot_forward=0.015,
    )

    assert result == "SHIFT_DOWN"

def test_forward_movement_stays_active_after_threshold_is_crossed():
    detector = GearShiftDetector()

    detector._update_forward_movement(0.025)
    assert detector._forward_movement_active is False

    detector._update_forward_movement(0.034)
    assert detector._forward_movement_active is True

    # Forward value may fall again during the actual shift.
    detector._update_forward_movement(0.018)
    assert detector._forward_movement_active is True

def test_forward_movement_resets_on_return_to_footpeg():
    detector = GearShiftDetector()

    detector._update_forward_movement(0.034)

    assert detector._forward_movement_active is True

    detector._reset_forward_movement()

    assert detector._forward_movement_active is False

def test_initial_down_zone_can_still_become_shift_up_when_angle_trend_rises():
    detector = GearShiftDetector()

    # FOOTPEG
    detector.update(
        0.120,
        155.0,
    )

    # Foot moves forward; first angle can dip.
    detector.update(
        0.120,
        142.0,
        left_foot_forward=0.035,
    )

    detector.update(
        0.120,
        145.0,
        left_foot_forward=0.020,
    )
    detector.update(
        0.120,
        151.0,
        left_foot_forward=0.018,
    )
    detector.update(
        0.120,
        158.0,
        left_foot_forward=0.016,
    )

    assert detector._angle_trend() == "RISING"

def test_negative_forward_movement_can_activate_shift_attempt():
    detector = GearShiftDetector()

    detector._update_forward_movement(-0.035)

    assert detector._forward_movement_active is True

def test_footpeg_forward_baseline_can_be_set():
    detector = GearShiftDetector()

    detector._set_forward_baseline(0.018)

    assert detector._forward_baseline == 0.018

    assert detector._forward_offset(-0.002) == pytest.approx(-0.020)

def test_forward_offset_is_none_without_baseline():
    detector = GearShiftDetector()

    assert detector._forward_offset(0.030) is None

def test_forward_movement_uses_offset_from_baseline():
    detector = GearShiftDetector()

    detector._set_forward_baseline(0.018)

    detector._update_forward_movement_from_baseline(0.038)

    assert detector._forward_movement_active is False

    detector._update_forward_movement_from_baseline(0.039)

    assert detector._forward_movement_active is True

def test_backward_movement_from_baseline_can_activate_shift_attempt():
    detector = GearShiftDetector()

    detector._set_forward_baseline(0.018)

    detector._update_forward_movement_from_baseline(-0.002)

    assert detector._forward_movement_active is False

    detector._update_forward_movement_from_baseline(-0.003)

    assert detector._forward_movement_active is True

def test_forward_baseline_is_learned_on_footpeg():
    detector = GearShiftDetector()

    detector._update_forward_baseline(
        left_foot_forward=0.018,
        on_footpeg=True,
    )

    assert detector._forward_baseline == pytest.approx(0.018)

def test_forward_baseline_is_not_updated_off_footpeg():
    detector = GearShiftDetector()

    detector._set_forward_baseline(0.018)

    detector._update_forward_baseline(
        left_foot_forward=0.040,
        on_footpeg=False,
    )

    assert detector._forward_baseline == pytest.approx(0.018)
def test_shift_attempt_resets_after_too_many_outside_frames():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_movement_active = True
    detector._outside_footpeg_frames = 100
    detector._zone_history = ["DOWN", "UP", "DOWN"]

    detector._reset_stale_shift_attempt()

    assert detector._forward_movement_active is False
    assert detector._outside_footpeg_frames == 0
    assert detector._zone_history == []
def test_shift_direction_can_change_before_confirmation():
    detector = GearShiftDetector()

    detector._pending_zones = ["UP"]

    detector._add_shift_candidate("DOWN")

    assert detector._pending_zones == ["UP", "DOWN"]
def test_update_does_not_confirm_direction_from_single_candidate():
    detector = GearShiftDetector()

    # Establish footpeg / baseline.
    detector.update(
        0.110,
        155.0,
        left_foot_forward=0.015,
    )

    detector.update(
        0.090,
        145.0,
        left_foot_forward=0.040,
    )
    detector.update(
        0.085,
        142.0,
        left_foot_forward=0.040,
    )

    # Angle oscillation eventually produces only
    # one RISING candidate.
    detector.update(
        0.090,
        151.0,
        left_foot_forward=0.040,
    )
    detector.update(
        0.095,
        158.0,
        left_foot_forward=0.040,
    )

    assert detector._zone_history == []
    assert detector._pending_zones == ["UP"]
def test_update_uses_add_shift_candidate(monkeypatch):
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_movement_active = True

    candidates = []

    monkeypatch.setattr(
        detector,
        "_add_shift_candidate",
        lambda candidate: candidates.append(candidate),
    )

    monkeypatch.setattr(
        detector,
        "_angle_trend",
        lambda: "RISING",
    )

    detector.update(
        0.070,
        160.0,
        left_foot_forward=0.040,
    )

    assert candidates == ["UP"]

def test_single_pending_candidate_does_not_lock_direction():
    detector = GearShiftDetector()

    detector._pending_zones = ["UP"]

    detector._add_shift_candidate("DOWN")

    assert detector._pending_zones == ["UP", "DOWN"]

def test_repeated_candidate_confirms_shift_direction():
    detector = GearShiftDetector()

    detector._add_shift_candidate("UP")
    detector._add_shift_candidate("UP")

    assert detector._zone_history == ["UP"]
def test_confirmed_shift_direction_cannot_be_reversed():
    detector = GearShiftDetector()

    detector._add_shift_candidate("UP")
    detector._add_shift_candidate("UP")

    detector._add_shift_candidate("DOWN")
    detector._add_shift_candidate("DOWN")

    assert detector._zone_history == ["UP"]
def test_real_shift_down_is_not_confused_by_angle_oscillation():
    detector = GearShiftDetector()

    events = []

    # Neutral footpeg position - establishes READY and baseline.
    result = detector.update(
        0.1049,
        152.7,
        left_foot_forward=0.0229,
    )
    if result is not None:
        events.append(result)

    # Real SHIFT_DOWN-like movement from live measurements.
    samples = [
        (0.0797, 173.3, -0.0141),
        (0.0589, 179.9, -0.0022),
        (0.0739, 178.7, -0.0025),
        (0.0690, 170.3, -0.0033),
        (-0.0272, 154.8, 0.0026),
        (0.0077, 137.9, 0.0009),
        (-0.0193, 168.0, -0.0028),
        (0.1187, 175.5, -0.0133),
    ]

    for drop, angle, forward in samples:
        result = detector.update(
            drop,
            angle,
            left_foot_forward=forward,
        )

        print(
            "TEST:",
            "angle=", angle,
            "zone=", detector._direction_zone,
            "frames=", detector._direction_zone_frames,
            "history=", detector._zone_history,
        )

        if result is not None:
            events.append(result)

    # Return to neutral footpeg position.
    result = detector.update(
        0.1049,
        154.0,
        left_foot_forward=0.0229,
    )
    if result is not None:
        events.append(result)

    assert events == ["SHIFT_DOWN"]


def test_forward_drift_on_stable_footpeg_does_not_start_shift_attempt():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.020

    for forward in [0.040, 0.041, 0.039, 0.040]:
        result = detector.update(
            0.120,
            155.0,
            left_foot_forward=forward,
        )

        assert result is None

    assert detector._forward_movement_active is True
    assert detector._angle_trend() == "STABLE"
    assert detector._outside_footpeg_frames == 0
    assert detector._zone_history == []
    assert detector._pending_zones == []

def test_forward_movement_outside_footpeg_starts_shift_attempt():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.020

    result = detector.update(
        0.160,
        147.0,
        left_foot_forward=0.040,
    )

    assert result is None
    assert detector._forward_movement_active is False

    result = detector.update(
        0.160,
        147.0,
        left_foot_forward=0.041,
    )

    assert result is None
    assert detector._forward_movement_active is True
def test_forward_movement_uses_difference_from_baseline():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.030

    detector._update_forward_movement_from_baseline(
        0.041
    )

    assert detector._forward_movement_active is False   
def test_forward_baseline_does_not_chase_foot_movement():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.021

    detector._update_forward_baseline(
        left_foot_forward=0.031,
        on_footpeg=True,
    )

    assert detector._forward_baseline == pytest.approx(0.021)

def test_gear_detector_ignores_shift_during_initial_calibration():
    detector = GearShiftDetector()

    result = detector.update(
        left_foot_drop=0.120,
        left_foot_angle=160.0,
        left_foot_forward=0.040,
        elapsed_seconds=3.0,
    )

    assert result is None
def test_wrong_first_candidate_can_be_overruled_before_confirmation():
    detector = GearShiftDetector()

    detector._add_shift_candidate("UP")
    detector._add_shift_candidate("DOWN")
    detector._add_shift_candidate("DOWN")
    assert detector._zone_history == ["DOWN"]

def test_current_live_footpeg_position_is_recognized():
    assert GearShiftDetector._is_footpeg_position(
        0.058,
        177.0,
    ) is True

def test_confirmed_direction_can_be_overruled_by_stronger_opposite_evidence():
    detector = GearShiftDetector()

    detector._add_shift_candidate("DOWN")
    detector._add_shift_candidate("DOWN")

    detector._add_shift_candidate("UP")
    detector._add_shift_candidate("UP")
    detector._add_shift_candidate("UP")

    assert detector._zone_history == ["UP"]

def test_shift_attempt_emits_first_shift_up():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
        left_foot_forward=0.015,
    )

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=159.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.130,
        left_foot_angle=161.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=160.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=166.0,
        left_foot_forward=0.04,
    )

    first_event = detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
        left_foot_forward=0.015,
    )

    assert first_event == "SHIFT_UP"
    
    # Foot moves again immediately, without a stable
# re-arming period on the footpeg.
    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=159.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.130,
        left_foot_angle=161.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=160.0,
        left_foot_forward=0.04,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=166.0,
        left_foot_forward=0.04,
    )

    second_event = detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
        left_foot_forward=0.015,
    )
    
    assert second_event is None
def test_confirmed_down_is_not_lost_at_attempt_timeout():
    detector = GearShiftDetector()
    
    detector._state = "READY"
    detector._forward_movement_active = True
    detector._zone_history = ["DOWN"]
    detector._outside_footpeg_frames = (
        detector.MAX_SHIFT_ATTEMPT_FRAMES - 1
    )

    result = detector.update(
        left_foot_drop=0.080,
        left_foot_angle=148.0,
        left_foot_forward=0.040,
    )

    assert result == "SHIFT_DOWN"

def test_back_movement_is_detected_when_foot_returns_to_baseline():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.015

    assert detector._is_foot_moved_back(
        left_foot_forward=0.015,
    ) is True

def test_back_movement_becomes_active_after_forward_movement_and_return():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.015
    detector._forward_movement_active = True

    detector._update_back_movement(
        left_foot_forward=0.015,
    )

    assert detector._back_movement_active is True

def test_back_movement_is_reset_with_shift_attempt():
    detector = GearShiftDetector()

    detector._back_movement_active = True

    detector._reset_stale_shift_attempt()

    assert detector._back_movement_active is False

def test_rearm_completes_after_back_movement():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._shift_rearm_pending = True
    detector._forward_baseline = 0.015

    detector._forward_movement_active = True
    detector._back_movement_active = True
    for _ in range(3):
        detector.update(
            left_foot_drop=0.120,
            left_foot_angle=155.0,
            left_foot_forward=0.015,
        )
    result = detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
        left_foot_forward=0.015,
    )

    assert result is None
    assert detector._shift_rearm_pending is False

def test_update_detects_back_movement_after_forward_attempt():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.015
    detector._forward_movement_active = True

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
        left_foot_forward=0.015,
    )

    assert detector._back_movement_active is True

def test_new_forward_movement_clears_old_back_movement():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.015
    detector._back_movement_active = True

    detector._update_forward_movement_from_baseline(
        left_foot_forward=0.040,
    )

    assert detector._forward_movement_active is False
    assert detector._back_movement_active is True

    detector._update_forward_movement_from_baseline(
        left_foot_forward=0.041,
    )

    assert detector._forward_movement_active is True
    assert detector._back_movement_active is False

def test_completed_rearm_resets_movement_state():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._shift_rearm_pending = True
    detector._forward_baseline = 0.015

    detector._forward_movement_active = True
    detector._back_movement_active = True
    for _ in range(3):
        detector.update(
            left_foot_drop=0.120,
            left_foot_angle=155.0,
            left_foot_forward=0.015,
        )

    assert detector._shift_rearm_pending is False
    assert detector._forward_movement_active is False
    assert detector._back_movement_active is False

def test_confirmed_direction_is_not_overridden_after_back_movement():
    detector = GearShiftDetector()

    detector._zone_history = ["DOWN"]
    detector._back_movement_active = True

    detector._add_shift_candidate("UP")
    detector._add_shift_candidate("UP")
    detector._add_shift_candidate("UP")

    assert detector._zone_history == ["DOWN"]

def test_rearm_uses_return_to_baseline_not_absolute_forward_position():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._shift_rearm_pending = True

    detector._forward_baseline = 0.050
    detector._forward_movement_active = True
    detector._back_movement_active = True
    for _ in range(3):
        
        detector.update(
            left_foot_drop=0.120,
            left_foot_angle=155.0,
            left_foot_forward=0.050,
        )

    assert detector._shift_rearm_pending is False

def test_angle_trend_inside_transition_does_not_confirm_shift():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.015

    # Foot moves away from baseline, but angle remains
    # inside the TRANSITION region.
    detector.update(
        0.120,
        153.0,
        left_foot_forward=0.040,
    )
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.040,
    )
    detector.update(
        0.120,
        155.0,
        left_foot_forward=0.040,
    )
    detector.update(
        0.120,
        156.0,
        left_foot_forward=0.040,
    )

    assert detector._zone_history == []

def test_live_baseline_is_not_learned_from_first_frame():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
        left_foot_forward=0.010,
        elapsed_seconds=5.1,
    )

    assert detector._forward_baseline is None

def test_live_baseline_is_learned_after_five_frames():
    detector = GearShiftDetector()

    values = [
        0.010,
        0.011,
        0.009,
        0.010,
        0.010,
    ]

    for value in values:
        detector.update(
            left_foot_drop=0.120,
            left_foot_angle=155.0,
            left_foot_forward=value,
            elapsed_seconds=5.1,
        )

    assert detector._forward_baseline == pytest.approx(
        0.010
    )   
def test_forward_down_back_emits_shift_down():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.035

    # Forward movement starts the attempt.
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.010,
    )

    # Clear DOWN phase.
    detector.update(
        0.120,
        149.0,
        left_foot_forward=0.010,
    )
    detector.update(
        0.120,
        147.0,
        left_foot_forward=0.010,
    )
    detector.update(
        0.120,
        148.0,
        left_foot_forward=0.010,
    )

    # Foot returns to baseline.
    result = detector.update(
        0.120,
        155.0,
        left_foot_forward=0.035,
    )

    assert result == "SHIFT_DOWN"

def test_update_counts_three_down_zones_during_forward_movement():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.035
    detector._forward_movement_active = True

    detector.update(
        0.120,
        149.0,
        left_foot_forward=0.010,
    )
    detector.update(
        0.120,
        147.0,
        left_foot_forward=0.010,
    )
    detector.update(
        0.120,
        148.0,
        left_foot_forward=0.010,
    )

    assert detector._direction_zone == "DOWN"
    assert detector._direction_zone_frames == 3

def test_direction_zone_counts_consecutive_down_frames():
    detector = GearShiftDetector()

    detector._update_direction_zone("DOWN")
    detector._update_direction_zone("DOWN")
    detector._update_direction_zone("DOWN")

    assert detector._direction_zone == "DOWN"
    assert detector._direction_zone_frames == 3

def test_update_counts_down_zones_during_forward_movement():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.035

    # First strong movement sample.
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.010,
    )

    detector.update(
        0.120,
        149.0,
        left_foot_forward=0.010,
    )
    detector.update(
        0.120,
        147.0,
        left_foot_forward=0.010,
    )
    detector.update(
        0.120,
        148.0,
        left_foot_forward=0.010,
    )

    assert detector._direction_zone == "DOWN"
    assert detector._direction_zone_frames == 3

def test_three_initial_up_zones_do_not_confirm_up_during_real_down():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.0229

    # First strong movement sample.
    detector.update(
        0.120,
        154.0,
        left_foot_forward=-0.0141,
    )

    detector.update(
        0.0797,
        173.3,
        left_foot_forward=-0.0141,
    )
    detector.update(
        0.0589,
        179.9,
        left_foot_forward=-0.0022,
    )
    detector.update(
        0.0739,
        178.7,
        left_foot_forward=-0.0025,
    )

    assert detector._direction_zone == "UP"
    assert detector._direction_zone_frames == 3
    assert detector._zone_history == []

def test_forward_up_back_emits_shift_up():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.035

    # Forward movement starts the attempt.
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.010,
    )

    # Clear UP phase.
    detector.update(
        0.120,
        161.0,
        left_foot_forward=0.010,
    )
    detector.update(
        0.120,
        163.0,
        left_foot_forward=0.010,
    )
    detector.update(
        0.120,
        165.0,
        left_foot_forward=0.010,
    )

    # Foot returns to baseline.
    result = detector.update(
        0.120,
        155.0,
        left_foot_forward=0.035,
    )

    assert result == "SHIFT_UP"
def test_real_shift_up_is_not_classified_as_down_from_down_zones():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.033

    # Real SHIFT_UP sample:
    # forward movement followed by several DOWN geometry zones.
    detector.update(
        0.1064,
        148.4,
        left_foot_forward=0.0524,
    )
    detector.update(
        0.1017,
        146.1,
        left_foot_forward=0.0553,
        left_heel_y=0.7296,
    )
    detector.update(
        0.1001,
        145.4,
        left_foot_forward=0.0559,
        left_heel_y=0.7327,
    )
    detector.update(
        0.1004,
        145.1,
        left_foot_forward=0.0563,
        left_heel_y=0.7377,
    )

    # Foot starts returning.
    result = detector.update(
        0.1016,
        148.9,
        left_foot_forward=0.0478,
        left_heel_y=0.7409,
    )

    assert result == "SHIFT_UP"

def test_heel_end_trend_detects_upward_movement():
    heel_y = [
        0.6869,
        0.6358,
        0.5839,
    ]

    assert GearShiftDetector._heel_end_trend(
        heel_y
    ) == "UP"
def test_heel_end_trend_detects_downward_movement():
    heel_y = [
        0.7014,
        0.7046,
        0.7176,
    ]

    assert GearShiftDetector._heel_end_trend(
        heel_y
    ) == "DOWN"

def test_heel_end_trend_ignores_small_jitter():
    heel_y = [
        0.7000,
        0.7004,
        0.7008,
    ]

    assert GearShiftDetector._heel_end_trend(
        heel_y
    ) == "STABLE"

def test_heel_up_at_end_means_shift_down():
    assert GearShiftDetector._shift_from_heel_trend(
        "UP"
    ) == "SHIFT_DOWN"

def test_heel_down_at_end_means_shift_up():
    assert GearShiftDetector._shift_from_heel_trend(
        "DOWN"
    ) == "SHIFT_UP"

def test_stable_heel_trend_emits_no_shift():
    assert GearShiftDetector._shift_from_heel_trend(
        "STABLE"
    ) is None

def test_update_heel_history_keeps_recent_values():
    detector = GearShiftDetector()

    detector._update_heel_history(0.70)
    detector._update_heel_history(0.69)
    detector._update_heel_history(0.68)

    assert detector._heel_y_history == [
        0.70,
        0.69,
        0.68,
    ]

def test_update_heel_history_ignores_none():
    detector = GearShiftDetector()

    detector._update_heel_history(0.70)
    detector._update_heel_history(None)
    detector._update_heel_history(0.68)

    assert detector._heel_y_history == [
        0.70,
        0.68,
    ]

def test_update_heel_history_keeps_only_last_ten_values():
    detector = GearShiftDetector()

    for i in range(12):
        detector._update_heel_history(
            0.60 + i * 0.01
        )

    assert len(detector._heel_y_history) == 10

    assert detector._heel_y_history[0] == 0.62
    assert detector._heel_y_history[-1] == 0.71

def test_clear_heel_history_removes_old_values():
    detector = GearShiftDetector()

    detector._update_heel_history(0.70)
    detector._update_heel_history(0.69)
    detector._update_heel_history(0.68)

    detector._clear_heel_history()

    assert detector._heel_y_history == []

def test_heel_history_is_not_updated_without_forward_movement():
        detector = GearShiftDetector()

        detector._forward_movement_active = False

        detector._update_shift_heel_history(
            0.70
        )

        assert detector._heel_y_history == []

def test_heel_history_is_updated_during_forward_movement():
    detector = GearShiftDetector()

    detector._forward_movement_active = True

    detector._update_shift_heel_history(
        0.70
    )

    assert detector._heel_y_history == [
        0.70
    ]

def test_heel_history_ignores_none_during_forward_movement():
    detector = GearShiftDetector()

    detector._forward_movement_active = True

    detector._update_shift_heel_history(0.70)
    detector._update_shift_heel_history(None)
    detector._update_shift_heel_history(0.68)

    assert detector._heel_y_history == [
        0.70,
        0.68,
    ]

def test_confirmed_shift_attempt_keeps_first_heel_sample():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.035

    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.010,
        left_heel_y=0.700,
    )

    assert detector._forward_movement_active is False

    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.009,
        left_heel_y=0.680,
    )

    assert detector._forward_movement_active is True
    assert detector._heel_y_history == [
        0.700,
        0.680,
    ]
def test_update_does_not_collect_heel_y_without_forward_movement():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.035

    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.034,
        left_heel_y=0.700,
    )

    assert detector._heel_y_history == []

def test_update_collects_multiple_heel_y_values_during_shift_attempt():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.035

    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.010,
        left_heel_y=0.700,
    )

    detector.update(
        0.120,
        149.0,
        left_foot_forward=0.010,
        left_heel_y=0.680,
    )

    detector.update(
        0.120,
        147.0,
        left_foot_forward=0.010,
        left_heel_y=0.660,
    )

    assert detector._heel_y_history == [
        0.700,
        0.680,
        0.660,
    ]

def test_new_forward_movement_starts_with_fresh_heel_history():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.035

    # Old data from a previous attempt.
    detector._heel_y_history = [
        0.750,
        0.740,
    ]

    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.010,
        left_heel_y=0.700,
    )

    # First movement sample is not enough
    # to confirm a new attempt.
    assert detector._heel_y_history == [
        0.750,
        0.740,
    ]

    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.009,
        left_heel_y=0.680,
    )

    assert detector._heel_y_history == [
        0.700,
        0.680,
    ]

def test_active_forward_movement_keeps_existing_heel_history():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.035
    detector._forward_movement_active = True
    detector._heel_y_history = [
        0.700,
        0.680,
    ]

    detector.update(
        0.120,
        149.0,
        left_foot_forward=0.010,
        left_heel_y=0.660,
    )

    assert detector._heel_y_history == [
        0.700,
        0.680,
        0.660,
    ]

def test_shift_attempt_heel_history_produces_up_end_trend():
    detector = GearShiftDetector()

    detector._heel_y_history = [
        0.6869,
        0.6358,
        0.5839,
    ]

    assert detector._heel_end_trend(
        detector._heel_y_history
    ) == "UP"
def test_real_down_heel_history_maps_to_shift_down():
    detector = GearShiftDetector()

    detector._heel_y_history = [
        0.6869,
        0.6358,
        0.5839,
    ]

    heel_trend = detector._heel_end_trend(
        detector._heel_y_history
    )

    shift = detector._shift_from_heel_trend(
        heel_trend
    )

    assert shift == "SHIFT_DOWN"

def test_update_uses_heel_end_trend_for_real_shift_down():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.035

    # Shift attempt starts.
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.010,
        left_heel_y=0.6869,
    )

    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.010,
        left_heel_y=0.6358,
    )

    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.010,
        left_heel_y=0.5839,
    )

    # Foot returns.
    result = detector.update(
        0.120,
        154.0,
        left_foot_forward=0.035,
        left_heel_y=0.5839,
    )

    assert result == "SHIFT_DOWN"
def test_heel_end_trend_uses_end_of_motion():
    heel_y = [
        0.7430,
        0.7437,
        0.7296,
        0.7327,
        0.7377,
        0.7387,
        0.7409,
    ]

    assert GearShiftDetector._heel_end_trend(
        heel_y
    ) == "DOWN"

def test_real_shift_up_does_not_emit_down_too_early():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.0103

    detector.update(
        0.1008,
        147.8,
        left_foot_forward=0.0314,
        left_heel_y=0.6478,
    )

    detector.update(
        0.0912,
        149.8,
        left_foot_forward=0.0272,
        left_heel_y=0.6489,
    )

    detector.update(
        0.0888,
        146.2,
        left_foot_forward=0.0334,
        left_heel_y=0.6502,
    )

    result = detector.update(
        0.1245,
        152.5,
        left_foot_forward=0.0288,
        left_heel_y=0.6335,
    )

    assert result is None

def test_real_positive_forward_sequence_starts_shift_attempt():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.0103

    detector._update_forward_movement_from_baseline(
        0.0314
    )
    detector._update_forward_movement_from_baseline(
        0.0272
    )
    detector._update_forward_movement_from_baseline(
        0.0334
    )

    assert detector._forward_movement_active is True

def test_heel_history_continues_during_back_movement():
    detector = GearShiftDetector()

    detector._forward_movement_active = False
    detector._back_movement_active = True

    detector._update_shift_heel_history(
        0.6380
    )

    assert detector._heel_y_history == [
        0.6380
    ]
def test_real_shift_up_final_heel_window_trends_down():
    heel_y = [
        0.6489,
        0.6502,
        0.6335,
        0.6380,
        0.6678,
    ]

    assert GearShiftDetector._heel_end_trend(
        heel_y
    ) == "DOWN"

def test_heel_end_trend_does_not_confirm_on_single_reversal_step():
    heel_y = [
        0.6502,
        0.6335,
        0.6380,
    ]

    assert GearShiftDetector._heel_end_trend(
        heel_y
    ) == "STABLE"
def test_heel_end_trend_keeps_confirmed_direction_when_last_sample_is_flat():
    heel_y = [
        0.6869,
        0.6358,
        0.5839,
        0.5839,
    ]

    assert GearShiftDetector._heel_end_trend(
        heel_y
    ) == "UP"

def test_heel_end_trend_uses_two_confirmed_final_steps():
    heel_y = [
        0.6489,
        0.6502,
        0.6335,
        0.6380,
        0.6678,
    ]

    assert GearShiftDetector._heel_end_trend(
        heel_y
    ) == "DOWN"

def test_shift_rearms_after_foot_returns_to_footpeg():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._shift_rearm_pending = True
    detector._forward_movement_active = False
    for _ in range(3):
        result = detector.update(
            0.120,
            155.0,
            left_foot_forward=0.0315,
            left_heel_y=0.7200,
        )
    assert detector._is_foot_moved_forward(
            0.0315
        ) is True
    assert result is None
    assert detector._shift_rearm_pending is False
def test_real_shift_up_forward_sequence_starts_attempt():
    detector = GearShiftDetector()
    detector._forward_baseline = 0.0271457

    detector._update_forward_movement_from_baseline(
        0.0355449
    )
    detector._update_forward_movement_from_baseline(
        0.0288923
    )
    detector._update_forward_movement_from_baseline(
        0.0179184
    )

    assert detector._forward_movement_active is True

def test_real_shift_up_long_forward_sequence_starts_attempt():
    detector = GearShiftDetector()
    detector._forward_baseline = 0.0271457

    samples = [
        0.0355449,
        0.0288923,
        0.0268735,
        0.0246129,
        0.0241584,
        0.0234572,
        0.0231537,
        0.0225031,
        0.0179184,
    ]

    for forward in samples:
        detector._update_forward_movement_from_baseline(
            forward
        )

    assert detector._forward_movement_active is True
def test_shift_does_not_rearm_on_single_footpeg_frame():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._shift_rearm_pending = True
    detector._forward_movement_active = True
    detector._back_movement_active = True

    detector.update(
        0.1052,
        152.5,
        left_foot_forward=0.0362,
        left_heel_y=0.6963,
    )

    assert detector._shift_rearm_pending is True
def test_shift_rearms_after_three_footpeg_frames():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._shift_rearm_pending = True
    detector._forward_movement_active = True
    detector._back_movement_active = True

    for _ in range(3):
        result = detector.update(
            0.1052,
            152.5,
            left_foot_forward=0.0362,
            left_heel_y=0.6963,
        )

        assert result is None

    assert detector._shift_rearm_pending is False
    assert detector._forward_movement_active is False
    assert detector._back_movement_active is False
def test_stale_forward_offsets_do_not_start_new_shift_attempt():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.0336

    # Old movement on one side of baseline.
    detector._forward_offset_history = [
        0.0083,
        0.0090,
        0.0101,
    ]

    # Foot has settled back on the footpeg.
    for _ in range(3):
        detector.update(
            0.120,
            155.0,
            left_foot_forward=0.0336,
            left_heel_y=0.705,
        )

    # Much later movement to the other side must not
    # combine with the old samples.
    detector.update(
        0.120,
        155.0,
        left_foot_forward=0.0230,
        left_heel_y=0.705,
    )

    assert detector._forward_movement_active is False
def test_real_shift_up_forward_sequence_starts_attempt_from_live_log():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.03358926773071289

    samples = [
        0.02847588062286377,
        0.02580583095550537,
        0.024242818355560303,
        0.02369558811187744,
    ]

    for forward in samples:
        detector.update(
            0.120,
            155.0,
            left_foot_forward=forward,
            left_heel_y=0.705,
        )

    assert detector._forward_movement_active is True

def test_one_sided_forward_offsets_do_not_start_attempt_on_footpeg():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.025184369087219237

    detector.update(
        0.11752963066101074,
        153.99234063162567,
        left_foot_forward=0.03983575105667114,
        left_heel_y=0.7230,
    )

    print(
        "TEST STATE 1:",
        detector._forward_movement_active,
        detector._forward_offset_history,
    )

    detector.update(
        0.11550647020339966,
        152.61576507649488,
        left_foot_forward=0.04246330261230469,
        left_heel_y=0.7225,
    )

    print(
        "TEST STATE 2:",
        detector._forward_movement_active,
        detector._forward_offset_history,
    )

    assert detector._forward_movement_active is False
def test_live_pre_shift_footpeg_sequence_does_not_start_attempt():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.025184369087219237

    detector._forward_offset_history = [
        0.007910871505737306,
        0.007852160930633546,
    ]

    detector.update(
        0.11752963066101074,
        153.99234063162567,
        left_foot_forward=0.03983575105667114,
        left_heel_y=0.7230,
    )

    assert detector._forward_movement_active is False

    detector.update(
        0.11550647020339966,
        152.61576507649488,
        left_foot_forward=0.04246330261230469,
        left_heel_y=0.7225,
    )

    assert detector._forward_movement_active is False
def test_one_sided_offsets_wait_until_foot_leaves_footpeg_stay():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.025184369087219237

    detector._forward_offset_history = [
        0.007910871505737306,
        0.007852160930633546,
    ]

    # Still on footpeg-stay geometry.
    result = detector.update(
        0.11752963066101074,
        153.99234063162567,
        left_foot_forward=0.03983575105667114,
        left_heel_y=0.7230,
    )

    assert result is None
    assert detector._forward_movement_active is False

    result = detector.update(
        0.11550647020339966,
        152.61576507649488,
        left_foot_forward=0.04246330261230469,
        left_heel_y=0.7225,
    )

    assert result is None
    assert detector._forward_movement_active is False
def test_live_sequence_before_first_false_shift_reproduces_forward_activation():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.025184369087219237

    samples = [
        # drop, angle, forward, heel_y
        (0.11898112297058105, 157.77335344732091, 0.032104551792144775, 0.7163),
        (0.1212470531463623, 157.57637186969785, 0.03309524059295654, 0.7207),
        (0.12224197387695312, 157.5476909005396, 0.03303653001785278, 0.7208),
        (0.11752963066101074, 153.99234063162567, 0.03983575105667114, 0.7230),
        (0.11550647020339966, 152.61576507649488, 0.04246330261230469, 0.7225),
    ]

    for drop, angle, forward, heel_y in samples:
        detector.update(
            drop,
            angle,
            left_foot_forward=forward,
            left_heel_y=heel_y,
        )

    assert detector._forward_movement_active is False
def test_live_sequence_builds_baseline_before_false_forward_activation():
    detector = GearShiftDetector()

    samples = [
        # drop, angle, forward, heel_y
        (0.12265884876251221, 158.0691896304767, 0.035069942474365234, 0.7067),
        (0.12761628627777100, 160.02161614544076, 0.03344923257827759, 0.7191),
        (0.12357544898986816, 159.4384919865464, 0.03160583972930908, 0.7166),
        (0.12124508619308472, 159.3488361916606, 0.029671847820281982, 0.7152),
        (0.11968600749969482, 159.36785457527375, 0.02931499481201172, 0.7135),
        (0.12177491188049316, 158.75931156280308, 0.031088650226593018, 0.7159),
        (0.11898112297058105, 157.77335344732091, 0.032104551792144775, 0.7163),
        (0.12124705314636230, 157.57637186969785, 0.03309524059295654, 0.7207),
        (0.12224197387695312, 157.5476909005396, 0.03303653001785278, 0.7208),
        (0.11752963066101074, 153.99234063162567, 0.03983575105667114, 0.7230),
        (0.11550647020339966, 152.61576507649488, 0.04246330261230469, 0.7225),
    ]

    for drop, angle, forward, heel_y in samples:
        detector.update(
            drop,
            angle,
            left_foot_forward=forward,
            left_heel_y=heel_y,
        )

    assert detector._forward_movement_active is False
def test_single_forward_spike_does_not_start_shift_attempt():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.03407981395721436

    detector._update_forward_movement_from_baseline(
        0.0577734112739563
    )

    assert detector._forward_movement_active is False
def test_shift_attempt_does_not_immediately_count_as_back_movement():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.03358926773071289

    detector.update(
        0.120,
        155.0,
        left_foot_forward=0.024242818355560303,
        left_heel_y=0.705,
    )

    detector.update(
        0.120,
        155.0,
        left_foot_forward=0.02369558811187744,
        left_heel_y=0.704,
    )

    assert detector._forward_movement_active is True


def test_settled_baseline_clears_old_forward_offsets():
    detector = GearShiftDetector()
    detector._forward_baseline = 0.0336

    detector._forward_offset_history = [
        0.0083,
        0.0090,
        0.0101,
    ]

    detector._update_forward_movement_from_baseline(
        0.0336
    )
    detector._update_forward_movement_from_baseline(
        0.0336
    )
    detector._update_forward_movement_from_baseline(
        0.0336
    )

    assert detector._forward_offset_history == []

def test_live_positive_shift_sequence_starts_attempt():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.015255022048950195

    samples = [
        0.025336146354675293,
        0.029669225215911865,
        0.029373466968536377,
        0.029087424278259277,
        0.029112577438354492,
    ]

    for forward in samples:
        detector._update_forward_movement_from_baseline(
            forward
        )
    print(
        "HISTORY:",
        detector._forward_offset_history,
    )
    print(
        "ACTIVE:",
        detector._forward_movement_active,
    )
    assert detector._forward_movement_active is True

def test_rearm_releases_after_three_stable_footpeg_frames():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._shift_rearm_pending = True
    detector._forward_movement_active = True
    detector._back_movement_active = True

    for _ in range(3):
        detector.update(
            0.120,
            155.0,
            left_foot_forward=0.024,
            left_heel_y=0.700,
        )

    assert detector._shift_rearm_pending is False
def test_static_foot_before_real_shift_does_not_emit_shift_up():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.04155937433242798

    samples = [
        (0.09269791841506958, 155.9005, 0.0122032, 0.6207),
        (0.09330868721008301, 155.2652, 0.0307264, 0.6891),
        (0.10287582874298096, 159.6000, 0.0291452, 0.7148),
    ]

    events = []

    for drop, angle, forward, heel_y in samples:
        event = detector.update(
            drop,
            angle,
            left_foot_forward=forward,
            left_heel_y=heel_y,
        )
        print(
            "FRAME:",
            "forward_value=", forward,
            "offset=", detector._forward_offset(forward),
            "forward_active=", detector._forward_movement_active,
            "back_active=", detector._back_movement_active,
            "heel=", detector._heel_y_history,
            "event=", event,
        )
        if event is not None:
            events.append(event)
    print("EVENTS:", events)
    print(
        "FORWARD:",
        detector._forward_movement_active,
    )
    print(
        "BACK:",
        detector._back_movement_active,
    )
    print(
        "HEEL:",
        detector._heel_y_history,
    )
    assert "SHIFT_UP" not in events
def test_newly_confirmed_forward_movement_is_not_back_movement():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.04155937433242798

    detector.update(
        0.09269791841506958,
        155.9005,
        left_foot_forward=0.0122032,
        left_heel_y=0.6207,
    )

    detector.update(
        0.09330868721008301,
        155.2652,
        left_foot_forward=0.0307264,
        left_heel_y=0.6891,
    )

    assert detector._forward_movement_active is True
    assert detector._back_movement_active is False
def test_back_movement_requires_motion_toward_baseline():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.04155937433242798
    detector._forward_movement_active = True

    detector._forward_offset_history = [
        -0.010832974332427976,
        -0.012414174332427978,
    ]

    detector._update_back_movement(
        0.0291452
    )

    assert detector._back_movement_active is False
def test_heel_visibility_history_starts_empty():
    detector = GearShiftDetector()

    assert detector._heel_visibility_history == []

def test_heel_visibility_history_keeps_last_ten_samples():
    detector = GearShiftDetector()

    for visibility in range(12):
        detector._update_heel_visibility_history(
            visibility
        )

    assert detector._heel_visibility_history == list(
        range(2, 12)
    )

def test_shift_heel_history_also_records_visibility():
    detector = GearShiftDetector()

    detector._forward_movement_active = True

    detector._update_shift_heel_history(
        heel_y=0.700,
        heel_visibility=0.82,
    )

    assert detector._heel_y_history == [0.700]
    assert detector._heel_visibility_history == [0.82]

def test_clear_heel_history_also_clears_visibility_history():
    detector = GearShiftDetector()

    detector._heel_y_history = [
        0.70,
        0.71,
    ]
    detector._heel_visibility_history = [
        0.82,
        0.79,
    ]

    detector._clear_heel_history()

    assert detector._heel_y_history == []
    assert detector._heel_visibility_history == []

def test_live_forward_baseline_is_not_set_from_unstable_samples():
    detector = GearShiftDetector()

    samples = [
        0.02710205316543579,
        0.016630470752716064,
        0.003628671169281006,
        0.002749025821685791,
        0.03849148750305176,
    ]

    for sample in samples:
        detector.update(
            0.120,
            155.0,
            left_foot_forward=sample,
            elapsed_seconds=6.0,
        )

    assert detector._forward_baseline is None

def test_rearm_clears_forward_offset_history():
    detector = GearShiftDetector()

    detector._shift_rearm_pending = True
    detector._forward_movement_active = True
    detector._forward_baseline = 0.035
    detector._forward_offset_history = [
        -0.024,
        -0.023,
        -0.020,
    ]

    for _ in range(5):
        detector.update(
            0.120,
            155.0,
            left_foot_forward=0.035,
        )

    assert detector._shift_rearm_pending is False
    assert all(
        abs(offset) < 0.002
        for offset in detector._forward_offset_history
    )
def test_rearm_itself_clears_forward_offset_history():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._shift_rearm_pending = True
    detector._forward_movement_active = True
    detector._forward_baseline = 0.035
    detector._forward_offset_history = [
        -0.024,
        -0.023,
        -0.020,
    ]

    for forward in [
        0.038,
        0.039,
        0.038,
    ]:
        detector.update(
            0.120,
            155.0,
            left_foot_forward=forward,
        )

    assert detector._shift_rearm_pending is False
    assert detector._forward_offset_history == []
def test_real_shift_up_heel_sequence_is_shift_up():
    heel_y = [
        0.6868953704833984,
        0.6853688359260559,
        0.7004469037055969,
        0.7065775394439697,
        0.717322826385498,
        0.7111089825630188,
        0.7124395966529846,
        0.7113640904426575,
        0.7085505127906799,
    ]

    trend = GearShiftDetector._heel_end_trend(
        heel_y
    )

    shift = GearShiftDetector._shift_from_heel_trend(
        trend
    )

    assert shift == "SHIFT_UP"
def test_cross_baseline_does_not_start_on_single_opposite_sample():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.03982442617416382

    detector._forward_offset_history = [
        -0.0057545,
        -0.0042937,
        -0.0017009,
        0.0052419,
        0.0024597,
        0.0060472,
        -0.0050849,
        -0.0048865,
        -0.0141431,
    ]

    detector._update_forward_movement_from_baseline(
        0.055329740047454834
    )

    assert detector._forward_movement_active is False
def test_cross_baseline_starts_when_path_passes_through_baseline():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.0271457

    for forward in [
        0.0355449,  # +0.0084
        0.0288923,  # +0.0017, near baseline
        0.0179184,  # -0.0092
    ]:
        detector._update_forward_movement_from_baseline(
            forward
        )

    assert detector._forward_movement_active is True
def test_shift_attempt_keeps_recent_heel_history_before_confirmation():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.04044

    samples = [
        (0.0345, 0.7771),
        (0.0325, 0.7770),
        (0.0326, 0.7692),
        (0.0264, 0.7749),
        (0.0250, 0.7752),
    ]

    for forward, heel_y in samples:
        detector.update(
            0.125,
            162.0,
            left_foot_forward=forward,
            left_heel_y=heel_y,
        )

    assert detector._forward_movement_active is True

    assert detector._heel_y_history == [
        0.7771,
        0.7770,
        0.7692,
        0.7749,
        0.7752,
    ]
def test_static_negative_forward_jitter_does_not_start_shift():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.028452062606811525

    detector._update_forward_movement_from_baseline(
        0.017528116703033447
    )

    detector._update_forward_movement_from_baseline(
        0.01415717601776123
    )

    assert detector._forward_movement_active is False
def test_negative_shift_attempt_requires_progressive_path():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.03358926773071289

    samples = [
        0.02847588062286377,
        0.02580583095550537,
        0.024242818355560303,
        0.02369558811187744,
    ]

    for forward in samples:
        detector._update_forward_movement_from_baseline(
            forward
        )

    assert detector._forward_movement_active is True
def test_two_consecutive_one_sided_offsets_do_not_start_shift_attempt():
    detector = GearShiftDetector()
    detector._forward_baseline = 0.03358926773071289

    detector._update_forward_movement_from_baseline(
        0.024242818355560303
    )

    assert detector._forward_movement_active is False

    detector._update_forward_movement_from_baseline(
        0.02369558811187744
    )

    assert detector._forward_movement_active is False
def test_shift_attempt_does_not_immediately_count_as_back_movement():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.03358926773071289

    samples = [
        0.02847588062286377,
        0.02580583095550537,
        0.024242818355560303,
        0.02369558811187744,
    ]

    for forward in samples:
        detector.update(
            0.120,
            155.0,
            left_foot_forward=forward,
            left_heel_y=0.705,
        )

    assert detector._forward_movement_active is True
    assert detector._back_movement_active is False
def test_newly_confirmed_forward_movement_is_not_back_movement():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.03358926773071289

    samples = [
        0.02847588062286377,
        0.02580583095550537,
        0.024242818355560303,
        0.02369558811187744,
    ]

    for forward in samples:
        detector.update(
            0.120,
            155.0,
            left_foot_forward=forward,
            left_heel_y=0.705,
        )

    assert detector._forward_movement_active is True
    assert detector._back_movement_active is False
def test_static_positive_forward_sequence_does_not_start_shift():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.03342646360397339

    samples = [
        0.04566586017608643,  # +0.0122394
        0.04456490278244019,  # +0.0111384
        0.04229289293289185,  # +0.0088664
        0.04368025064468384,  # +0.0102538
        0.04520499706268311,  # +0.0117785
    ]

    for forward in samples:
        detector._update_forward_movement_from_baseline(
            forward
        )

    assert detector._forward_movement_active is False
def test_live_positive_shift_has_outward_movement():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.015255022048950195

    samples = [
        0.025336146354675293,
        0.029669225215911865,
        0.029373466968536377,
        0.029087424278259277,
        0.029112577438354492,
    ]

    for forward in samples:
        detector._update_forward_movement_from_baseline(
            forward
        )

    assert detector._forward_movement_active is True
def test_static_negative_drift_with_single_large_offset_does_not_start_shift():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.04003293514251709

    samples = [
        0.037344157695770264,  # -0.00269
        0.032955169677734375,  # -0.00708
        0.02207845449447632,   # -0.01795
        0.001446843147277832,  # -0.03859
    ]

    for forward in samples:
        detector._update_forward_movement_from_baseline(
            forward
        )

    assert detector._forward_movement_active is False

def test_real_shift_up_sequence_activates_forward_movement():
    detector = GearShiftDetector()

    detector._set_forward_baseline(
        0.04004952907562256
    )

    forward_values = [
        0.04377186298370361,
        0.04371899366378784,
        0.03924596309661865,
        0.03854548931121826,
        0.059136271476745605,
        0.058198750019073486,
        0.05042147636413574,
        0.049142539501190186,
        0.048832714557647705,
        0.04775357246398926,
        0.05772686004638672,
        0.054556965827941895,
    ]

    for value in forward_values:
        detector._update_forward_movement_from_baseline(
            value
        )

    assert detector._forward_movement_active is True
def test_ready_position_establishes_forward_baseline():
    detector = GearShiftDetector()

    left_foot_drop = 0.06
    left_foot_angle = 152.0
    left_foot_forward = -0.045

    detector.update(
        left_foot_drop=left_foot_drop,
        left_foot_angle=left_foot_angle,
        left_foot_forward=left_foot_forward,
    )

    assert detector._state == "READY"
    assert detector._forward_baseline is not None

def test_real_idle_heel_motion_does_not_trigger_shift_down():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.0009360909461975098
    detector._forward_movement_active = True
    detector._back_movement_active = True
    detector._direction_zone = "UP"
    detector._direction_zone_frames = 4

    detector._heel_y_history = [
        0.7714046239852905,
        0.770157516002655,
        0.7658402323722839,
        0.7639350891113281,
        0.7642208933830261,
        0.7918588519096375,
        0.7855291366577148,
        0.784561038017273,
        0.7819739580154419,
        0.7593326568603516,
    ]

    result = detector.update(
        left_foot_drop=0.11205101013183594,
        left_foot_angle=162.7,
        left_foot_forward=0.0184,
        left_heel_y=0.7593326568603516,
        left_heel_visibility=0.68,
    )

    assert result is None
def test_heel_end_trend_distinguishes_false_motion_from_real_shift_down():
    false_heel_y = [
        0.7714046239852905,
        0.770157516002655,
        0.7658402323722839,
        0.7639350891113281,
        0.7642208933830261,
        0.7918588519096375,
        0.7855291366577148,
        0.784561038017273,
        0.7819739580154419,
        0.7593326568603516,
    ]

    real_shift_down_heel_y = [
        0.6869,
        0.6358,
        0.5839,
        0.5839,
    ]

    false_trend = GearShiftDetector._heel_end_trend(
        false_heel_y
    )

    real_trend = GearShiftDetector._heel_end_trend(
        real_shift_down_heel_y
    )

    assert false_trend == "STABLE"
    assert real_trend == "UP"
def test_gear_shift_is_suppressed_during_initial_settling_period():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.011

    detector._forward_movement_active = True
    detector._back_movement_active = True

    detector._heel_y_history = [
        0.650,
        0.655,
        0.665,
    ]

    result = detector.update(
        left_foot_drop=0.100,
        left_foot_angle=155.0,
        left_foot_forward=0.030,
        left_heel_y=0.670,
        left_heel_visibility=0.9,
        elapsed_seconds=5.5,
    )

    assert result is None
def test_settling_motion_does_not_emit_shift_after_settling_period():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.010

    # Simulate a shift attempt created while the rider
    # is still settling in front of the camera.
    detector._forward_movement_active = True
    detector._back_movement_active = True
    detector._heel_y_history = [
        0.83,
        0.80,
        0.77,
    ]

    detector.update(
        left_foot_drop=0.100,
        left_foot_angle=155.0,
        left_foot_forward=0.020,
        left_heel_y=0.74,
        left_heel_visibility=0.9,
        elapsed_seconds=5.9,
    )

    result = detector.update(
        left_foot_drop=0.100,
        left_foot_angle=155.0,
        left_foot_forward=0.020,
        left_heel_y=0.72,
        left_heel_visibility=0.9,
        elapsed_seconds=6.1,
    )

    assert result is None
def test_settling_shift_attempt_does_not_survive_past_six_seconds():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.027

    # During settling, movement starts.
    detector.update(
        left_foot_drop=0.097,
        left_foot_angle=172.0,
        left_foot_forward=0.001,
        left_heel_y=0.770,
        left_heel_visibility=0.9,
        elapsed_seconds=5.8,
    )

    detector.update(
        left_foot_drop=0.097,
        left_foot_angle=172.0,
        left_foot_forward=0.001,
        left_heel_y=0.760,
        left_heel_visibility=0.9,
        elapsed_seconds=5.9,
    )

    # Settling is now over, but there has been
    # no new genuine shift attempt.
    result = detector.update(
        left_foot_drop=0.095,
        left_foot_angle=169.0,
        left_foot_forward=0.004,
        left_heel_y=0.750,
        left_heel_visibility=0.9,
        elapsed_seconds=6.1,
    )

    assert result is None
    assert detector._shift_rearm_pending is False
def test_real_settling_sequence_leaves_clean_shift_state():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = (
        0.027106642723083496
    )

    samples = [
        (
            5.781,
            0.0986553430557251,
            171.09699897163063,
            0.002892792224884033,
            0.7699,
            0.81,
        ),
        (
            5.843,
            0.09732240438461304,
            172.4183813360996,
            0.0016916990280151367,
            0.7700,
            0.81,
        ),
        (
            5.906,
            0.09663575887680054,
            172.0797695328112,
            0.0011313557624816895,
            0.7707,
            0.80,
        ),
        (
            5.953,
            0.0915117859840393,
            171.7115536223066,
            0.0020338892936706543,
            0.7713,
            0.80,
        ),
    ]

    for (
        elapsed,
        drop,
        angle,
        forward,
        heel_y,
        visibility,
    ) in samples:
        result = detector.update(
            left_foot_drop=drop,
            left_foot_angle=angle,
            left_foot_forward=forward,
            left_heel_y=heel_y,
            left_heel_visibility=visibility,
            elapsed_seconds=elapsed,
        )

        assert result is None

    assert detector._forward_movement_active is False
    assert detector._back_movement_active is False
    assert detector._shift_rearm_pending is False
    assert detector._heel_y_history == []
    assert detector._pending_heel_y_history == []
    assert detector._forward_offset_history == []
def test_first_shift_after_settling_requires_stable_footpeg():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._forward_baseline = 0.027

    # Settling period has finished, but the foot
    # is still moving and is not yet stably on the footpeg.
    moving_frames = [
        (6.00, 0.091, 168.4, 0.0045),
        (6.06, 0.094, 169.3, 0.0034),
        (6.11, 0.097, 169.5, 0.0033),
    ]

    for elapsed, drop, angle, forward in moving_frames:
        detector.update(
            left_foot_drop=drop,
            left_foot_angle=angle,
            left_foot_forward=forward,
            left_heel_y=0.76,
            left_heel_visibility=0.9,
            elapsed_seconds=elapsed,
        )

    assert detector._forward_movement_active is False
def test_real_pre_shift_motion_does_not_emit_false_shift_down():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._startup_ready = True
    detector._forward_baseline = (
        0.013139069080352783
    )

    samples = [
        # elapsed, drop, angle, forward, heel_y, visibility
        (
            6.906,
            0.07146942615509033,
            143.14348849290496,
            0.030182957649230957,
            0.6910,
            0.61,
        ),
        (
            6.969,
            0.07867449522018433,
            149.33734901004058,
            0.02929025888442993,
            0.6930,
            0.63,
        ),
        (
            7.031,
            0.09845495223999023,
            157.40067000044434,
            0.0195620059967041,
            0.6932,
            0.65,
        ),
        (
            7.094,
            0.10272592306137085,
            161.83292739902478,
            0.01412808895111084,
            0.7015,
            0.67,
        ),
        (
            7.156,
            0.10667645931243896,
            165.77632391732067,
            0.008904039859771729,
            0.6951,
            0.69,
        ),
        (
            7.219,
            0.11518383026123047,
            166.89536972094152,
            0.00785815715789795,
            0.7196,
            0.70,
        ),
        (
            7.297,
            0.12544453144073486,
            167.08800716312672,
            0.00730586051940918,
            0.7187,
            0.71,
        ),
        (
            7.360,
            0.1355353593826294,
            166.80396217325165,
            0.0021372437477111816,
            0.6868,
            0.71,
        ),
        (
            7.422,
            0.1193990707397461,
            167.6,
            0.0056,
            0.7045,
            0.73,
        ),
    ]

    shifts = []

    for (
        elapsed,
        drop,
        angle,
        forward,
        heel_y,
        visibility,
    ) in samples:
        result = detector.update(
            left_foot_drop=drop,
            left_foot_angle=angle,
            left_foot_forward=forward,
            left_heel_y=heel_y,
            left_heel_visibility=visibility,
            elapsed_seconds=elapsed,
        )

        if result is not None:
            shifts.append(result)

    assert shifts == []
def test_heel_end_trend_rejects_reversed_end_movement():
    heel_y = [
        0.6932,
        0.7015,
        0.6951,
        0.7196,
        0.7187,
        0.6868,
        0.7045,
    ]

    assert GearShiftDetector._heel_end_trend(
        heel_y
    ) == "STABLE"

def test_real_pre_shift_motion_at_six_seconds_does_not_emit_shift_up():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._startup_ready = True
    detector._forward_baseline = (
        0.034899353981018066
    )

    samples = [
        # elapsed, drop, angle, forward, heel_y, visibility
        (
            6.218,
            0.12055468559265137,
            155.6785055069093,
            0.02478128671646118,
            0.7610,
            0.86,
        ),
        (
            6.281,
            0.11482447385787964,
            155.15053493771254,
            0.02620309591293335,
            0.7778,
            0.86,
        ),
        (
            6.343,
            0.1252613067626953,
            156.55893958875873,
            0.025733113288879395,
            0.7748,
            0.86,
        ),
        (
            6.406,
            0.12260735034942627,
            155.743539976939,
            0.030365467071533203,
            0.7760,
            0.86,
        ),
        (
            6.468,
            0.1327560544013977,
            156.2239812050022,
            0.030506134033203125,
            0.7634,
            0.86,
        ),
        (
            6.515,
            0.14222514629364014,
            159.09308113858316,
            0.022153198719024658,
            0.7735,
            0.86,
        ),
        (
            6.578,
            0.14027541875839233,
            160.82570610431094,
            0.017367005348205566,
            0.7803,
            0.86,
        ),
        (
            6.625,
            0.13455075025558472,
            161.57190392457227,
            0.017161071300506592,
            0.7829,
            0.86,
        ),
        (
            6.687,
            0.13122576475143433,
            164.3,
            0.0177,
            0.7825,
            0.86,
        ),
    ]

    shifts = []

    for (
        elapsed,
        drop,
        angle,
        forward,
        heel_y,
        visibility,
    ) in samples:
        result = detector.update(
            left_foot_drop=drop,
            left_foot_angle=angle,
            left_foot_forward=forward,
            left_heel_y=heel_y,
            left_heel_visibility=visibility,
            elapsed_seconds=elapsed,
        )

        if result is not None:
            shifts.append(result)

    assert shifts == []

def test_live_footpeg_stay_position():
    assert GearShiftDetector._is_footpeg_stay_position(
        left_foot_drop=0.048,
        left_foot_angle=100.0,
    ) is True
def test_live_up_sequence_is_detected_as_shift_up():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._startup_ready = True
    detector._forward_baseline = -0.060

    sequence = [
        # neutral / start
        (0.0404,  99.0, -0.060),
        (0.0373, 107.2, -0.058),

        # real UP trajectory
        (0.0330, 109.5, -0.045),
        (0.0342, 109.0, -0.030),
        (0.0096, 127.0, -0.015),
        (-0.0150, 154.9, -0.010),

        # return toward footpeg
        (0.0400, 105.0, -0.040),
        (0.0480, 100.0, -0.058),
    ]

    events = []

    for drop, angle, forward in sequence:
        event = detector.update(
            drop,
            angle,
            left_foot_forward=forward,
        )

        if event is not None:
            events.append(event)

    assert "SHIFT_UP" in events
    assert "SHIFT_DOWN" not in events
def test_live_ready_transition_does_not_set_baseline_from_single_frame():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.080,
        left_foot_angle=160.0,
        left_foot_forward=-0.005,
        elapsed_seconds=6.1,
    )

    assert detector._state == "READY"
    assert detector._forward_baseline is None
def test_live_footpeg_stay_position_with_high_neutral_angle():
    assert GearShiftDetector._is_footpeg_stay_position(
        left_foot_drop=0.045,
        left_foot_angle=167.0,
    ) is True
def test_live_footpeg_stay_position_with_negative_drop():
    assert GearShiftDetector._is_footpeg_stay_position(
        left_foot_drop=-0.115,
        left_foot_angle=157.0,
    ) is True
def test_live_footpeg_stay_position_with_negative_small_drop():
    assert GearShiftDetector._is_footpeg_stay_position(
        left_foot_drop=-0.049,
        left_foot_angle=165.0,
    ) is True
def test_live_footpeg_position_with_negative_drop():
    assert GearShiftDetector._is_footpeg_position(
        left_foot_drop=-0.050,
        left_foot_angle=165.0,
    ) is True
def test_live_baseline_accepts_small_real_world_jitter():
    detector = GearShiftDetector()

    samples = [
        -0.0094,
        -0.0036,
        -0.0022,
        -0.0021,
        -0.0096,
    ]

    for forward in samples:
        detector.update(
            left_foot_drop=0.100,
            left_foot_angle=156.0,
            left_foot_forward=forward,
            elapsed_seconds=10.0,
        )

    assert detector._forward_baseline is not None

def test_live_down_forward_sequence_activates_forward_movement():
    detector = GearShiftDetector()

    detector._forward_baseline = 0.022690469026565553

    samples = [
        0.026180773973464966,
        0.028219670057296753,
        0.028722494840621948,
        0.029509335756301880,
        0.029705554246902466,
    ]

    for forward in samples:
        detector._update_forward_movement_from_baseline(
            forward
        )

    assert detector._forward_movement_active is True