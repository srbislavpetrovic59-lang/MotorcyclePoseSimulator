from collections.abc import Mapping

from pose.models.rider_state import RiderState


class RiderStateMapper:
    """Converts pose analysis results into a RiderState model."""

    @staticmethod
    def from_analysis(
        result: Mapping[str, float],
    ) -> RiderState:
        """Creates a RiderState from pose analysis output."""

        return RiderState(
            left_elbow_angle=result["left_elbow_angle"],
            right_elbow_angle=result["right_elbow_angle"],
            pose_confidence=result["pose_confidence"],
        )