from pose.analyzers.hand_control_analyzer import HandControlAnalyzer

def test_rotation_delta_returns_none_without_current():
    delta = HandControlAnalyzer._rotation_delta(
        neutral_rotation=260.0,
        current_rotation=None,
    )

    assert delta is None