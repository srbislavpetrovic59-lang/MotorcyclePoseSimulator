import cv2


class OverlayRenderer:

    def draw(
        self,
        frame,
        metrics,
        evaluation,
        feedback,
    ):

        self._draw_metrics(frame, metrics)
        self._draw_evaluation(frame, evaluation)
        self._draw_feedback(frame, feedback)

    def _draw_metrics(
        self,
        frame,
        metrics,
    ):
         cv2.putText(
            frame,
            f"Left elbow: {metrics['left_elbow_angle']:.1f} deg",
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

         cv2.putText(
            frame,
            f"Right elbow: {metrics['right_elbow_angle']:.1f} deg",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
         )
         cv2.putText(
            frame,
            f"Left knee: {metrics['left_knee_angle']:.1f}",
            (20, 190),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
         )

         cv2.putText(
            frame,
            f"Right knee: {metrics['right_knee_angle']:.1f}",
            (20, 220),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
         )
         cv2.putText(
            frame,
            f"Torso angle: {metrics['torso_angle']:.1f}",
            (20, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
         )

         cv2.putText(
            frame,
            f"Confidence: {metrics['pose_confidence']:.2f}",
            (20, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
         )

    def _draw_evaluation(
        self,
        frame,
        evaluation,
    ):
        cv2.putText(
            frame,
            f"Score: {evaluation.score}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"State: {evaluation.rider_state}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

    def _draw_feedback(
        self,
        frame,
        feedback,
    ):
        text = (
            feedback.message
            if feedback is not None
            else "Good posture"
        )

        cv2.putText(
            frame,
            text,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )