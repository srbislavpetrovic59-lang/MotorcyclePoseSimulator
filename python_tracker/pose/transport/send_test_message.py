'''from pose.transport.websocket_server import WebSocketServer


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
    '''
import asyncio
import websockets


async def send_hello():
    uri = "ws://127.0.0.1:8765"

    async with websockets.connect(uri) as websocket:
        await websocket.send("hello")
        print("Sent: hello")


asyncio.run(send_hello())