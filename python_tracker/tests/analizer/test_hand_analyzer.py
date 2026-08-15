import pytest
from types import SimpleNamespace

from mediapipe.python.solutions.hands import HandLandmark
from pose.models.throttle_calibration import ThrottleCalibration


from pose.analyzers.hand_analyzer import HandAnalyzer
from pose.analyzers.hand_control_analyzer import HandControlAnalyzer
from pose.models.front_brake_calibration import FrontBrakeCalibration


def test_hand_analyzer_returns_index_finger_bend():
    analyzer = HandAnalyzer()

    result = analyzer.analyze({})

    assert "left_index_finger_bend" in result
    assert result["left_index_finger_bend"] is None

   


def test_index_finger_bend_returns_none():
    analyzer = HandAnalyzer()

    assert (
        analyzer._index_finger_bend(None)
        is None
    )

def test_index_finger_bend_returns_none_without_hand():
    analyzer = HandAnalyzer()

    assert (
        analyzer._index_finger_bend(None)
        is None
    )

def _get_landmark(
    self,
    hand,
    landmark,
):
    ...

def test_hand_analyzer_returns_index_finger_bend():
    analyzer = HandAnalyzer()

    result = analyzer.analyze({})

    assert "left_index_finger_bend" in result
    assert result["left_index_finger_bend"] is None

    assert "left_index_finger_bend_3d" in result
    assert result["left_index_finger_bend_3d"] is None


def test_index_tip_to_mcp_ratio_returns_none_without_hand():
    analyzer = HandAnalyzer()

    assert (
        analyzer._index_tip_to_mcp_ratio(None)
        is None
    )

def test_throttle_progress_handles_angle_wraparound():
    progress = HandControlAnalyzer._throttle_progress(
        closed_rotation=350.0,
        open_rotation=120.0,
        current_rotation=4.0,
    )

    assert progress == pytest.approx(
        14.0 / 130.0,
        abs=0.01,
    )




def test_index_tip_to_mcp_ratio_returns_expected_ratio():
    analyzer = HandAnalyzer()

    landmarks = [
        SimpleNamespace(x=0.0, y=0.0)
        for _ in range(21)
    ]

    landmarks[HandLandmark.INDEX_FINGER_MCP] = (
        SimpleNamespace(x=0.0, y=0.0)
    )
    landmarks[HandLandmark.INDEX_FINGER_TIP] = (
        SimpleNamespace(x=2.0, y=0.0)
    )

    landmarks[HandLandmark.WRIST] = (
        SimpleNamespace(x=0.0, y=0.0)
    )
    landmarks[HandLandmark.MIDDLE_FINGER_MCP] = (
        SimpleNamespace(x=4.0, y=0.0)
    )

    hand = SimpleNamespace(
        landmark=landmarks
    )

    result = analyzer._index_tip_to_mcp_ratio(
        hand
    )

    assert result == 0.5

def test_clutch_progress_is_zero_when_released():
    progress = HandControlAnalyzer._clutch_progress(
        released_angle=176,
        pulled_angle=131,
        current_angle=176,
    )

    assert progress == 0.0

def test_clutch_progress_is_one_when_fully_pulled():
    progress = HandControlAnalyzer._clutch_progress(
        released_angle=176,
        pulled_angle=131,
        current_angle=131,
    )

    assert progress == 1.0

def test_clutch_progress_is_about_sixty_percent_in_friction_zone():
    progress = HandControlAnalyzer._clutch_progress(
        released_angle=176,
        pulled_angle=131,
        current_angle=149,
    )

    assert progress == pytest.approx(
        0.60,
        abs=0.01,
    )

def test_clutch_progress_is_consistent_at_different_camera_angle():
    progress = HandControlAnalyzer._clutch_progress(
        released_angle=175,
        pulled_angle=119,
        current_angle=141,
    )

    assert progress == pytest.approx(
        0.61,
        abs=0.02,
    )

def test_clutch_progress_is_consistent_at_ninety_degree_camera_angle():
    progress = HandControlAnalyzer._clutch_progress(
        released_angle=162,
        pulled_angle=85,
        current_angle=113,
    )

    assert progress == pytest.approx(
        0.64,
        abs=0.02,
    )

def test_hand_analyzer_returns_none_for_right_index_without_hand():
    analyzer = HandAnalyzer()

    result = analyzer.analyze({})

    assert result["right_index_finger_bend"] is None

def test_front_brake_calibration_starts_incomplete():
    calibration = FrontBrakeCalibration()

    assert calibration.released_angle is None
    assert calibration.pulled_angle is None
    assert calibration.is_complete() is False

def test_capture_front_brake_released_calibration():
    analyzer = HandControlAnalyzer()

    analyzer.capture_front_brake_released(
        current_angle=134.0
    )

    assert (
        analyzer._front_brake_calibration.released_angle
        == 134.0
    )

def test_capture_front_brake_pulled_calibration():
    analyzer = HandControlAnalyzer()

    analyzer.capture_front_brake_pulled(
        current_angle=80.0
    )

    assert (
        analyzer._front_brake_calibration.pulled_angle
        == 80.0
    )

def test_front_brake_is_active():
    assert (
        HandControlAnalyzer._is_front_brake_active(
            0.20
        )
        is True
    )

def test_front_brake_is_not_active_when_released():
    assert (
        HandControlAnalyzer._is_front_brake_active(
            0.0
        )
        is False
    )

def test_front_brake_is_not_active_when_progress_is_none():
    assert (
        HandControlAnalyzer._is_front_brake_active(
            None
        )
        is False
    )

