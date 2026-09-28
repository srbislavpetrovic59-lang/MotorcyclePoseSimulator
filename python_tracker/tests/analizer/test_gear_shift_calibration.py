import pytest
from pose.models.gear_shift_calibration import GearShiftCalibration
from pose.analyzers.gear_shift_detector import GearShiftDetector
from statistics import median

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

def test_shift_up_ranges_use_each_signals_own_extreme():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    samples = [
        (0.020, 0.100, 165.0),  # REST
        (0.024, 0.098, 164.0),  # forward extreme
        (0.023, 0.092, 163.5),  # drop extreme
        (0.022, 0.096, 162.0),  # angle extreme
        (0.020, 0.100, 165.0),  # REST
    ]

    calibration.add_shift_up_sequence(samples)

    ranges = calibration.shift_up_ranges()

    assert ranges["forward"] == 0.004
    assert ranges["drop"] == pytest.approx(0.008)
    assert ranges["angle"] == 3.0

def test_shift_up_movement_is_normalized_by_calibrated_ranges():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    calibration.shift_up_sequence = [
        {"forward": 0.004, "drop": -0.008, "angle": -2.0},
    ]

    normalized = calibration.normalized_movement_from_rest(
        forward=0.022,
        drop=0.096,
        angle=164.0,
    )

    assert normalized["forward"] == pytest.approx(0.5)
    assert normalized["drop"] == pytest.approx(-0.5)
    assert normalized["angle"] == pytest.approx(-0.5)

def test_shift_up_normalized_distances_move_away_and_return():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    calibration.shift_up_sequence = [
        {"forward": 0.000, "drop": 0.000, "angle": 0.0},
        {"forward": 0.002, "drop": -0.004, "angle": -1.0},
        {"forward": 0.004, "drop": -0.008, "angle": -2.0},
        {"forward": 0.002, "drop": -0.004, "angle": -1.0},
        {"forward": 0.000, "drop": 0.000, "angle": 0.0},
    ]

    distances = calibration.shift_up_normalized_distances_from_rest()

    assert distances[0] < distances[2]
    assert distances[4] < distances[2]

def test_shift_up_pattern_uses_normalized_distances(monkeypatch):
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    calibration.shift_up_sequence = [
        {"forward": 0.000, "drop": 0.000, "angle": 0.0},
        {"forward": 0.002, "drop": -0.004, "angle": -1.0},
        {"forward": 0.004, "drop": -0.008, "angle": -2.0},
        {"forward": 0.002, "drop": -0.004, "angle": -1.0},
        {"forward": 0.000, "drop": 0.000, "angle": 0.0},
    ]

    def fail_if_old_distances_are_used():
        raise AssertionError("old unnormalized distances were used")

        monkeypatch.setattr(
        calibration,
        "shift_up_distances_from_rest",
        fail_if_old_distances_are_used,
        )

        assert calibration.shift_up_has_away_and_return_pattern() is True

def test_normalized_shift_up_distance_ignores_zero_range_signal():
    calibration = GearShiftCalibration()

    calibration.shift_up_sequence = [
        {"forward": 0.000, "drop": 0.000, "angle": 0.0},
        {"forward": 0.000, "drop": -0.004, "angle": -1.0},
        {"forward": 0.000, "drop": -0.008, "angle": -2.0},
    ]

    distances = calibration.shift_up_normalized_distances_from_rest()

    assert distances[0] == pytest.approx(0.0)
    assert distances[1] > distances[0]
    assert distances[2] > distances[1]

def test_rest_uses_only_latest_stable_window():
    calibration = GearShiftCalibration()

    # Earlier movement / unstable samples.
    calibration.add_rest_sample(0.010, 0.080, 150.0)
    calibration.add_rest_sample(0.030, 0.120, 175.0)

    # Stable REST window.
    stable_samples = [
        (0.0200, 0.1000, 165.0),
        (0.0201, 0.1005, 165.2),
        (0.0202, 0.1010, 165.4),
        (0.0201, 0.1008, 165.3),
        (0.0200, 0.1004, 165.1),
    ]

    for forward, drop, angle in stable_samples:
        calibration.add_rest_sample(forward, drop, angle)

    assert calibration.rest_forward == pytest.approx(
        sum(sample[0] for sample in stable_samples) / 5
    )

def test_normalized_movement_ignores_zero_range_signal():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    calibration.shift_up_sequence = [
        {"forward": 0.000, "drop": -0.008, "angle": -2.0},
    ]

    normalized = calibration.normalized_movement_from_rest(
        forward=0.020,
        drop=0.096,
        angle=164.0,
    )

    assert normalized["forward"] == pytest.approx(0.0)
    assert normalized["drop"] == pytest.approx(-0.5)
    assert normalized["angle"] == pytest.approx(-0.5)

