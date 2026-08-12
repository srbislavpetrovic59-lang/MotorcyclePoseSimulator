import json

from pose.models.rider_state import RiderState


def test_rider_state_to_json():
    rider_state = RiderState(
        left_elbow_angle=90.0,
        right_elbow_angle=95.0,
        clutch_progress=0.61,
        pose_confidence=0.98,
        left_knee_angle=120.0,
        left_foot_angle=92.0,
        right_foot_angle=94.0,
        right_knee_angle=125.0,
        torso_angle=45.0
    )

    data = json.loads(rider_state.to_json())

    assert data["left_elbow_angle"] == 90.0
    assert data["right_elbow_angle"] == 95.0
    assert data["clutch_progress"] == 0.61
    assert data["left_knee_angle"] == 120
    assert data["right_knee_angle"] == 125
    assert data["left_foot_angle"] == 92.0
    assert data["right_foot_angle"] == 94.0
    assert data["torso_angle"] == 45
    assert data["pose_confidence"] == 0.98