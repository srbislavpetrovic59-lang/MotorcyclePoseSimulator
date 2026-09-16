import pytest
from pose.analyzers.foot_analyzer import FootAnalyzer
from pose.models.rear_brake_calibration import RearBrakeCalibration
from pose.analyzers.gear_shift_detector import GearShiftDetector

from types import SimpleNamespace

def test_rear_brake_ready_when_foot_is_over_brake():
    assert FootAnalyzer._is_rear_brake_ready(
        65.0
    ) is True


def test_rear_brake_not_ready_when_foot_is_on_footpeg():
    assert FootAnalyzer._is_rear_brake_ready(
        140.0
    ) is False

def test_rear_brake_not_ready_without_rotation():
    assert FootAnalyzer._is_rear_brake_ready(
        None
    ) is False
def test_rear_brake_ready_uses_hysteresis():
    analyzer = FootAnalyzer()

    # Foot starts on the footpeg.
    assert analyzer._update_rear_brake_ready(140.0) is False

    # Foot moves onto the brake.
    assert analyzer._update_rear_brake_ready(70.0) is True

    # Measurement enters the uncertain area.
    # Previous READY state must be preserved.
    assert analyzer._update_rear_brake_ready(120.0) is True

    # Foot clearly returns to the footpeg.
    assert analyzer._update_rear_brake_ready(120.0) is False

def test_rear_brake_calibration_starts_empty():
    calibration = RearBrakeCalibration()

    assert calibration.released_drop is None
    assert calibration.full_drop is None
    assert calibration.is_complete() is False

def test_rear_brake_calibration_can_set_endpoints():
    calibration = RearBrakeCalibration()

    calibration.set_released(0.08)
    calibration.set_full(0.12)

    assert calibration.released_drop == 0.08
    assert calibration.full_drop == 0.12

    assert calibration.is_complete() is True

def test_rear_brake_progress_is_zero_when_released():
    progress = FootAnalyzer._rear_brake_progress(
        released_drop=0.08,
        full_drop=0.12,
        current_drop=0.08,
    )

    assert progress == 0.0


def test_rear_brake_progress_is_half_when_half_pressed():
    progress = FootAnalyzer._rear_brake_progress(
        released_drop=0.0,
        full_drop=10.0,
        current_drop=5.0,
    )

    assert progress == 0.5

@pytest.mark.parametrize(
    "current_drop, expected",
    [
        (-2.0, 0.0),
        (12.0, 1.0),
    ],
)
def test_rear_brake_progress_is_clamped(
    current_drop,
    expected,
):
    progress = FootAnalyzer._rear_brake_progress(
        released_drop=0.0,
        full_drop=10.0,
        current_drop=current_drop,
    )

    assert progress == expected

def test_rear_brake_progress_is_one_when_fully_pressed():
    progress = FootAnalyzer._rear_brake_progress(
        released_drop=0.08,
        full_drop=0.12,
        current_drop=0.12,
    )

    assert progress == 1.0


def test_rear_brake_is_inactive_when_released():
    analyzer = FootAnalyzer()

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=0.0
    )

    assert active is False

def test_rear_brake_is_inactive_when_progress_is_none():
    analyzer = FootAnalyzer()

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=None
    )

    assert active is False



def test_rear_brake_hysteresis_releases_below_lower_threshold():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_active(
        rear_brake_progress=0.5
    )

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=0.05
    )

    assert active is False

def test_rear_brake_detection_loss_keeps_previous_state():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_active_from_press(
        True
    )

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=None
    )

    assert active is True

def test_rear_brake_progress_is_none_when_measurement_missing():
    progress = FootAnalyzer._rear_brake_progress(
        released_drop=0.08,
        full_drop=0.12,
        current_drop=None,
    )

    assert progress is None



def test_right_foot_not_visible_when_landmark_visibility_is_low():
    right_heel = SimpleNamespace(
        visibility=0.9
    )
    
    right_ankle = SimpleNamespace(
        visibility=0.9
    )

    right_foot = SimpleNamespace(
        visibility=0.2
    )

    assert (
        FootAnalyzer._right_foot_visible(
            right_heel,
            right_ankle,
            right_foot,
        )
        is False
    )

