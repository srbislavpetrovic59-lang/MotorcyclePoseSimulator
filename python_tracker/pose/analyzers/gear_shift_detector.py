class GearShiftDetector:

    LOW_THRESHOLD = 0.045
    HIGH_THRESHOLD = 0.065

    FOOTPEG_MIN = 0.070
    FOOTPEG_MAX = 0.075

    FOOTPEG_EXIT_CONFIRM_FRAMES = 3

    UP_MIN = 0.085
    UP_MAX = 0.095

    DOWN_MIN = 0.100
    DOWN_MAX = 0.110

    def __init__(self):
        self._state = "IDLE"
        self._last_zone = None
        self._zone_history = []
        self._outside_footpeg_frames = 0
        self._pending_zones = []
        self._angle_history = []
      
   
   
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
        left_foot_forward=None,
    ):
        self._update_angle_history(left_foot_angle)
        foot_moved_forward = self._is_foot_moved_forward(
            left_foot_forward
        )

        zone = self._movement_zone(
            left_foot_drop,
            left_foot_angle,
        )
        

        print(
            "GEAR:",
            f"drop={left_foot_drop}",
            f"angle={left_foot_angle}",
            f"zone={zone}",
            f"state={self._state}",
            f"history={self._zone_history}",
            f"pending={self._pending_zones}",
            f"outside={self._outside_footpeg_frames}",
            f"forward={left_foot_forward}",
            f"moved_forward={foot_moved_forward}",
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
            if (
                self._is_footpeg_stay_position(
                    left_foot_drop,
                    left_foot_angle,
                )
                and not foot_moved_forward
            ):
                self._outside_footpeg_frames = 0
                self._pending_zones.clear()

                if self._zone_history == ["UP"]:
                    self._zone_history.clear()
                    return "SHIFT_UP"

                if self._zone_history == ["DOWN"]:
                    self._zone_history.clear()
                    return "SHIFT_DOWN"

                self._zone_history.clear()
                return None

            if not foot_moved_forward:
                self._outside_footpeg_frames = 0
                self._pending_zones.clear()
                return None

            self._outside_footpeg_frames += 1

            if zone in ("UP", "DOWN"):
                if (
                    not self._pending_zones
                    or self._pending_zones[-1] != zone
                ):
                    self._pending_zones.append(zone)

            if (
                self._outside_footpeg_frames
                < self.FOOTPEG_EXIT_CONFIRM_FRAMES
            ):
                return None

            for pending_zone in self._pending_zones:
                if (
                    not self._zone_history
                    or self._zone_history[-1] != pending_zone
                ):
                    self._zone_history.append(pending_zone)

            self._pending_zones.clear()

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
            0.095 <= left_foot_drop <= 0.135
            and 150.0 <= left_foot_angle <= 157.0
        )

    @staticmethod
    def _is_footpeg_stay_position(
        left_foot_drop,
        left_foot_angle,
    ) -> bool:
        if (
            left_foot_drop is None
            or left_foot_angle is None
        ):
            return False

        return (
            0.090 <= left_foot_drop <= 0.140
            and 150.0 <= left_foot_angle <= 158.0
        )
    @classmethod
    def _movement_zone(
        cls,
        left_foot_drop,
        left_foot_angle,
    ):
        if (
            left_foot_drop is None
            or left_foot_angle is None
        ):
            return None

        if left_foot_angle >= 158.0:
            return "UP"

        if left_foot_angle <= 150.0:
            return "DOWN"

        return "TRANSITION"

    @staticmethod
    def _is_foot_moved_forward(left_foot_forward):
        if left_foot_forward is None:
            return False

        return left_foot_forward >= 0.030

    def _angle_trend(self):
        if len(self._angle_history) < 4:
            return None

        first = self._angle_history[0]
        last = self._angle_history[-1]

        delta = last - first

        if delta >= 5.0:
            return "RISING"

        if delta <= -5.0:
            return "FALLING"

        return "STABLE"

    def _update_angle_history(self, angle):
        if angle is None:
            return

        self._angle_history.append(angle)

        if len(self._angle_history) > 4:
            self._angle_history.pop(0)