def test_calibration_stores_multiple_shift_up_attempts():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    first_attempt = [
        (0.020, 0.100, 165.0),
        (0.024, 0.094, 163.0),
        (0.020, 0.100, 165.0),
    ]

    second_attempt = [
        (0.020, 0.100, 165.0),
        (0.023, 0.092, 162.0),
        (0.020, 0.100, 165.0),
    ]

    calibration.add_shift_up_sequence(first_attempt)
    calibration.add_shift_up_sequence(second_attempt)

    assert len(calibration.shift_up_sequences) == 2

def test_shift_up_typical_forward_range_uses_median_of_attempts():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.096, 164.0),  # forward range 0.004
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.026, 0.095, 163.0),  # forward range 0.006
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.040, 0.090, 160.0),  # outlier: 0.020
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in attempts:
        calibration.add_shift_up_sequence(attempt)

    ranges = calibration.shift_up_typical_ranges()

    assert ranges["forward"] == pytest.approx(0.006)

def test_shift_up_typical_drop_range_uses_median_of_attempts():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.096, 164.0),  # drop range 0.004
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.092, 163.0),  # drop range 0.008
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.026, 0.070, 162.0),  # outlier: 0.030
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in attempts:
        calibration.add_shift_up_sequence(attempt)

    ranges = calibration.shift_up_typical_ranges()

    assert ranges["drop"] == pytest.approx(0.008)

def test_shift_up_typical_angle_range_uses_median_of_attempts():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.096, 163.0),  # angle range 2.0
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.094, 162.0),  # angle range 3.0
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.026, 0.092, 150.0),  # outlier: 15.0
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in attempts:
        calibration.add_shift_up_sequence(attempt)

    ranges = calibration.shift_up_typical_ranges()

    assert ranges["angle"] == pytest.approx(3.0)

def test_shift_up_attempt_has_normalized_distance_trajectory():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempt = [
        (0.020, 0.100, 165.0),  # REST
        (0.022, 0.096, 164.0),  # away
        (0.024, 0.092, 162.0),  # farther away
        (0.022, 0.096, 164.0),  # returning
        (0.020, 0.100, 165.0),  # REST
    ]

    calibration.add_shift_up_sequence(attempt)

    trajectory = calibration.shift_up_normalized_trajectory(
        calibration.shift_up_sequences[0]
    )

    assert trajectory[0] == pytest.approx(0.0)
    assert trajectory[0] < trajectory[1] < trajectory[2]
    assert trajectory[2] > trajectory[3] > trajectory[4]
    assert trajectory[4] == pytest.approx(0.0)

def test_shift_up_attempt_has_normalized_component_trajectory():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempt = [
        (0.020, 0.100, 165.0),
        (0.022, 0.096, 164.0),
        (0.024, 0.092, 162.0),
        (0.020, 0.100, 165.0),
    ]

    calibration.add_shift_up_sequence(attempt)

    trajectory = calibration.shift_up_normalized_component_trajectory(
        calibration.shift_up_sequences[0]
    )

    assert trajectory[0] == {
        "forward": pytest.approx(0.0),
        "drop": pytest.approx(0.0),
        "angle": pytest.approx(0.0),
    }

    assert trajectory[2] == {
        "forward": pytest.approx(1.0),
        "drop": pytest.approx(-1.0),
        "angle": pytest.approx(-1.0),
    }

    assert trajectory[-1] == {
        "forward": pytest.approx(0.0),
        "drop": pytest.approx(0.0),
        "angle": pytest.approx(0.0),
    }

def test_typical_shift_up_trajectory_uses_median_per_component():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.096, 163.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.026, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.040, 0.070, 150.0),  # outlier
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in attempts:
        calibration.add_shift_up_sequence(attempt)

    trajectory = calibration.shift_up_typical_trajectory()

    assert trajectory[0] == {
        "forward": pytest.approx(0.0),
        "drop": pytest.approx(0.0),
        "angle": pytest.approx(0.0),
    }

    assert trajectory[1] == {
        "forward": pytest.approx(1.0),
        "drop": pytest.approx(-1.0),
        "angle": pytest.approx(-1.0),
    }

    assert trajectory[2] == {
        "forward": pytest.approx(0.0),
        "drop": pytest.approx(0.0),
        "angle": pytest.approx(0.0),
    }

def test_typical_shift_up_trajectory_handles_attempts_with_different_lengths():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    short_attempt = [
        (0.020, 0.100, 165.0),
        (0.024, 0.092, 162.0),
        (0.020, 0.100, 165.0),
    ]

    long_attempt = [
        (0.020, 0.100, 165.0),
        (0.022, 0.096, 164.0),
        (0.024, 0.092, 162.0),
        (0.022, 0.096, 164.0),
        (0.020, 0.100, 165.0),
    ]

    calibration.add_shift_up_sequence(short_attempt)
    calibration.add_shift_up_sequence(long_attempt)

    trajectory = calibration.shift_up_typical_trajectory()

    assert len(trajectory) == 5

