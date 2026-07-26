import json

from pose.models.rider_state import RiderState


def test_rider_state_to_json():
    rider_state = RiderState(
        left_elbow_angle=90.0,
        right_elbow_angle=95.0,
        pose_confidence=0.98,
    )

    data = json.loads(rider_state.to_json())

    assert data["left_elbow_angle"] == 90.0
    assert data["right_elbow_angle"] == 95.0
    assert data["pose_confidence"] == 0.98