def test_right_foot_visible_when_landmarks_are_visible():
    right_heel = SimpleNamespace(
        visibility=0.9
    )   

    right_ankle = SimpleNamespace(
        visibility=0.9
    )
    right_foot = SimpleNamespace(
        visibility=0.8
    )

    assert (
        FootAnalyzer._right_foot_visible(
            right_heel,
            right_ankle,
            right_foot,
        )
        is True
    )

def test_zone_is_low():
    assert GearShiftDetector._zone(0.040) == "LOW"


def test_zone_is_transition():
    assert GearShiftDetector._zone(0.055) == "TRANSITION"


def test_zone_is_high():
    assert GearShiftDetector._zone(0.075) == "HIGH"

def test_zone_is_none_without_measurement():
    assert GearShiftDetector._zone(None) is None
'''
def test_update_remembers_last_valid_zone():
    detector = GearShiftDetector()

    detector.update(0.040)

    assert detector._last_zone == "LOW"

def test_update_keeps_last_zone_when_measurement_is_missing():
    detector = GearShiftDetector()

    detector.update(0.040)
    detector.update(None)

    assert detector._last_zone == "LOW"
'''

def test_holding_high_does_not_emit_shift():
    detector = GearShiftDetector()

    assert detector.update(0.075) is None
    assert detector.update(0.078) is None
    assert detector.update(0.080) is None
    assert detector.update(0.076) is None

def test_holding_low_does_not_emit_shift():
    detector = GearShiftDetector()

    assert detector.update(0.040) is None
    assert detector.update(0.042) is None
    assert detector.update(0.038) is None
    assert detector.update(0.041) is None

def test_zone_classifies_measured_shift_up_peak_as_high():
    assert GearShiftDetector._zone(0.090) == "HIGH"

def test_zone_keeps_value_below_high_threshold_in_transition():
    assert GearShiftDetector._zone(0.055) == "TRANSITION"

def test_left_foot_visible_with_slightly_lower_ankle_visibility():
    analyzer = FootAnalyzer()
    
    class Landmark:
        def __init__(self, visibility):
            self.visibility = visibility

    left_heel = Landmark(0.52)
    left_ankle = Landmark(0.46)
    left_foot = Landmark(0.52)

    

    assert analyzer._left_foot_visible_for_gear_shift(
        left_heel,
        left_ankle,
        left_foot,
    ) is True

def test_left_foot_visible_for_gear_shift_with_low_ankle_visibility(): 
    analyzer = FootAnalyzer()
    
    class Landmark:
        def __init__(self, visibility):
            self.visibility = visibility

    left_heel = Landmark(0.62)
    left_ankle = Landmark(0.40)
    left_foot = Landmark(0.58)

   

    assert analyzer._left_foot_visible_for_gear_shift(
        left_heel,
        left_ankle,
        left_foot,
    ) is True
def test_gear_shift_visibility_survives_brief_ankle_visibility_drop():
    analyzer = FootAnalyzer()

    class Landmark:
        def __init__(self, visibility):
            self.visibility = visibility

    # Good tracking first.
    assert analyzer._left_foot_visible_for_gear_shift(
        Landmark(0.65),
        Landmark(0.41),
        Landmark(0.58),
    ) is True

    # Ankle briefly drops below the normal threshold,
    # while heel and foot are still visible.
    assert analyzer._left_foot_visible_for_gear_shift(
        Landmark(0.63),
        Landmark(0.39),
        Landmark(0.56),
    ) is True
def test_gear_shift_visibility_survives_two_brief_ankle_visibility_drops():
    analyzer = FootAnalyzer()

    class Landmark:
        def __init__(self, visibility):
            self.visibility = visibility

    # Good tracking.
    assert analyzer._left_foot_visible_for_gear_shift(
        Landmark(0.64),
        Landmark(0.40),
        Landmark(0.57),
    ) is True

    # First degraded frame.
    assert analyzer._left_foot_visible_for_gear_shift(
        Landmark(0.63),
        Landmark(0.39),
        Landmark(0.56),
    ) is True

    # Second degraded frame.
    assert analyzer._left_foot_visible_for_gear_shift(
        Landmark(0.62),
        Landmark(0.37),
        Landmark(0.54),
    ) is True