def test_shift_up_trajectory_can_be_resampled_to_five_points():
    calibration = GearShiftCalibration()

    trajectory = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 1.0, "drop": -1.0, "angle": -1.0},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    resampled = calibration.resample_shift_up_trajectory(
        trajectory,
        target_length=5,
    )

    assert resampled == [
        {
            "forward": pytest.approx(0.0),
            "drop": pytest.approx(0.0),
            "angle": pytest.approx(0.0),
        },
        {
            "forward": pytest.approx(0.5),
            "drop": pytest.approx(-0.5),
            "angle": pytest.approx(-0.5),
        },
        {
            "forward": pytest.approx(1.0),
            "drop": pytest.approx(-1.0),
            "angle": pytest.approx(-1.0),
        },
        {
            "forward": pytest.approx(0.5),
            "drop": pytest.approx(-0.5),
            "angle": pytest.approx(-0.5),
        },
        {
            "forward": pytest.approx(0.0),
            "drop": pytest.approx(0.0),
            "angle": pytest.approx(0.0),
        },
    ]

def test_identical_shift_up_trajectories_have_zero_distance():
    calibration = GearShiftCalibration()

    trajectory = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 1.0, "drop": -1.0, "angle": -1.0},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    distance = calibration.shift_up_trajectory_distance(
        trajectory,
        trajectory,
    )

    assert distance == pytest.approx(0.0)

def test_different_shift_up_trajectories_have_nonzero_distance():
    calibration = GearShiftCalibration()

    typical = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 1.0, "drop": -1.0, "angle": -1.0},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    different = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 0.2, "drop": -0.1, "angle": -0.2},
        {"forward": 0.3, "drop": -0.2, "angle": -0.1},
        {"forward": 0.1, "drop": -0.1, "angle": -0.1},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    distance = calibration.shift_up_trajectory_distance(
        typical,
        different,
    )

    assert distance > 0.0

def test_more_similar_shift_up_trajectory_has_smaller_distance():
    calibration = GearShiftCalibration()

    typical = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 1.0, "drop": -1.0, "angle": -1.0},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    similar = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 0.45, "drop": -0.45, "angle": -0.45},
        {"forward": 0.9, "drop": -0.9, "angle": -0.9},
        {"forward": 0.45, "drop": -0.45, "angle": -0.45},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    different = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 0.1, "drop": -0.1, "angle": -0.1},
        {"forward": 0.2, "drop": -0.2, "angle": -0.2},
        {"forward": 0.1, "drop": -0.1, "angle": -0.1},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    similar_distance = calibration.shift_up_trajectory_distance(
        typical,
        similar,
    )

    different_distance = calibration.shift_up_trajectory_distance(
        typical,
        different,
    )

    assert similar_distance < different_distance

def test_longer_similar_trajectory_matches_after_resampling():
    calibration = GearShiftCalibration()

    typical = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 1.0, "drop": -1.0, "angle": -1.0},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    longer = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 0.25, "drop": -0.25, "angle": -0.25},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 0.75, "drop": -0.75, "angle": -0.75},
        {"forward": 1.0, "drop": -1.0, "angle": -1.0},
        {"forward": 0.75, "drop": -0.75, "angle": -0.75},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 0.25, "drop": -0.25, "angle": -0.25},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    resampled = calibration.resample_shift_up_trajectory(
        longer,
        target_length=len(typical),
    )

    distance = calibration.shift_up_trajectory_distance(
        typical,
        resampled,
    )

    assert distance == pytest.approx(0.0)

def test_opposite_trajectory_is_farther_than_similar_shift_up():
    calibration = GearShiftCalibration()

    typical = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 1.0, "drop": -1.0, "angle": -1.0},
        {"forward": 0.5, "drop": -0.5, "angle": -0.5},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    similar = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": 0.45, "drop": -0.45, "angle": -0.45},
        {"forward": 0.9, "drop": -0.9, "angle": -0.9},
        {"forward": 0.45, "drop": -0.45, "angle": -0.45},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    opposite = [
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
        {"forward": -0.5, "drop": 0.5, "angle": 0.5},
        {"forward": -1.0, "drop": 1.0, "angle": 1.0},
        {"forward": -0.5, "drop": 0.5, "angle": 0.5},
        {"forward": 0.0, "drop": 0.0, "angle": 0.0},
    ]

    similar_distance = calibration.shift_up_trajectory_distance(
        typical,
        similar,
    )

    opposite_distance = calibration.shift_up_trajectory_distance(
        typical,
        opposite,
    )

    assert opposite_distance > similar_distance