def test_front_brake_is_not_active_when_released():
    assert (
        HandControlAnalyzer._is_front_brake_active(0.0)
        is False
    )


def test_front_brake_is_not_active_when_progress_is_none():
    assert (
        HandControlAnalyzer._is_front_brake_active(None)
        is False
    )


def test_front_brake_hysteresis_keeps_active_state():
    assert (
        HandControlAnalyzer._is_front_brake_active(
            front_brake_progress=0.09,
            was_active=True,
        )
        is True
    )

def test_front_brake_hysteresis_keeps_state_between_calls():
    analyzer = HandControlAnalyzer()

    analyzer._front_brake_active = True

    front_brake_active = analyzer._is_front_brake_active(
        front_brake_progress=0.09,
        was_active=analyzer._front_brake_active,
    )

    analyzer._front_brake_active = front_brake_active

    assert analyzer._front_brake_active is True

def test_front_brake_active_starts_false():
    analyzer = HandControlAnalyzer()

    assert analyzer._front_brake_active is False

def test_front_brake_hysteresis_sequence():
    analyzer = HandControlAnalyzer()

    active = analyzer._is_front_brake_active(
        0.13,
        was_active=False,
    )
    assert active is True

    active = analyzer._is_front_brake_active(
        0.09,
        was_active=active,
    )
    assert active is True

    active = analyzer._is_front_brake_active(
        0.05,
        was_active=active,
    )
    assert active is False

def test_throttle_progress_is_zero_when_closed():
    progress = HandControlAnalyzer._throttle_progress(
        closed_rotation=180.0,
        open_rotation=260.0,
        current_rotation=180.0,
    )

    assert progress == 0.0

def test_throttle_progress_is_one_when_fully_open():
    progress = HandControlAnalyzer._throttle_progress(
        closed_rotation=180.0,
        open_rotation=260.0,
        current_rotation=260.0,
    )

    assert progress == 1.0

def test_throttle_progress_is_half_at_midpoint():
    progress = HandControlAnalyzer._throttle_progress(
        closed_rotation=180.0,
        open_rotation=260.0,
        current_rotation=220.0,
    )

    assert progress == 0.5

def test_throttle_progress_is_small_near_closed_after_wraparound():
    progress = HandControlAnalyzer._throttle_progress(
        closed_rotation=350.0,
        open_rotation=120.0,
        current_rotation=359.0,
    )

    assert progress == pytest.approx(
        9.0 / 130.0,
        abs=0.01,
    )

def test_throttle_calibration_starts_incomplete():
    calibration = ThrottleCalibration()

    assert calibration.closed_rotation is None
    assert calibration.open_rotation is None
    assert calibration.is_complete() is False

def test_throttle_calibration_sets_closed_rotation():
    calibration = ThrottleCalibration()

    calibration.set_closed(350.0)

    assert calibration.closed_rotation == 350.0

def test_throttle_calibration_sets_open_rotation():
    calibration = ThrottleCalibration()

    calibration.set_open(120.0)

    assert calibration.open_rotation == 120.0

def test_throttle_calibration_becomes_complete():
    calibration = ThrottleCalibration()

    calibration.set_closed(350.0)

    assert calibration.is_complete() is False

    calibration.set_open(120.0)

    assert calibration.is_complete() is True    

def test_current_throttle_progress_returns_none_without_calibration():
    analyzer = HandControlAnalyzer()

    progress = analyzer._current_throttle_progress(
        current_rotation=20.0
    )

    assert progress is None
def test_current_throttle_progress_uses_calibration():
    analyzer = HandControlAnalyzer()

    analyzer._throttle_calibration.set_closed(
        350.0
    )
    analyzer._throttle_calibration.set_open(
        120.0
    )

    progress = analyzer._current_throttle_progress(
        current_rotation=4.0
    )

    assert progress == pytest.approx(
        14.0 / 130.0,
        abs=0.01,
    )
def test_calibrate_throttle_closed():
    analyzer = HandControlAnalyzer()

    analyzer.calibrate_throttle_closed(
        current_rotation=350.0
    )

    assert (
        analyzer._throttle_calibration.closed_rotation
        == 350.0
    )
def test_calibrate_throttle_open():
    analyzer = HandControlAnalyzer()

    analyzer.calibrate_throttle_open(
        current_rotation=120.0
    )

    assert (
        analyzer._throttle_calibration.open_rotation
        == 120.0
    )
def test_capture_throttle_closed_calibration():
    analyzer = HandControlAnalyzer()

    analyzer.capture_throttle_closed(
        current_rotation=350.0
    )

    assert (
        analyzer._throttle_calibration.closed_rotation
        == 350.0
    )
def test_capture_throttle_open_calibration():
    analyzer = HandControlAnalyzer()

    analyzer.capture_throttle_open(
        current_rotation=120.0
    )

    assert (
        analyzer._throttle_calibration.open_rotation
        == 120.0
    )

def test_throttle_progress_does_not_wrap_closed_jitter_to_full():
    progress = HandControlAnalyzer._throttle_progress(
        closed_rotation=44.0,
        open_rotation=170.0,
        current_rotation=329.0,
    )

    assert progress == 0.0

def test_throttle_progress_handles_half_turn_range():
    progress = HandControlAnalyzer._throttle_progress(
        closed_rotation=340.0,
        open_rotation=160.0,
        current_rotation=153.0,
    )

    assert progress == pytest.approx(
        173.0 / 180.0,
        abs=0.01,
    )