def test_rear_brake_forward_position_without_downward_press_has_zero_progress():
    analyzer = FootAnalyzer()

    progress = analyzer._rear_brake_progress_from_motion(
        right_foot_forward=0.05,
        right_foot_drop=0.08,
        forward_baseline=0.00,
        released_drop=0.08,
        full_drop=0.12,
    )

    assert progress == 0.0


def test_rear_brake_forward_position_with_downward_press_has_progress():
    analyzer = FootAnalyzer()

    progress = analyzer._rear_brake_progress_from_motion(
        right_foot_forward=0.05,
        right_foot_drop=0.10,
        forward_baseline=0.00,
        released_drop=0.08,
        full_drop=0.12,
    )

    assert progress > 0.0


def test_rear_brake_progress_is_clamped_to_one():
    analyzer = FootAnalyzer()

    progress = analyzer._rear_brake_progress_from_motion(
        right_foot_forward=0.05,
        right_foot_drop=0.15,
        forward_baseline=0.00,
        released_drop=0.08,
        full_drop=0.12,
    )

    assert progress == 1.0


def test_rear_brake_downward_press_without_forward_position_has_zero_progress():
    analyzer = FootAnalyzer()

    progress = analyzer._rear_brake_progress_from_motion(
        right_foot_forward=0.00,
        right_foot_drop=0.10,
        forward_baseline=0.00,
        released_drop=0.08,
        full_drop=0.12,
    )

    assert progress == 0.0


def test_rear_brake_tiny_forward_motion_does_not_enable_progress():
    analyzer = FootAnalyzer()

    progress = analyzer._rear_brake_progress_from_motion(
        right_foot_forward=0.001,
        right_foot_drop=0.10,
        forward_baseline=0.00,
        released_drop=0.08,
        full_drop=0.12,
    )

    assert progress == 0.0

def test_rear_brake_forward_baseline_starts_unset():
    analyzer = FootAnalyzer()

    assert analyzer._right_foot_forward_baseline is None


def test_rear_brake_forward_baseline_is_not_set_from_first_position():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_forward_baseline(
        right_foot_forward=0.02
    )

    assert analyzer._right_foot_forward_baseline is None


def test_rear_brake_forward_baseline_does_not_follow_foot():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_forward_baseline(0.049)
    analyzer._update_rear_brake_forward_baseline(0.051)
    analyzer._update_rear_brake_forward_baseline(0.050)
    analyzer._update_rear_brake_forward_baseline(0.050)
    analyzer._update_rear_brake_forward_baseline(0.050)

    assert analyzer._right_foot_forward_baseline == pytest.approx(0.050)

    analyzer._update_rear_brake_forward_baseline(0.080)

    assert analyzer._right_foot_forward_baseline == pytest.approx(0.050)

def test_rear_brake_forward_baseline_is_set_after_five_samples():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_forward_baseline(0.049)
    analyzer._update_rear_brake_forward_baseline(0.051)
    analyzer._update_rear_brake_forward_baseline(0.050)
    analyzer._update_rear_brake_forward_baseline(0.050)
    analyzer._update_rear_brake_forward_baseline(0.050)

    assert analyzer._right_foot_forward_baseline == pytest.approx(
        0.050
    )

def test_rear_brake_progress_is_zero_without_forward_baseline():
    analyzer = FootAnalyzer()

    progress = analyzer._rear_brake_progress_from_motion(
        right_foot_forward=0.05,
        right_foot_drop=0.10,
        forward_baseline=None,
        released_drop=0.08,
        full_drop=0.12,
    )

    assert progress == 0.0

def test_forward_baseline_requires_stable_rest_samples():
    detector = GearShiftDetector()

    # Three samples, but the foot is still moving.
    detector.update(
        left_foot_drop=0.080,
        left_foot_angle=160.0,
        left_foot_forward=0.040,
        elapsed_seconds=6.1,
    )
    detector.update(
        left_foot_drop=0.080,
        left_foot_angle=160.0,
        left_foot_forward=0.050,
        elapsed_seconds=6.2,
    )
    detector.update(
        left_foot_drop=0.080,
        left_foot_angle=160.0,
        left_foot_forward=0.060,
        elapsed_seconds=6.3,
    )

    assert detector._forward_baseline is None

