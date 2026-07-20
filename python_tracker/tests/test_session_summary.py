from pose.session.session_event import (
    SessionEvent,
    SessionEventType,
)
from pose.session.session_summary import SessionSummary


def run_manual_test():
    test_events = [
        ...
    ]

    summary = SessionSummary()

    report = summary.generate(
        events=test_events,
        session_duration=60.0,
    )

    print(report)


if __name__ == "__main__":
    test_session_summary()