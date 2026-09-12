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
        throttle_progress=0.0,
        front_brake_progress=0.30,
    )

    phase = None

    for _ in range(3):
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

    for _ in range(3):
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
        torso_angle=88.0,
    )

    assert phase == RidingPhase.EXIT


def test_exit_moves_back_to_acceleration():
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

    detector.update(
        throttle_progress=0.40,
        front_brake_progress=0.0,
        rear_brake_progress=0.0,
        torso_angle=15.0,
    )

    phase = detector.update(
        throttle_progress=0.50,
        front_brake_progress=0.0,
        rear_brake_progress=0.0,
        torso_angle=10.0,
    )

    assert phase == RidingPhase.ACCELERATION


def test_cornering_transitions_to_exit_when_rider_returns_upright():
    detector = RidingPhaseDetector()

    detector._phase = RidingPhase.CORNERING

    phase = detector.update(
        throttle_progress=0.50,
        front_brake_progress=0.0,
        rear_brake_progress=0.0,
        torso_angle=88.0,
    )

    assert phase == RidingPhase.EXIT


def test_braking_does_not_switch_to_cornering_on_single_frame():
    detector = RidingPhaseDetector()

    # Enter BRAKING.
    phase = detector.update(
        throttle_progress=0.0,
        front_brake_progress=0.30,
        rear_brake_progress=0.0,
        torso_angle=50.0,
    )
    assert phase == RidingPhase.BRAKING

    # Brake briefly drops below the threshold.
    phase = detector.update(
        throttle_progress=0.0,
        front_brake_progress=0.05,
        rear_brake_progress=0.0,
        torso_angle=50.0,
    )

    # One frame must not be enough to enter CORNERING.
    assert phase == RidingPhase.BRAKING


def test_braking_switches_to_cornering_after_three_stable_frames():
    detector = RidingPhaseDetector()

    detector.update(
        throttle_progress=0.0,
        front_brake_progress=0.30,
        rear_brake_progress=0.0,
        torso_angle=50.0,
    )

    for _ in range(2):
        phase = detector.update(
            throttle_progress=0.0,
            front_brake_progress=0.05,
            rear_brake_progress=0.0,
            torso_angle=50.0,
        )

        assert phase == RidingPhase.BRAKING

    phase = detector.update(
        throttle_progress=0.0,
        front_brake_progress=0.05,
        rear_brake_progress=0.0,
        torso_angle=50.0,
    )

    assert phase == RidingPhase.CORNERING