def test_rear_brake_forward_baseline_not_set_from_unstable_samples():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_forward_baseline(0.000)
    analyzer._update_rear_brake_forward_baseline(0.020)
    analyzer._update_rear_brake_forward_baseline(0.040)

    assert analyzer._right_foot_forward_baseline is None

def test_rear_brake_forward_baseline_set_from_stable_samples():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_forward_baseline(0.003)
    analyzer._update_rear_brake_forward_baseline(0.006)
    analyzer._update_rear_brake_forward_baseline(0.005)
    analyzer._update_rear_brake_forward_baseline(0.004)
    analyzer._update_rear_brake_forward_baseline(0.005)

    assert analyzer._right_foot_forward_baseline == pytest.approx(
        (0.003 + 0.006 + 0.005 + 0.004 + 0.005) / 5
    )

def test_rear_brake_forward_baseline_recovers_after_unstable_samples():
    analyzer = FootAnalyzer()

    # Unstable movement first.
    analyzer._update_rear_brake_forward_baseline(0.000)
    analyzer._update_rear_brake_forward_baseline(0.020)
    analyzer._update_rear_brake_forward_baseline(0.040)

    assert analyzer._right_foot_forward_baseline is None

    # Foot then becomes stable.
    analyzer._update_rear_brake_forward_baseline(0.041)
    analyzer._update_rear_brake_forward_baseline(0.042)
    analyzer._update_rear_brake_forward_baseline(0.041)
    analyzer._update_rear_brake_forward_baseline(0.040)

    assert analyzer._right_foot_forward_baseline == pytest.approx(
        (0.040 + 0.041 + 0.042 + 0.041 + 0.040) / 5
    )


def test_rear_brake_baseline_learned_when_brake_not_ready():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_forward_baseline_if_released(
        right_foot_forward=0.003,
        rear_brake_ready=False,
    )
    analyzer._update_rear_brake_forward_baseline_if_released(
        right_foot_forward=0.006,
        rear_brake_ready=False,
    )
    analyzer._update_rear_brake_forward_baseline_if_released(
        right_foot_forward=0.005,
        rear_brake_ready=False,
    )
    analyzer._update_rear_brake_forward_baseline_if_released(
        right_foot_forward=0.004,
        rear_brake_ready=False,
    )
    analyzer._update_rear_brake_forward_baseline_if_released(
        right_foot_forward=0.005,
        rear_brake_ready=False,
    )

    assert analyzer._right_foot_forward_baseline == pytest.approx(
        (0.003 + 0.006 + 0.005 + 0.004 + 0.005) / 5
    )

def test_rear_brake_progress_starts_from_measured_forward_motion():
    analyzer = FootAnalyzer()

    progress = analyzer._rear_brake_progress_from_motion(
        right_foot_forward=0.043,
        right_foot_drop=0.110,
        forward_baseline=0.032,
        released_drop=0.08,
        full_drop=0.12,
    )

    assert progress > 0.0

def test_rear_brake_baseline_can_learn_from_stable_ready_position():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_forward_baseline_if_released(
        right_foot_forward=0.037,
        rear_brake_ready=True,
    )
    analyzer._update_rear_brake_forward_baseline_if_released(
        right_foot_forward=0.038,
        rear_brake_ready=True,
    )
    analyzer._update_rear_brake_forward_baseline_if_released(
        right_foot_forward=0.037,
        rear_brake_ready=True,
    )
    analyzer._update_rear_brake_forward_baseline_if_released(
        right_foot_forward=0.038,
        rear_brake_ready=True,
    )
    analyzer._update_rear_brake_forward_baseline_if_released(
        right_foot_forward=0.037,
        rear_brake_ready=True,
    )

    assert analyzer._right_foot_forward_baseline == pytest.approx(
        (0.037 + 0.038 + 0.037 + 0.038 + 0.037) / 5
    )


def test_rear_brake_not_active_from_single_progress_frame():
    analyzer = FootAnalyzer()

    active = analyzer._update_rear_brake_active(
        0.75
    )

    assert active is False

def test_rear_brake_forward_baseline_not_learned_too_early():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_forward_baseline(
        -0.010
    )
    analyzer._update_rear_brake_forward_baseline(
        -0.009
    )
    analyzer._update_rear_brake_forward_baseline(
        -0.008
    )

    assert analyzer._right_foot_forward_baseline is None

