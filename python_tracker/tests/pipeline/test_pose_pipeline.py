from unittest.mock import MagicMock
from unittest.mock import patch

from pipeline.pose_pipeline import PosePipeline
from pose.session.session_report import SessionReport


def test_complete_session_generates_and_dispatches_narration() -> None:
    camera = MagicMock()
    detector = MagicMock()
    hand_detector = MagicMock()
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
    rider_state_mapper = MagicMock()
    websocket_server = MagicMock()

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
        hand_detector=hand_detector,
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
        rider_state_mapper=rider_state_mapper,
        websocket_server=websocket_server,
    )

    pipeline._complete_session()

    recorder.finish.assert_called_once_with()

    session_summary.generate.assert_called_once_with(
        events=events,
        session_duration=session_duration,
    )

    narrator.narrate.assert_called_once_with(report)
    output_dispatcher.dispatch.assert_called_once_with(narration)
    
def test_run_loop_processes_pose_once_per_frame() -> None:
    camera = MagicMock()
    detector = MagicMock()
    hand_detector = MagicMock()
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
    rider_state_mapper = MagicMock()
    websocket_server = MagicMock()

    frame = MagicMock()
    pose_landmarks = MagicMock()

    camera.read_with_id.side_effect = [
    (frame, 7),
    (None, 8),
]

    detector.detect.return_value = pose_landmarks
    hand_detector.detect.return_value = (
        None,
        None,
    )

    pipeline = PosePipeline(
        camera=camera,
        detector=detector,
        hand_detector=hand_detector,
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
        rider_state_mapper=rider_state_mapper,
        websocket_server=websocket_server,
    )

    pipeline._process_pose = MagicMock()
    pipeline._last_analysis_result = {
        "test": True,
    }

    with patch("pipeline.pose_pipeline.cv2.imshow"), \
     patch(
         "pipeline.pose_pipeline.cv2.waitKey",
         return_value=-1,
     ):
     pipeline._run_loop()

    pipeline._process_pose.assert_called_once()
def test_run_loop_does_not_process_same_frame_twice() -> None:
    camera = MagicMock()
    detector = MagicMock()
    hand_detector = MagicMock()
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
    rider_state_mapper = MagicMock()
    websocket_server = MagicMock()

    frame = MagicMock()
    pose_landmarks = MagicMock()

    camera.read.side_effect = [
        frame,
        frame,
        None,
    ]

    camera.read_with_id.side_effect = [
        (frame, 7),
        (frame, 7),
        (None, 8),
    ]

    detector.detect.return_value = pose_landmarks
    hand_detector.detect.return_value = (
        None,
        None,
    )

    pipeline = PosePipeline(
        camera=camera,
        detector=detector,
        hand_detector=hand_detector,
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
        rider_state_mapper=rider_state_mapper,
        websocket_server=websocket_server,
    )

    pipeline._process_pose = MagicMock()

    with patch("pipeline.pose_pipeline.cv2.imshow"), \
         patch(
             "pipeline.pose_pipeline.cv2.waitKey",
             return_value=-1,
         ):
        pipeline._run_loop()

    pipeline._process_pose.assert_called_once()