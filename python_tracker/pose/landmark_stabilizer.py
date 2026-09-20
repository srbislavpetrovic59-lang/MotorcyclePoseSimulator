class LandmarkStabilizer:
    def __init__(self):
        self._values = {}
        self._candidates = {}
        self._candidate_counts = {}

    def update(self, name: str, value: float) -> float:
        
        if value is None:
            self._values.pop(name, None)
            self._candidates.pop(name, None)
            self._candidate_counts.pop(name, None)
            return None
        previous = self._values.get(name)

        if previous is None:
            self._values[name] = value
            return value

        if abs(value - previous) <= 0.10:
            self._values[name] = value
            self._candidates.pop(name, None)
            self._candidate_counts.pop(name, None)
            return value

        candidate = self._candidates.get(name)

        if candidate is not None:
            close = abs(value - candidate) <= 0.0200001

            previous_direction = candidate - previous
            current_direction = value - candidate

            same_direction = (
                previous_direction * current_direction > 0
            )

            if close or same_direction:
                self._candidate_counts[name] += 1
            else:
                self._candidate_counts[name] = 1
        else:
            self._candidate_counts[name] = 1

        self._candidates[name] = value

        if self._candidate_counts[name] >= 3:
            self._values[name] = value
            self._candidates.pop(name, None)
            self._candidate_counts.pop(name, None)
            return value

        return previous