def test_new_shift_up_trajectory_can_be_compared_with_learned_typical_trajectory():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    learned_attempt = [
        (0.020, 0.100, 165.0),
        (0.022, 0.096, 164.0),
        (0.024, 0.092, 162.0),
        (0.022, 0.096, 164.0),
        (0.020, 0.100, 165.0),
    ]

    calibration.add_shift_up_sequence(learned_attempt)

    new_attempt = [
        (0.020, 0.100, 165.0),
        (0.022, 0.096, 164.0),
        (0.024, 0.092, 162.0),
        (0.022, 0.096, 164.0),
        (0.020, 0.100, 165.0),
    ]

    distance = calibration.shift_up_distance_from_typical(
        new_attempt
    )

    assert distance == pytest.approx(0.0)

def test_similar_new_attempt_is_closer_to_learned_shift_up_than_different_attempt():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    learned_attempt = [
        (0.020, 0.100, 165.0),
        (0.022, 0.096, 164.0),
        (0.024, 0.092, 162.0),
        (0.022, 0.096, 164.0),
        (0.020, 0.100, 165.0),
    ]

    calibration.add_shift_up_sequence(learned_attempt)

    similar_attempt = [
        (0.020, 0.100, 165.0),
        (0.022, 0.095, 164.0),
        (0.024, 0.091, 162.0),
        (0.022, 0.095, 164.0),
        (0.020, 0.100, 165.0),
    ]

    different_attempt = [
        (0.020, 0.100, 165.0),
        (0.018, 0.104, 166.0),
        (0.016, 0.108, 168.0),
        (0.018, 0.104, 166.0),
        (0.020, 0.100, 165.0),
    ]

    similar_distance = calibration.shift_up_distance_from_typical(
        similar_attempt
    )

    different_distance = calibration.shift_up_distance_from_typical(
        different_attempt
    )

    assert similar_distance < different_distance

def test_learned_shift_up_attempts_have_distances_from_typical():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.091, 161.5),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.023, 0.093, 162.5),
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in attempts:
        calibration.add_shift_up_sequence(attempt)

    distances = calibration.shift_up_calibration_distances()

    assert len(distances) == 3
    assert all(distance >= 0.0 for distance in distances)

def test_shift_up_calibration_max_distance_comes_from_learned_attempts():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.091, 161.5),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.023, 0.093, 162.5),
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in attempts:
        calibration.add_shift_up_sequence(attempt)

    distances = calibration.shift_up_calibration_distances()

    max_distance = calibration.shift_up_calibration_max_distance()

    assert max_distance == pytest.approx(max(distances))

def test_shift_up_calibration_max_distance_grows_with_outlier_attempt():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    normal_attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.091, 161.5),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.023, 0.093, 162.5),
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in normal_attempts:
        calibration.add_shift_up_sequence(attempt)

    normal_max_distance = (
        calibration.shift_up_calibration_max_distance()
    )

    outlier_attempt = [
        (0.020, 0.100, 165.0),
        (0.040, 0.070, 150.0),
        (0.020, 0.100, 165.0),
    ]

    calibration.add_shift_up_sequence(outlier_attempt)

    outlier_max_distance = (
        calibration.shift_up_calibration_max_distance()
    )

    assert outlier_max_distance > normal_max_distance

def test_shift_up_calibration_typical_distance_is_median():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.091, 161.5),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.023, 0.093, 162.5),
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in attempts:
        calibration.add_shift_up_sequence(attempt)

    distances = calibration.shift_up_calibration_distances()

    typical_distance = (
        calibration.shift_up_calibration_typical_distance()
    )

    assert typical_distance == pytest.approx(
        median(distances)
    )

def test_shift_up_calibration_typical_distance_is_robust_to_outlier():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    normal_attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.091, 161.5),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.023, 0.093, 162.5),
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in normal_attempts:
        calibration.add_shift_up_sequence(attempt)

    typical_before = (
        calibration.shift_up_calibration_typical_distance()
    )
    max_before = (
        calibration.shift_up_calibration_max_distance()
    )

    outlier_attempt = [
        (0.020, 0.100, 165.0),
        (0.040, 0.070, 150.0),
        (0.020, 0.100, 165.0),
    ]

    calibration.add_shift_up_sequence(outlier_attempt)

    typical_after = (
        calibration.shift_up_calibration_typical_distance()
    )
    max_after = (
        calibration.shift_up_calibration_max_distance()
    )

    typical_change = abs(typical_after - typical_before)
    max_change = abs(max_after - max_before)

    assert typical_change < max_change

def test_shift_up_calibration_distance_deviation_is_median_absolute_deviation():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.091, 161.5),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.023, 0.093, 162.5),
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in attempts:
        calibration.add_shift_up_sequence(attempt)

    distances = calibration.shift_up_calibration_distances()
    typical = median(distances)

    expected_deviation = median(
        abs(distance - typical)
        for distance in distances
    )

    deviation = (
        calibration.shift_up_calibration_distance_deviation()
    )

    assert deviation == pytest.approx(expected_deviation)

