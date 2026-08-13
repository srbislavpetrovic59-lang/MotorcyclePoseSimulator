from pose.rider_event_detector import RiderEventDetector
from pose.rider_events import RiderEventType    
from pose.models.rider_state import RiderState


def test_detect_returns_empty_list():
    detector = RiderEventDetector()

    events = detector.detect(None)

    assert events == []


def test_clutch_reenters_friction_zone_from_pulled():
    detector = RiderEventDetector()

    pulled = RiderState(
        clutch_in_friction_zone=False,
        clutch_progress=0.90,
        timestamp=1.0,
    )

    friction = RiderState(
        clutch_in_friction_zone=True,
        clutch_progress=0.62,
        timestamp=2.0,
    )

    detector.detect(pulled)

    events = detector.detect(friction)

    assert len(events) == 1
    assert (
        events[0].type
        == RiderEventType.CLUTCH_FRICTION_ZONE_REACHED
    )

def test_clutch_reenters_friction_zone_from_released():
    detector = RiderEventDetector()

    released = RiderState(
        clutch_in_friction_zone=False,
        clutch_progress=0.20,
        timestamp=1.0,
    )

    friction = RiderState(
        clutch_in_friction_zone=True,
        clutch_progress=0.61,
        timestamp=2.0,
    )

    detector.detect(released)

    events = detector.detect(friction)

    assert len(events) == 1
    assert (
        events[0].type
        == RiderEventType.CLUTCH_FRICTION_ZONE_REACHED
    )

def test_clutch_detection_recovery_does_not_emit_reached_event():
    detector = RiderEventDetector()

    lost = RiderState(
        clutch_in_friction_zone=False,
        clutch_progress=None,
        timestamp=1.0,
    )

    recovered = RiderState(
        clutch_in_friction_zone=True,
        clutch_progress=0.62,
        timestamp=2.0,
    )

    detector.detect(lost)

    events = detector.detect(recovered)

    assert not any(
        event.type
        == RiderEventType.CLUTCH_FRICTION_ZONE_REACHED
        for event in events
    )