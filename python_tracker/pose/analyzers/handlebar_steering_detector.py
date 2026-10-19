class HandlebarSteeringDetector:

    def __init__(self, sensitivity: float = 1.0):
        self._neutral_depth_difference = None
        self._sensitivity = sensitivity
        self._neutral_x_difference = None

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
        current_difference = left_wrist_x - right_wrist_x

        steering = (
            self._neutral_x_difference - current_difference
        ) * self._sensitivity
        if abs(steering) < 0.05:
            return 0.0

        return max(-1.0, min(1.0, steering))


    