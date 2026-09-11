from pose.analyzers.riding_phase_detector import RidingPhaseDetector
from pose.models.riding_phase import RidingPhase


def test_throttle_moves_idle_to_acceleration():
    detector = RidingPhaseDetector()

    phase = detector.update(
        throttle_progress=0.30,
    )

    assert phase == RidingPhase.ACCELERATION


def test_low_throttle_keeps_idle():
    detector = RidingPhaseDetector()

    phase = detector.update(
        throttle_progress=0.10,
    )

    assert phase == RidingPhase.IDLE


def test_brake_moves_acceleration_to_braking():
    detector = RidingPhaseDetector()

    detector.update(
        throttle_progress=0.40,
    )

    phase = detector.update(
        throttle_progress=0.0,
        front_brake_progress=0.30,
    )

    assert phase == RidingPhase.BRAKING


def test_rear_brake_moves_acceleration_to_braking():
    detector = RidingPhaseDetector()

    detector.update(
        throttle_progress=0.40,
    )

    phase = detector.update(
        throttle_progress=0.0,
        rear_brake_progress=0.30,
    )

    assert phase == RidingPhase.BRAKING


def test_braking_moves_to_cornering_when_body_leans():
    detector = RidingPhaseDetector()

    detector.update(
        throttle_progress=0.40,
    )

    detector.update(
        throttle_progress=0.0,
        front_brake_progress=0.30,
    )

    phase = detector.update(
        throttle_progress=0.10,
        front_brake_progress=0.0,
        rear_brake_progress=0.0,
        torso_angle=35.0,
    )

    assert phase == RidingPhase.CORNERING


def test_cornering_moves_to_exit_on_throttle_and_upright_body():
    detector = RidingPhaseDetector()

    detector.update(
        throttle_progress=0.40,
    )

    detector.update(
        throttle_progress=0.0,
        front_brake_progress=0.30,
    )

    detector.update(
        throttle_progress=0.10,
        front_brake_progress=0.0,
        rear_brake_progress=0.0,
        torso_angle=35.0,
    )

    phase = detector.update(
        throttle_progress=0.40,
        front_brake_progress=0.0,
        rear_brake_progress=0.0,
        torso_angle=15.0,
    )

    assert phase == RidingPhase.EXIT