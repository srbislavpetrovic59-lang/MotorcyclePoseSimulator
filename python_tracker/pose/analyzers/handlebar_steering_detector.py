class HandlebarSteeringDetector:

    def __init__(self, sensitivity: float = 1.0):
        self._neutral_depth_difference = None
        self._sensitivity = sensitivity
        self._neutral_x_difference = None
        self._neutral_left_x = None
        self._neutral_right_x = None

    def calibrate(
        self,
        left_wrist_z: float,
        right_wrist_z: float,
    ) -> None:
        self._neutral_depth_difference = (
            left_wrist_z - right_wrist_z
        )

    def update(
        self,
        left_wrist_z: float | None,
        right_wrist_z: float | None,
    ) -> float:
        if left_wrist_z is None or right_wrist_z is None:
            return 0.0

        if self._neutral_depth_difference is None:
            return 0.0

        current_difference = (
            left_wrist_z - right_wrist_z
        )

        steering = (
            current_difference
            - self._neutral_depth_difference
        ) * self._sensitivity

        return max(-1.0, min(1.0, steering))


    def calibrate_x(
        self,
        left_wrist_x: float,
        right_wrist_x: float,
    ) -> None:
        self._neutral_x_difference = left_wrist_x - right_wrist_x


    def update_x(
        self,
        left_wrist_x: float | None,
        right_wrist_x: float | None,
    ) -> float:
        if left_wrist_x is None or right_wrist_x is None:
            return 0.0
        if self._neutral_x_difference is None:
            return 0.0

        left_delta = left_wrist_x - self._neutral_left_x
        right_delta = right_wrist_x - self._neutral_right_x

        print(
            f"Hand deltas: "
            f"L={left_delta:+.3f} | "
            f"R={right_delta:+.3f}"
        )

        current_difference = left_wrist_x - right_wrist_x
        left_delta = left_wrist_x - self._neutral_left_x
        right_delta = right_wrist_x - self._neutral_right_x

        if right_delta > 0.05:
            steering = right_delta
        elif left_delta < -0.02:
            steering = left_delta
        else:
            steering = 0.0

        return max(-1.0, min(1.0, steering * self._sensitivity))


    def calibrate_x(
        self,
        left_wrist_x: float,
        right_wrist_x: float,
    ) -> None:
        self._neutral_x_difference = left_wrist_x - right_wrist_x
        self._neutral_left_x = left_wrist_x
        self._neutral_right_x = right_wrist_x


    def calibrate_x_samples(
        self,
        samples: list[tuple[float, float, float, float]],
    ) -> None:
        if not samples:
            return
        # Compatibility with existing two-value calibration samples.
        if len(samples[0]) == 2:
            samples = [
                (left_x, right_x, 0.0, 0.0)
                for left_x, right_x in samples
            ]

        self._neutral_left_x = sum(
            left_x for left_x, _, _, _ in samples
        ) / len(samples)

        self._neutral_right_x = sum(
            right_x for _, right_x, _, _ in samples
        ) / len(samples)

        self._neutral_x_difference = (
            self._neutral_left_x - self._neutral_right_x
        )

        self._neutral_depth_difference = sum(
            left_z - right_z
            for _, _, left_z, right_z in samples
        ) / len(samples)

    