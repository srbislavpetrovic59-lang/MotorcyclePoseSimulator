from pose.rider_event_detector import RiderEventDetector
from pose.models.rider_state import RiderState

def test_has_valid_pose():
    detector = RiderEventDetector()

    invalid_state = RiderState(
        pose_confidence=0.5,
    )

    valid_state = RiderState(
        pose_confidence=0.9,
    )

    assert not detector._has_valid_pose(invalid_state)
    assert detector._has_valid_pose(valid_state)