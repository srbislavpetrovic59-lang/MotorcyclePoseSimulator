import pytest
from types import SimpleNamespace

from pose.analyzers.body_analyzer import BodyAnalyzer
from pose.landmarks import PoseLandmark


def test_shoulder_tilt_horizontal():
    landmarks = {
        PoseLandmark.LEFT_SHOULDER: SimpleNamespace(x=0.3, y=0.4),
        PoseLandmark.RIGHT_SHOULDER: SimpleNamespace(x=0.7, y=0.4),
    }

    analyzer = BodyAnalyzer()
    angle = analyzer._shoulder_tilt(landmarks)

    assert angle == pytest.approx(0.0)

def test_shoulder_tilt_positive():
    landmarks = {
        PoseLandmark.LEFT_SHOULDER: SimpleNamespace(x=0.3, y=0.4),
        PoseLandmark.RIGHT_SHOULDER: SimpleNamespace(x=0.7, y=0.5),
    }

    analyzer = BodyAnalyzer()
    angle = analyzer._shoulder_tilt(landmarks)

    assert angle > 0.0


def test_shoulder_tilt_negative():
    landmarks = {
        PoseLandmark.LEFT_SHOULDER: SimpleNamespace(x=0.3, y=0.5),
        PoseLandmark.RIGHT_SHOULDER: SimpleNamespace(x=0.7, y=0.4),
    }

    analyzer = BodyAnalyzer()
    angle = analyzer._shoulder_tilt(landmarks)

    assert angle < 0.0

def test_shoulder_tilt_reversed_horizontal():
    landmarks = {
        PoseLandmark.LEFT_SHOULDER: SimpleNamespace(x=0.7, y=0.4),
        PoseLandmark.RIGHT_SHOULDER: SimpleNamespace(x=0.3, y=0.4),
    }

    analyzer = BodyAnalyzer()
    angle = analyzer._shoulder_tilt(landmarks)

    assert angle == pytest.approx(0.0)