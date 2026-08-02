from pose.rider_events import RiderEvent


class RiderEventDetector:


    def __init__(self) -> None:
        self._previous_state = None

    def detect(
        self,
        rider_state,
    ) -> list[RiderEvent]:
        
        if self._is_first_frame():
            self._previous_state = rider_state
            return []

        previous_state = self._previous_state

        self._previous_state = rider_state
        
        return []

    def _is_first_frame(self) -> bool:
        
        return self._previous_state is None