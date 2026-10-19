import pytest
from pose.analyzers.handlebar_steering_detector import (
    HandlebarSteeringDetector,
)


def test_neutral_handlebar_position():
    detector = HandlebarSteeringDetector()

    detector.calibrate(
        left_wrist_z=-0.20,
        right_wrist_z=-0.20,
    )

    steering = detector.update(
        left_wrist_z=-0.20,
        right_wrist_z=-0.20,
    )

    assert steering == 0.0


def test_both_hands_moving_forward_does_not_steer():
    detector = HandlebarSteeringDetector()

    detector.calibrate(
        left_wrist_z=-0.20,
        right_wrist_z=-0.20,
    )

    steering = detector.update(
        left_wrist_z=-0.30,
        right_wrist_z=-0.30,
    )

    assert steering == 0.0


def test_opposite_hand_movement_produces_steering():
    detector = HandlebarSteeringDetector()

    detector.calibrate(
        left_wrist_z=-0.20,
        right_wrist_z=-0.20,
    )

    # Leva šaka napred, desna nazad.
    steering = detector.update(
        left_wrist_z=-0.30,
        right_wrist_z=-0.10,
    )

    assert steering < 0.0


def test_opposite_hand_movement_reverses_steering():
    detector = HandlebarSteeringDetector()

    detector.calibrate(
        left_wrist_z=-0.20,
        right_wrist_z=-0.20,
    )

    # Leva šaka nazad, desna napred.
    steering = detector.update(
        left_wrist_z=-0.10,
        right_wrist_z=-0.30,
    )

    assert steering > 0.0


def test_larger_hand_movement_produces_more_steering():
    detector = HandlebarSteeringDetector()

    detector.calibrate(
        left_wrist_z=-0.20,
        right_wrist_z=-0.20,
    )

    small_steering = detector.update(
        left_wrist_z=-0.22,
        right_wrist_z=-0.18,
    )

    large_steering = detector.update(
        left_wrist_z=-0.30,
        right_wrist_z=-0.10,
    )

    assert abs(large_steering) > abs(small_steering)


def test_steering_is_clamped_to_unit_range():
    detector = HandlebarSteeringDetector()

    detector.calibrate(
        left_wrist_z=-0.20,
        right_wrist_z=-0.20,
    )

    steering = detector.update(
        left_wrist_z=-2.0,
        right_wrist_z=2.0,
    )

    assert steering == -1.0


def test_missing_wrist_returns_neutral_steering():
    detector = HandlebarSteeringDetector()

    detector.calibrate(
        left_wrist_z=-0.20,
        right_wrist_z=-0.20,
    )

    steering = detector.update(
        left_wrist_z=None,
        right_wrist_z=-0.10,
    )

    assert steering == 0.0


def test_steering_sensitivity():
    detector = HandlebarSteeringDetector(
        sensitivity=5.0,
    )

    detector.calibrate(
        left_wrist_z=-0.20,
        right_wrist_z=-0.20,
    )

    steering = detector.update(
        left_wrist_z=-0.25,
        right_wrist_z=-0.15,
    )

    assert abs(steering - (-0.5)) < 1e-9


def test_steering_sensitivity_is_symmetric():
    detector = HandlebarSteeringDetector(
        sensitivity=5.0,
    )

    detector.calibrate(
        left_wrist_z=-0.20,
        right_wrist_z=-0.20,
    )

    left = detector.update(
        left_wrist_z=-0.25,
        right_wrist_z=-0.15,
    )

    right = detector.update(
        left_wrist_z=-0.15,
        right_wrist_z=-0.25,
    )

    assert abs(left + right) < 1e-9
    assert abs(left) == 0.5


from types import SimpleNamespace


def test_pose_wrist_depth_is_accessible():
    landmarks = [
        SimpleNamespace(z=0.0)
        for _ in range(33)
    ]

    landmarks[15].z = -0.25  # LEFT_WRIST
    landmarks[16].z = -0.15  # RIGHT_WRIST

    left_z = landmarks[15].z
    right_z = landmarks[16].z

    assert left_z == -0.25
    assert right_z == -0.15


def test_right_turn_from_horizontal_wrist_positions():
    detector = HandlebarSteeringDetector()

    detector.calibrate_x(
        left_wrist_x=0.194,
        right_wrist_x=-0.104,
    )

    steering = detector.update_x(
        left_wrist_x=0.100,
        right_wrist_x=-0.020,
    )

    assert steering > 0.0


def test_horizontal_steering_returns_to_neutral():
    detector = HandlebarSteeringDetector()

    detector.calibrate_x(
        left_wrist_x=0.194,
        right_wrist_x=-0.104,
    )

    detector.update_x(
        left_wrist_x=0.100,
        right_wrist_x=-0.020,
    )

    steering = detector.update_x(
        left_wrist_x=0.194,
        right_wrist_x=-0.104,
    )

    assert steering == pytest.approx(0.0)


def test_horizontal_steering_left_turn():
        detector = HandlebarSteeringDetector()

        detector.calibrate_x(
            left_wrist_x=0.194,
            right_wrist_x=-0.104,
        )

        steering = detector.update_x(
            left_wrist_x=0.250,
            right_wrist_x=-0.150,
        )

        assert steering < 0.0


@pytest.mark.parametrize(
    "left_x, right_x",
    [
        (None, -0.104),
        (0.194, None),
        (None, None),
    ],
)
def test_horizontal_steering_handles_missing_wrist(
    left_x, right_x
):
    detector = HandlebarSteeringDetector()

    detector.calibrate_x(
        left_wrist_x=0.194,
        right_wrist_x=-0.104,
    )

    steering = detector.update_x(
        left_wrist_x=left_x,
        right_wrist_x=right_x,
    )

    assert steering == 0.0


def test_horizontal_steering_without_calibration():
    detector = HandlebarSteeringDetector()

    steering = detector.update_x(
        left_wrist_x=0.194,
        right_wrist_x=-0.104,
    )

    assert steering == 0.0


def test_horizontal_steering_sensitivity():
    detector = HandlebarSteeringDetector(sensitivity=2.0)

    detector.calibrate_x(
        left_wrist_x=0.194,
        right_wrist_x=-0.104,
    )

    steering = detector.update_x(
        left_wrist_x=0.100,
        right_wrist_x=-0.020,
    )

    assert steering == pytest.approx(0.356)


def test_horizontal_steering_is_clamped():
    detector = HandlebarSteeringDetector(sensitivity=10.0)

    detector.calibrate_x(
        left_wrist_x=0.194,
        right_wrist_x=-0.104,
    )

    steering = detector.update_x(
        left_wrist_x=0.100,
        right_wrist_x=-0.020,
    )

    assert steering == 1.0


def test_horizontal_steering_negative_clamp():
    detector = HandlebarSteeringDetector(sensitivity=10.0)

    detector.calibrate_x(
        left_wrist_x=0.194,
        right_wrist_x=-0.104,
    )

    steering = detector.update_x(
        left_wrist_x=0.350,
        right_wrist_x=-0.150,
    )

    assert steering == -1.0


def test_horizontal_steering_deadzone():
    detector = HandlebarSteeringDetector()

    detector.calibrate_x(
        left_wrist_x=0.194,
        right_wrist_x=-0.104,
    )

    steering = detector.update_x(
        left_wrist_x=0.164,
        right_wrist_x=-0.104,
    )

    assert steering == 0.0