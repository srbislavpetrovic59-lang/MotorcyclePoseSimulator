from pose.analyzers.hand_control_analyzer import HandControlAnalyzer



def test_left_rotation_is_active():
    assert HandControlAnalyzer._is_left_rotation_active(
        25.0,
    )

def test_left_rotation_is_not_active():
    assert not HandControlAnalyzer._is_left_rotation_active(
        10.0,
    )

def test_left_rotation_is_not_active_when_none():
    assert not HandControlAnalyzer._is_left_rotation_active(
        None,
    )