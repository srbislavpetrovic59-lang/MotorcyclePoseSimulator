from pose.rider_events import RiderEventType


def test_pose_events_are_defined():
    assert RiderEventType.POSE_ACQUIRED is not None
    assert RiderEventType.POSE_LOST is not None