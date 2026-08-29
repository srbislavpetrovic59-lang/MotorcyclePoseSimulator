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

    assert detector._forward_movement_active is True

def test_backward_movement_from_baseline_can_activate_shift_attempt():
    detector = GearShiftDetector()

    detector._set_forward_baseline(0.018)

    detector._update_forward_movement_from_baseline(-0.002)

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
    print(
        "SECOND ATTEMPT:",
        "forward=", detector._forward_movement_active,
        "back=", detector._back_movement_active,
        "direction=", detector._direction_zone,
        "frames=", detector._direction_zone_frames,
        "history=", detector._zone_history,
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

    assert detector._forward_movement_active is True
    assert detector._back_movement_active is False

def test_completed_rearm_resets_movement_state():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._shift_rearm_pending = True
    detector._forward_baseline = 0.015

    detector._forward_movement_active = True
    detector._back_movement_active = True

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