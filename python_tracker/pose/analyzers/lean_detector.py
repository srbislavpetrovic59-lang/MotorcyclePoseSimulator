import math

class LeanDetector:

    def __init__(self):
        self._neutral_angle = 0.0
        self._dead_zone = 3.0
        self._release_zone = 2.0
        self._direction = 0
        self._smoothing_alpha = 0.25
        self._smoothed_lean = 0.0

    def calibrate(self, shoulder_tilt: float) -> None:
        self._neutral_angle = shoulder_tilt
        self._direction = 0
        self._smoothed_lean = 0.0

    def update(self, shoulder_tilt: float) -> float:
        relative_lean = shoulder_tilt - self._neutral_angle

        if self._direction == -1:
            if relative_lean > -self._release_zone:
                self._direction = 0

        elif self._direction == 1:
            if relative_lean < self._release_zone:
                self._direction = 0

        if self._direction == 0:
            if relative_lean < -self._dead_zone:
                self._direction = -1
            elif relative_lean > self._dead_zone:
                self._direction = 1

        if self._direction == 0:
            return 0.0

        return relative_lean

    def update_normalized(self, shoulder_tilt: float) -> float:
        relative_lean = self.update(shoulder_tilt)

        normalized = relative_lean / 30.0

        return max(-1.0, min(1.0, normalized))

    def update_smoothed(
        self,
        shoulder_tilt: float,
        dt: float | None = None,
    ) -> float:
        normalized = self.update_normalized(shoulder_tilt)

        if dt is None:
            alpha = self._smoothing_alpha
        else:
            tau = 0.1

            if dt > 0.2:
                alpha = 0.0
            elif dt > 0.0:
                alpha = 1.0 - math.exp(-dt / tau)
            else:
                alpha = 0.0
        self._smoothed_lean = (
            alpha * normalized
            + (1.0 - alpha) * self._smoothed_lean
        )

        if normalized == 0.0 and abs(self._smoothed_lean) < 0.001:
            self._smoothed_lean = 0.0

        return self._smoothed_lean

    def reset(self) -> None:
        self._direction = 0
        self._smoothed_lean = 0.0