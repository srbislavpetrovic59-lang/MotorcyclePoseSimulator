import pytest
from pose.models.gear_shift_calibration import GearShiftCalibration


def test_learns_rest_position_from_stable_samples():
    calibration = GearShiftCalibration()

    rest_samples = [
        (-0.0105, 0.116, 176.8),
        (-0.0106, 0.115, 176.9),
        (-0.0107, 0.116, 177.0),
        (-0.0106, 0.115, 176.8),
        (-0.0107, 0.116, 176.9),
    ]

    for forward, drop, angle in rest_samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    assert calibration.rest_forward == pytest.approx(-0.01062)
    assert calibration.rest_drop == pytest.approx(0.1156)
    assert calibration.rest_angle == pytest.approx(176.88)

def test_does_not_learn_rest_from_unstable_samples():
    calibration = GearShiftCalibration()

    unstable_samples = [
        (-0.010, 0.115, 176.0),
        (-0.020, 0.130, 165.0),
        (0.005, 0.100, 182.0),
        (-0.030, 0.145, 155.0),
        (0.010, 0.095, 185.0),
    ]

    for forward, drop, angle in unstable_samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    assert calibration.rest_forward is None
    assert calibration.rest_drop is None
    assert calibration.rest_angle is None

def test_does_not_learn_rest_before_enough_samples():
    calibration = GearShiftCalibration()

    samples = [
        (-0.0105, 0.116, 176.8),
        (-0.0106, 0.115, 176.9),
        (-0.0107, 0.116, 177.0),
        (-0.0106, 0.115, 176.8),
    ]

    for forward, drop, angle in samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    assert calibration.rest_forward is None
    assert calibration.rest_drop is None
    assert calibration.rest_angle is None

def test_real_rest_window_is_stable():
    calibration = GearShiftCalibration()

    samples = [
        (-0.0121, 0.11538642644882202, 175.6),
        (-0.0122, 0.11486434936523438, 175.5),
        (-0.0122, 0.11484903097152710, 175.5),
        (-0.0122, 0.11477601528167725, 175.6),
        (-0.0121, 0.11471205949783325, 175.7),
    ]

    for forward, drop, angle in samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    assert calibration._is_rest_window_stable() is True

def test_unstable_rest_window_is_not_stable():
    calibration = GearShiftCalibration()

    samples = [
        (-0.010, 0.115, 176.0),
        (-0.020, 0.130, 165.0),
        (0.005, 0.100, 182.0),
        (-0.030, 0.145, 155.0),
        (0.010, 0.095, 185.0),
    ]

    for forward, drop, angle in samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    assert calibration._is_rest_window_stable() is False

def test_real_rest_window_with_natural_noise_is_stable():
    calibration = GearShiftCalibration()

    samples = [
        (-0.0117, 0.1170879602432251, 176.0),
        (-0.0119, 0.11722564697265625, 176.0),
        (-0.0120, 0.11720585823059082, 175.9),
        (-0.0121, 0.1170583963394165, 175.8),
        (-0.0121, 0.11699312925338745, 175.8),
    ]

    for forward, drop, angle in samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    assert calibration._is_rest_window_stable() is True

def test_rest_window_is_not_stable_when_drop_and_angle_move():
    calibration = GearShiftCalibration()

    samples = [
        (-0.0121, 0.115, 176.0),
        (-0.0122, 0.120, 172.0),
        (-0.0121, 0.130, 165.0),
        (-0.0122, 0.140, 158.0),
        (-0.0121, 0.150, 150.0),
    ]

    for forward, drop, angle in samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    assert calibration._is_rest_window_stable() is False

def test_rest_window_is_unstable_when_angle_moves():
    calibration = GearShiftCalibration()

    samples = [
        (-0.0121, 0.115, 176.0),
        (-0.0122, 0.115, 170.0),
        (-0.0121, 0.115, 164.0),
        (-0.0122, 0.115, 158.0),
        (-0.0121, 0.115, 152.0),
    ]

    for forward, drop, angle in samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    assert calibration._is_rest_window_stable() is False
