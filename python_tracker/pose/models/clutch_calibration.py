from dataclasses import dataclass


@dataclass(slots=True)
class ClutchCalibration:
    released_angle: float | None = None
    pulled_angle: float | None = None

    def is_complete(self) -> bool:
        return (
            self.released_angle is not None
            and self.pulled_angle is not None
        )

    def set_released(self, angle: float) -> None:
        self.released_angle = angle

    def set_pulled(self, angle: float) -> None:
        self.pulled_angle = angle