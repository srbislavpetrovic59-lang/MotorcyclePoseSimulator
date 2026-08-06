from pose.rider_event_detector import RiderEventDetector
from pose.models.rider_state import RiderState
from pose.rider_events import RiderEventType


detector = RiderEventDetector()

previous = RiderState(
    right_hand_rotation=260.0,
    throttle_open=False,
    timestamp=1.0,
)

current = RiderState(
    right_hand_rotation=196.0,
    throttle_open=True,
    timestamp=2.0,
)

detector.detect(previous)

events = detector.detect(current)

assert len(events) == 1
assert events[0].type == RiderEventType.THROTTLE_OPENED
assert events[0].timestamp == 2.0