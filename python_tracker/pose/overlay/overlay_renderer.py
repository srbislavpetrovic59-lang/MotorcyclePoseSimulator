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
            f"Throttle_active: {metrics['throttle_active']}",
            (20, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
         )
         cv2.putText(frame, f"Right hand visible: {metrics.get('right_hand_detected', False)}", (20, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
         
         '''
         cv2.putText(
            frame,
            f"Confidence: {metrics['pose_confidence']:.2f}",
            (20, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
         )
            '''
         clutch_progress = metrics.get("clutch_progress")
         clutch_in_friction_zone = metrics.get(
                "clutch_in_friction_zone",
                False,
            )
         clutch_text = (
            f"Clutch: {clutch_progress:.2f}"
            if clutch_progress is not None
            else "Clutch: INVALID"
         )

         cv2.putText(
            frame,
            clutch_text,
            (20, 310),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
         )
         left_foot_angle = metrics.get("left_foot_angle")
         lef_foot_drop = metrics.get("left_foot_drop")

         left_foot_text = (
             f"Left foot angle: {left_foot_angle:.1f}"
             if left_foot_angle is not None
             else "Left foot angle: INVALID"
         )

         cv2.putText(
             frame,
             left_foot_text,
             (20, 370),
             cv2.FONT_HERSHEY_SIMPLEX,
             0.7,
             (255, 255, 255),
             2,
         )

         left_foot_drop_text = (
             f"Left foot drop: {lef_foot_drop:.1f}"
             if lef_foot_drop is not None
             else "Left foot drop: INVALID"
         )

         cv2.putText(
             frame,
             left_foot_drop_text,
             (20, 400),
             cv2.FONT_HERSHEY_SIMPLEX,
             0.7,
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