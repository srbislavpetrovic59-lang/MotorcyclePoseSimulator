from __future__ import annotations

import cv2

import config

from camera import Camera
from pose_detector import PoseDetector
from pose_renderer import PoseRenderer
from pose.pose_analyzer import PoseAnalyzer
from pose.evaluators.pose_evaluator import PoseEvaluator
from pose.feedback.feedback_manager import FeedbackManager
from pose.feedback.pose_coach import PoseCoach
from pose.output.output_dispatcher import OutputDispatcher
from pose.overlay.overlay_renderer import OverlayRenderer
from pose.session.session_narrator import SessionNarrator
from pose.session.session_recorder import SessionRecorder
from pose.session.session_summary import SessionSummary


class PosePipeline:
    """Coordinates the real-time motorcycle pose coaching workflow."""

    def __init__(
        self,
        camera: Camera,
        detector: PoseDetector,
        renderer: PoseRenderer,
        analyzer: PoseAnalyzer,
        evaluator: PoseEvaluator,
        feedback_manager: FeedbackManager,
        coach: PoseCoach,
        recorder: SessionRecorder,
        overlay: OverlayRenderer,
        session_summary: SessionSummary,
        narrator: SessionNarrator,
        output_dispatcher: OutputDispatcher,
    ) -> None:
        self._camera = camera
        self._detector = detector
        self._renderer = renderer
        self._analyzer = analyzer
        self._evaluator = evaluator
        self._feedback_manager = feedback_manager
        self._coach = coach
        self._recorder = recorder
        self._overlay = overlay
        self._session_summary = session_summary
        self._narrator = narrator
        self._output_dispatcher = output_dispatcher

    def run(self) -> None:
        try:
            self._run_loop()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received. Exiting...")
        finally:
            try:
                self._complete_session()
            finally:
                self._release_resources()

    def _run_loop(self) -> None:
        while True:
            frame = self._camera.read()

            if frame is None:
                break

            landmarks = self._detector.detect(frame)

            if landmarks is not None:
                self._process_pose(frame, landmarks)

            cv2.imshow(config.WINDOW_TITLE, frame)

            if cv2.waitKey(1) == 27:
                break

    def _process_pose(self, frame, landmarks) -> None:
        metrics = self._analyzer.analyze(landmarks)
        evaluation = self._evaluator.evaluate(metrics)

        active_feedback = self._feedback_manager.process(
            evaluation.feedback
        )

        self._coach.update(active_feedback)
        self._recorder.update(active_feedback)

        self._renderer.draw(frame, landmarks)

        self._overlay.draw(
            frame,
            metrics,
            evaluation,
            active_feedback,
        )

    def _complete_session(self) -> None:
        session_duration = self._recorder.finish()

        report = self._session_summary.generate(
            events=self._recorder.events,
            session_duration=session_duration,
        )

        narration = self._narrator.narrate(report)
        self._output_dispatcher.dispatch(narration)

    def _release_resources(self) -> None:
        self._detector.release()
        self._camera.release()
        cv2.destroyAllWindows()