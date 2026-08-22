import pytest
from pose.models.clutch_calibration import ClutchCalibration
from  pose.analyzers.hand_control_analyzer import HandControlAnalyzer


def test_clutch_calibration_starts_empty():
    calibration = ClutchCalibration()

    assert calibration.released_angle is None
    assert calibration.pulled_angle is None

def test_clutch_calibration_is_not_complete_when_empty():
    calibration = ClutchCalibration()

    assert calibration.is_complete() is False

def test_clutch_calibration_is_complete_when_both_angles_are_set():
    calibration = ClutchCalibration(
        released_angle=176.0,
        pulled_angle=131.0,
    )

    assert calibration.is_complete() is True

def test_hand_control_analyzer_has_clutch_calibration():
    analyzer = HandControlAnalyzer()

    assert isinstance(
        analyzer.clutch_calibration,
        ClutchCalibration,
    )

def test_current_clutch_progress_returns_none_without_calibration():
    analyzer = HandControlAnalyzer()

    progress = analyzer._current_clutch_progress(
        current_angle=150.0,
    )

    assert progress is None

def test_current_clutch_progress_uses_calibration():
    analyzer = HandControlAnalyzer()

    analyzer.clutch_calibration.released_angle = 176.0
    analyzer.clutch_calibration.pulled_angle = 131.0

    progress = analyzer._current_clutch_progress(
        current_angle=149.0,
    )

    assert progress == pytest.approx(
        0.60,
        abs=0.01,
    )

def test_clutch_calibration_sets_released_angle():
    calibration = ClutchCalibration()

    calibration.set_released(176.0)

    assert calibration.released_angle == 176.0

def test_clutch_calibration_sets_pulled_angle():
    calibration = ClutchCalibration()

    calibration.set_pulled(131.0)

    assert calibration.pulled_angle == 131.0

def test_calibrate_clutch_released_stores_current_angle():
    analyzer = HandControlAnalyzer()

    analyzer.calibrate_clutch_released(
        176.0
    )

    assert (
        analyzer.clutch_calibration.released_angle
        == 176.0
    )

def test_calibrate_clutch_pulled_stores_current_angle():
    analyzer = HandControlAnalyzer()

    analyzer.calibrate_clutch_pulled(
        131.0
    )

    assert (
        analyzer.clutch_calibration.pulled_angle
        == 131.0
    )


def test_clutch_calibration_and_progress_work_together():
    analyzer = HandControlAnalyzer()

    analyzer.calibrate_clutch_released(
        176.0
    )
    analyzer.calibrate_clutch_pulled(
        131.0
    )

    progress = analyzer._current_clutch_progress(
        current_angle=149.0
    )

    assert progress == pytest.approx(
        0.60,
        abs=0.01,
    )

def test_clutch_is_in_friction_zone():
    analyzer = HandControlAnalyzer()

    assert analyzer._update_clutch_in_friction_zone(
        0.60
    ) is True

def test_clutch_is_not_in_friction_zone_when_released():
    analyzer = HandControlAnalyzer()

    assert analyzer._update_clutch_in_friction_zone(
        0.0
    ) is False

def test_clutch_is_not_in_friction_zone_when_fully_pulled():
    analyzer = HandControlAnalyzer()

    assert analyzer._update_clutch_in_friction_zone(
        1.0
    ) is False

def test_clutch_keeps_friction_zone_when_progress_is_none():
    analyzer = HandControlAnalyzer()

    assert analyzer._update_clutch_in_friction_zone(
        0.60
    ) is True

    assert analyzer._update_clutch_in_friction_zone(
        None
    ) is True

def test_clutch_keeps_outside_friction_zone_when_progress_is_none():
    analyzer = HandControlAnalyzer()

    assert analyzer._update_clutch_in_friction_zone(
        0.0
    ) is False

    assert analyzer._update_clutch_in_friction_zone(
        None
    ) is False

def test_clutch_tracking_timeout_keeps_missing_progress_initially():
    analyzer = HandControlAnalyzer()

    analyzer._apply_clutch_tracking_timeout(
        0.60,
        now=10.0,
    )

    progress = analyzer._apply_clutch_tracking_timeout(
        None,
        now=10.2,
    )

    assert progress is None

def test_clutch_tracking_timeout_releases_after_timeout():
    analyzer = HandControlAnalyzer()

    analyzer._apply_clutch_tracking_timeout(
        0.60,
        now=10.0,
    )

    progress = analyzer._apply_clutch_tracking_timeout(
        None,
        now=10.5,
    )

    assert progress == 0.0

def test_clutch_tracking_timeout_resets_on_new_measurement():
    analyzer = HandControlAnalyzer()

    analyzer._apply_clutch_tracking_timeout(
        0.60,
        now=10.0,
    )

    analyzer._apply_clutch_tracking_timeout(
        0.65,
        now=10.3,
    )

    progress = analyzer._apply_clutch_tracking_timeout(
        None,
        now=10.5,
    )

    assert progress is None


def test_throttle_tracking_timeout_keeps_missing_progress_initially():
    analyzer = HandControlAnalyzer()

    analyzer._apply_throttle_tracking_timeout(
        1.0,
        now=10.0,
    )

    progress = analyzer._apply_throttle_tracking_timeout(
        None,
        now=10.2,
    )

    assert progress is None


def test_throttle_tracking_timeout_releases_after_timeout():
    analyzer = HandControlAnalyzer()

    analyzer._apply_throttle_tracking_timeout(
        1.0,
        now=10.0,
    )

    progress = analyzer._apply_throttle_tracking_timeout(
        None,
        now=10.5,
    )

    assert progress == 0.0


def test_throttle_tracking_timeout_resets_on_new_measurement():
    analyzer = HandControlAnalyzer()

    analyzer._apply_throttle_tracking_timeout(
        1.0,
        now=10.0,
    )

    analyzer._apply_throttle_tracking_timeout(
        0.8,
        now=10.3,
    )

    progress = analyzer._apply_throttle_tracking_timeout(
        None,
        now=10.5,
    )

    assert progress is None