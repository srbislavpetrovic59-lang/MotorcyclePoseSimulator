from __future__ import annotations

import json
from time import sleep

from pose.transport.websocket_server import WebSocketServer


def main() -> None:
    server = WebSocketServer()
    server.start()

    print("Waiting for Unreal...")

    if not server.wait_for_client(timeout=10.0):
        print("No Unreal client connected.")
        server.stop()
        return

    message = {
        "left_elbow": 90.0,
        "right_elbow": 95.0,
        "left_knee": 108.0,
        "right_knee": 110.0,
        "torso_angle": 88.5,
        "pose_confidence": 0.98,
    }

    server.send(json.dumps(message))
    print("Test JSON sent.")

    sleep(2)

    server.stop()


if __name__ == "__main__":
    main()