def test_rear_brake_progress_starts_from_latest_measured_forward_motion():
    analyzer = FootAnalyzer()

    progress = analyzer._rear_brake_progress_from_motion(
        right_foot_forward=0.0509,
        right_foot_drop=0.110,
        forward_baseline=0.0475,
        released_drop=0.08,
        full_drop=0.12,
    )

    assert progress > 0.0

def test_rear_brake_progress_stays_zero_for_latest_stationary_pose():
    analyzer = FootAnalyzer()

    progress = analyzer._rear_brake_progress_from_motion(
        right_foot_forward=0.0490,
        right_foot_drop=0.0851,
        forward_baseline=0.0475,
        released_drop=0.08,
        full_drop=0.12,
    )

    assert progress == 0.0



def test_rear_brake_prepare_detected_when_toes_lift():
    analyzer = FootAnalyzer()

    prepared = analyzer._is_rear_brake_prepare(
        current_angle=162.0,
        baseline_angle=166.7,
    )

    assert prepared is True

def test_rear_brake_prepare_not_detected_for_small_angle_change():
        analyzer = FootAnalyzer()

        prepared = analyzer._is_rear_brake_prepare(
            current_angle=165.5,
            baseline_angle=166.7,
        )

        assert prepared is False

def test_rear_brake_prepare_stays_latched_after_toes_lift():
        analyzer = FootAnalyzer()

        analyzer._update_rear_brake_prepare(
            current_angle=162.0,
            baseline_angle=166.7,
        )

        prepared = analyzer._update_rear_brake_prepare(
            current_angle=165.5,
            baseline_angle=166.7,
        )

        assert prepared is True

def test_rear_brake_prepare_alone_does_not_activate_brake():
        analyzer = FootAnalyzer()

        analyzer._update_rear_brake_prepare(
            current_angle=162.0,
            baseline_angle=166.7,
        )

        assert analyzer._rear_brake_active is False

def test_rear_brake_press_detected_after_prepare():
        analyzer = FootAnalyzer()

        analyzer._update_rear_brake_prepare(
            current_angle=162.0,
            baseline_angle=166.7,
        )

        pressing = analyzer._is_rear_brake_press(
            right_foot_drop=0.1064,
            released_drop=0.08,
        )

        assert pressing is True

def test_rear_brake_press_not_detected_without_prepare():
    analyzer = FootAnalyzer()

    pressing = analyzer._is_rear_brake_press(
        right_foot_drop=0.1064,
        released_drop=0.08,
    )

    assert pressing is False

def test_rear_brake_press_not_detected_before_sufficient_drop():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_prepare(
        current_angle=162.0,
        baseline_angle=166.7,
    )

    pressing = analyzer._is_rear_brake_press(
        right_foot_drop=0.095,
        released_drop=0.08,
    )

    assert pressing is False

def test_rear_brake_press_can_activate_brake():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_prepare(
        current_angle=162.0,
        baseline_angle=166.7,
    )

    pressing = analyzer._is_rear_brake_press(
        right_foot_drop=0.1064,
        released_drop=0.08,
    )

    active = analyzer._update_rear_brake_active_from_press(
        pressing
    )

    assert active is True

def test_rear_brake_active_survives_single_non_press_frame():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_active_from_press(True)

    active = analyzer._update_rear_brake_active_from_press(False)

    assert active is True




def test_rear_brake_not_active_without_press():
    analyzer = FootAnalyzer()

    active = analyzer._update_rear_brake_active_from_press(False)

    assert active is False

def test_rear_brake_press_matches_live_measured_sequence():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_prepare(
        current_angle=162.0,
        baseline_angle=166.7,
    )

    pressing = analyzer._is_rear_brake_press(
        right_foot_drop=0.1104,
        released_drop=0.08,
    )

    assert pressing is True

def test_rear_brake_motion_sequence_activates_brake():
    analyzer = FootAnalyzer()
    analyzer._rear_brake_ready = True

    active = analyzer._update_rear_brake_motion(
        right_foot_angle=162.0,
        baseline_angle=166.7,
        right_foot_drop=0.0771,
        released_drop=0.08,
    )

    assert active is False

    active = analyzer._update_rear_brake_motion(
        right_foot_angle=167.2,
        baseline_angle=166.7,
        right_foot_drop=0.1104,
        released_drop=0.08,
    )

    assert active is True

