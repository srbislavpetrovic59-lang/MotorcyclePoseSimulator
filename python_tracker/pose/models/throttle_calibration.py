from dataclasses import dataclass


@dataclass(slots=True)
class ThrottleCalibration:
    closed_rotation: float | None = None
    open_rotation: float | None = None

    def is_complete(self) -> bool:
        return (
            self.closed_rotation is not None
            and self.open_rotation is not None
        )

    def set_closed(
        self,
        rotation: float,
    ) -> None:
        self.closed_rotation = rotation

    def set_open(
        self,
        rotation: float,
    ) -> None:
        self.open_rotation = rotation