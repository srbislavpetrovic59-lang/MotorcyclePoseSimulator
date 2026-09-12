from pose.models.riding_phase import RidingPhase


class RidingPhaseDetector:

    def __init__(self):
        self._phase = RidingPhase.IDLE

    def update(
        self,
        throttle_progress: float | None,
        front_brake_progress: float | None = None,
        rear_brake_progress: float | None = None,
        torso_angle: float | None = None,
    ) -> RidingPhase:
        if (
            (
                front_brake_progress is not None
                and front_brake_progress >= 0.20
            )
            or
            (
                rear_brake_progress is not None
                and rear_brake_progress >= 0.20
            )
        ):
            self._phase = RidingPhase.BRAKING

        elif (
            self._phase == RidingPhase.BRAKING
            and torso_angle is not None
            and torso_angle >= 35.0
            and (
                front_brake_progress is None
                or front_brake_progress <= 0.10
            )
            and (
                rear_brake_progress is None
                or rear_brake_progress <= 0.10
            )
        ):
            self._phase = RidingPhase.CORNERING
        
        
        
        elif (
            self._phase == RidingPhase.CORNERING
            and throttle_progress is not None
            and throttle_progress >= 0.30
            and torso_angle is not None
            and torso_angle <= 15.0
        ):
            self._phase = RidingPhase.EXIT

        elif (
            throttle_progress is not None
            and throttle_progress >= 0.30
        ):
            self._phase = RidingPhase.ACCELERATION

        return self._phase