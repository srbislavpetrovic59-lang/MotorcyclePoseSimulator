import cv2

import config

from camera import Camera
from pose_detector import PoseDetector
from pose_renderer import PoseRenderer
from pose.pose_analyzer import PoseAnalyzer



def main():
    camera = Camera(config.CAMERA_URL)
    detector = PoseDetector()
    renderer = PoseRenderer()
    analyzer = PoseAnalyzer()
    
    while True:

        frame = camera.read()

        if frame is None:
            break

        landmarks = detector.detect(frame)
        state = analyzer.analyze(landmarks)

        renderer.draw(frame, landmarks)
        cv2.putText(
            frame,
            f"Left elbow: {state['left_elbow_angle']:.1f} deg",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Right elbow: {state['right_elbow_angle']:.1f} deg",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Left knee: {state['left_knee_angle']:.1f} deg",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Right knee: {state['right_knee_angle']:.1f} deg",
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )


        cv2.putText(
            frame,
            f"Pose confidence: {state['pose_confidence']:.2f}",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        print(
            f"Left arm extended : {state['left_arm_extended']}"
            f"Right arm extended: {state['right_arm_extended']}"  
            f"Arm symmetry      : {state['arm_symmetry']:.1f}%"
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