def test_shift_up_calibration_distances_can_be_expressed_in_mad_units():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.091, 161.5),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.023, 0.093, 162.5),
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in attempts:
        calibration.add_shift_up_sequence(attempt)

    distances = calibration.shift_up_calibration_distances()
    typical = calibration.shift_up_calibration_typical_distance()
    deviation = calibration.shift_up_calibration_distance_deviation()

    mad_units = (
        [
            abs(distance - typical) / deviation
            for distance in distances
        ]
        if deviation > 0.0
        else None
    )

    print("distances:", distances)
    print("typical:", typical)
    print("MAD:", deviation)
    print("MAD units:", mad_units)

    assert deviation == 0.0
    assert mad_units is None

def test_shift_up_calibration_tiny_distance_deviation_is_treated_as_zero():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.091, 161.5),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.023, 0.093, 162.5),
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in attempts:
        calibration.add_shift_up_sequence(attempt)

    deviation = (
        calibration.shift_up_calibration_distance_deviation()
    )

    assert deviation == 0.0

def test_shift_up_calibration_attempt_count():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempt = [
        (0.020, 0.100, 165.0),
        (0.024, 0.092, 162.0),
        (0.020, 0.100, 165.0),
    ]

    calibration.add_shift_up_sequence(attempt)
    calibration.add_shift_up_sequence(attempt)
    calibration.add_shift_up_sequence(attempt)

    assert calibration.shift_up_calibration_attempt_count() == 3

def test_shift_up_distance_ratio_compares_new_attempt_with_calibration():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.091, 161.5),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.023, 0.093, 162.5),
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    new_attempt = [
        (0.020, 0.100, 165.0),
        (0.024, 0.092, 162.0),
        (0.020, 0.100, 165.0),
    ]

    distance = calibration.shift_up_distance_from_typical(
        new_attempt
    )

    typical_distance = (
        calibration.shift_up_calibration_typical_distance()
    )

    ratio = calibration.shift_up_distance_ratio(
        new_attempt
    )

    assert ratio == pytest.approx(
        distance / typical_distance
    )

def test_shift_up_distance_ratio_is_none_when_typical_distance_is_zero():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    attempt = [
        (0.020, 0.100, 165.0),
        (0.024, 0.092, 162.0),
        (0.020, 0.100, 165.0),
    ]

    calibration.add_shift_up_sequence(attempt)
    calibration.add_shift_up_sequence(attempt)
    calibration.add_shift_up_sequence(attempt)

    new_attempt = [
        (0.020, 0.100, 165.0),
        (0.024, 0.092, 162.0),
        (0.020, 0.100, 165.0),
    ]

    assert calibration.shift_up_calibration_typical_distance() == 0.0

    assert calibration.shift_up_distance_ratio(
        new_attempt
    ) is None

