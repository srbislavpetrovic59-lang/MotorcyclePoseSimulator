from pose.session.session_event import SessionEvent, SessionEventType
from pose.session.session_summary import SessionSummary


def run_manual_test():

    test_events = [
        SessionEvent(
                event_type=SessionEventType.ISSUE_STARTED,
                message="Relax your shoulders",
                timestamp=10.0,
            ),
            SessionEvent(
                event_type=SessionEventType.ISSUE_RESOLVED,
                message="Relax your shoulders",
                timestamp=20.0,
            ),
            SessionEvent(
                event_type=SessionEventType.ISSUE_STARTED,
                message="Keep your back straight",
                timestamp=45.0,
            ),
            SessionEvent(
                event_type=SessionEventType.ISSUE_RESOLVED,
                message="Keep your back straight",
                timestamp=50.0,
            ),
            SessionEvent(
                event_type=SessionEventType.ISSUE_STARTED,
                message="Relax your shoulders",
                timestamp=55.0,
            ),
            SessionEvent(
                event_type=SessionEventType.ISSUE_RESOLVED,
                message="Relax your shoulders",
                timestamp=58.0,
            ),
    ]

    summary = SessionSummary()

    report = summary.generate(
        events=test_events,
        session_duration=60.0,
    )

    print("\nTest SessionReport:\n")
    print(report)


if __name__ == "__main__":
    run_manual_test()