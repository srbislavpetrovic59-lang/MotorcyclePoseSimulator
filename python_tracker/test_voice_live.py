import time
import win32com.client

from pose.feedback.voice_output import VoiceOutput


def create_sapi_engine():
    return win32com.client.Dispatch("SAPI.SpVoice")


voice = VoiceOutput(enabled=True)

voice.start(engine_factory=create_sapi_engine)

try:
    print("First message...", flush=True)
    assert voice.speak("Lean calibration in three seconds.")

    time.sleep(3)

    print("Second message...", flush=True)
    assert voice.speak("Lean calibration complete.")

    time.sleep(3)

finally:
    voice.stop()

print("Finished.", flush=True)