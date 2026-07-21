from pose.session.session_event import SessionEvent, SessionEventType
from pose.session.session_summary import SessionSummary


def test_generate_session_summary():
    """
    Timeline

    0----10==20-------------45==50---55==58--60

    longest clear = 25 s
    """
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

    report = generate_report(events)

    assert report.duration == 60.0
    assert report.most_common_issue == "Relax your shoulders"
    assert report.longest_clear_period_seconds == 25.0


def test_empty_session():
    """
    Timeline

    0--------------------------------60

    No issues recorded.
    """

    events = []

    report = generate_report(events)

    assert report.duration == 60.0
    assert report.most_common_issue is None
    assert report.longest_clear_period_seconds == 60.0


def test_issue_until_session_end():
    """
    Timeline

    0----------10========================60

    clear = 10 s
    issue remains active until session end
    """

    events = [
        SessionEvent(
            event_type=SessionEventType.ISSUE_STARTED,
            timestamp=10.0,
            message="Relax your shoulders",
        ),
    ]

    report = generate_report(events)

    assert report.duration == 60.0
    assert report.most_common_issue == "Relax your shoulders"
    assert report.longest_clear_period_seconds == 10.0

def test_multiple_issues_same_frequency():
    """
    Two issues occur twice each.

    The first issue encountered wins the tie.
    """

    events = [
        SessionEvent(
            event_type=SessionEventType.ISSUE_STARTED,
            timestamp=5.0,
            message="Relax your shoulders",
        ),
        SessionEvent(
            event_type=SessionEventType.ISSUE_RESOLVED,
            timestamp=10.0,
            message="Relax your shoulders",
        ),
        SessionEvent(
            event_type=SessionEventType.ISSUE_STARTED,
            timestamp=20.0,
            message="Straighten your back",
        ),
        SessionEvent(
            event_type=SessionEventType.ISSUE_RESOLVED,
            timestamp=25.0,
            message="Straighten your back",
        ),
        SessionEvent(
            event_type=SessionEventType.ISSUE_STARTED,
            timestamp=35.0,
            message="Relax your shoulders",
        ),
        SessionEvent(
            event_type=SessionEventType.ISSUE_RESOLVED,
            timestamp=40.0,
            message="Relax your shoulders",
        ),
        SessionEvent(
            event_type=SessionEventType.ISSUE_STARTED,
            timestamp=50.0,
            message="Straighten your back",
        ),
        SessionEvent(
            event_type=SessionEventType.ISSUE_RESOLVED,
            timestamp=55.0,
            message="Straighten your back",
        ),
    ]

    report = generate_report(events)

    assert report.duration == 60.0
    assert report.most_common_issue == "Relax your shoulders"
    assert report.longest_clear_period_seconds == 10.0

def generate_report(events, duration=60.0):
    summary = SessionSummary()

    return summary.generate(
        events=events,
        session_duration=duration,
    )