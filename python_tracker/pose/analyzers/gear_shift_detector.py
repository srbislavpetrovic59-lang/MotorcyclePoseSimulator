class GearShiftDetector:

    LOW_THRESHOLD = 0.045
    HIGH_THRESHOLD = 0.065

    FOOTPEG_MIN = 0.070
    FOOTPEG_MAX = 0.075

    FOOTPEG_EXIT_CONFIRM_FRAMES = 3
    MAX_SHIFT_ATTEMPT_FRAMES = 30

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
        self._forward_movement_active = False
        self._forward_baseline = None
        self._shift_rearm_pending = False
        self._back_movement_active = False
        self._live_forward_baseline_samples = []
        self._direction_zone = None
        self._direction_zone_frames = 0
        self._heel_y_history = []
        self._forward_offset_history = []
        self._pending_heel_y = None
        self._rearm_footpeg_frames = 0
        self._baseline_settle_frames = 0
      
   
   
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
        elapsed_seconds=None,
        left_heel_y=None,
    ):  
        if (
            elapsed_seconds is not None
            and elapsed_seconds < 5.0
        ):
            return None

        self._update_angle_history(left_foot_angle)

        trend = self._angle_trend()

        on_footpeg = self._is_footpeg_stay_position(
            left_foot_drop,
            left_foot_angle,
        )
        
        zone = self._movement_zone(
            left_foot_drop,
            left_foot_angle,
        )

        was_forward_active = self._forward_movement_active
        pending_heel_y = self._pending_heel_y

        self._update_forward_movement_from_baseline(
            left_foot_forward,
        )

        if (
            not was_forward_active
            and self._forward_movement_active
        ):
            self._clear_heel_history()

            if pending_heel_y is not None:
                self._update_heel_history(
                    pending_heel_y
                )

            self._pending_heel_y = None

        elif not self._forward_movement_active:
            self._pending_heel_y = left_heel_y

        self._update_shift_heel_history(
            left_heel_y
        )

        self._update_back_movement(
            left_foot_forward,
        )

        if (
            not self._shift_rearm_pending
            and self._back_movement_active
            and len(self._heel_y_history) >= 3
        ):
            print(
                "HEEL DECISION:",
                self._heel_y_history,
            )
            heel_trend = self._heel_end_trend(
                self._heel_y_history
            )

            heel_shift = self._shift_from_heel_trend(
                heel_trend
            )

            if heel_shift is not None:
                self._shift_rearm_pending = True
                self._back_movement_active = False
                return heel_shift


        if (
            not self._shift_rearm_pending
            and self._back_movement_active
            and not self._heel_y_history
            and self._direction_zone == "DOWN"
            and self._direction_zone_frames >= 3
        ):
            self._shift_rearm_pending = True
            self._back_movement_active = False
            return "SHIFT_DOWN"

        if (
            not self._shift_rearm_pending
            and self._back_movement_active
            and not self._heel_y_history
            and self._direction_zone == "UP"
            and self._direction_zone_frames >= 3
        ):
            self._shift_rearm_pending = True
            self._back_movement_active = False
            return "SHIFT_UP"
        

        if self._forward_movement_active:
            self._update_direction_zone(zone)

        foot_moved_forward = self._is_foot_moved_forward(
                left_foot_forward
            )

        if elapsed_seconds is not None:
            if self._forward_baseline is None and on_footpeg:
                self._live_forward_baseline_samples.append(
                    left_foot_forward
                )

                print(
                    "BASELINE SAMPLE:",
                    left_foot_forward,
                    "samples=",
                    self._live_forward_baseline_samples,
                )

                if len(self._live_forward_baseline_samples) < 5:
                    return None

                self._forward_baseline = (
                    sum(self._live_forward_baseline_samples)
                    / len(self._live_forward_baseline_samples)
                )

                print(
                    "LIVE BASELINE SET:",
                    self._forward_baseline,
                )

        if elapsed_seconds is None:
            self._update_forward_baseline(
                left_foot_forward=left_foot_forward,
                on_footpeg=on_footpeg,
            )

       
        

        print(
            f"GEAR: drop={left_foot_drop} "
            f"angle={left_foot_angle} "
            f"zone={zone} "
            f"trend={trend} "
            f"state={self._state} "
            f"history={self._zone_history} "
            f"pending={self._pending_zones} "
            f"outside={self._outside_footpeg_frames} "
            f"forward={left_foot_forward} "
            f"moved_forward={self._forward_movement_active}"
            f"back={self._back_movement_active} "
            f"rearm={self._shift_rearm_pending}"
            f"baseline={self._forward_baseline} "
            f"offset={self._forward_offset(left_foot_forward)} "
            f"offset_history={self._forward_offset_history} "
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
           
            if self._shift_rearm_pending:
                if on_footpeg:
                    self._rearm_footpeg_frames += 1
                else:
                    self._rearm_footpeg_frames = 0

                if self._rearm_footpeg_frames >= 3:
                    self._shift_rearm_pending = False
                    self._forward_movement_active = False
                    self._back_movement_active = False
                    self._rearm_footpeg_frames = 0

                return None

            if (
                was_forward_active
                and self._is_footpeg_stay_position(
                    left_foot_drop,
                    left_foot_angle,
                )
                and self._back_movement_active
            ):
                self._reset_forward_movement()
                self._outside_footpeg_frames = 0
                self._pending_zones.clear()

                if self._zone_history == ["UP"]:
                    self._zone_history.clear()
                    self._shift_rearm_pending = True
                    return "SHIFT_UP"

                if self._zone_history == ["DOWN"]:
                    self._zone_history.clear()
                    self._shift_rearm_pending = True
                    return "SHIFT_DOWN"
               
                self._zone_history.clear()
                return None
            
            if not self._forward_movement_active:
                self._outside_footpeg_frames = 0
                self._pending_zones.clear()
                return None

           
            if on_footpeg and trend in (None, "STABLE"):
                return None

            self._outside_footpeg_frames += 1

            if (
                self._outside_footpeg_frames
                >= self.MAX_SHIFT_ATTEMPT_FRAMES
            ):
                if self._zone_history == ["UP"]:
                    self._reset_stale_shift_attempt()
                    self._shift_rearm_pending = True
                    return "SHIFT_UP"

                if self._zone_history == ["DOWN"]:
                    self._reset_stale_shift_attempt()
                    self._shift_rearm_pending = True
                    return "SHIFT_DOWN"

                self._reset_stale_shift_attempt()
                return None

            candidate = None

            if trend == "RISING":
                candidate = "UP"
            elif trend == "FALLING":
                candidate = "DOWN"

            if candidate is not None:
                self._add_shift_candidate(candidate)

            if (
                self._outside_footpeg_frames
                < self.FOOTPEG_EXIT_CONFIRM_FRAMES
            ):
                return None

            
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
            0.050 <= left_foot_drop <= 0.135
            and 150.0 <= left_foot_angle <= 180.0
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

        return abs(left_foot_forward) >= 0.030

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

    def _update_forward_movement(self, left_foot_forward):
        if self._is_foot_moved_forward(left_foot_forward):
            self._forward_movement_active = True

    def _reset_forward_movement(self):
        self._forward_movement_active = False
        

    def _set_forward_baseline(self, value):
        self._forward_baseline = value

    def _forward_offset(self, left_foot_forward):
        if (
            self._forward_baseline is None
            or left_foot_forward is None
        ):
            return None

        return left_foot_forward - self._forward_baseline

    def _update_forward_movement_from_baseline(
        self,
        left_foot_forward,
    ):
        offset = self._forward_offset(
            left_foot_forward
        )

        if offset is None:
            return

        if abs(offset) < 0.002:
            self._baseline_settle_frames += 1
        else:
            self._baseline_settle_frames = 0

        if self._baseline_settle_frames >= 3:
            self._forward_offset_history.clear()
            self._baseline_settle_frames = 0
            return



        self._forward_offset_history.append(offset)

        if len(self._forward_offset_history) > 10:
            self._forward_offset_history.pop(0)

        if (
            len(self._forward_offset_history) >= 2
        ):
            previous = self._forward_offset_history[-2]
            current = self._forward_offset_history[-1]

            if (
                previous >= 0.019
                and current >= 0.019
            ):
                self._forward_movement_active = True
                self._back_movement_active = False
                return

            if (
                previous <= -0.019
                and current <= -0.019
            ):
                self._forward_movement_active = True
                self._back_movement_active = False
                return


        if len(self._forward_offset_history) >= 3:
            recent = self._forward_offset_history[-3:]

            if (
                all(offset > 0.0 for offset in recent)
                and sum(
                    offset >= 0.019
                    for offset in recent
                ) >= 2
            ):
                self._forward_movement_active = True
                self._back_movement_active = False
                return

        if (
            max(self._forward_offset_history) >= 0.008
            and min(self._forward_offset_history) <= -0.008
        ):
            self._forward_movement_active = True
            self._back_movement_active = False
            return

        if len(self._forward_offset_history) >= 2:
            previous = self._forward_offset_history[-2]
            current = self._forward_offset_history[-1]
                       
            if (
                previous <= -0.008
                and current <= -0.008
            ):
                self._forward_movement_active = True
                self._back_movement_active = False
                return

    def _update_forward_baseline(
        self,
        left_foot_forward,
        on_footpeg,
    ):
        if left_foot_forward is None:
            return

        if not on_footpeg:
            return

        if self._forward_baseline is not None:
            return

        self._forward_baseline = left_foot_forward

        print(
            "GEAR BASELINE SET:",
            self._forward_baseline,
        )

    def _reset_stale_shift_attempt(self):
        self._forward_movement_active = False
        self._back_movement_active = False
        self._outside_footpeg_frames = 0
        self._pending_zones.clear()
        self._zone_history.clear()
        

    def _add_shift_candidate(self, candidate):
        if candidate not in ("UP", "DOWN"):
            return

        if (
            self._zone_history
            and self._back_movement_active
        ):
            return

        self._pending_zones.append(candidate)

        if not self._zone_history:
            if (
                len(self._pending_zones) >= 2
                and self._pending_zones[-1] == self._pending_zones[-2]
            ):
                self._zone_history = [candidate]
            return

        confirmed = self._zone_history[0]

        if candidate == confirmed:
            return

        if (
            len(self._pending_zones) >= 3
            and self._pending_zones[-1] == candidate
            and self._pending_zones[-2] == candidate
            and self._pending_zones[-3] == candidate
        ):
            self._zone_history = [candidate]

    def _is_foot_moved_back(
        self,
        left_foot_forward,
    ):
        if (
            self._forward_baseline is None
            or left_foot_forward is None
        ):
            return False

        return (
            abs(
                left_foot_forward
                - self._forward_baseline
            )
            < 0.019
        )

    def _update_back_movement(
        self,
        left_foot_forward,
    ):
        if not self._forward_movement_active:
            return

        if self._is_foot_moved_back(
            left_foot_forward
        ):
            self._back_movement_active = True

    def _update_direction_zone(
        self,
        zone,
    ):
        if zone not in ("UP", "DOWN"):
            self._direction_zone = None
            self._direction_zone_frames = 0
            return

        if zone == self._direction_zone:
            self._direction_zone_frames += 1
        else:
            self._direction_zone = zone
            self._direction_zone_frames = 1

    @staticmethod
    def _heel_end_trend(heel_y):
        if heel_y is None or len(heel_y) < 2:
            return None

        if heel_y[-1] < heel_y[0]:
            return "UP"

        if heel_y[-1] > heel_y[0]:
            return "DOWN"

        return "STABLE"

        
    @staticmethod
    def _heel_end_trend(heel_y):
        if heel_y is None or len(heel_y) < 2:
            return None

        delta = heel_y[-1] - heel_y[0]

        if abs(delta) < 0.005:
            return "STABLE"

        if delta < 0:
            return "UP"

        return "DOWN"

    @staticmethod
    def _shift_from_heel_trend(heel_trend):
        if heel_trend == "UP":
            return "SHIFT_DOWN"

        if heel_trend == "DOWN":
            return "SHIFT_UP"

        return None

    def _update_heel_history(self, heel_y):
        if heel_y is None:
            return

        self._heel_y_history.append(heel_y)

    def _update_heel_history(self, heel_y):
        if heel_y is None:
            return

        self._heel_y_history.append(heel_y)

        if len(self._heel_y_history) > 10:
            self._heel_y_history.pop(0)

    def _clear_heel_history(self):
        self._heel_y_history.clear()

    def _update_shift_heel_history(self, heel_y):
        if (
            not self._forward_movement_active
            and not self._back_movement_active
        ):
            return

        self._update_heel_history(heel_y)
  
    @staticmethod
    def _heel_end_trend(heel_y):
        if heel_y is None or len(heel_y) < 3:
            return None

        end_samples = heel_y[-5:]
        

        total_delta = (
            end_samples[-1] - end_samples[0]
        )

        if abs(total_delta) < 0.005:
            return "STABLE"

        deltas = [
            end_samples[index] - end_samples[index - 1]
            for index in range(1, len(end_samples))
        ]

        directions = []

        for delta in deltas:
            if delta < 0:
                directions.append("UP")
            elif delta > 0:
                directions.append("DOWN")
            else:
                directions.append("STABLE")

        # Ignore flat samples at the very end.
        while (
            directions
            and directions[-1] == "STABLE"
        ):
            directions.pop()

        if len(directions) < 2:
            return "STABLE"
        
        if (
            directions[-1] == directions[-2]
            and directions[-1] in ("UP", "DOWN")
        ):
            return directions[-1]

        return "STABLE"
   