def test_similar_shift_up_attempt_has_smaller_distance_ratio_than_different_attempt():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.100
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.020, 0.100, 165.0),
            (0.024, 0.092, 162.0),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.025, 0.091, 161.5),
            (0.020, 0.100, 165.0),
        ],
        [
            (0.020, 0.100, 165.0),
            (0.023, 0.093, 162.5),
            (0.020, 0.100, 165.0),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    similar_attempt = [
        (0.020, 0.100, 165.0),
        (0.024, 0.091, 162.0),
        (0.020, 0.100, 165.0),
    ]

    different_attempt = [
        (0.020, 0.100, 165.0),
        (0.016, 0.108, 168.0),
        (0.020, 0.100, 165.0),
    ]

    similar_ratio = calibration.shift_up_distance_ratio(
        similar_attempt
    )

    different_ratio = calibration.shift_up_distance_ratio(
        different_attempt
    )

    assert similar_ratio < different_ratio

def test_real_held_out_shift_up_attempt_has_distance_ratio():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    held_out_attempt = [
        (0.0228, 0.10337, 164.2),
        (0.0235, 0.09916, 163.2),
        (0.0218, 0.10075, 164.7),
        (0.0212, 0.09872, 164.9),
        (0.0229, 0.10338, 164.0),
    ]

    ratio = calibration.shift_up_distance_ratio(
        held_out_attempt
    )

    print("real held-out SHIFT_UP ratio:", ratio)

    assert ratio is not None

def test_real_non_shift_segment_has_distance_ratio():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    non_shift_segment = [
        (0.0193, 0.11182, 166.8),
        (0.0194, 0.10847, 166.5),
        (0.0196, 0.10762, 166.3),
        (0.0197, 0.10728, 166.1),
        (0.0196, 0.10717, 166.1),
    ]

    ratio = calibration.shift_up_distance_ratio(
        non_shift_segment
    )

    print("real NON-SHIFT ratio:", ratio)

    assert ratio is not None

def test_second_real_non_shift_segment_has_distance_ratio():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    non_shift_segment = [
        (0.0192, 0.09952, 165.1),
        (0.0193, 0.09968, 165.0),
        (0.0193, 0.09952, 165.0),
        (0.0194, 0.09935, 164.9),
        (0.0195, 0.09934, 164.9),
    ]

    ratio = calibration.shift_up_distance_ratio(
        non_shift_segment
    )

    print("second real NON-SHIFT ratio:", ratio)

    assert ratio is not None

def test_second_real_held_out_shift_up_attempt_has_distance_ratio():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
        [
            (0.0228, 0.10337, 164.2),
            (0.0235, 0.09916, 163.2),
            (0.0218, 0.10075, 164.7),
            (0.0212, 0.09872, 164.9),
            (0.0229, 0.10338, 164.0),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    held_out_attempt = [
        (0.0206, 0.10295, 165.6),
        (0.0233, 0.09721, 163.3),
        (0.0233, 0.09722, 163.6),
        (0.0211, 0.10351, 164.8),
        (0.0206, 0.10479, 165.2),
    ]

    ratio = calibration.shift_up_distance_ratio(
        held_out_attempt
    )

    print("second real held-out SHIFT_UP ratio:", ratio)

    assert ratio is not None

def test_moving_non_shift_has_distance_ratio():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    # Noga se stvarno pomera, ali putanja nije SHIFT_UP:
    # napred + nadole + promena ugla, pa povratak u REST.
    non_shift_movement = [
        (0.0200, 0.1030, 165.0),
        (0.0215, 0.1060, 166.0),
        (0.0230, 0.1100, 168.0),
        (0.0215, 0.1060, 166.0),
        (0.0200, 0.1030, 165.0),
    ]

    ratio = calibration.shift_up_distance_ratio(
        non_shift_movement
    )

    print("moving NON-SHIFT ratio:", ratio)

    assert ratio is not None

def test_shift_up_like_movement_with_wrong_timing_has_distance_ratio():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    # Slične amplitude kao SHIFT_UP,
    # ali namerno pogrešan vremenski redosled komponenti.
    shift_up_like_non_shift = [
        (0.0200, 0.1030, 165.0),
        (0.0205, 0.1025, 163.5),  # ugao se menja prerano
        (0.0230, 0.0980, 164.5),  # forward/drop dolaze kasnije
        (0.0215, 0.1015, 164.8),
        (0.0200, 0.1030, 165.0),
    ]

    ratio = calibration.shift_up_distance_ratio(
        shift_up_like_non_shift
    )

    print("SHIFT_UP-like wrong-timing ratio:", ratio)

    assert ratio is not None

def test_correct_shift_up_timing_is_closer_than_wrong_timing():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    correct_timing = [
        (0.0200, 0.1030, 165.0),
        (0.0215, 0.1015, 164.8),
        (0.0230, 0.0980, 164.5),
        (0.0205, 0.1025, 163.5),
        (0.0200, 0.1030, 165.0),
    ]

    wrong_timing = [
        (0.0200, 0.1030, 165.0),
        (0.0205, 0.1025, 163.5),
        (0.0230, 0.0980, 164.5),
        (0.0215, 0.1015, 164.8),
        (0.0200, 0.1030, 165.0),
    ]

    correct_ratio = calibration.shift_up_distance_ratio(
        correct_timing
    )

    wrong_ratio = calibration.shift_up_distance_ratio(
        wrong_timing
    )

    print("correct timing ratio:", correct_ratio)
    print("wrong timing ratio:", wrong_ratio)

    assert correct_ratio < wrong_ratio

def test_shift_up_trajectory_deltas_preserve_movement_order():
    calibration = GearShiftCalibration()

    trajectory = [
        {
            "forward": 0.000,
            "drop": 0.000,
            "angle": 0.0,
        },
        {
            "forward": 0.002,
            "drop": -0.001,
            "angle": -0.5,
        },
        {
            "forward": 0.005,
            "drop": -0.004,
            "angle": -1.5,
        },
    ]

    deltas = calibration.shift_up_trajectory_deltas(
        trajectory
    )

    assert deltas == [
        {
            "forward": 0.002,
            "drop": -0.001,
            "angle": -0.5,
        },
        {
            "forward": 0.003,
            "drop": -0.003,
            "angle": -1.0,
        },
    ]

def test_shift_up_delta_distance_distinguishes_timing():
    calibration = GearShiftCalibration()

    typical = [
        {"forward": 0.0000, "drop": 0.0000, "angle": 0.0},
        {"forward": 0.0015, "drop": -0.0015, "angle": -0.2},
        {"forward": 0.0030, "drop": -0.0050, "angle": -0.5},
        {"forward": 0.0005, "drop": -0.0005, "angle": -1.5},
        {"forward": 0.0000, "drop": 0.0000, "angle": 0.0},
    ]

    correct_timing = [
        {"forward": 0.0000, "drop": 0.0000, "angle": 0.0},
        {"forward": 0.0015, "drop": -0.0015, "angle": -0.2},
        {"forward": 0.0030, "drop": -0.0050, "angle": -0.5},
        {"forward": 0.0005, "drop": -0.0005, "angle": -1.5},
        {"forward": 0.0000, "drop": 0.0000, "angle": 0.0},
    ]

    wrong_timing = [
        {"forward": 0.0000, "drop": 0.0000, "angle": 0.0},
        {"forward": 0.0005, "drop": -0.0005, "angle": -1.5},
        {"forward": 0.0030, "drop": -0.0050, "angle": -0.5},
        {"forward": 0.0015, "drop": -0.0015, "angle": -0.2},
        {"forward": 0.0000, "drop": 0.0000, "angle": 0.0},
    ]

    typical_deltas = calibration.shift_up_trajectory_deltas(
        typical
    )

    correct_deltas = calibration.shift_up_trajectory_deltas(
        correct_timing
    )

    wrong_deltas = calibration.shift_up_trajectory_deltas(
        wrong_timing
    )

    correct_distance = calibration.shift_up_trajectory_distance(
        typical_deltas,
        correct_deltas,
    )

    wrong_distance = calibration.shift_up_trajectory_distance(
        typical_deltas,
        wrong_deltas,
    )

    print("correct delta distance:", correct_distance)
    print("wrong delta distance:", wrong_distance)

    assert correct_distance < wrong_distance

def test_real_calibration_delta_distance_prefers_correct_timing():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    correct_timing = [
        (0.0200, 0.1030, 165.0),
        (0.0215, 0.1015, 164.8),
        (0.0230, 0.0980, 164.5),
        (0.0205, 0.1025, 163.5),
        (0.0200, 0.1030, 165.0),
    ]

    wrong_timing = [
        (0.0200, 0.1030, 165.0),
        (0.0205, 0.1025, 163.5),
        (0.0230, 0.0980, 164.5),
        (0.0215, 0.1015, 164.8),
        (0.0200, 0.1030, 165.0),
    ]

    typical = calibration.shift_up_typical_trajectory()

    correct = [
        calibration.movement_from_rest(
            forward=forward,
            drop=drop,
            angle=angle,
        )
        for forward, drop, angle in correct_timing
    ]

    wrong = [
        calibration.movement_from_rest(
            forward=forward,
            drop=drop,
            angle=angle,
        )
        for forward, drop, angle in wrong_timing
    ]

    correct = calibration.shift_up_normalized_component_trajectory(
        correct
    )

    wrong = calibration.shift_up_normalized_component_trajectory(
        wrong
    )

    correct = calibration.resample_shift_up_trajectory(
        correct,
        target_length=len(typical),
    )

    wrong = calibration.resample_shift_up_trajectory(
        wrong,
        target_length=len(typical),
    )

    typical_deltas = calibration.shift_up_trajectory_deltas(
        typical
    )

    correct_deltas = calibration.shift_up_trajectory_deltas(
        correct
    )

    wrong_deltas = calibration.shift_up_trajectory_deltas(
        wrong
    )

    correct_distance = calibration.shift_up_trajectory_distance(
        typical_deltas,
        correct_deltas,
    )

    wrong_distance = calibration.shift_up_trajectory_distance(
        typical_deltas,
        wrong_deltas,
    )

    print("real correct delta distance:", correct_distance)
    print("real wrong delta distance:", wrong_distance)

    assert correct_distance < wrong_distance

def test_print_real_shift_up_typical_trajectory():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    typical = calibration.shift_up_typical_trajectory()

    print("\nREAL SHIFT_UP TYPICAL TRAJECTORY")

    for index, point in enumerate(typical):
        print(
            index,
            "forward=", point["forward"],
            "drop=", point["drop"],
            "angle=", point["angle"],
        )

    assert typical

def test_print_real_shift_up_attempt_end_points_from_rest():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    print("\nREAL SHIFT_UP END POINTS FROM REST")

    for index, attempt in enumerate(learned_attempts, start=1):
        forward, drop, angle = attempt[-1]

        end_point = calibration.movement_from_rest(
            forward=forward,
            drop=drop,
            angle=angle,
        )

        print(
            index,
            "forward=", end_point["forward"],
            "drop=", end_point["drop"],
            "angle=", end_point["angle"],
        )

    assert len(learned_attempts) == 3

def test_print_real_shift_up_normalized_trajectories():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]
    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)
    
    print("\nREAL SHIFT_UP NORMALIZED TRAJECTORIES")

    for attempt_index, attempt in enumerate(
        learned_attempts,
        start=1,
    ):
        trajectory = [
            calibration.movement_from_rest(
                forward=forward,
                drop=drop,
                angle=angle,
            )
            for forward, drop, angle in attempt
        ]

        normalized = (
            calibration.shift_up_normalized_component_trajectory(
                trajectory
            )
        )

        print(f"\nATTEMPT {attempt_index}")

        for point_index, point in enumerate(normalized):
            print(
                point_index,
                "forward=", round(point["forward"], 3),
                "drop=", round(point["drop"], 3),
                "angle=", round(point["angle"], 3),
            )

    assert len(learned_attempts) == 3

