class WebSocketClient:
    """Handles WebSocket transport to Unreal Engine."""

    def send(self, message: str) -> None:
        raise NotImplementedError