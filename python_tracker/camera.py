import cv2


class Camera:
    def __init__(self, source="http://192.168.1.6:8080/video"):
        self.source = source
        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera: {source}")

    def read(self):
        ok, frame = self.cap.read()

        if not ok:
            return None

        frame = cv2.flip(frame, 1)
        return frame

    def release(self):
        self.cap.release()