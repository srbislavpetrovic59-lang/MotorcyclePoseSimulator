from pose.analyzers.hand_analyzer import HandAnalyzer


def test_hand_analyzer_returns_empty_measurements():
    analyzer = HandAnalyzer()

    result = analyzer.analyze({})

    assert result == {}

   


def test_index_finger_bend_returns_none():
    analyzer = HandAnalyzer()

    assert (
        analyzer._index_finger_bend(None)
        is None
    )