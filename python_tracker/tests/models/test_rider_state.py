import json

from pose.models.rider_state import RiderState


def test_rider_state_to_json():
    rider_state = RiderState(
        left_elbow_angle=90.0,
        right_elbow_angle=95.0,
        clutch_progress=0.61,
        front_brake_progress=0.42,
        pose_confidence=0.98,
        left_knee_angle=120.0,
        left_foot_angle=92.0,
        gear_shift="SHIFT_UP",
        right_foot_angle=94.0,
        right_knee_angle=125.0,
        torso_angle=45.0,
        throttle_progress=0.65,
        rear_brake_progress=0.65,
        rear_brake_active=True

    )

    data = json.loads(rider_state.to_json())

    assert data["left_elbow_angle"] == 90.0
    assert data["right_elbow_angle"] == 95.0
    assert data["clutch_progress"] == 0.61
    assert data["left_knee_angle"] == 120
    assert data["right_knee_angle"] == 125
    assert data["left_foot_angle"] == 92.0
    assert data["gear_shift"] == "SHIFT_UP"
    assert data["right_foot_angle"] == 94.0
    assert data["torso_angle"] == 45
    assert data["pose_confidence"] == 0.98 
    assert data["front_brake_progress"] == 0.42
    assert data["throttle_progress"] == 0.65
    assert data["rear_brake_progress"] == 0.65
    assert data["rear_brake_active"] is True
  
def test_rider_state_to_json_without_gear_shift():
    rider_state = RiderState(
        gear_shift=None,
    )

    data = json.loads(rider_state.to_json())

    assert data["gear_shift"] is None    