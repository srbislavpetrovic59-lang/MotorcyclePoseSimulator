from pose.rider_event_detector import RiderEventDetector

def test_detector_stores_previous_state():
    detector = RiderEventDetector()

    state = object()

    detector.detect(state)

    assert detector._previous_state is state