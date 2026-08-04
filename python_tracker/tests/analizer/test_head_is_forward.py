from pose.analyzers.head_analyzer import HeadAnalyzer


def test_head_is_forward():
    
    analyzer = HeadAnalyzer()

    assert analyzer.is_head_forward(
        head_roll=0.02,
        head_yaw_ratio=0.0,
    )