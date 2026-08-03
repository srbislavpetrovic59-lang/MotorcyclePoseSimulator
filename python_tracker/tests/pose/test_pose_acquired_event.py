from pose.rider_event_detector import RiderEventDetector
from pose.models.rider_state import RiderState
from pose.rider_events import RiderEventType

def test_pose_acquired_event():
    detector = RiderEventDetector()

    previous = RiderState(
        pose_confidence=0.0,
    )

    current = RiderState(
        pose_confidence=0.9,
        timestamp=1.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert events[0].type == RiderEventType.POSE_ACQUIRED