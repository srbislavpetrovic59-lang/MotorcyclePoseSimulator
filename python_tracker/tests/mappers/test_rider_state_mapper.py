from pose.mapping.rider_state_mapper import RiderStateMapper


def test_from_analysis():
    analysis = {
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

    assert state.left_elbow_angle == 90.0
    assert state.right_elbow_angle == 95.0
    assert state.pose_confidence == 0.98
    assert state.left_knee_angle == 120.0
    assert state.right_knee_angle == 125.0
    assert state.left_foot_angle == 92.0
    assert state.right_foot_angle == 94.0
    assert state.torso_angle == 45.0