from __future__ import annotations
from pose.mapping.rider_state_mapper import RiderStateMapper
from pose.transport.websocket_server import WebSocketServer
import time
import cv2

import config

from camera import Camera
from pose.pose_detector import PoseDetector
from pose.hand_detector import HandDetector
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
from pose.models.frame_analysis import FrameAnalysis

class PosePipeline:
    """Coordinates the real-time motorcycle pose coaching workflow."""

    def __init__(
        self,
        camera: Camera,
        detector: PoseDetector,
        hand_detector: HandDetector,
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
        rider_state_mapper: RiderStateMapper,
        websocket_server: WebSocketServer,
    ) -> None:
        self._camera = camera
        self._detector = detector
        self._hand_detector = hand_detector
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
        self._rider_state_mapper = rider_state_mapper
        self._websocket_server = websocket_server
        self._last_analysis_result = None
    
    

    def run(self) -> None:
        self._websocket_server.start()

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
            start = time.perf_counter()

            frame = self._camera.read()

            if frame is None:
                break

            landmarks = self._detector.detect(frame)

            hand_landmarks, hand_handedness = (
                self._hand_detector.detect(frame)
            )

            frame_analysis = FrameAnalysis(
                pose_landmarks=landmarks,
                hand_landmarks=hand_landmarks,
                hand_handedness=hand_handedness,
            )

            if (
                frame_analysis.hand_landmarks is not None
                and frame_analysis.hand_handedness is not None
            ):
                for handedness in frame_analysis.hand_handedness:
                    label = handedness.classification[0].label
                    print(label)

            if frame_analysis.pose_landmarks is not None:
                self._process_pose(
                    frame,
                    frame_analysis,
                )

            cv2.imshow(
                config.WINDOW_TITLE,
                frame,
            )

            print(
                f"Frame: "
                f"{(time.perf_counter() - start) * 1000:.1f} ms"
            )

            key = cv2.waitKey(1) & 0xFF

            if key == 27:
                break

            if self._last_analysis_result is not None:
                right_index_finger_bend = (
                    self._last_analysis_result.get(
                        "right_index_finger_bend"
                    )
                )

                if (
                    key == ord("r")
                    and right_index_finger_bend is not None
                ):
                    self._analyzer.calibrate_front_brake_released(
                        right_index_finger_bend
                    )

                    print(
                        f"Front brake RELEASED calibrated: "
                        f"{right_index_finger_bend:.1f}"
                    )

                if (
                    key == ord("p")
                    and right_index_finger_bend is not None
                ):
                    self._analyzer.calibrate_front_brake_pulled(
                        right_index_finger_bend
                    )

                    print(
                        f"Front brake PULLED calibrated: "
                        f"{right_index_finger_bend:.1f}"
                    )
                 # Throttle
                right_hand_rotation = (
                    self._last_analysis_result.get(
                        "right_hand_rotation"
                    )
                )

                if (
                    key == ord("c")
                    and right_hand_rotation is not None
                ):
                    self._analyzer.capture_throttle_closed(
                        right_hand_rotation
                    )

                    print(
                        f"Throttle CLOSED calibrated: "
                        f"{right_hand_rotation:.1f}"
                    )

                if (
                    key == ord("o")
                    and right_hand_rotation is not None
                ):
                    self._analyzer.capture_throttle_open(
                        right_hand_rotation
                    )

                    print(
                        f"Throttle OPEN calibrated: "
                        f"{right_hand_rotation:.1f}"
                    )


    def _process_pose(
        self,
        frame,
        frame_analysis: FrameAnalysis,
    ) -> None:
        metrics = self._analyzer.analyze(
            frame_analysis
        )
       
        self._last_analysis_result = metrics

        rider_state = self._rider_state_mapper.from_analysis(
            metrics
        )
        try:
           
            self._websocket_server.send(
                rider_state.to_json()
            )
            
        except RuntimeError:
            pass

        evaluation = self._evaluator.evaluate(metrics)

        active_feedback = self._feedback_manager.process(
            evaluation.feedback
        )

        self._coach.update(active_feedback)
        self._recorder.update(active_feedback)

        self._renderer.draw(
            frame,
            frame_analysis.pose_landmarks,
        )

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
        self._websocket_server.stop()
        self._detector.release()
        self._hand_detector.close()
        self._camera.release()
        cv2.destroyAllWindows()

    