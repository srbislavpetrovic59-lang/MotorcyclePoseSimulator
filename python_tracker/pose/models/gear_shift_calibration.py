class GearShiftCalibration:
    def __init__(self):
        self.rest_forward = None
        self.rest_drop = None
        self.rest_angle = None

        self._rest_samples = []

    def add_rest_sample(self, forward, drop, angle):
        self._rest_samples.append(
            (forward, drop, angle)
        )

        if len(self._rest_samples) < 5:
            return
        
        if not self._is_rest_window_stable():
            return

        self.rest_forward = sum(
            sample[0] for sample in self._rest_samples
        ) / len(self._rest_samples)

        self.rest_drop = sum(
            sample[1] for sample in self._rest_samples
        ) / len(self._rest_samples)

        self.rest_angle = sum(
            sample[2] for sample in self._rest_samples
        ) / len(self._rest_samples)

    def _is_rest_window_stable(self):
        samples = self._rest_samples[-5:]

        forward_values = [
            sample[0] for sample in samples
        ]

        drop_values = [
            sample[1] for sample in samples
        ]

        forward_range = max(forward_values) - min(forward_values)
        drop_range = max(drop_values) - min(drop_values)
        angle_values = [sample[2] for sample in samples]
        angle_range = max(angle_values) - min(angle_values)

        return (
            forward_range <= 0.001
            and drop_range <= 0.005
            and angle_range <= 2.0
        )