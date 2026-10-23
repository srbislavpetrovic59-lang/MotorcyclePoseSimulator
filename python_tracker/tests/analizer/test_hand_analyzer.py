import pytest
import json
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

    analyzer._throttle_calibration = ThrottleCalibration()

    progress = analyzer._current_throttle_progress(
        current_rotation=20.0
    )

    assert progress is None

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
def test_throttle_calibration_can_be_serialized():
    calibration = ThrottleCalibration(
        closed_rotation=350.0,
        open_rotation=120.0,
    )

    data = calibration.to_dict()

    assert data == {
        "closed_rotation": 350.0,
        "open_rotation": 120.0,
    }

def test_throttle_calibration_can_be_deserialized():
    data = {
        "closed_rotation": 350.0,
        "open_rotation": 120.0,
    }

    calibration = ThrottleCalibration.from_dict(data)

    assert calibration.closed_rotation == 350.0
    assert calibration.open_rotation == 120.0
    assert calibration.is_complete() is True

def test_throttle_calibration_can_be_saved(tmp_path):
    calibration = ThrottleCalibration(
        closed_rotation=350.0,
        open_rotation=120.0,
    )

    file_path = tmp_path / "throttle_calibration.json"

    calibration.save(file_path)

    assert file_path.exists()

def test_throttle_calibration_can_be_saved(tmp_path):
    calibration = ThrottleCalibration(
        closed_rotation=350.0,
        open_rotation=120.0,
    )

    file_path = tmp_path / "throttle_calibration.json"

    calibration.save(file_path)

    assert file_path.exists()

    saved_data = json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )

    assert saved_data == {
        "closed_rotation": 350.0,
        "open_rotation": 120.0,
    }

def test_throttle_calibration_can_be_loaded(tmp_path):
    file_path = tmp_path / "throttle_calibration.json"

    file_path.write_text(
        """
        {
            "closed_rotation": 350.0,
            "open_rotation": 120.0
        }
        """,
        encoding="utf-8",
    )

    calibration = ThrottleCalibration.load(
        file_path
    )

    assert calibration.closed_rotation == 350.0
    assert calibration.open_rotation == 120.0
    assert calibration.is_complete() is True

def test_throttle_calibration_load_returns_empty_when_file_missing(
    tmp_path,
):
    file_path = tmp_path / "missing_throttle_calibration.json"

    calibration = ThrottleCalibration.load(
        file_path
    )

    assert calibration.closed_rotation is None
    assert calibration.open_rotation is None
    assert calibration.is_complete() is False

def test_throttle_calibration_save_creates_parent_directory(
    tmp_path,
):
    file_path = (
        tmp_path
        / "config"
        / "throttle_calibration.json"
    )

    calibration = ThrottleCalibration(
        closed_rotation=350.0,
        open_rotation=120.0,
    )

    calibration.save(file_path)

    assert file_path.exists()

def test_throttle_becomes_active_above_open_threshold():
    analyzer = HandControlAnalyzer()

    active = analyzer._update_throttle_active(
        throttle_progress=0.15,
    )

    assert active is True

def test_throttle_stays_active_inside_hysteresis_zone():
    analyzer = HandControlAnalyzer()

    analyzer._update_throttle_active(
        throttle_progress=0.15,
    )

    active = analyzer._update_throttle_active(
        throttle_progress=0.07,
    )

    assert active is True

def test_throttle_becomes_inactive_below_close_threshold():
    analyzer = HandControlAnalyzer()

    analyzer._update_throttle_active(
        throttle_progress=0.15,
    )

    analyzer._update_throttle_active(
        throttle_progress=0.07,
    )

    active = analyzer._update_throttle_active(
        throttle_progress=0.04,
    )

    assert active is False


def test_throttle_filter_smooths_opening():
    analyzer = HandControlAnalyzer()

    # Početni položaj: zatvoren gas.
    assert analyzer._filter_throttle_progress(0.0) == 0.0

    # Nagli skok sa 0% na 100%.
    filtered = analyzer._filter_throttle_progress(1.0)

    # Gas treba da raste, ali ne odmah na 100%.
    assert 0.0 < filtered < 1.0


def test_throttle_filter_closes_immediately():
    analyzer = HandControlAnalyzer()

    analyzer._filter_throttle_progress(0.0)

    # Postepeno otvaramo gas.
    for _ in range(10):
        analyzer._filter_throttle_progress(1.0)

    # Zatvaranje mora biti trenutno.
    assert analyzer._filter_throttle_progress(0.0) == 0.0


def test_throttle_filter_resets_when_tracking_lost():
    analyzer = HandControlAnalyzer()

    analyzer._filter_throttle_progress(0.0)

    # Otvaramo gas.
    analyzer._filter_throttle_progress(1.0)

    # MediaPipe gubi šaku.
    assert analyzer._filter_throttle_progress(None) is None

    # Nakon ponovnog prepoznavanja,
    # filter ne sme koristiti staru vrednost.
    assert analyzer._filter_throttle_progress(0.0) == 0.0


def test_index_tip_relative_depth():
    analyzer = HandAnalyzer()

    hand = SimpleNamespace(
        landmark=[
            SimpleNamespace(x=0.0, y=0.0, z=0.0)
            for _ in range(21)
        ]
    )

    hand.landmark[HandLandmark.INDEX_FINGER_MCP].z = -0.10
    hand.landmark[HandLandmark.INDEX_FINGER_TIP].z = 0.05

    depth = analyzer._index_tip_relative_depth(hand)

    assert depth == pytest.approx(0.15)

from pose.analyzers.index_angle_filter import IndexAngleFilter


def test_hand_analyzer_has_index_angle_filter():
    analyzer = HandAnalyzer()

    assert isinstance(
        analyzer._left_index_angle_filter,
        IndexAngleFilter,
    )

def test_hand_analyzer_resets_index_filter_when_hand_missing():
    analyzer = HandAnalyzer()

    analyzer._left_index_angle_filter.update(175.0)
    analyzer._left_index_angle_filter.update(170.0)

    result = analyzer.analyze({})

    assert result["left_index_finger_bend"] is None

    assert (
        analyzer._left_index_angle_filter.update(145.0)
        == 145.0
    )


from unittest.mock import patch


from unittest.mock import patch


from unittest.mock import patch


from unittest.mock import patch


def test_hand_analyzer_filters_index_angle_spike():
    analyzer = HandAnalyzer()

    angles = [172.0, 171.0, 65.0, 170.0, 169.0]
    readings = iter(angles)

    left_hand = object()

    def fake_index_bend(hand):
        if hand is left_hand:
            return next(readings)
        return None

    filter_update = analyzer._left_index_angle_filter.update

    with (
        patch.object(
            analyzer,
            "_index_finger_bend",
            side_effect=fake_index_bend,
        ),
        patch.object(
            analyzer,
            "_index_finger_bend_3d",
            return_value=None,
        ),
        patch.object(
            analyzer,
            "_index_tip_to_mcp_ratio",
            return_value=None,
        ),
        patch.object(
            analyzer,
            "_index_tip_to_mcp_ratio_3d",
            return_value=None,
        ),
        patch.object(
            analyzer,
            "_index_tip_relative_depth",
            return_value=None,
        ),
        patch.object(
            analyzer._left_index_angle_filter,
            "update",
            wraps=filter_update,
        ) as mock_filter_update,
    ):
        results = [
            analyzer.analyze({"Left": left_hand})[
                "left_index_finger_bend"
            ]
            for _ in angles
        ]

    assert results[-1] == 170.0
    assert len(results) == 5
    assert next(readings, None) is None
    assert mock_filter_update.call_count == 5

