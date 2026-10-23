from pose.feedback.voice_output import VoiceOutput


def test_voice_output_can_be_disabled():
    voice = VoiceOutput(enabled=False)

    assert voice.speak("Calibration complete") is False

def test_voice_output_accepts_message_when_enabled():
    voice = VoiceOutput(enabled=True)

    assert voice.speak("Lean calibration complete") is True

def test_voice_output_rejects_message_when_queue_is_full():
    voice = VoiceOutput(enabled=True)

    assert voice.speak("Message 1") is True
    assert voice.speak("Message 2") is True
    assert voice.speak("Message 3") is True

    assert voice.speak("Message 4") is False

    assert voice._queue.qsize() == 3

def test_voice_output_takes_next_message():
    voice = VoiceOutput(enabled=True)

    assert voice.speak("Lean calibration complete") is True

    assert voice._take_next_message() == "Lean calibration complete"
    assert voice._queue.empty()

def test_voice_output_plays_message_with_engine():
    class FakeEngine:
        def __init__(self):
            self.messages = []

        def say(self, message):
            self.messages.append(message)

        def runAndWait(self):
            pass

    engine = FakeEngine()
    voice = VoiceOutput(enabled=True)

    voice.speak("Lean calibration complete")

    assert voice._play_next_message(engine) is True
    assert engine.messages == ["Lean calibration complete"]
    assert voice._queue.empty()

def test_voice_output_starts_worker_thread():
    import threading

    class FakeEngine:
        def __init__(self):
            self.messages = []

        def say(self, message):
            self.messages.append(message)

        def runAndWait(self):
            pass

    voice = VoiceOutput(enabled=True)
    engine = FakeEngine()

    voice.start(engine)

    assert voice._worker is not None
    assert isinstance(voice._worker, threading.Thread)
    assert voice._worker.is_alive()

    voice.stop()

def test_voice_worker_plays_queued_message():
    import threading

    spoken = threading.Event()

    class FakeEngine:
        def say(self, message):
            if message == "Lean calibration complete":
                spoken.set()

        def runAndWait(self):
            pass

    voice = VoiceOutput(enabled=True)
    voice.start(FakeEngine())

    try:
        assert voice.speak("Lean calibration complete") is True
        assert spoken.wait(timeout=1.0)
    finally:
        voice.stop()

def test_voice_output_creates_sapi_engine_in_worker():
    import threading

    voice = VoiceOutput(enabled=True)

    created_in = []
    engine_created = threading.Event()

    def fake_engine_factory():
        created_in.append(threading.current_thread())
        engine_created.set()
        return object()

    voice.start(engine_factory=fake_engine_factory)

    try:
        assert engine_created.wait(timeout=1.0)
        assert created_in[0] is voice._worker
    finally:
        voice.stop()
def test_voice_output_initializes_com_in_worker(monkeypatch):
    import threading
    import pythoncom

    voice = VoiceOutput(enabled=True)

    events = []
    worker_finished = threading.Event()

    monkeypatch.setattr(
        pythoncom,
        "CoInitialize",
        lambda: events.append("initialize"),
    )

    monkeypatch.setattr(
        pythoncom,
        "CoUninitialize",
        lambda: events.append("uninitialize"),
    )

    def fake_engine_factory():
        events.append("create_engine")
        worker_finished.set()
        return object()

    voice.start(engine_factory=fake_engine_factory)

    try:
        assert worker_finished.wait(timeout=1.0)
    finally:
        voice.stop()

    assert events == [
        "initialize",
        "create_engine",
        "uninitialize",
    ]