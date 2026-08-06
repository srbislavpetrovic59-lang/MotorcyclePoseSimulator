from pose.mapping.rider_state_mapper import RiderStateMapper


def test_from_analysis():
    analysis = {
        "head_roll": 10.0,
        "head_yaw_ratio": 0.25,
        "left_hand_detected": True,
        "right_hand_detected": False,
        "right_hand_rotation": 215.0,
        "left_hand_rotation": 180.0,
        "throttle_open": True,
        "head_forward": True,
        "left_elbow_angle": 90.0,
        "right_elbow_angle": 95.0,
        "pose_confidence": 0.98,
        "left_knee_angle": 120.0,
        "right_knee_angle": 125.0,
        "left_foot_angle": 92.0,
        "right_foot_angle": 94.0,
        "torso_angle": 45.0
    }

    state = RiderStateMapper.from_analysis(analysis)
    
    assert state.timestamp > 0.0
    assert state.head_roll == 10.0
    assert state.head_yaw_ratio == 0.25
    assert state.left_hand_detected is True
    assert state.right_hand_detected is False
    assert state.right_hand_rotation == 215.0
    assert state.left_hand_rotation == 180.0  
    assert state.throttle_open is True
    assert state.head_forward is True
    assert state.left_elbow_angle == 90.0
    assert state.right_elbow_angle == 95.0
    assert state.pose_confidence == 0.98
    assert state.left_knee_angle == 120.0
    assert state.right_knee_angle == 125.0
    assert state.left_foot_angle == 92.0
    assert state.right_foot_angle == 94.0
    assert state.torso_angle == 45.0