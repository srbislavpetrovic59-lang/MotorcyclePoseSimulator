from pose.analyzers.hand_control_analyzer import HandControlAnalyzer

def test_rotation_is_open():
    assert HandControlAnalyzer._is_rotation_open(25.0)

def test_rotation_is_not_open():
    assert not HandControlAnalyzer._is_rotation_open(10.0)

def test_rotation_is_not_open_when_none():
    assert not HandControlAnalyzer._is_rotation_open(None)