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
        clutch_progress=0.20,
        timestamp=1.0,
    )

    current = RiderState(
        clutch_in_friction_zone=True,
        clutch_progress=0.61,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert len(events) == 1
    assert (
        events[0].type
        == RiderEventType.CLUTCH_FRICTION_ZONE_REACHED
    )

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

def test_lost_hand_does_not_emit_clutch_exit_event():
    detector = RiderEventDetector()

    previous = RiderState(
        clutch_in_friction_zone=True,
        clutch_progress=0.61,
        timestamp=1.0,
    )

    current = RiderState(
        clutch_in_friction_zone=False,
        clutch_progress=None,
        timestamp=2.0,
    )

    detector.detect(previous)

    events = detector.detect(current)

    assert events == []

def test_lost_hand_from_pulled_emits_no_clutch_event():
        detector = RiderEventDetector()

        previous = RiderState(
            clutch_in_friction_zone=False,
            clutch_progress=0.90,
            timestamp=1.0,
        )

        lost = RiderState(
            clutch_in_friction_zone=False,
            clutch_progress=None,
            timestamp=2.0,
        )

        detector.detect(previous)

        events = detector.detect(lost)

        clutch_events = [
            event
            for event in events
            if event.type in (
                RiderEventType.CLUTCH_FRICTION_ZONE_REACHED,
                RiderEventType.CLUTCH_RELEASED_FROM_FRICTION_ZONE,
                RiderEventType.CLUTCH_PULLED_FROM_FRICTION_ZONE,
            )
        ]

        assert clutch_events == []

def test_clutch_change_during_detection_loss_emits_no_clutch_event():
    detector = RiderEventDetector()

    pulled = RiderState(
        clutch_in_friction_zone=False,
        clutch_progress=0.90,
        timestamp=1.0,
    )

    lost = RiderState(
        clutch_in_friction_zone=False,
        clutch_progress=None,
        timestamp=2.0,
    )

    released = RiderState(
        clutch_in_friction_zone=False,
        clutch_progress=0.20,
        timestamp=3.0,
    )

    detector.detect(pulled)
    detector.detect(lost)

    events = detector.detect(released)

    clutch_events = [
        event
        for event in events
        if event.type in (
            RiderEventType.CLUTCH_FRICTION_ZONE_REACHED,
            RiderEventType.CLUTCH_RELEASED_FROM_FRICTION_ZONE,
            RiderEventType.CLUTCH_PULLED_FROM_FRICTION_ZONE,
        )
    ]

    assert clutch_events == []