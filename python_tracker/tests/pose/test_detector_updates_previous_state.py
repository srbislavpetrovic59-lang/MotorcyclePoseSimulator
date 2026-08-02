from pose.rider_event_detector import RiderEventDetector


def test_detector_updates_previous_state():
    detector = RiderEventDetector()

    first_state = object()
    second_state = object()

    detector.detect(first_state)
    detector.detect(second_state)

    assert detector._previous_state is second_state