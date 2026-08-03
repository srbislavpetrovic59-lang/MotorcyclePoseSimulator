from pose.rider_event_detector import RiderEventDetector
from pose.models.rider_state import RiderState


def test_detector_updates_previous_state():
    detector = RiderEventDetector()

    first_state = RiderState(
        pose_confidence=0.2,
    )

    second_state = RiderState(
        pose_confidence=0.3,
    )

    detector.detect(first_state)
    detector.detect(second_state)

    assert detector._previous_state is second_state