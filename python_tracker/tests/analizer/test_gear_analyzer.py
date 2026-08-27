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
    )

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=159.0,
        left_foot_forward=0.034,
    )
    detector.update(
        left_foot_drop=0.130,
        left_foot_angle=161.0,
        left_foot_forward=0.034,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=160.0,
        left_foot_forward=0.034,
    )

    result = detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
    )

    assert result == "SHIFT_UP"

def test_front_view_shift_down_path():
    detector = GearShiftDetector()

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
    )

    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=149.0,
        left_foot_forward=0.034,
    )
    detector.update(
        left_foot_drop=0.130,
        left_foot_angle=147.0,
        left_foot_forward=0.034,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=148.0,
        left_foot_forward=0.034,
    )

    result = detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
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
    )

    # Forward movement starts, angle first dips slightly...
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.034,
    )

    # ...then rises through transition into UP.
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
    assert detector._zone_history == ["UP"]

def test_falling_trend_with_forward_movement_builds_down_history():
    detector = GearShiftDetector()

    # FOOTPEG
    detector.update(
        0.120,
        155.0,
    )

    detector.update(
        0.120,
        156.0,
        left_foot_forward=0.034,
    )
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.034,
    )
    detector.update(
        0.120,
        152.0,
        left_foot_forward=0.034,
    )
    detector.update(
        0.120,
        149.0,
        left_foot_forward=0.034,
    )

    assert detector._angle_trend() == "FALLING"
    assert detector._zone_history == ["DOWN"]

def test_rising_shift_emits_only_on_return_to_footpeg():
    detector = GearShiftDetector()

    # FOOTPEG
    detector.update(
        0.120,
        155.0,
    )

    # Forward + rising movement
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

    # While still away from footpeg, no event yet.
    result = detector.update(
        0.120,
        160.0,
        left_foot_forward=0.034,
    )

    assert result is None

    # Return to footpeg confirms the shift.
    result = detector.update(
        0.120,
        155.0,
        left_foot_forward=0.025,
    )

    assert result == "SHIFT_UP"

def test_falling_shift_emits_only_on_return_to_footpeg():
    detector = GearShiftDetector()

    # FOOTPEG
    detector.update(
        0.120,
        155.0,
    )

    # Forward + falling movement
    detector.update(
        0.120,
        156.0,
        left_foot_forward=0.034,
    )
    detector.update(
        0.120,
        154.0,
        left_foot_forward=0.034,
    )
    detector.update(
        0.120,
        152.0,
        left_foot_forward=0.034,
    )

    # Still away from footpeg -> no event yet.
    result = detector.update(
        0.120,
        149.0,
        left_foot_forward=0.034,
    )

    assert result is None

    # Return to footpeg confirms the shift.
    result = detector.update(
        0.120,
        155.0,
        left_foot_forward=0.025,
    )

    assert result == "SHIFT_DOWN"

