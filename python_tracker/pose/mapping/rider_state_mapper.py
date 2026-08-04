from collections.abc import Mapping
import time
from pose.models.rider_state import RiderState


class RiderStateMapper:
    """Converts pose analysis results into a RiderState model."""

    @staticmethod
    def from_analysis(
        result: Mapping[str, float],
    ) -> RiderState:
        """Creates a RiderState from pose analysis output."""

        return RiderState(
            timestamp=time.monotonic(),

            head_roll=result["head_roll"],
            head_yaw_ratio = result["head_yaw_ratio"],

            left_hand_detected=result["left_hand_detected"],
            right_hand_detected=result["right_hand_detected"],

            head_forward=result["head_forward"],
            
            left_elbow_angle=result["left_elbow_angle"],
            right_elbow_angle=result["right_elbow_angle"],
            
            left_knee_angle=result["left_knee_angle"],
            right_knee_angle=result["right_knee_angle"],
            
            left_foot_angle=result["left_foot_angle"],
            right_foot_angle=result["right_foot_angle"],
            
            torso_angle=result["torso_angle"],
            pose_confidence=result["pose_confidence"],

           
        )