def test_rear_brake_angle_baseline_not_learned_too_early():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_angle_baseline(166.7)
    analyzer._update_rear_brake_angle_baseline(166.5)
    analyzer._update_rear_brake_angle_baseline(166.8)

    assert analyzer._right_foot_angle_baseline is None

def test_rear_brake_angle_baseline_set_after_five_stable_samples():
    analyzer = FootAnalyzer()

    samples = [
        166.7,
        166.5,
        166.8,
        166.6,
        166.7,
    ]

    for angle in samples:
        analyzer._update_rear_brake_angle_baseline(angle)

    assert analyzer._right_foot_angle_baseline == pytest.approx(
        sum(samples) / 5
    )

def test_rear_brake_angle_baseline_not_set_from_unstable_samples():
    analyzer = FootAnalyzer()

    samples = [
        166.7,
        165.5,
        164.0,
        162.0,
        167.2,
    ]

    for angle in samples:
        analyzer._update_rear_brake_angle_baseline(angle)

    assert analyzer._right_foot_angle_baseline is None
def test_rear_brake_can_be_pressed_again_without_new_prepare():
    analyzer = FootAnalyzer()

    # Foot moves over the brake.
    analyzer._update_rear_brake_prepare(
        current_angle=162.0,
        baseline_angle=166.7,
    )

    first_press = analyzer._is_rear_brake_press(
        right_foot_drop=0.1104,
        released_drop=0.08,
    )

    assert first_press is True

    # Rider eases pressure but keeps the foot over the brake.
    partial_release = analyzer._is_rear_brake_press(
        right_foot_drop=0.095,
        released_drop=0.08,
    )

    assert partial_release is False

    # Rider applies the rear brake again.
    second_press = analyzer._is_rear_brake_press(
        right_foot_drop=0.1104,
        released_drop=0.08,
    )

    assert second_press is True

def test_rear_brake_angle_baseline_recovers_after_unstable_samples():
    analyzer = FootAnalyzer()

    unstable = [
        166.7,
        164.0,
        162.0,
        165.0,
        167.2,
    ]

    for angle in unstable:
        analyzer._update_rear_brake_angle_baseline(angle)

    stable = [
        166.6,
        166.7,
        166.5,
        166.6,
        166.7,
    ]

    for angle in stable:
        analyzer._update_rear_brake_angle_baseline(angle)

    assert analyzer._right_foot_angle_baseline is not None

def test_rear_brake_prepare_not_updated_without_angle_baseline():
    analyzer = FootAnalyzer()

    assert analyzer._right_foot_angle_baseline is None
    assert analyzer._rear_brake_prepare is False

def test_rear_brake_motion_uses_learned_angle_baseline():
    analyzer = FootAnalyzer()
    analyzer._rear_brake_ready = True

    for angle in [
        166.7,
        166.5,
        166.8,
        166.6,
        166.7,
    ]:
        analyzer._update_rear_brake_angle_baseline(angle)

    active = analyzer._update_rear_brake_motion(
        right_foot_angle=162.0,
        baseline_angle=analyzer._right_foot_angle_baseline,
        right_foot_drop=0.0771,
        released_drop=0.08,
    )

    assert active is False
    assert analyzer._rear_brake_prepare is True

def test_rear_brake_motion_not_used_before_angle_baseline_exists():
    analyzer = FootAnalyzer()

    assert analyzer._right_foot_angle_baseline is None
    assert analyzer._rear_brake_prepare is False
    assert analyzer._rear_brake_active is False

def test_rear_brake_progress_alone_does_not_activate_brake():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_active(0.50)
    active = analyzer._update_rear_brake_active(0.50)

    assert active is False

def test_rear_brake_stays_active_after_single_low_progress_frame():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_active_from_press(
        True
    )

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=0.0
    )

    assert active is True

def test_rear_brake_releases_after_two_low_progress_frames():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_active_from_press(
        True
    )

    analyzer._update_rear_brake_active(
        rear_brake_progress=0.0
    )

    active = analyzer._update_rear_brake_active(
        rear_brake_progress=0.0
    )

    assert active is False

