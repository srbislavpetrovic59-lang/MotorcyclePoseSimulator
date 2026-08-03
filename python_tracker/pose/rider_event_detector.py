from pose.rider_events import RiderEvent
from pose.rider_events import RiderEventType

POSE_CONFIDENCE_THRESHOLD = 0.8


class RiderEventDetector:


    def __init__(self) -> None:
        self._previous_state = None

    def detect(
        self,
        rider_state,
    ) -> list[RiderEvent]:

        if self._is_first_frame():
            self._update_previous_state(rider_state)
            return []

        previous_state = self._previous_state
        events = []

        previous_valid = self._has_valid_pose(previous_state)
        current_valid = self._has_valid_pose(rider_state)

        if (
            not previous_valid
            and current_valid
        ):
            events.append(
                RiderEvent(
                    type=RiderEventType.POSE_ACQUIRED,
                    timestamp=rider_state.timestamp,
                )
            )
        
        if (
            previous_valid
            and not current_valid
        ):
            events.append(
                RiderEvent(
                    type=RiderEventType.POSE_LOST,
                    timestamp=rider_state.timestamp,
                )
            )



        self._update_previous_state(rider_state)

        return events

    def _is_first_frame(self) -> bool:
        
        return self._previous_state is None

    def _update_previous_state(
        self,
        rider_state,
    ) -> None:
        self._previous_state = rider_state

    def _has_valid_pose(
        self,
        rider_state,
    ) -> bool:
        return (
            rider_state.pose_confidence
            >= POSE_CONFIDENCE_THRESHOLD
        )