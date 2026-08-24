class GearShiftDetector:

    LOW_THRESHOLD = 0.045
    HIGH_THRESHOLD = 0.065

    FOOTPEG_MIN = 0.070
    FOOTPEG_MAX = 0.075

    UP_MIN = 0.085
    UP_MAX = 0.095

    DOWN_MIN = 0.100
    DOWN_MAX = 0.110

    def __init__(self):
        self._state = "IDLE"
        self._last_zone = None
        self._zone_history = []
      
   
   
    @classmethod
    def _zone(cls, left_foot_drop):
        if left_foot_drop is None:
            return None

        if left_foot_drop <= cls.LOW_THRESHOLD:
            return "LOW"

        if left_foot_drop >= cls.HIGH_THRESHOLD:
            return "HIGH"

        return "TRANSITION"

    def update(
        self,
        left_foot_drop,
        left_foot_angle=None,
    ):
        zone = self._drop_zone(left_foot_drop)

        print(
            "GEAR:",
            f"drop={left_foot_drop}",
            f"angle={left_foot_angle}",
            f"zone={zone}",
            f"state={self._state}",
            f"history={self._zone_history}",
        )

        if self._state == "IDLE":
            if self._is_footpeg_position(
                left_foot_drop,
                left_foot_angle,
            ):
                self._state = "READY"

            return None
        
        if zone is None:
            return None

        if self._state == "READY":
            if self._is_footpeg_position(
                left_foot_drop,
                left_foot_angle,
            ):
                if self._zone_history == ["LOW", "HIGH"]:
                    self._zone_history.clear()
                    return "SHIFT_UP"

                if self._zone_history == ["HIGH", "LOW"]:
                    self._zone_history.clear()
                    return "SHIFT_DOWN"

                self._zone_history.clear()
                return None

            if zone is not None:
                if (
                    not self._zone_history
                    or self._zone_history[-1] != zone
                ):
                    self._zone_history.append(zone)

            return None
        
        return None

    @classmethod
    def _drop_zone(cls, left_foot_drop):
        if left_foot_drop is None:
            return None

        if left_foot_drop <= cls.LOW_THRESHOLD:
            return "LOW"

        if left_foot_drop >= cls.HIGH_THRESHOLD:
            return "HIGH"

        return "MID"
    @staticmethod
    def _is_footpeg_position(
        left_foot_drop,
        left_foot_angle,
    ) -> bool:
        if (
            left_foot_drop is None
            or left_foot_angle is None
        ):
            return False

        return (
            0.055 <= left_foot_drop <= 0.065
            and 120.0 <= left_foot_angle <= 134.0
        )