from statistics import median

class GearShiftCalibration:
    def __init__(self):
        self.rest_forward = None
        self.rest_drop = None
        self.rest_angle = None
        self.shift_up_forward = None
        self.shift_up_drop = None
        self.shift_up_angle = None
        self._rest_samples = []
        self.shift_up_sequence = []
        self.shift_up_sequences = []

    def add_rest_sample(self, forward, drop, angle):
        self._rest_samples.append(
            (forward, drop, angle)
        )

        if len(self._rest_samples) < 5:
            return
        
        if not self._is_rest_window_stable():
            return

        stable_samples = self._rest_samples[-5:]

        self.rest_forward = sum(
            sample[0] for sample in stable_samples
        ) / len(stable_samples)
        self.rest_drop = sum(
            sample[1] for sample in stable_samples
        ) / len(stable_samples)

        self.rest_angle = sum(
            sample[2] for sample in stable_samples
        ) / len(stable_samples)

    def movement_from_rest(self, forward, drop, angle):
        return {
            "forward": forward - self.rest_forward,
            "drop": drop - self.rest_drop,
            "angle": angle - self.rest_angle,
        }

    def add_shift_up_sample(self, forward, drop, angle):
        movement = self.movement_from_rest(
            forward=forward,
            drop=drop,
            angle=angle,
        )

        self.shift_up_forward = movement["forward"]
        self.shift_up_drop = movement["drop"]
        self.shift_up_angle = movement["angle"]

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
    
    def add_shift_up_sequence(self, samples):
        self.shift_up_sequence = [
            self.movement_from_rest(
                forward=forward,
                drop=drop,
                angle=angle,
            )
            for forward, drop, angle in samples
        ]

        self.shift_up_sequences.append(
            self.shift_up_sequence
        )

    def shift_up_distances_from_rest(self):
        return [
            (
                movement["forward"] ** 2
                + movement["drop"] ** 2
                + movement["angle"] ** 2
            ) ** 0.5
            for movement in self.shift_up_sequence
        ]

    def shift_up_has_away_and_return_pattern(self):
        distances = self.shift_up_normalized_distances_from_rest()

        if len(distances) < 3:
            return False

        peak_index = distances.index(max(distances))

        if peak_index == 0 or peak_index == len(distances) - 1:
            return False

        return (
            distances[peak_index] > distances[0]
            and distances[-1] < distances[peak_index]
        )

    def shift_up_ranges(self):
        return {
            "forward": max(
                abs(movement["forward"])
                for movement in self.shift_up_sequence
            ),
            "drop": max(
                abs(movement["drop"])
                for movement in self.shift_up_sequence
            ),
            "angle": max(
                abs(movement["angle"])
                for movement in self.shift_up_sequence
            ),
        }

    def normalized_movement_from_rest(self, forward, drop, angle):
        movement = self.movement_from_rest(
            forward=forward,
            drop=drop,
            angle=angle,
        )

        ranges = self.shift_up_ranges()

        def normalized(value, range_value):
            if range_value == 0:
                return 0.0
            return value / range_value

        return {
            "forward": normalized(
                movement["forward"], ranges["forward"]
            ),
            "drop": normalized(
                movement["drop"], ranges["drop"]
            ),
            "angle": normalized(
                movement["angle"], ranges["angle"]
            ),
        }

    def shift_up_normalized_distances_from_rest(self):
        ranges = self.shift_up_ranges()

        def normalized(value, range_value):
            if range_value == 0:
                return 0.0
            return value / range_value

        return [
            (
                normalized(movement["forward"], ranges["forward"]) ** 2
                + normalized(movement["drop"], ranges["drop"]) ** 2
                + normalized(movement["angle"], ranges["angle"]) ** 2
            ) ** 0.5
            for movement in self.shift_up_sequence
        ]


    def shift_up_typical_ranges(self):
        forward_ranges = [
            max(
                abs(movement["forward"])
                for movement in sequence
            )
            for sequence in self.shift_up_sequences
        ]

        drop_ranges = [
            max(
                abs(movement["drop"])
                for movement in sequence
            )
            for sequence in self.shift_up_sequences
        ]

        angle_ranges = [
            max(
                abs(movement["angle"])
                for movement in sequence
            )
            for sequence in self.shift_up_sequences
        ]

        return {
            "forward": median(forward_ranges),
            "drop": median(drop_ranges),
            "angle": median(angle_ranges),
        }        