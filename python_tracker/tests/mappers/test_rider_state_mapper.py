from pose.mapping.rider_state_mapper import RiderStateMapper


def test_from_analysis():
    analysis = {
        "left_elbow_angle": 90.0,
        "right_elbow_angle": 95.0,
        "pose_confidence": 0.98,
    }

    state = RiderStateMapper.from_analysis(analysis)

    assert state.left_elbow_angle == 90.0
    assert state.right_elbow_angle == 95.0
    assert state.pose_confidence == 0.98