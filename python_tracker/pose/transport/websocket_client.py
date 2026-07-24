class WebSocketClient:
    """Handles WebSocket transport."""

    def __init__(self) -> None:
        """Initializes the WebSocket client."""

    def connect(self) -> None:
        raise NotImplementedError

    def disconnect(self) -> None:
        raise NotImplementedError

    def send(self, message: str) -> None:
        raise NotImplementedError