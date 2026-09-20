import pytest
from pose.landmark_stabilizer import LandmarkStabilizer



def test_single_frame_heel_jump_is_rejected():
    stabilizer = LandmarkStabilizer()

    assert stabilizer.update("left_heel", 0.80) == 0.80
    assert stabilizer.update("left_heel", 0.801) == 0.801

    # MediaPipe suddenly reports an implausible position.
    result = stabilizer.update("left_heel", 0.15)

    assert result == 0.801

def test_persistent_heel_movement_is_accepted():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)

    stabilizer.update("left_heel", 0.65)
    stabilizer.update("left_heel", 0.65)
    result = stabilizer.update("left_heel", 0.65)

    assert result == 0.65

def test_alternating_heel_jumps_are_rejected():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)

    assert stabilizer.update("left_heel", 0.20) == 0.80
    assert stabilizer.update("left_heel", 0.60) == 0.80
    assert stabilizer.update("left_heel", 0.20) == 0.80
    assert stabilizer.update("left_heel", 0.60) == 0.80

def test_valid_measurement_resets_jump_candidate():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)

    assert stabilizer.update("left_heel", 0.65) == 0.80
    assert stabilizer.update("left_heel", 0.80) == 0.80

    # A new jump must start counting from scratch.
    assert stabilizer.update("left_heel", 0.65) == 0.80
    assert stabilizer.update("left_heel", 0.65) == 0.80
    assert stabilizer.update("left_heel", 0.65) == 0.65

def test_landmarks_have_independent_state():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)
    stabilizer.update("right_heel", 0.40)

    # Left heel starts a jump candidate.
    assert stabilizer.update("left_heel", 0.65) == 0.80

    # Right heel moves normally.
    assert stabilizer.update("right_heel", 0.42) == 0.42

    # Left heel must still require two more confirmations.
    assert stabilizer.update("left_heel", 0.65) == 0.80
    assert stabilizer.update("left_heel", 0.65) == 0.65

def test_missing_landmark_resets_jump_candidate():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)

    assert stabilizer.update("left_heel", 0.65) == 0.80
    assert stabilizer.update("left_heel", 0.65) == 0.80

    # MediaPipe loses the heel.
    assert stabilizer.update("left_heel", None) is None

    # The old candidate must not survive the loss.
    assert stabilizer.update("left_heel", 0.65) == 0.65

def test_missing_landmark_does_not_reset_other_landmarks():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)
    stabilizer.update("right_heel", 0.40)

    assert stabilizer.update("right_heel", 0.20) == 0.40
    assert stabilizer.update("right_heel", 0.20) == 0.40

    # Only the left heel disappears.
    assert stabilizer.update("left_heel", None) is None

    # The right heel retains its candidate and accepts
    # the third consecutive measurement.
    assert stabilizer.update("right_heel", 0.20) == 0.20

def test_fast_gradual_motion_is_preserved():
    stabilizer = LandmarkStabilizer()

    positions = [0.80, 0.72, 0.64, 0.56, 0.48]

    results = [
        stabilizer.update("left_heel", value)
        for value in positions
    ]

    assert results == positions

def test_fast_motion_with_small_variations_is_accepted():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)

    assert stabilizer.update("left_heel", 0.60) == 0.80
    assert stabilizer.update("left_heel", 0.59) == 0.80
    assert stabilizer.update("left_heel", 0.58) == 0.58 

def test_fast_continuous_motion_is_accepted():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)

    assert stabilizer.update("left_heel", 0.60) == 0.80
    assert stabilizer.update("left_heel", 0.56) == 0.80
    assert stabilizer.update("left_heel", 0.52) == 0.52

def test_large_alternating_jumps_are_rejected():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)

    assert stabilizer.update("left_heel", 0.20) == 0.80
    assert stabilizer.update("left_heel", 0.60) == 0.80
    assert stabilizer.update("left_heel", 0.20) == 0.80
    assert stabilizer.update("left_heel", 0.60) == 0.80

def test_three_large_jumps_in_same_direction_are_rejected():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)

    # Three erroneous measurements drifting in one direction.
    assert stabilizer.update("left_heel", 0.60) == 0.80
    assert stabilizer.update("left_heel", 0.50) == 0.80
    assert stabilizer.update("left_heel", 0.40) == 0.80




@pytest.mark.xfail(
    reason="Requires additional evidence to distinguish motion from drift",
    strict=True,
)
def test_three_large_jumps_in_same_direction_are_rejected():
    stabilizer = LandmarkStabilizer()

    stabilizer.update("left_heel", 0.80)

    assert stabilizer.update("left_heel", 0.60) == 0.80
    assert stabilizer.update("left_heel", 0.50) == 0.80
    assert stabilizer.update("left_heel", 0.40) == 0.80



