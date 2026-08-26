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

    # FOOTPEG
    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
    )

    # UP movement
    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=159.0,
    )
    detector.update(
        left_foot_drop=0.130,
        left_foot_angle=161.0,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=160.0,
    )

    # FOOTPEG
    result = detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
    )

    assert result == "SHIFT_UP"

def test_front_view_shift_down_path():
    detector = GearShiftDetector()

    # FOOTPEG
    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=155.0,
    )

    # DOWN movement
    detector.update(
        left_foot_drop=0.120,
        left_foot_angle=149.0,
    )
    detector.update(
        left_foot_drop=0.130,
        left_foot_angle=147.0,
    )
    detector.update(
        left_foot_drop=0.125,
        left_foot_angle=148.0,
    )

    # FOOTPEG
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