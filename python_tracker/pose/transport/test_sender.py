import time

from pose.models.rider_state import RiderState
from pose.transport.websocket_server import WebSocketServer


def main() -> None:
    server = WebSocketServer()
    server.start()

    try:
        print("Waiting for Unreal client...")
        time.sleep(3.0)

        rider_state = RiderState(
            left_elbow_angle=90.0,
            right_elbow_angle=95.0,
            pose_confidence=0.98,
        )

        message = rider_state.to_json()

        server.send(message)
        print(f"Sent RiderState: {message}")

        time.sleep(1.0)

    finally:
        server.stop()


if __name__ == "__main__":
    main()