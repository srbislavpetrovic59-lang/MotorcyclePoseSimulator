class GearShiftDetector:

    LOW_THRESHOLD = 0.045
    HIGH_THRESHOLD = 0.060

    def __init__(self):
        self._state = "IDLE"
        self._last_zone = None

   
    @classmethod
    def _zone(cls, left_foot_drop):
        if left_foot_drop is None:
            return None

        if left_foot_drop <= cls.LOW_THRESHOLD:
            return "LOW"

        if left_foot_drop >= cls.HIGH_THRESHOLD:
            return "HIGH"

        return "TRANSITION"

    def update(self, left_foot_drop):
        zone = self._zone(left_foot_drop)

        if zone is None:
            return None

        if self._state == "IDLE":
            if zone == "LOW":
                self._state = "LOW_SEEN"
            elif zone == "HIGH":
                self._state = "HIGH_SEEN"

        elif self._state == "LOW_SEEN":
            if zone == "HIGH":
                self._state = "LOW_TO_HIGH"

        elif self._state == "LOW_TO_HIGH":
            if zone != "HIGH":
                self._state = "IDLE"
                self._last_zone = zone
                return "SHIFT_UP"

        elif self._state == "HIGH_SEEN":
            if zone == "LOW":
                self._state = "HIGH_TO_LOW"

        elif self._state == "HIGH_TO_LOW":
            if zone == "HIGH":
                self._state = "IDLE"
                self._last_zone = zone
                return "SHIFT_DOWN"

        self._last_zone = zone

        return None