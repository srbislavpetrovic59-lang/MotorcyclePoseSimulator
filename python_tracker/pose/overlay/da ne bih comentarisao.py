    cv2.putText(
            frame,
            "Pose not detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
            )

            cv2.imshow("Motorcycle Pose Simulator", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            continue

        

        renderer.draw(frame, landmarks)
        cv2.putText(
            frame,
            f"Left elbow: {metrics['left_elbow_angle']:.1f} deg",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Right elbow: {metrics['right_elbow_angle']:.1f} deg",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Left knee: {metrics['left_knee_angle']:.1f} deg",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Right knee: {metrics['right_knee_angle']:.1f} deg",
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )


        cv2.putText(
            frame,
            f"Pose confidence: {metrics['pose_confidence']:.2f}",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Score: {evaluation.score}",
            (20, 190),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"State: {evaluation.rider_state}",
            (20, 220),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        
        

        cv2.putText(
            frame,
            feedback_text,
            (20, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )



