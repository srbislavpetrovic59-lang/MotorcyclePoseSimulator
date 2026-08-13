from pose.rider_events import RiderEvent
from pose.rider_events import RiderEventType
from pose.models.rider_state import RiderState

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
            self._emit(
                events,
                RiderEventType.POSE_ACQUIRED,
                rider_state,
            )
        
        if (
            previous_valid
            and not current_valid
        ):
            self._emit(
                events,
                RiderEventType.POSE_LOST,
                rider_state,
            )

        # Detect clutch friction zone reached event
        previous_clutch_friction = (
            previous_state.clutch_in_friction_zone
        )

        current_clutch_friction = (
            rider_state.clutch_in_friction_zone
        )

        if (
            previous_state.clutch_progress is not None
            and not previous_clutch_friction
            and current_clutch_friction
        ):
            self._emit(
                events,
                RiderEventType.CLUTCH_FRICTION_ZONE_REACHED,
                rider_state,
            )

        if (
            previous_state.clutch_in_friction_zone
            and not rider_state.clutch_in_friction_zone
            and rider_state.clutch_progress is not None
            and rider_state.clutch_progress < 0.55
        ):
            self._emit(
                events,
                RiderEventType.CLUTCH_RELEASED_FROM_FRICTION_ZONE,
                rider_state,
            )
        if (
            previous_state.clutch_in_friction_zone
            and not rider_state.clutch_in_friction_zone
            and rider_state.clutch_progress is not None
            and rider_state.clutch_progress > 0.70
        ):
            self._emit(
                events,
                RiderEventType.CLUTCH_PULLED_FROM_FRICTION_ZONE,
                rider_state,
            )

        # Detect left hand detected event
        previous_left = previous_state.left_hand_detected
        current_left = rider_state.left_hand_detected

        if (
            not previous_left
            and current_left
        ):
            self._emit(
                events,
                RiderEventType.LEFT_HAND_DETECTED,
                rider_state,
            )
         # Detect left hand lost event
        if (
            previous_left
            and not current_left
        ):
            self._emit(
                events,
                RiderEventType.LEFT_HAND_LOST,
                rider_state,
            )
         # Detect right hand detected event
        previous_right = previous_state.right_hand_detected
        current_right = rider_state.right_hand_detected

        if (
            not previous_right
            and current_right
        ):
            self._emit(
                events,
                RiderEventType.RIGHT_HAND_DETECTED,
                rider_state,
            )
         # Detect right hand lost event
        if (
            previous_right
            and not current_right
        ):
            self._emit(
                events,
                RiderEventType.RIGHT_HAND_LOST,
                rider_state,
            )

        previous_head_forward = previous_state.head_forward
        current_head_forward = rider_state.head_forward

        if (
            not previous_head_forward
            and current_head_forward
        ):
            self._emit(
                events,
                RiderEventType.LOOKING_AHEAD,
                rider_state,
            )

        if (
            previous_head_forward
            and not current_head_forward
        ):
            self._emit(
                events,
                RiderEventType.LOOKING_AWAY,
                rider_state,
            )

        if (
            not previous_state.throttle_open
            and rider_state.throttle_open
        ):
            self._emit(
                events,
                RiderEventType.THROTTLE_OPENED,
                rider_state,
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

    def _emit(
        self,
        events: list[RiderEvent],
        event_type: RiderEventType,
        rider_state: RiderState,
    ) -> None:
        events.append(
            RiderEvent(
                type=event_type,
                timestamp=rider_state.timestamp,
            )
        )

