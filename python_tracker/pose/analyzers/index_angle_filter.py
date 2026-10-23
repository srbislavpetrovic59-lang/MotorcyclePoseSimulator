from collections import deque
from statistics import median


class IndexAngleFilter:
    def __init__(self, window_size: int = 5):
        self._angles = deque(maxlen=window_size)

    def update(self, angle: float | None) -> float | None:
        if angle is None:
            self._angles.clear()
            return None

        self._angles.append(angle)
        return float(median(self._angles))