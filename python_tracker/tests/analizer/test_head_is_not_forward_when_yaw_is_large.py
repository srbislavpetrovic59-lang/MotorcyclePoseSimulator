from pose.analyzers.head_analyzer import HeadAnalyzer

def test_head_is_not_forward_when_yaw_is_large():
    
    analyzer = HeadAnalyzer()
    
    assert not analyzer.is_head_forward(
        head_roll=0.01,
        head_yaw_ratio=0.45,
    )