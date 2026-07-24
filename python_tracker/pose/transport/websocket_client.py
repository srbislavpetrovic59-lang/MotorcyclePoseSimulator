from websockets.sync.client import ClientConnection, connect


class WebSocketClient:
    """Handles WebSocket transport."""

    def __init__(
        self,
        host: str,
        port: int,
    ) -> None:
        self._uri = f"ws://{host}:{port}"
        self._connection: ClientConnection | None = None

    def connect(self) -> None:
        """Opens the WebSocket connection."""
        self._connection = connect(self._uri)

    def disconnect(self) -> None:
        """Closes the WebSocket connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def send(
        self,
        message: str,
    ) -> None:
        """Sends a serialized message."""
        if self._connection is None:
            raise RuntimeError("WebSocket client is not connected.")

        self._connection.send(message)