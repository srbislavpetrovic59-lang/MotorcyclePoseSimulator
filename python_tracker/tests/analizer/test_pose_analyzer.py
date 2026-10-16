import pytest

from pose.pose_analyzer import PoseAnalyzer
from pose.analyzers.lean_detector import LeanDetector


def test_pose_analyzer_has_lean_detector():
    analyzer = PoseAnalyzer()

    assert isinstance(
        analyzer.lean_detector,
        LeanDetector,
    )

import pytest


def test_pose_analyzer_calculates_normalized_lean():
    analyzer = PoseAnalyzer()

    analyzer.lean_detector.calibrate(-5.5)

    result = analyzer._calculate_lean(
        shoulder_tilt=-20.5,
    )

    assert result == pytest.approx(-0.5)

def test_pose_analyzer_adds_normalized_lean():
    analyzer = PoseAnalyzer()
    analyzer.lean_detector.calibrate(-5.5)

    body_result = {
        "shoulder_tilt": -20.5,
        "torso_angle": 10.0,
    }

    result = analyzer._add_lean_to_result(body_result)

    assert result["lean_normalized"] == pytest.approx(-0.5)

    # Postojeci podaci moraju ostati sacuvani.
    assert result["shoulder_tilt"] == -20.5
    assert result["torso_angle"] == 10.0

def test_pose_analyzer_calibrates_neutral_lean():
    analyzer = PoseAnalyzer()

    analyzer.calibrate_lean(-5.5)

    assert analyzer._calculate_lean(-5.5) == pytest.approx(0.0)
    assert analyzer._calculate_lean(-20.5) == pytest.approx(-0.5)
    assert analyzer._calculate_lean(9.5) == pytest.approx(0.5)

def test_pose_analyzer_can_request_lean_calibration():
    analyzer = PoseAnalyzer()

    assert analyzer._lean_calibration_requested is False

    analyzer.request_lean_calibration()

    assert analyzer._lean_calibration_requested is True

def test_pose_analyzer_processes_lean_calibration():
    analyzer = PoseAnalyzer()

    analyzer.request_lean_calibration(now=10.0)

    # Pre isteka tri sekunde nema kalibracije.
    result = analyzer._add_lean_to_result(
        {"shoulder_tilt": -10.0},
        now=12.0,
    )

    assert analyzer._lean_calibration_requested is True

    # Nakon tri sekunde kalibrišemo neutralni položaj.
    result = analyzer._add_lean_to_result(
        {"shoulder_tilt": -5.5},
        now=13.0,
    )

    assert result["lean_normalized"] == pytest.approx(0.0)
    assert analyzer._lean_calibration_requested is False

    # Proveravamo da novi neutralni položaj važi.
    result = analyzer._add_lean_to_result(
        {"shoulder_tilt": -20.5},
        now=13.1,
    )

    assert result["lean_normalized"] == pytest.approx(-0.5)

def test_lean_calibration_waits_three_seconds():
    analyzer = PoseAnalyzer()

    analyzer.request_lean_calibration(now=10.0)

    # Vozač se još vraća od tastature.
    result = analyzer._add_lean_to_result(
        {"shoulder_tilt": -15.0},
        now=12.9,
    )

    assert analyzer._lean_calibration_requested is True

    # Tri sekunde su prošle.
    result = analyzer._add_lean_to_result(
        {"shoulder_tilt": -5.5},
        now=13.0,
    )

    assert result["lean_normalized"] == pytest.approx(0.0)
    assert analyzer._lean_calibration_requested is False
    assert analyzer.lean_detector._neutral_angle == pytest.approx(-5.5)


def test_lean_calibration_reports_completion_once():
    analyzer = PoseAnalyzer()

    analyzer.request_lean_calibration(now=10.0)

    body_result = {"shoulder_tilt": 5.0}

    before = analyzer._add_lean_to_result(
        body_result,
        now=12.9,
    )

    completed = analyzer._add_lean_to_result(
        body_result,
        now=13.0,
    )

    after = analyzer._add_lean_to_result(
        body_result,
        now=13.1,
    )

    assert before["lean_calibration_completed"] is False
    assert completed["lean_calibration_completed"] is True
    assert after["lean_calibration_completed"] is False