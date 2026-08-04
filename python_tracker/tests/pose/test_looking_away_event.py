from pose.rider_event_detector import RiderEventDetector
from pose.models.rider_state import RiderState
from pose.rider_events import RiderEventType


def test_looking_away_event():
    detector = RiderEventDetector()

    previous = RiderState(
        head_forward=True,
        timestamp=1.0,
    )

    current = RiderState(
        head_forward=False,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert events[0].type == RiderEventType.LOOKING_AWAY
    assert events[0].timestamp == 2.0