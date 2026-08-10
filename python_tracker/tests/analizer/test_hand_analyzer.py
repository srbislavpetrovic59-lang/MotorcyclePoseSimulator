import pytest
from types import SimpleNamespace

from mediapipe.python.solutions.hands import HandLandmark


from pose.analyzers.hand_analyzer import HandAnalyzer
from pose.analyzers.hand_control_analyzer import HandControlAnalyzer


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

