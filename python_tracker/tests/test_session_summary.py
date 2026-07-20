from pose.session.session_event import SessionEvent, SessionEventType
from pose.session.session_summary import SessionSummary


def test_generate_session_summary():
    events = [
        SessionEvent(
            timestamp=10.0,
            event_type=SessionEventType.ISSUE_STARTED,
            message="Relax your shoulders",
        ),
        SessionEvent(
            timestamp=20.0,
            event_type=SessionEventType.ISSUE_RESOLVED,
            message="Relax your shoulders",
        ),
        SessionEvent(
            timestamp=45.0,
            event_type=SessionEventType.ISSUE_STARTED,
            message="Relax your shoulders",
        ),
        SessionEvent(
            timestamp=50.0,
            event_type=SessionEventType.ISSUE_RESOLVED,
            message="Relax your shoulders",
        ),
        SessionEvent(
            timestamp=55.0,
            event_type=SessionEventType.ISSUE_STARTED,
            message="Keep your back straight",
        ),
        SessionEvent(
            timestamp=58.0,
            event_type=SessionEventType.ISSUE_RESOLVED,
            message="Keep your back straight",
        ),
    ]

    summary = SessionSummary()

    report = summary.generate(
        events=events,
        session_duration=60.0,
    )

    assert report.duration == 60.0
    assert report.most_common_issue == "Relax your shoulders"
    assert report.longest_clear_period_seconds == 25.0