from pose.models.riding_phase import RidingPhase


def test_riding_phase_contains_track_phases():
    assert RidingPhase.IDLE.value == "IDLE"
    assert RidingPhase.ACCELERATION.value == "ACCELERATION"
    assert RidingPhase.BRAKING.value == "BRAKING"
    assert RidingPhase.CORNERING.value == "CORNERING"
    assert RidingPhase.EXIT.value == "EXIT"