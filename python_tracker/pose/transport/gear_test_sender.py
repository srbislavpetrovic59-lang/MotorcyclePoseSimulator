import time

from pose.models.rider_state import RiderState
from pose.transport.websocket_server import WebSocketServer


def main() -> None:
    server = WebSocketServer()
    server.start()

    try:
        print("Waiting for Unreal client...")
        time.sleep(10.0)

        for gear_shift in ["SHIFT_UP", "SHIFT_UP", "SHIFT_UP","SHIFT_UP", "SHIFT_UP", "SHIFT_UP","SHIFT_DOWN", "SHIFT_DOWN", "SHIFT_DOWN","SHIFT_DOWN", "SHIFT_DOWN", "SHIFT_DOWN"]:
            rider_state = RiderState(
                gear_shift=gear_shift,
                pose_confidence=0.98,
            )

            message = rider_state.to_json()
            server.send(message)

            print(f"Sent gear shift: {gear_shift}")
            time.sleep(2.0)

    finally:
        server.stop()


if __name__ == "__main__":
    main()