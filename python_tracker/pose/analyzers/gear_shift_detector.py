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
        self._heel_visibility_history = []
        self._forward_offset_history = []
        self._pending_heel_y_history = []
        self._rearm_footpeg_frames = 0
        self._baseline_settle_frames = 0
        self._startup_ready = False
        self._startup_footpeg_frames = 0
      
   
    def update(
        self,
        left_foot_drop,
        left_foot_angle=None,
        left_foot_forward=None,
        elapsed_seconds=None,
        left_heel_y=None,
        left_heel_visibility=None,
        ):
            if (
                elapsed_seconds is not None
                and elapsed_seconds < 5.0
            ):
                return None

            suppress_shift_event = (
                elapsed_seconds is not None
                and elapsed_seconds < 6.0
            )

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

            # ---------------------------------------------------------
            # Live baseline learning
            # ---------------------------------------------------------

            if elapsed_seconds is not None:
                if (
                    self._forward_baseline is None
                    and on_footpeg
                ):
                    self._live_forward_baseline_samples.append(
                        left_foot_forward
                    )

                    print(
                        "BASELINE SAMPLE:",
                        left_foot_forward,
                        "samples=",
                        self._live_forward_baseline_samples,
                    )

                    if (
                        len(
                            self._live_forward_baseline_samples
                        )
                        < 5
                    ):
                        return None

                    recent = (
                        self._live_forward_baseline_samples[-5:]
                    )

                    if (
                        max(recent) - min(recent)
                        > 0.008
                    ):
                        self._live_forward_baseline_samples.pop(
                            0
                        )
                        return None

                    self._forward_baseline = (
                        sum(recent)
                        / len(recent)
                    )

                    print(
                        "LIVE BASELINE SET:",
                        self._forward_baseline,
                    )

            # Unit-test / non-live baseline handling
            if elapsed_seconds is None:
                self._update_forward_baseline(
                    left_foot_forward=left_foot_forward,
                    on_footpeg=on_footpeg,
                )

            # ---------------------------------------------------------
            # State initialization
            # ---------------------------------------------------------

            if self._state == "IDLE":
                if self._is_footpeg_position(
                    left_foot_drop,
                    left_foot_angle,
                ):
                    self._state = "READY"

                    if (
                        elapsed_seconds is None
                        and self._forward_baseline is None
                    ):
                        self._set_forward_baseline(
                            left_foot_forward
                        )

                return None

            # ---------------------------------------------------------
            # Settling period
            #
            # 5-6 s:
            # - READY and baseline are allowed
            # - no shift-attempt state may survive
            # ---------------------------------------------------------

            if suppress_shift_event:
                self._forward_movement_active = False
                self._back_movement_active = False
                self._shift_rearm_pending = False

                self._clear_heel_history()
                self._pending_heel_y_history.clear()
                self._forward_offset_history.clear()

                return None

            # ---------------------------------------------------------
            # startup stabilization after 6 s
            # ---------------------------------------------------------

            if (
                elapsed_seconds is not None
                and not self._startup_ready
            ):
                if on_footpeg:
                    self._startup_footpeg_frames += 1
                

                if self._startup_footpeg_frames >= 3:
                    self._startup_ready = True

                    self._forward_movement_active = False
                    self._back_movement_active = False
                    self._forward_offset_history.clear()

                print(
                    "STARTUP:",
                    "on_footpeg=", on_footpeg,
                    "frames=", self._startup_footpeg_frames,
                    "ready=", self._startup_ready,
                )

                return None

            # ---------------------------------------------------------
            # Normal gear-shift detection starts here
            # ---------------------------------------------------------

            was_forward_active = (
                self._forward_movement_active
            )

            pending_heel_y_history = (
                self._pending_heel_y_history.copy()
            )

            self._update_forward_movement_from_baseline(
                left_foot_forward,
            )

            if was_forward_active:
                self._update_back_movement(
                    left_foot_forward,
                )

            if (
                not was_forward_active
                and self._forward_movement_active
            ):
                self._clear_heel_history()

                for heel_y in pending_heel_y_history:
                    self._update_heel_history(
                        heel_y
                    )

                self._pending_heel_y_history.clear()

            elif not self._forward_movement_active:
                if left_heel_y is not None:
                    self._pending_heel_y_history.append(
                        left_heel_y
                    )

                    if (
                        len(
                            self._pending_heel_y_history
                        )
                        > 5
                    ):
                        self._pending_heel_y_history.pop(
                            0
                        )

            self._update_shift_heel_history(
                left_heel_y,
                left_heel_visibility,
            )

            # ---------------------------------------------------------
            # Heel-based shift decision
            # ---------------------------------------------------------

            if (
                not self._shift_rearm_pending
                and self._back_movement_active
                and len(self._heel_y_history) >= 3
            ):
                print(
                    "HEEL DECISION:",
                    self._heel_y_history,
                    "visibility=",
                    self._heel_visibility_history,
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

            # ---------------------------------------------------------
            # Direction-zone fallback
            # ---------------------------------------------------------

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

            # ---------------------------------------------------------
            # Direction tracking
            # ---------------------------------------------------------

            if self._forward_movement_active:
                self._update_direction_zone(
                    zone
                )

            foot_moved_forward = (
                self._is_foot_moved_forward(
                    left_foot_forward
                )
            )

            # ---------------------------------------------------------
            # Debug output
            # ---------------------------------------------------------

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

            if zone is None:
                return None

            # ---------------------------------------------------------
            # READY state
            # ---------------------------------------------------------

            if self._state == "READY":

                # -----------------------------------------------------
                # Rearm after detected shift
                # -----------------------------------------------------

                if self._shift_rearm_pending:
                    print(
                        "REARM:",
                        "on_footpeg=", on_footpeg,
                        "frames=",
                        self._rearm_footpeg_frames,
                        "drop=", left_foot_drop,
                        "angle=", left_foot_angle,
                    )

                    if on_footpeg:
                        self._rearm_footpeg_frames += 1
                    else:
                        self._rearm_footpeg_frames = 0

                    if (
                        self._rearm_footpeg_frames
                        >= 3
                    ):
                        self._shift_rearm_pending = False
                        self._forward_movement_active = False
                        self._back_movement_active = False

                        self._forward_offset_history.clear()

                        self._rearm_footpeg_frames = 0

                    return None

                # -----------------------------------------------------
                # Foot returned to footpeg after shift attempt
                # -----------------------------------------------------

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

                # -----------------------------------------------------
                # No shift attempt
                # -----------------------------------------------------

                if not self._forward_movement_active:
                    self._outside_footpeg_frames = 0
                    self._pending_zones.clear()

                    return None

                if (
                    on_footpeg
                    and trend in (None, "STABLE")
                ):
                    return None

                self._outside_footpeg_frames += 1

                # -----------------------------------------------------
                # Shift attempt timeout
                # -----------------------------------------------------

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

                # -----------------------------------------------------
                # Shift direction candidate
                # -----------------------------------------------------

                candidate = None

                if trend == "RISING":
                    candidate = "UP"

                elif trend == "FALLING":
                    candidate = "DOWN"

                if candidate is not None:
                    self._add_shift_candidate(
                        candidate
                    )

                if (
                    self._outside_footpeg_frames
                    < self.FOOTPEG_EXIT_CONFIRM_FRAMES
                ):
                    return None

                return None

            return None
    @classmethod
    def _zone(cls, left_foot_drop):
        if left_foot_drop is None:
            return None

        if left_foot_drop <= cls.LOW_THRESHOLD:
            return "LOW"

        if left_foot_drop >= cls.HIGH_THRESHOLD:
            return "HIGH"

        return "TRANSITION"

    

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
            (
                0.050 <= left_foot_drop <= 0.135
                and 150.0 <= left_foot_angle <= 180.0
            )
            or
            (
                -0.060 <= left_foot_drop <= -0.040
                and 160.0 <= left_foot_angle <= 175.0
            )
            or (0.050 <= left_foot_drop <= 0.060 and 138.0 <= left_foot_angle <= 150.0)
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
            (
                0.090 <= left_foot_drop <= 0.140
                and 150.0 <= left_foot_angle <= 158.0
            )
            or
            (
                0.040 <= left_foot_drop <= 0.060
                and 90.0 <= left_foot_angle <= 110.0
            )
            or
            (
                0.040 <= left_foot_drop <= 0.060
                and 160.0 <= left_foot_angle <= 175.0
            )
            or
            (
                -0.140 <= left_foot_drop <= -0.090
                and 150.0 <= left_foot_angle <= 158.0
            )
            or
            (
                -0.060 <= left_foot_drop <= -0.040
                and 160.0 <= left_foot_angle <= 175.0
            )
            or (0.070 <= left_foot_drop <= 0.085 and 140.0 <= left_foot_angle <= 147.0)
            or (0.050 <= left_foot_drop <= 0.060 and 138.0 <= left_foot_angle <= 153.0)
           
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
            print("FORWARD BRANCH: recent positive")
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

        if self._rearm_footpeg_frames >= 3:
            self._shift_rearm_pending = False
            self._forward_movement_active = False
            self._back_movement_active = False
            self._forward_offset_history.clear()
            self._rearm_footpeg_frames = 0



        self._forward_offset_history.append(offset)

        if len(self._forward_offset_history) > 10:
            self._forward_offset_history.pop(0)

        if len(self._forward_offset_history) >= 5:
            recent = self._forward_offset_history[-5:]

            moved_outward = (
                max(recent) - recent[0] >= 0.003
            )
            
            recent_steps = [
                abs(recent[index] - recent[index - 1])
                for index in range(1, len(recent))
            ]

            smooth_outward_movement = (
                max(recent_steps) <= 0.005
            )

            if (
                all(offset > 0.0 for offset in recent)
                and recent[-1] >= 0.007
                and moved_outward
                and smooth_outward_movement
            ): 
                print("FORWARD BRANCH: two negative")
                self._forward_movement_active = True
                self._back_movement_active = False
                return

        if len(self._forward_offset_history) >= 4:
            recent = self._forward_offset_history[-4:]

            outward = recent[:3]
            returned = recent[-1]

            if (
                all(0.005 <= offset <= 0.008 for offset in outward)
                and abs(returned) <= 0.002
                and max(outward) - returned >= 0.005
            ):
                self._forward_movement_active = True
                self._back_movement_active = False
                return
                
        if len(self._forward_offset_history) >= 4:
            recent = self._forward_offset_history[-4:]

            moved_outward = (
                max(recent) - recent[0] >= 0.003
            )

            recent_steps = [
                abs(recent[index] - recent[index - 1])
                for index in range(1, len(recent))
            ]

            smooth_outward_movement = (
                max(recent_steps) <= 0.005
            )

            if (
                all(offset > 0.0 for offset in recent)
                and recent[-1] >= 0.008
                and moved_outward
                and smooth_outward_movement
            ):
                self._forward_movement_active = True
                self._back_movement_active = False
                return

        if (
            len(self._forward_offset_history) >= 2
        ):
            previous = self._forward_offset_history[-2]
            current = self._forward_offset_history[-1]

            if (
                previous >= 0.019
                and current >= 0.019
            ):
                print("FORWARD BRANCH: 8 recent positive")
                self._forward_movement_active = True
                self._back_movement_active = False
                return

            if (
                previous <= -0.019
                and current <= -0.019
            ):
                print("FORWARD BRANCH: 3 positive")
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
                print("FORWARD BRANCH: recent 4 positive")
                self._forward_movement_active = True
                self._back_movement_active = False
                return

        if len(self._forward_offset_history) >= 3:
            current = self._forward_offset_history[-1]

            if current <= -0.008:
                for index in range(
                    len(self._forward_offset_history) - 2,
                    -1,
                    -1,
                ):
                    previous = self._forward_offset_history[index]

                    if previous >= 0.008:
                        between = self._forward_offset_history[
                            index + 1:-1
                        ]

                        if any(
                            abs(offset) < 0.004
                            for offset in between
                        ):
                            print("FORWARD BRANCH: 9 recent positive")
                            self._forward_movement_active = True
                            self._back_movement_active = False
                            return

                        break

            elif current >= 0.008:
                for index in range(
                    len(self._forward_offset_history) - 2,
                    -1,
                    -1,
                ):
                    previous = self._forward_offset_history[index]

                    if previous <= -0.008:
                        between = self._forward_offset_history[
                            index + 1:-1
                        ]

                        if any(
                            abs(offset) < 0.004
                            for offset in between
                        ):
                            print("FORWARD BRANCH: recent  5 positive")
                            self._forward_movement_active = True
                            self._back_movement_active = False
                            return

                        break
       
        if len(self._forward_offset_history) >= 3:
            previous = self._forward_offset_history[-2]
            current = self._forward_offset_history[-1]

            approached_from_negative_side = any(
                -0.008 < offset < 0.0
                for offset in self._forward_offset_history[:-2]
            )
            prior = self._forward_offset_history[-3]

            previous_step = abs(previous - prior)
            current_step = abs(current - previous)

            recent_offsets = self._forward_offset_history[-4:]

            recent_steps = [
                abs(recent_offsets[index] - recent_offsets[index - 1])
                for index in range(1, len(recent_offsets))
            ]

            settling_negative_path = (
                len(recent_steps) >= 2
                and max(recent_steps) <= 0.008
                and current_step <= previous_step
            )
            #==========================================
            print(
                "BRANCH 6 DATA:",
                "history=", self._forward_offset_history,
                "prior=", prior,
                "previous=", previous,
                "current=", current,
                "previous_step=", previous_step,
                "current_step=", current_step,
            )
            #=========================================



            if (
                approached_from_negative_side
                and previous <= -0.008
                and current <= -0.008
                and settling_negative_path
            ):
                print("FORWARD BRANCH: 6 recent positive")
                self._forward_movement_active = True
                self._back_movement_active = False
                return
        if len(self._forward_offset_history) >= 2:
            previous = self._forward_offset_history[-2]
            current = self._forward_offset_history[-1]

            if (
                previous >= 0.019
                and current >= 0.018
            ):
                print("FORWARD BRANCH: 7 recent positive")
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

        offset = self._forward_offset(
            left_foot_forward
        )

        if offset is None:
            return

        if abs(offset) < 0.002:
            self._back_movement_active = True
            return

        if len(self._forward_offset_history) < 2:
            return

        previous = self._forward_offset_history[-2]
        current = self._forward_offset_history[-1]

        moving_toward_baseline = (
            abs(current) < abs(previous)
        )

        if (
            moving_toward_baseline
            and self._is_foot_moved_back(
                left_foot_forward
            )
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
        self._heel_visibility_history.clear()

    def _update_shift_heel_history(
        self,
        heel_y,
        heel_visibility=None,
    ):
        if (
            not self._forward_movement_active
            and not self._back_movement_active
        ):
            return

        self._update_heel_history(heel_y)

        self._update_heel_visibility_history(
            heel_visibility
        )
     

    def _update_heel_visibility_history(
        self,
        visibility,
    ):
        if visibility is None:
            return

        self._heel_visibility_history.append(
            visibility
        )

        if len(self._heel_visibility_history) > 10:
            self._heel_visibility_history.pop(0)

    @staticmethod
    def _heel_end_trend(heel_y):
        if heel_y is None or len(heel_y) < 3:
            return None
        deltas = [
            heel_y[index] - heel_y[index - 1]
            for index in range(1, len(heel_y))
        ]

        sorted_deltas = sorted(
            deltas,
            key=abs,
            reverse=True,
        )

        if (
            abs(sorted_deltas[0]) >= 0.030
            and abs(sorted_deltas[0]) >= 2 * abs(sorted_deltas[1])
        ):
            return (
                "UP"
                if sorted_deltas[0] < 0
                else "DOWN"
            )
        confirmed_directions = set()

        current_direction = None
        current_steps = 0
        current_movement = 0.0

        for index in range(1, len(heel_y)):
            delta = (
                heel_y[index]
                - heel_y[index - 1]
            )

            if delta < 0:
                direction = "UP"
            elif delta > 0:
                direction = "DOWN"
            else:
                continue

            if direction == current_direction:
                current_steps += 1
                current_movement += abs(delta)
            else:
                current_direction = direction
                current_steps = 1
                current_movement = abs(delta)

            if (
                current_steps >= 2
                and current_movement >= 0.005
            ):
                confirmed_directions.add(
                    current_direction
                )

        # ======================================
        if len(confirmed_directions) != 1:
            return "STABLE"

        confirmed_direction = next(
            iter(confirmed_directions)
        )

        last_delta = (
            heel_y[-1]
            - heel_y[-2]
        )

        if last_delta < 0:
            last_direction = "UP"
        elif last_delta > 0:
            last_direction = "DOWN"
        else:
            last_direction = None

        if (
            last_direction is not None
            and last_direction != confirmed_direction
            and abs(last_delta) >= 0.005
        ):
            return "STABLE"

        return confirmed_direction
     