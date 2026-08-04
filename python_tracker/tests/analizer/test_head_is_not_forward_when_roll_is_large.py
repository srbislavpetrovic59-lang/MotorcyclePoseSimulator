from pose.analyzers.head_analyzer import HeadAnalyzer


def test_head_is_not_forward_when_roll_is_large():
    analyzer = HeadAnalyzer()

    assert not analyzer.is_head_forward(
        head_roll=0.25,
        head_yaw_ratio=0.02,
    )