def test_print_real_shift_up_middle_activity_ratio():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    print("\nREAL SHIFT_UP MIDDLE ACTIVITY")

    for index, sequence in enumerate(
        calibration.shift_up_sequences,
        start=1,
    ):
        normalized = (
            calibration.shift_up_normalized_component_trajectory(
                sequence
            )
        )

        activity = [
            (
                point["forward"] ** 2
                + point["drop"] ** 2
                + point["angle"] ** 2
            ) ** 0.5
            for point in normalized
        ]

        total_activity = sum(activity)
        middle_activity = activity[1] + activity[2]

        ratio = middle_activity / total_activity

        print(
            f"attempt {index}:",
            "activity=",
            [round(value, 3) for value in activity],
            "middle_ratio=",
            round(ratio, 3),
        )

    assert len(calibration.shift_up_sequences) == 3

def test_print_non_shift_middle_activity_ratios():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    non_shift_movements = {
        "moving NON-SHIFT": [
            (0.0200, 0.1030, 165.0),
            (0.0215, 0.1060, 166.0),
            (0.0230, 0.1100, 168.0),
            (0.0215, 0.1060, 166.0),
            (0.0200, 0.1030, 165.0),
        ],
        "wrong-timing NON-SHIFT": [
            (0.0200, 0.1030, 165.0),
            (0.0205, 0.1025, 163.5),
            (0.0230, 0.0980, 164.5),
            (0.0215, 0.1015, 164.8),
            (0.0200, 0.1030, 165.0),
        ],
    }

    print("\nNON-SHIFT MIDDLE ACTIVITY")

    for name, samples in non_shift_movements.items():
        trajectory = [
            calibration.movement_from_rest(
                forward=forward,
                drop=drop,
                angle=angle,
            )
            for forward, drop, angle in samples
        ]

        normalized = (
            calibration.shift_up_normalized_component_trajectory(
                trajectory
            )
        )

        activity = [
            (
                point["forward"] ** 2
                + point["drop"] ** 2
                + point["angle"] ** 2
            ) ** 0.5
            for point in normalized
        ]

        total_activity = sum(activity)
        middle_activity = activity[1] + activity[2]

        ratio = middle_activity / total_activity

        print(
            name,
            "activity=",
            [round(value, 3) for value in activity],
            "middle_ratio=",
            round(ratio, 3),
        )

    assert len(non_shift_movements) == 2

