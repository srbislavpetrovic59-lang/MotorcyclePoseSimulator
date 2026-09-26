import pytest
from pose.models.gear_shift_calibration import GearShiftCalibration
from pose.analyzers.gear_shift_detector import GearShiftDetector


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

def test_gear_shift_detector_has_calibration():
    detector = GearShiftDetector()

    assert isinstance(
        detector._calibration,
        GearShiftCalibration,
    )
def test_gear_shift_detector_feeds_rest_sample_to_calibration():
    detector = GearShiftDetector()
    
    detector.update(
        left_foot_drop=0.116,
        left_foot_angle=176.0,
        left_foot_forward=-0.0121,
        elapsed_seconds=6.1,
    )

    assert len(detector._calibration._rest_samples) == 1

def test_gear_shift_detector_learns_rest_through_update():
    detector = GearShiftDetector()

    rest_samples = [
        (-0.0105, 0.116, 176.8),
        (-0.0106, 0.115, 176.9),
        (-0.0107, 0.116, 177.0),
        (-0.0106, 0.115, 176.8),
        (-0.0107, 0.116, 176.9),
    ]

    for index, (forward, drop, angle) in enumerate(rest_samples):
        detector.update(
            left_foot_drop=drop,
            left_foot_angle=angle,
            left_foot_forward=forward,
            elapsed_seconds=6.1 + index * 0.05,
        )

    assert detector._calibration.rest_forward == pytest.approx(-0.01062)
    assert detector._calibration.rest_drop == pytest.approx(0.1156)
    assert detector._calibration.rest_angle == pytest.approx(176.88)

def test_calculates_movement_from_rest():
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

    movement = calibration.movement_from_rest(
        forward=-0.0130,
        drop=0.120,
        angle=175.0,
    )

    assert movement["forward"] == pytest.approx(-0.00238)
    assert movement["drop"] == pytest.approx(0.0044)
    assert movement["angle"] == pytest.approx(-1.88)

#=======================test kalibracije sa stvarnim podacima========================
def test_calculates_real_live_movement_from_rest():
    calibration = GearShiftCalibration()

    rest_samples = [
        (0.0234, 0.10357, 162.9),
        (0.0234, 0.10346, 162.9),
        (0.0234, 0.10325, 162.9),
        (0.0235, 0.10266, 162.8),
        (0.0234, 0.10273, 162.9),
    ]

    for forward, drop, angle in rest_samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    movement = calibration.movement_from_rest(
        forward=0.0219,
        drop=0.09445,
        angle=163.7,
    )

    assert movement["forward"] < 0
    assert movement["drop"] < 0
    assert movement["angle"] > 0

#============Tu prvi put počinjemo da učimo SHIFT_UP================================
def test_learns_shift_up_movement_from_rest():
    calibration = GearShiftCalibration()

    rest_samples = [
        (0.0234, 0.10357, 162.9),
        (0.0234, 0.10346, 162.9),
        (0.0234, 0.10325, 162.9),
        (0.0235, 0.10266, 162.8),
        (0.0234, 0.10273, 162.9),
    ]

    for forward, drop, angle in rest_samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    calibration.add_shift_up_sample(
        forward=0.0219,
        drop=0.09445,
        angle=163.7,
    )

    assert calibration.shift_up_forward < 0
    assert calibration.shift_up_drop < 0
    assert calibration.shift_up_angle > 0

def test_learns_shift_up_from_movement_sequence():
    calibration = GearShiftCalibration()

    rest_samples = [
        (0.0234, 0.10357, 162.9),
        (0.0234, 0.10346, 162.9),
        (0.0234, 0.10325, 162.9),
        (0.0235, 0.10266, 162.8),
        (0.0234, 0.10273, 162.9),
    ]

    for forward, drop, angle in rest_samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    shift_up_samples = [
        (0.0230, 0.1010, 163.1),
        (0.0225, 0.0980, 163.4),
        (0.0219, 0.09445, 163.7),
        (0.0226, 0.0985, 163.3),
        (0.0233, 0.1020, 163.0),
    ]

    calibration.add_shift_up_sequence(
        shift_up_samples
    )

    assert len(calibration.shift_up_sequence) == 5

def test_shift_up_sequence_is_relative_to_rest():
    calibration = GearShiftCalibration()

    rest_samples = [
        (0.0234, 0.10357, 162.9),
        (0.0234, 0.10346, 162.9),
        (0.0234, 0.10325, 162.9),
        (0.0235, 0.10266, 162.8),
        (0.0234, 0.10273, 162.9),
    ]

    for forward, drop, angle in rest_samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    shift_up_samples = [
        (0.0230, 0.1010, 163.1),
        (0.0225, 0.0980, 163.4),
        (0.0219, 0.09445, 163.7),
    ]

    calibration.add_shift_up_sequence(
        shift_up_samples
    )

    first = calibration.shift_up_sequence[0]

    assert first["forward"] == pytest.approx(
        0.0230 - calibration.rest_forward
    )
    assert first["drop"] == pytest.approx(
        0.1010 - calibration.rest_drop
    )
    assert first["angle"] == pytest.approx(
        163.1 - calibration.rest_angle
    )

def test_shift_up_sequence_moves_away_and_returns_toward_rest():
    calibration = GearShiftCalibration()

    rest_samples = [
        (0.0234, 0.10357, 162.9),
        (0.0234, 0.10346, 162.9),
        (0.0234, 0.10325, 162.9),
        (0.0235, 0.10266, 162.8),
        (0.0234, 0.10273, 162.9),
    ]

    for forward, drop, angle in rest_samples:
        calibration.add_rest_sample(
            forward=forward,
            drop=drop,
            angle=angle,
        )

    shift_up_samples = [
        (0.0230, 0.1010, 163.1),
        (0.0225, 0.0980, 163.4),
        (0.0219, 0.09445, 163.7),
        (0.0226, 0.0985, 163.3),
        (0.0233, 0.1020, 163.0),
    ]

    calibration.add_shift_up_sequence(
        shift_up_samples
    )

    distances = calibration.shift_up_distances_from_rest()

    assert distances[0] < distances[2]
    assert distances[4] < distances[2]

def test_shift_up_sequence_has_movement_away_from_rest_and_return():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.0210
    calibration.rest_drop = 0.1040
    calibration.rest_angle = 165.0

    shift_up_samples = [
        (0.0210, 0.1040, 165.0),  # REST
        (0.0220, 0.1020, 164.5),  # moving away
        (0.0235, 0.0980, 163.2),  # active movement
        (0.0225, 0.1000, 164.0),  # returning
        (0.0211, 0.1035, 164.9),  # near REST
    ]

    calibration.add_shift_up_sequence(shift_up_samples)

    assert calibration.shift_up_has_away_and_return_pattern() is True