def test_rear_brake_can_reactivate_after_release_without_new_prepare():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_prepare(
        current_angle=162.0,
        baseline_angle=166.7,
    )

    analyzer._update_rear_brake_active_from_press(True)

    analyzer._update_rear_brake_active(0.0)
    analyzer._update_rear_brake_active(0.0)

    assert analyzer._rear_brake_active is False
    assert analyzer._rear_brake_prepare is True

    pressing = analyzer._is_rear_brake_press(
        right_foot_drop=0.1104,
        released_drop=0.08,
    )

    active = analyzer._update_rear_brake_active_from_press(
        pressing
    )

    assert active is True

def test_rear_brake_prepare_resets_when_foot_returns_to_footpeg():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_prepare(
        current_angle=162.0,
        baseline_angle=166.7,
    )

    assert analyzer._rear_brake_prepare is True

    analyzer._reset_rear_brake_prepare_if_not_ready(
        rear_brake_ready=False
    )

    assert analyzer._rear_brake_prepare is False

def test_rear_brake_prepare_not_reset_when_ready_is_unknown():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_prepare(
        current_angle=162.0,
        baseline_angle=166.7,
    )

    analyzer._reset_rear_brake_prepare_if_not_ready(
        rear_brake_ready=None
    )

    assert analyzer._rear_brake_prepare is True

def test_rear_brake_return_to_footpeg_deactivates_brake():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_prepare(
        current_angle=162.0,
        baseline_angle=166.7,
    )

    analyzer._update_rear_brake_active_from_press(
        True
    )

    assert analyzer._rear_brake_active is True

    analyzer._reset_rear_brake_prepare_if_not_ready(
        rear_brake_ready=False
    )

    assert analyzer._rear_brake_active is False

def test_rear_brake_released_drop_baseline_not_learned_from_single_frame():
    analyzer = FootAnalyzer()

    analyzer._update_rear_brake_released_drop_baseline(
        right_foot_drop=0.135
    )

    assert analyzer._right_foot_released_drop_baseline is None

def test_rear_brake_released_drop_baseline_learned_from_five_stable_frames():
    analyzer = FootAnalyzer()

    samples = [
        0.135,
        0.136,
        0.134,
        0.135,
        0.135,
    ]

    for drop in samples:
        analyzer._update_rear_brake_released_drop_baseline(
            right_foot_drop=drop
        )

    assert analyzer._right_foot_released_drop_baseline is not None

def test_rear_brake_released_drop_baseline_not_learned_from_unstable_frames():
    analyzer = FootAnalyzer()

    samples = [
        0.135,
        0.150,
        0.120,
        0.145,
        0.130,
    ]

    for drop in samples:
        analyzer._update_rear_brake_released_drop_baseline(
            right_foot_drop=drop
        )

    assert analyzer._right_foot_released_drop_baseline is None

def test_rear_brake_released_drop_baseline_recovers_after_unstable_frames():
    analyzer = FootAnalyzer()

    samples = [
        0.120,
        0.150,
        0.110,
        0.160,
        0.140,
        0.135,
        0.136,
        0.134,
        0.135,
        0.135,
    ]

    for drop in samples:
        analyzer._update_rear_brake_released_drop_baseline(
            right_foot_drop=drop
        )

    assert analyzer._right_foot_released_drop_baseline is not None

def test_rear_brake_press_uses_learned_released_drop_baseline():
    analyzer = FootAnalyzer()

    analyzer._right_foot_released_drop_baseline = 0.135
    analyzer._rear_brake_prepare = True

    pressing = analyzer._is_rear_brake_press(
        right_foot_drop=0.145,
        released_drop=analyzer._right_foot_released_drop_baseline,
    )

    assert pressing is False

def test_rear_brake_motion_uses_learned_released_drop_baseline():
    analyzer = FootAnalyzer()

    analyzer._rear_brake_prepare = True
    analyzer._right_foot_released_drop_baseline = 0.135

    active = analyzer._update_rear_brake_motion(
        right_foot_angle=166.7,
        baseline_angle=166.7,
        right_foot_drop=0.145,
        released_drop=analyzer._right_foot_released_drop_baseline,
    )

    assert active is False