def test_print_real_moving_non_shift_distance_ratio():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    real_moving_non_shift = [
        (-0.0014, 0.12917, 176.2),
        (-0.0109, 0.15191, 178.4),
        (-0.0132, 0.16061, 177.0),
        (-0.0111, 0.12927, 177.0),
        (-0.0102, 0.18014, 178.4),
    ]

    ratio = calibration.shift_up_distance_ratio(
        real_moving_non_shift
    )

    print(
        "\nREAL MOVING NON-SHIFT DISTANCE RATIO:",
        ratio,
    )

    assert ratio is not None

def test_print_real_clean_SHIFT_UP_distance_ratio():
    calibration = GearShiftCalibration()

    calibration.rest_forward = 0.020
    calibration.rest_drop = 0.103
    calibration.rest_angle = 165.0

    learned_attempts = [
        [
            (0.0208, 0.10250, 165.1),
            (0.0220, 0.10239, 164.6),
            (0.0229, 0.09980, 163.6),
            (0.0219, 0.10229, 164.5),
            (0.0221, 0.10295, 164.3),
        ],
        [
            (0.0206, 0.10295, 165.6),
            (0.0233, 0.09721, 163.3),
            (0.0233, 0.09722, 163.6),
            (0.0211, 0.10351, 164.8),
            (0.0206, 0.10479, 165.2),
        ],
        [
            (0.0218, 0.10787, 165.2),
            (0.0232, 0.09798, 163.6),
            (0.0217, 0.09711, 164.5),
            (0.0212, 0.10222, 165.1),
            (0.0217, 0.10225, 164.5),
        ],
    ]

    for attempt in learned_attempts:
        calibration.add_shift_up_sequence(attempt)

    real_clean_non_shift = [
        (0.0229, 0.10126, 164.0),
        (0.0230, 0.10127, 164.1),
        (0.0231, 0.10105, 164.1),
        (0.0235, 0.10085, 163.7),
        (0.0233, 0.10044, 163.7),
    ]

    ratio = calibration.shift_up_distance_ratio(
        real_clean_non_shift
    )

    print(
        "\nREAL CLEAN NON-SHIFT DISTANCE RATIO:",
        ratio,
    )

    assert ratio is not None