import time

from pose.models.feedback_item import FeedbackItem
from pose.session.session_event import (
    SessionEvent,
    SessionEventType,
)


class SessionRecorder:
    """
    Records posture events during a riding session.
    """

    def __init__(self) -> None:
        self._current_feedback_message: str | None = None
        self._events: list[SessionEvent] = []

    @property
    def events(self) -> list[SessionEvent]:
        return self._events

    def update(
        self,
        feedback: FeedbackItem | None,
    ) -> None:
        now = time.monotonic()

        if feedback is None:
            self._resolve_issue(now)
            return

        if self._current_feedback_message is None:
            self._start_issue(feedback, now)
            return

        if feedback.message == self._current_feedback_message:
            return

        self._resolve_issue(now)
        self._start_issue(feedback, now)

    def _start_issue(
        self,
        feedback: FeedbackItem,
        now: float,
    ) -> None:
        self._current_feedback_message = feedback.message

        self._events.append(
            SessionEvent(
                event_type=SessionEventType.ISSUE_STARTED,
                message=feedback.message,
                timestamp=now,
            )
        )

    def _resolve_issue(
        self,
        now: float,
    ) -> None:
        if self._current_feedback_message is None:
            return

        self._events.append(
            SessionEvent(
                event_type=SessionEventType.ISSUE_RESOLVED,
                message=self._current_feedback_message,
                timestamp=now,
            )
        )

        self._current_feedback_message = None

    """
        print("\nSession events:")

        for event in recorder.events:
            print(event)
            """