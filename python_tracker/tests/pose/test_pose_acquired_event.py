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

def test_clutch_friction_zone_reached_event():
    detector = RiderEventDetector()

    previous = RiderState(
        clutch_in_friction_zone=False,
        timestamp=1.0,
        )

    current = RiderState(
            clutch_in_friction_zone=True,
            timestamp=2.0,
        )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert (
            events[0].type
            == RiderEventType.CLUTCH_FRICTION_ZONE_REACHED
        )
    assert events[0].timestamp == 2.0

def test_clutch_released_from_friction_zone():
    detector = RiderEventDetector()

    previous = RiderState(
        clutch_in_friction_zone=True,
        clutch_progress=0.61,
        timestamp=1.0,
    )

    current = RiderState(
        clutch_in_friction_zone=False,
        clutch_progress=0.30,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert (
        events[0].type
        == RiderEventType.CLUTCH_RELEASED_FROM_FRICTION_ZONE
    )

def test_clutch_pulled_from_friction_zone():
    detector = RiderEventDetector()

    previous = RiderState(
        clutch_in_friction_zone=True,
        clutch_progress=0.61,
        timestamp=1.0,
    )

    current = RiderState(
        clutch_in_friction_zone=False,
        clutch_progress=0.90,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert (
        events[0].type
        == RiderEventType.CLUTCH_PULLED_FROM_FRICTION_ZONE
    )
    

def test_clutch_staying_in_friction_zone_emits_no_event():
    detector = RiderEventDetector()

    previous = RiderState(
        clutch_in_friction_zone=True,
        clutch_progress=0.61,
        timestamp=1.0,
    )

    current = RiderState(
        clutch_in_friction_zone=True,
        clutch_progress=0.63,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)
  
    assert events == []