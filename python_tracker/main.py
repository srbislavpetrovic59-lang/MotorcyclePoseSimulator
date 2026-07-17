from threading import activeCount
import cv2

import config

from camera import Camera
from pose_detector import PoseDetector
from pose_renderer import PoseRenderer
from pose.pose_analyzer import PoseAnalyzer
from pose.evaluators.pose_evaluator import PoseEvaluator
from pose.feedback.feedback_manager import FeedbackManager
from pose.overlay.overlay_renderer import OverlayRenderer
from pose.feedback.pose_coach import PoseCoach


def main():
    camera = Camera(config.CAMERA_URL)
    detector = PoseDetector()
    renderer = PoseRenderer()
    analyzer = PoseAnalyzer()
    evaluator = PoseEvaluator()
    overlay = OverlayRenderer()
    coach = PoseCoach(cooldown_seconds=3.0)

    feedback_manager = FeedbackManager()
    
    while True:

        frame = camera.read()

        if frame is None:
            break

        landmarks = detector.detect(frame)
        if landmarks is None:
            continue

        metrics = analyzer.analyze(landmarks)
        
        evaluation = evaluator.evaluate(metrics)
      
        active_feedback = feedback_manager.process(
            evaluation.feedback
        )
        coach.update(active_feedback)


        
        renderer.draw(frame, landmarks)
        
        overlay.draw(
                frame,
                metrics,
                evaluation,
                active_feedback,
            )

        cv2.imshow(
            config.WINDOW_TITLE,
            frame
        )

        if cv2.waitKey(1) == 27:
            break

    detector.release()
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()