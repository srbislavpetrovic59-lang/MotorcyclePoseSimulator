from pose.analyzers.hand_control_analyzer import HandControlAnalyzer


def test_left_rotation_delta():
    delta = HandControlAnalyzer._rotation_delta(
        neutral_rotation=325.0,
        current_rotation=265.0,
    )

    assert delta == 60.0