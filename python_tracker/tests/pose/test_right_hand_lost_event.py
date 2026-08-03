from pose.rider_event_detector import RiderEventDetector
from pose.models.rider_state import RiderState
from pose.rider_events import RiderEventType


def test_right_hand_lost_event():
    detector = RiderEventDetector()

    previous = RiderState(
        right_hand_detected=True,
        timestamp=1.0,
    )

    current = RiderState(
        right_hand_detected=False,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert events[0].type == RiderEventType.RIGHT_HAND_LOST
    assert events[0].timestamp == 2.0