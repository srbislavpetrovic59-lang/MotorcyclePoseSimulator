import json
from dataclasses import dataclass
from pathlib import Path

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

    def to_dict(self) -> dict:
        return {
            "closed_rotation": self.closed_rotation,
            "open_rotation": self.open_rotation,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "ThrottleCalibration":
        return cls(
            closed_rotation=data.get("closed_rotation"),
            open_rotation=data.get("open_rotation"),
        )

    def save(
        self,
        file_path: Path,
    ) -> None:
        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.to_dict(),
                file,
                indent=2,
            )

    @classmethod
    def load(
        cls,
        file_path: Path,
    ) -> "ThrottleCalibration":
        if not file_path.exists():
            return cls()

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return cls.from_dict(data)