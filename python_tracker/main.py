import cv2

import config

from camera import Camera
from pose_detector import PoseDetector
from pose_renderer import PoseRenderer



def main():
    camera = Camera(config.CAMERA_URL)
    detector = PoseDetector()
    renderer = PoseRenderer()
    
    while True:

        frame = camera.read()

        if frame is None:
            break

        landmarks = detector.detect(frame)

        renderer.draw(
            frame,
            landmarks
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