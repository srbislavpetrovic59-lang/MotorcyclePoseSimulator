from unittest.mock import MagicMock

from pipeline.pose_pipeline import PosePipeline
from pose.session.session_report import SessionReport


def test_complete_session_generates_and_dispatches_narration() -> None:
    camera = MagicMock()
    detector = MagicMock()
    renderer = MagicMock()
    analyzer = MagicMock()
    evaluator = MagicMock()
    feedback_manager = MagicMock()
    coach = MagicMock()
    recorder = MagicMock()
    overlay = MagicMock()
    session_summary = MagicMock()
    narrator = MagicMock()
    output_dispatcher = MagicMock()

    events = ["event-1", "event-2"]
    session_duration = 16.0

    report = SessionReport(
        duration=session_duration,
        most_frequent_message="Keep your shoulders level",
        longest_clear_period_seconds=4.0,
    )

    narration = "Session narration"

    recorder.finish.return_value = session_duration
    recorder.events = events
    session_summary.generate.return_value = report
    narrator.narrate.return_value = narration

    pipeline = PosePipeline(
        camera=camera,
        detector=detector,
        renderer=renderer,
        analyzer=analyzer,
        evaluator=evaluator,
        feedback_manager=feedback_manager,
        coach=coach,
        recorder=recorder,
        overlay=overlay,
        session_summary=session_summary,
        narrator=narrator,
        output_dispatcher=output_dispatcher,
    )

    pipeline._complete_session()

    recorder.finish.assert_called_once_with()

    session_summary.generate.assert_called_once_with(
        events=events,
        session_duration=session_duration,
    )

    narrator.narrate.assert_called_once_with(report)
    output_dispatcher.dispatch.assert_called_once_with(narration)