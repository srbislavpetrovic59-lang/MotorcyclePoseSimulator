from collections import Counter

from pose.session.session_event import SessionEvent, SessionEventType
from pose.session.session_report import SessionReport


class SessionSummary:

    def generate(
        self,
        events: list[SessionEvent],
        session_duration: float,
    ) -> SessionReport:
        most_common_issue = self._most_common_issue(events)

        longest_clear_period_seconds = self._longest_clear_period_seconds(
            events,
            session_duration,
        )

        return SessionReport(
            duration=session_duration,
            most_common_issue=most_common_issue,
            longest_clear_period_seconds=longest_clear_period_seconds,
        )

    def _most_common_issue(
        self,
        events: list[SessionEvent],
    ) -> str | None:
        issue_counts = Counter(
            event.message
            for event in events
            if event.event_type is SessionEventType.ISSUE_STARTED
        )

        if not issue_counts:
            return None

        return issue_counts.most_common(1)[0][0]

    def _longest_clear_period_seconds(
    self,
    events: list[SessionEvent],
    session_duration: float,
    ) -> float:
        longest_clear_period_seconds = 0.0
        clear_period_start = 0.0

        for event in events:
            if event.event_type is SessionEventType.ISSUE_STARTED:
                clear_period = event.timestamp - clear_period_start

                longest_clear_period_seconds = max(
                    longest_clear_period_seconds,
                    clear_period,
                )

            elif event.event_type is SessionEventType.ISSUE_RESOLVED:
                clear_period_start = event.timestamp

        final_clear_period = session_duration - clear_period_start

        return max(
            longest_clear_period_seconds,
            final_clear_period,
        )