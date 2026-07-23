import config

from camera import Camera
from pipeline.pose_pipeline import PosePipeline
from pose_detector import PoseDetector
from pose_renderer import PoseRenderer
from pose.pose_analyzer import PoseAnalyzer
from pose.evaluators.pose_evaluator import PoseEvaluator
from pose.feedback.feedback_manager import FeedbackManager
from pose.feedback.pose_coach import PoseCoach
from pose.overlay.overlay_renderer import OverlayRenderer
from pose.session.session_recorder import SessionRecorder
from pose.session.session_summary import SessionSummary
from pose.session.session_narrator import SessionNarrator
from pose.output.output_dispatcher import OutputDispatcher
from pose.output.console_output import ConsoleOutput


def main() -> None:
    pipeline = PosePipeline(
        camera=Camera(config.CAMERA_URL),
        detector=PoseDetector(),
        renderer=PoseRenderer(),
        analyzer=PoseAnalyzer(),
        evaluator=PoseEvaluator(),
        feedback_manager=FeedbackManager(),
        coach=PoseCoach(cooldown_seconds=3.0),
        recorder=SessionRecorder(),
        overlay=OverlayRenderer(),
        session_summary=SessionSummary(),
        narrator=SessionNarrator(),
        output_dispatcher = OutputDispatcher([ConsoleOutput(),])
    )

    pipeline.run()


if __name__ == "__main__":
    main()