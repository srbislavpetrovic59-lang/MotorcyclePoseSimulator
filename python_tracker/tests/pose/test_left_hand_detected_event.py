from pose.rider_event_detector import RiderEventDetector
from pose.models.rider_state import RiderState
from pose.rider_events import RiderEventType


def test_left_hand_detected_event():
    detector = RiderEventDetector()

    previous = RiderState(
        left_hand_detected=False,
        timestamp=1.0,
    )

    current = RiderState(
        left_hand_detected=True,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert events[0].type == RiderEventType.LEFT_HAND_DETECTED
    assert events[0].timestamp == 2.0