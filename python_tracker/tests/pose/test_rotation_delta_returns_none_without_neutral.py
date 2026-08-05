from pose.analyzers.hand_control_analyzer import HandControlAnalyzer

def test_rotation_delta_returns_none_without_neutral():
    delta = HandControlAnalyzer._rotation_delta(
        neutral_rotation=None,
        current_rotation=196.0,
    )

    assert delta is None

def test_rotation_delta():
    delta = HandControlAnalyzer._rotation_delta(
        neutral_rotation=260.0,
        current_rotation=196.0,
    )

    assert delta == 64.0