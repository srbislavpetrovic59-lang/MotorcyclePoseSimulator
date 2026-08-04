from pose.rider_event_detector import RiderEventDetector
from pose.models.rider_state import RiderState
from pose.rider_events import RiderEventType


detector = RiderEventDetector()

previous = RiderState(
    head_forward=False,
    timestamp=1.0,
)

current = RiderState(
    head_forward=True,
    timestamp=2.0,
)

detector.detect(previous)

events = detector.detect(current)

assert len(events) == 1
assert events[0].type == RiderEventType.LOOKING_AHEAD
assert events[0].timestamp == 2.0