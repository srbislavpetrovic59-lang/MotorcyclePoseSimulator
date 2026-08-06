from pose.analyzers.hand_control_analyzer import HandControlAnalyzer


def test_rotation_delta_handles_angle_wraparound():
    delta = HandControlAnalyzer._rotation_delta(
        neutral_rotation=350.0,
        current_rotation=10.0,
    )

    assert delta == -20.0