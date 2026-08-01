from pose.rider_event_detector import RiderEventDetector


def test_detect_returns_empty_list():
    detector = RiderEventDetector()

    events = detector.detect(None)

    assert events == []