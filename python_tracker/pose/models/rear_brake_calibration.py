from dataclasses import dataclass


@dataclass(slots=True)
class RearBrakeCalibration:
    released_drop: float | None = None
    full_drop: float | None = None

    def is_complete(self) -> bool:
        return (
            self.released_drop is not None
            and self.full_drop is not None
        )

    def set_released(
        self,
        drop: float,
    ) -> None:
        self.released_drop = drop

    def set_full(
        self,
        drop: float,
    ) -> None:
        self.full_drop = drop