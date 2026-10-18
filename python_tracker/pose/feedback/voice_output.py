import threading
import pythoncom
from queue import Queue, Empty


class VoiceOutput:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._queue = Queue(maxsize=3)
        self._worker = None
        self._stop_event = threading.Event()

    def speak(self, message: str) -> bool:
        if not self.enabled:
            return False

        if not message or not message.strip():
            return False

        if self._queue.full():
            return False

        self._queue.put_nowait(message)
        return True

    def _take_next_message(self) -> str | None:
        try:
            return self._queue.get_nowait()
        except Empty:
            return None

    def _play_next_message(self, engine) -> bool:
        message = self._take_next_message()

        if message is None:
            return False

        print(f"[VOICE] START: {message}", flush=True)

        if hasattr(engine, "Speak"):
            # Windows SAPI
            engine.Speak(message)
        else:
            # Postojeći FakeEngine / pyttsx3
            engine.say(message)
            engine.runAndWait()

        print(f"[VOICE] END: {message}", flush=True)

        return True

    def start(self, engine=None, engine_factory=None) -> None:
        if not self.enabled:
            return

        if self._worker is not None and self._worker.is_alive():
            return

        if engine is None and engine_factory is None:
            raise ValueError("Engine or engine_factory required")

        self._stop_event.clear()

        self._worker = threading.Thread(
            target=self._run,
            args=(engine, engine_factory),
            daemon=True,
        )
        self._worker.start()


    def _run(self, engine, engine_factory) -> None:
        if engine_factory is not None:
            pythoncom.CoInitialize()

            try:
                engine = engine_factory()

                while not self._stop_event.wait(0.05):
                    self._play_next_message(engine)

            finally:
                engine = None
                pythoncom.CoUninitialize()

        else:
            while not self._stop_event.wait(0.05):
                self._play_next_message(engine)

    def stop(self) -> None:
        self._stop_event.set()

        if self._worker is not None:
            self._worker.join(timeout=1.0)