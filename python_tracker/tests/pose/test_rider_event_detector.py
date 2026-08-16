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

def test_front_brake_applied_event():
    detector = RiderEventDetector()

    previous = RiderState(
        front_brake_active=False,
        timestamp=1.0,
    )

    current = RiderState(
        front_brake_active=True,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert (
        events[0].type
        == RiderEventType.FRONT_BRAKE_APPLIED
    )

def test_front_brake_released_event():
    detector = RiderEventDetector()

    previous = RiderState(
        front_brake_active=True,
        front_brake_progress=0.70,
        timestamp=1.0,
    )

    current = RiderState(
        front_brake_active=False,
        front_brake_progress=0.0,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert (
        events[0].type
        == RiderEventType.FRONT_BRAKE_RELEASED
    )

def test_lost_right_hand_does_not_emit_front_brake_released():
    detector = RiderEventDetector()

    previous = RiderState(
        front_brake_active=True,
        front_brake_progress=0.70,
        timestamp=1.0,
    )

    lost = RiderState(
        front_brake_active=False,
        front_brake_progress=None,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(lost)

    assert not any(
        event.type == RiderEventType.FRONT_BRAKE_RELEASED
        for event in events
    )

def test_throttle_opened_event():
    detector = RiderEventDetector()

    previous = RiderState(
        throttle_active=False,
        throttle_progress=0.0,
        timestamp=1.0,
    )

    current = RiderState(
        throttle_active=True,
        throttle_progress=0.15,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert (
        events[0].type
        == RiderEventType.THROTTLE_OPENED
    )

def test_throttle_closed_event():
    detector = RiderEventDetector()

    previous = RiderState(
        throttle_active=True,
        throttle_progress=0.15,
        timestamp=1.0,
    )

    current = RiderState(
        throttle_active=False,
        throttle_progress=0.04,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert (
        events[0].type
        == RiderEventType.THROTTLE_CLOSED
    )

def test_lost_throttle_measurement_does_not_emit_closed_event():
    detector = RiderEventDetector()

    previous = RiderState(
        throttle_active=True,
        throttle_progress=0.50,
        timestamp=1.0,
    )

    current = RiderState(
        throttle_active=True,
        throttle_progress=None,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert events == []