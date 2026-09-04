import threading
import cv2


class Camera:

    def __init__(self, source):

        self._source = source
        self._capture = cv2.VideoCapture(source)
        self._capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        print(
            "CAMERA BACKEND:",
            self._capture.getBackendName(),
        )

        print(
            "CAMERA BUFFER SIZE:",
            self._capture.get(
                cv2.CAP_PROP_BUFFERSIZE
            ),
        )

        print(
            "CAMERA FPS:",
            self._capture.get(
                cv2.CAP_PROP_FPS
            ),
        )

        if not self._capture.isOpened():
            raise RuntimeError(f"Cannot open camera: {source}")
        
        ok, frame = self._capture.read()

        if not ok:
            raise RuntimeError(
                f"Cannot read first camera frame: {source}"
            )

        self._latest_frame = frame
        self._frame_id = 0
        self._running = True


        self._thread = threading.Thread(
            target=self._capture_loop,
            daemon=True,
        )

        self._thread.start()

    def read(self):
     
        if self._latest_frame is None:
            return None

        return cv2.flip(
            self._latest_frame.copy(),
            1,
        )
       

    def release(self):

        self._running = False

        if self._thread.is_alive():
            self._thread.join(timeout=1.0)

        self._capture.release()


    def _capture_loop(self):

        while self._running:

            ok, frame = self._capture.read()

            if not ok:
                continue

            self._latest_frame = frame
            self._frame_id += 1
    def read_with_id(self):

        if self._latest_frame is None:
            return None, self._frame_id

        return (
            cv2.flip(
                self._latest_frame.copy(),
                1,
            ),
            self._frame_id,
        )