def test_rear_brake_motion_not_evaluated_without_released_drop_baseline():
    analyzer = FootAnalyzer()

    analyzer._rear_brake_prepare = True

    assert analyzer._right_foot_released_drop_baseline is None

    active = analyzer._rear_brake_active

    assert active is False

def test_rear_brake_released_drop_baseline_matches_stable_rest_position():
    analyzer = FootAnalyzer()

    samples = [
        0.1393,
        0.1377,
        0.1385,
        0.1390,
        0.1382,
    ]

    for drop in samples:
        analyzer._update_rear_brake_released_drop_baseline(
            right_foot_drop=drop
        )

    assert analyzer._right_foot_released_drop_baseline == pytest.approx(
        0.13854
    )

def test_rear_brake_released_drop_baseline_not_locked_from_early_stable_frames():
    analyzer = FootAnalyzer()

    early_samples = [
        0.1439,
        0.1382,
        0.1493,
        0.1436,
        0.1379,
    ]

    for drop in early_samples:
        analyzer._update_rear_brake_released_drop_baseline(
            right_foot_drop=drop
        )

    assert analyzer._right_foot_released_drop_baseline is None

def test_rear_brake_released_drop_baseline_not_learned_before_five_seconds():
    analyzer = FootAnalyzer()

    samples = [
        0.0723,
        0.0724,
        0.0725,
        0.0724,
        0.0723,
    ]

    for drop in samples:
        analyzer._update_rear_brake_released_drop_baseline(
            right_foot_drop=drop,
            elapsed_seconds=4.9,
        )

    assert analyzer._right_foot_released_drop_baseline is None

def test_rear_brake_motion_does_not_prepare_when_not_ready():
    analyzer = FootAnalyzer()

    analyzer._rear_brake_ready = False
    analyzer._rear_brake_prepare = False

    analyzer._update_rear_brake_motion(
        right_foot_angle=160.0,
        baseline_angle=170.0,
        right_foot_drop=0.12,
        released_drop=0.10,
    )

    assert analyzer._rear_brake_prepare is False

def test_right_ankle_depth_displacement_from_footpeg():
    baseline_z = -0.26
    current_z = -0.31

    displacement = FootAnalyzer._right_ankle_depth_displacement(
        current_z,
        baseline_z,
    )

    assert displacement == pytest.approx(-0.05)

def test_right_ankle_depth_baseline_requires_five_stable_samples():
    analyzer = FootAnalyzer()

    for z in [-0.260, -0.261, -0.259, -0.260]:
        analyzer._update_right_ankle_depth_baseline(z)

    assert analyzer._right_ankle_depth_baseline is None

    analyzer._update_right_ankle_depth_baseline(-0.260)

    assert analyzer._right_ankle_depth_baseline == pytest.approx(-0.260)

def test_rear_brake_depth_median_uses_last_five_samples():
    samples = [
        -0.01,
        -0.02,
        -0.03,
        -0.04,
        -0.05,
        -0.06,
    ]

    result = FootAnalyzer._depth_median(samples)

    assert result == -0.04

def test_rear_brake_depth_median_ignores_old_outlier():
    samples = [
        -100.0,
        -0.01,
        -0.02,
        -0.03,
        -0.04,
        -0.05,
    ]

    assert FootAnalyzer._depth_median(samples) == -0.03

def test_rear_brake_depth_median_with_three_samples():
    samples = [-0.01, -0.03, -0.02]

    assert FootAnalyzer._depth_median(samples) == -0.02

def test_rear_brake_depth_median_with_four_samples():
    samples = [-0.01, -0.02, -0.03, -0.04]

    assert FootAnalyzer._depth_median(samples) == -0.025

def test_rear_brake_depth_median_without_samples():
    assert FootAnalyzer._depth_median([]) is None

def test_rear_brake_depth_displacement_uses_median():
    analyzer = FootAnalyzer()

    samples = [-0.01, -0.02, -0.08, -0.03, -0.04]

    for value in samples:
        result = analyzer._filter_depth_displacement(value)

    assert result == -0.03

def test_rear_brake_ready_ignores_single_frame_rotation_spike():
    analyzer = FootAnalyzer()

    assert analyzer._update_rear_brake_ready(70.0) is True

    # Jedan šumni kadar ne sme da poništi READY.
    assert analyzer._update_rear_brake_ready(120.0) is True
