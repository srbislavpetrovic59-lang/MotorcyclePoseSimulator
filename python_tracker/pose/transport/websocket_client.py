class WebSocketClient:
    """Handles WebSocket transport."""

    def __init__(
        self,
        host: str,
        port: int,
    ) -> None:
        """Initializes the client."""
        self._host = host
        self._port = port

    def connect(self) -> None:
        """Opens the connection."""
        raise NotImplementedError

    def disconnect(self) -> None:
        """Closes the connection."""
        raise NotImplementedError

    def send(
        self,
        message: str,
    ) -> None:
        """Sends a serialized message."""
        raise NotImplementedError