from pose.transport.websocket_server import WebSocketServer


def main() -> None:
    server = WebSocketServer()

    server.start()

    print("Waiting for Unreal...")

    if server.wait_for_client(timeout=30):
        print("Client connected.")
        server.send(
            '{"type":"pose_feedback","message":"Hello Unreal!"}'
        )
        input("Press Enter to stop server...")
    else:
        print("No client connected.")

    server.stop()


if __name__ == "__main__":
    main()