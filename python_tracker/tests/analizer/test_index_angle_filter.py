from pose.analyzers.index_angle_filter import IndexAngleFilter


def test_single_angle_spike_is_rejected():
    angle_filter = IndexAngleFilter(window_size=5)

    angles = [172.0, 171.0, 65.0, 170.0, 169.0]

    results = [
        angle_filter.update(angle)
        for angle in angles
    ]

    assert results[-1] == 170.0

def test_gradual_angle_change_is_preserved():
    angle_filter = IndexAngleFilter(window_size=5)

    angles = [
        175.0,
        170.0,
        165.0,
        160.0,
        155.0,
        150.0,
        145.0,
    ]

    results = [
        angle_filter.update(angle)
        for angle in angles
    ]

    assert results[-1] == 155.0
    assert results[-1] < results[0]


def test_gradual_angle_release_is_preserved():
    angle_filter = IndexAngleFilter(window_size=5)

    angles = [
        145.0,
        150.0,
        155.0,
        160.0,
        165.0,
        170.0,
        175.0,
    ]

    results = [
        angle_filter.update(angle)
        for angle in angles
    ]

    assert results[-1] == 165.0
    assert results[-1] > results[0]


def test_tracking_loss_resets_angle_history():
    angle_filter = IndexAngleFilter(window_size=5)

    angle_filter.update(175.0)
    angle_filter.update(170.0)
    angle_filter.update(165.0)

    assert angle_filter.update(None) is None

    # Ponovo pronađen kažiprst.
    assert angle_filter.update(145.0) == 145.0