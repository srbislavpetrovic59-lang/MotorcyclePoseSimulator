from pose.rider_event_detector import RiderEventDetector


def test_first_frame_returns_no_events():
    detector = RiderEventDetector()

    events = detector.detect(object())

    assert events == []