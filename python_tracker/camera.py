import cv2


class Camera:

    def __init__(self, source):

        self._source = source
        self._capture = cv2.VideoCapture(source)

        if not self._capture.isOpened():
            raise RuntimeError(f"Cannot open camera: {source}")

    def read(self):

        ok, frame = self._capture.read()

        if not ok:
            return None

        return cv2.flip(frame, 1)

    def release(self):
        self._capture.release()